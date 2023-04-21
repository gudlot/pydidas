# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the SelectPointsForBeamcenterWindow class which allows to select points
in an image to define the beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ManuallySetBeamcenterWindow"]

from pathlib import Path

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.core import (
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import (
    STANDARD_FONT_SIZE,
    CONFIG_WIDGET_WIDTH,
    DEFAULT_TWO_LINE_PARAM_CONFIG,
)
from pydidas.core.utils import (
    is_hdf5_filename,
    get_hdf5_populated_dataset_keys,
    fit_circle_from_points,
    fit_detector_center_and_tilt_from_points,
    calc_points_on_ellipse,
)
from pydidas.data_io import IoMaster
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.dialogues import Hdf5DatasetSelectionPopup, QuestionBox
from pydidas.widgets.misc import SelectPointsInImage
from pydidas.gui.windows.pydidas_window import PydidasWindow


class ManuallySetBeamcenterWindow(PydidasWindow):
    """
    A window which allows to open a file and select points to determine the beam center.
    """

    show_frame = False
    default_params = get_generic_param_collection(
        "filename",
        "hdf5_key",
        "hdf5_frame",
        "beamcenter_x",
        "beamcenter_y",
        "detector_tilt_angle",
        "detector_tilt_plane",
    )

    sig_selected_beamcenter = QtCore.Signal(float, float)
    sig_about_to_close = QtCore.Signal()

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(
            self, parent, title="Define beamcenter through selected points", **kwargs
        )
        self.__import_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="open_file",
            caption="Import image",
            formats=IoMaster.get_string_of_formats(),
            qsettings_ref="SelectPointsForBeamcenterWindow__import",
        )
        self._config = self._config | dict(
            select_mode_active=False,
            beamcenter_set=False,
        )
        self._markers = {}

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "label_title",
            "Define beamcenter through selected point",
            fontsize=STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 3),
        )
        self.create_empty_widget(
            "left_container", fixedWidth=CONFIG_WIDGET_WIDTH, minimumHeight=400
        )
        self.create_spacer(None, fixedWidth=25, gridPos=(1, 1, 1, 1))
        self.create_any_widget(
            "selector",
            SelectPointsInImage,
            minimumWidth=1000,
            minimumHeight=600,
            gridPos=(1, 2, 1, 1),
            enabled=False,
        )
        _button_params = dict(
            fixedWidth=CONFIG_WIDGET_WIDTH,
            fixedHeight=25,
            parent_widget=self._widgets["left_container"],
        )
        _param_config = dict(
            parent_widget=self._widgets["left_container"],
            visible=False,
            width_total=CONFIG_WIDGET_WIDTH,
            width_io=100,
            width_text=CONFIG_WIDGET_WIDTH - 130,
            width_unit=30,
        )

        self.create_label(
            "label_title",
            "Input file",
            fontsize=STANDARD_FONT_SIZE + 1,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            bold=True,
            parent_widget=self._widgets["left_container"],
        )

        self.create_button(
            "but_open",
            "Select image file",
            icon=self.style().standardIcon(42),
            **_button_params,
        )
        self.create_param_widget(
            self.get_param("filename"),
            **(
                DEFAULT_TWO_LINE_PARAM_CONFIG
                | dict(
                    parent_widget=self._widgets["left_container"],
                    persistent_qsettings_ref="SelectPointsForBeamcenterWindow__import",
                )
            ),
        )
        self.create_param_widget(
            self.get_param("hdf5_key"),
            **(
                DEFAULT_TWO_LINE_PARAM_CONFIG
                | dict(
                    parent_widget=self._widgets["left_container"],
                    visible=False,
                )
            ),
        )
        self.create_param_widget(
            self.get_param("hdf5_frame"), **(_param_config | dict(width_unit=0))
        )
        self.create_button(
            "but_confirm_file",
            "Confirm file selection",
            **_button_params,
            visible=False,
        )
        self.create_line("line_file", parent_widget=self._widgets["left_container"])
        self.create_spacer(
            None, fixedWidth=25, parent_widget=self._widgets["left_container"]
        )
        self.create_button(
            "but_set_beamcenter",
            "Set point as beamcenter",
            **_button_params,
        )
        self.create_button(
            "but_fit_circle",
            "Fit beamcenter with circle",
            **_button_params,
        )
        self.create_button(
            "but_fit_ellipse",
            "Fit beamcenter with ellipse",
            **_button_params,
        )
        self.create_line(None, parent_widget=self._widgets["left_container"])
        self.create_param_widget(self.get_param("beamcenter_x"), **_param_config)
        self.create_param_widget(self.get_param("beamcenter_y"), **_param_config)
        self.create_line(
            "line_final",
            parent_widget=self._widgets["left_container"],
        )
        self.create_button(
            "but_confirm_selection",
            "Confirm selected beamcenter",
            **_button_params,
        )
        self.create_spacer(
            "final_spacer",
            vertical_policy=QtWidgets.QSizePolicy.Expanding,
            parent_widget=self._widgets["left_container"],
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["but_open"].clicked.connect(self.open_image_dialog)
        self._widgets["but_confirm_selection"].clicked.connect(self._confirm_points)
        self._widgets["but_confirm_file"].clicked.connect(self._selected_new_file)
        self.param_widgets["filename"].io_edited.connect(
            self.process_new_filename_input
        )
        self._widgets["but_set_beamcenter"].clicked.connect(self._set_beamcenter)
        self._widgets["but_fit_circle"].clicked.connect(self._fit_beamcenter_circle)
        self._widgets["but_fit_ellipse"].clicked.connect(self._fit_beamcenter_ellipse)
        self.param_widgets["beamcenter_x"].io_edited.connect(
            self._manual_beamcenter_update
        )
        self.param_widgets["beamcenter_y"].io_edited.connect(
            self._manual_beamcenter_update
        )

    def finalize_ui(self):
        """
        Finalize the user interface.
        """

    @QtCore.Slot()
    def open_image_dialog(self):
        """
        Open the image selected through the filename.
        """
        _fname = self.__import_dialog.get_user_response()
        self.set_param_value_and_widget("filename", _fname)
        self.process_new_filename_input(_fname)

    @QtCore.Slot(str)
    def process_new_filename_input(self, filename):
        """
        Process the input of a new filename in the Parameter widget.

        Parameters
        ----------
        filename : str
            The filename.
        """
        if not Path(filename).is_file():
            self._toggle_file_selected(False)
            raise UserConfigError(
                "The selected filename is not a valid file. Please check the input "
                "and correct the path."
            )
        self._toggle_file_selected(True)
        if is_hdf5_filename(filename):
            _dsets = get_hdf5_populated_dataset_keys(filename, min_dim=2)
            if not self.get_param_value("hdf5_key", dtype=str) in _dsets:
                _dset = Hdf5DatasetSelectionPopup(self, filename).get_dset()
                if _dset is not None:
                    self.set_param_value_and_widget("hdf5_key", _dset)
        if not is_hdf5_filename(filename):
            self._selected_new_file()

    def _toggle_file_selected(self, is_selected):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        is_selected : bool
            Flag to process.
        """
        self._widgets["selector"].setEnabled(is_selected)
        _is_hdf5 = is_hdf5_filename(self.get_param_value("filename"))
        for _name in ["but_confirm_file"]:
            self._widgets[_name].setVisible(is_selected and _is_hdf5)
        for _name in ["hdf5_key", "hdf5_frame"]:
            self.param_composite_widgets[_name].setVisible(is_selected and _is_hdf5)

    @QtCore.Slot()
    def _selected_new_file(self):
        """
        Open a new file / frame based on the input Parameters.
        """
        self._widgets["selector"].open_image(
            self.get_param_value("filename"),
            dataset=self.get_param_value("hdf5_key", dtype=str),
            frame=self.get_param_value("hdf5_frame"),
        )

    @QtCore.Slot()
    def _set_beamcenter(self):
        """
        Set the beamcenter from a single point.
        """
        _x, _y = self._widgets["selector"].get_selected_points()
        if _x.size != 1:
            self._toggle_beamcenter_is_set(False)
            self._widgets["selector"].set_beamcenter_marker(None)
            raise UserConfigError(
                "Please select exactly one point in the image to set the beamcenter "
                "directly."
            )
        self._widgets["selector"].set_beamcenter_marker((_x[0], _y[0]))
        self._widgets["selector"].show_outline(None)
        self.set_param_value_and_widget("beamcenter_x", _x[0])
        self.set_param_value_and_widget("beamcenter_y", _y[0])
        self._toggle_beamcenter_is_set(True)

    def _fit_beamcenter_circle(self):
        """
        Fit the beamcenter through a circle.
        """
        _x, _y = self._widgets["selector"].get_selected_points()
        if _x.size < 3:
            self._toggle_beamcenter_is_set(False)
            self._widgets["selector"].set_beamcenter_marker(None)
            self._widgets["selector"].show_outline(None)
            raise UserConfigError(
                "Please select at least three points to fit a circle for beamcenter "
                "determination."
            )
        _cx, _cy, _r = fit_circle_from_points(_x, _y)
        self._widgets["selector"].set_beamcenter_marker((_cx, _cy))
        self.set_param_value_and_widget("beamcenter_x", np.round(_cx, 4))
        self.set_param_value_and_widget("beamcenter_y", np.round(_cy, 4))
        self._toggle_beamcenter_is_set(True)
        _theta = np.linspace(0, 2 * np.pi, num=73, endpoint=True)
        _x = np.cos(_theta) * _r + _cx
        _y = np.sin(_theta) * _r + _cy
        self._widgets["selector"].show_outline((_x, _y))

    def _fit_beamcenter_ellipse(self):
        """
        Fit the beamcenter through an ellipse.
        """
        _x, _y = self._widgets["selector"].get_selected_points()
        if _x.size < 5:
            self._toggle_beamcenter_is_set(False)
            self._widgets["selector"].set_beamcenter_marker(None)
            self._widgets["selector"].show_outline(None)
            raise UserConfigError(
                "Please select at least five points to fit a fully-defined ellipse "
                "for beamcenter determination."
            )
        (
            _cx,
            _cy,
            _tilt,
            _tilt_plane,
            _coeffs,
        ) = fit_detector_center_and_tilt_from_points(_x, _y)
        self._widgets["selector"].set_beamcenter_marker((_cx, _cy))
        self.set_param_value_and_widget("beamcenter_x", np.round(_cx, 4))
        self.set_param_value_and_widget("beamcenter_y", np.round(_cy, 4))
        self._toggle_beamcenter_is_set(True)
        _x, _y = calc_points_on_ellipse(_coeffs)
        self._widgets["selector"].show_outline((_x, _y))

    def _toggle_beamcenter_is_set(self, is_set):
        """
        Toggle the visibility of the Parameter widgets for the results.

        Parameters
        ----------
        is_set : bool
            The new visibility.
        """
        for _name in ["beamcenter_x", "beamcenter_y"]:
            self.param_composite_widgets[_name].setVisible(is_set)
        self._config["beamcenter_set"] = is_set

    @QtCore.Slot(str)
    def _manual_beamcenter_update(self, pos):
        """
        Call the manual setting of a new beamcenter position

        Parameters
        ----------
        pos : str
            The new beamcenter pos value.
        """
        _x = self.get_param_value("beamcenter_x")
        _y = self.get_param_value("beamcenter_y")
        self._widgets["selector"].set_beamcenter_marker((_x, _y))
        self._widgets["selector"].show_outline(None)

    @QtCore.Slot()
    def _confirm_points(self):
        """
        Confirm the selection of the specified points.
        """
        if not self._config["beamcenter_set"]:
            _reply = QuestionBox(
                "Beamcenter not set",
                "No beamcenter has been set. Do you want to close the window without "
                "setting a beamcenter?",
            ).exec_()
            if _reply:
                self.close()
            return
        _x = self.get_param_value("beamcenter_x")
        _y = self.get_param_value("beamcenter_y")
        self.sig_selected_beamcenter.emit(_x, _y)
        self.close()

    def closeEvent(self, event):
        """
        Handle the close event and also emit a signal.

        Parameters
        ----------
        event : QEvent
            The calling event.
        """
        self.sig_about_to_close.emit()
        super().closeEvent(event)
