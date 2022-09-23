# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.
#
# Parts of this file are adapted based on the pyfai-calib widget which is distributed
# under the license given below:
#
# /*##########################################################################
#
# Copyright (C) 2016-2018 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


"""
Module with the PyfaiCalibFrame which is a subclassed pyfai-calib2 widget
to be used within pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PyfaiCalibFrame", "get_pyfai_calib_icon_path"]

import os
import functools

from qtpy import QtWidgets, QtGui, QtCore
import pyFAI
from pyFAI.app.calib2 import parse_options, setup_model
from pyFAI.gui.model import MarkerModel
from pyFAI.gui.utils import projecturl
from pyFAI.gui.CalibrationWindow import MenuItem
from pyFAI.gui.CalibrationContext import CalibrationContext

from ...core import constants
from ...widgets import BaseFrame
from ...experiment import SetupExperiment


EXP_SETUP = SetupExperiment()


def get_pyfai_calib_icon_path():
    """
    Get the pyFAI calibration icon.

    Returns
    -------
    str
        The full path and filename for pyFAI calibration icon.
    """
    return os.sep.join(
        [os.path.dirname(pyFAI.__file__), "resources", "gui", "images", "icon.png"]
    )


class PyfaiCalibFrame(BaseFrame):
    """
    A pyFAI Calibration frame similar to the "pyfai-calib2", adapted to be
    used within pydidas.

    Note: Because this code is taking almost 100 % from pyFAI, the names,
    nomenclature and code structure is different from the rest of pydidas.

    Acknowledgements go to the creators of pyFAI for making it freely
    available.
    """

    menu_icon = "path::" + get_pyfai_calib_icon_path()
    menu_title = "pyFAI calibration"
    menu_entry = "pyFAI calibration"

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)
        self._setup_pyfai_context()
        self._CALIB_CONTEXT.setParent(self)

        self.setUpdatesEnabled(False)
        self._list = QtWidgets.QListWidget(self)
        self._list.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding
        )
        self._list.setFixedWidth(150)
        self._help = QtWidgets.QPushButton(self)
        self._help.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        self._stack = QtWidgets.QStackedWidget(self)
        self._stack.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        self.create_label(
            "title",
            "pyFAI calibration",
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.add_any_widget("list", self._list, gridPos=(1, 0, 1, 1))
        self.add_any_widget("help", self._help, gridPos=(2, 0, 1, 1))
        self.add_any_widget("help", self._stack, gridPos=(1, 1, 2, 1))

        model = self._CALIB_CONTEXT.getCalibrationModel()

        self.__menu_connections = {}
        self.__tasks = self.createTasks()
        for task in self.__tasks:
            task.nextTaskRequested.connect(self.nextTask)
            item = MenuItem(self._list)
            item.setText(task.windowTitle())
            item.setIcon(task.windowIcon())
            self._stack.addWidget(task)
            self.__menu_connections[item.text()] = task
            task.warningUpdated.connect(
                functools.partial(self.__updateTaskState, task, item)
            )

        if len(self.__tasks) > 0:
            self._list.setCurrentRow(0)
            # Hide the nextStep button of the last task
            task.setNextStepVisible(False)

        self.setModel(model)
        self._list.currentRowChanged.connect(self._stack.setCurrentIndex)

        url = projecturl.get_documentation_url("")
        if url.startswith("http"):
            self._help.setText("Online help...")
        self._helpText = self._help.text()
        self._help.clicked.connect(self.__displayHelp)
        self.setUpdatesEnabled(True)

    def _setup_pyfai_context(self):
        """
        Setup the context for the pyfai calibration.
        """
        PYFAI_SETTINGS = QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            "pyfai",
            "pyfai-calib2",
            None,
        )

        CalibrationContext._releaseSingleton()
        _calib_context = CalibrationContext(PYFAI_SETTINGS)
        _calib_context.restoreSettings()
        options = parse_options()
        setup_model(_calib_context.getCalibrationModel(), options)
        self._CALIB_CONTEXT = _calib_context

    def __displayHelp(self):
        subpath = "usage/cookbook/calib-gui/index.html"
        url = projecturl.get_documentation_url(subpath)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def __updateTaskState(self, task, item):
        warnings = task.nextStepWarning()
        item.setWarnings(warnings)

    def update_stack(self, text):
        w = self.__menu_connections[text]
        self._stack.setCurrentWidget(w)

    def closeEvent(self, event):
        event.accept()
        for task in self.__tasks:
            task.aboutToClose()

    def createTasks(self):
        # Tasks must be imported here, a global import will cause errors
        # because they will create QtWidgets before the QtApplication
        # is instantiated.
        from pyFAI.gui.tasks import (
            ExperimentTask,
            MaskTask,
            PeakPickingTask,
            GeometryTask,
            IntegrationTask,
        )

        tasks = [
            ExperimentTask.ExperimentTask(),
            MaskTask.MaskTask(),
            PeakPickingTask.PeakPickingTask(),
            GeometryTask.GeometryTask(),
            IntegrationTask.IntegrationTask(),
        ]
        return tasks

    def model(self):
        return self.__model

    def setModel(self, model):
        self.__model = model
        if len(self.__model.markerModel()) == 0:
            origin = MarkerModel.PixelMarker("Origin", 0, 0)
            self.__model.markerModel().add(origin)
        for task in self.__tasks:
            task.setModel(self.__model)

    def nextTask(self):
        index = self._list.currentRow() + 1
        if index < self._list.count():
            self._list.setCurrentRow(index)

    def _store_geometry(self):
        geo = self.model().fittedGeometry()
        det = self.model().experimentSettingsModel().detector()
        EXP_SETUP.set_param_value("xray_wavelength", geo.wavelength().value())
        EXP_SETUP.set_param_value("detector_dist", geo.distance().value())
        EXP_SETUP.set_param_value("detector_poni1", geo.poni1().value())
        EXP_SETUP.set_param_value("detector_poni2", geo.poni2().value())
        EXP_SETUP.set_param_value("detector_rot1", geo.rotation1().value())
        EXP_SETUP.set_param_value("detector_rot2", geo.rotation2().value())
        EXP_SETUP.set_param_value("detector_rot3", geo.rotation3().value())
        EXP_SETUP.set_param_value("detector_name", det.name)
        EXP_SETUP.set_param_value("detector_npixx", det.shape[1])
        EXP_SETUP.set_param_value("detector_npixy", det.shape[0])
        EXP_SETUP.set_param_value("detector_pxsizex", det.pixel2)
        EXP_SETUP.set_param_value("detector_pxsizey", det.pixel1)
