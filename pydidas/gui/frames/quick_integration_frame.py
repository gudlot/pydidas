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
Module with the QuickIntegrationFrame which is allows to perform a quick integration
without fully defining Scan, DiffractionExperiment and Workflow.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["QuickIntegrationFrame"]


from functools import partial

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.contexts import DiffractionExperimentIo
from pydidas.contexts.diffraction_exp_context import DiffractionExperiment
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.framework import BaseFrame
from pydidas.core import get_generic_param_collection
from pydidas.data_io import import_data
from pydidas.widgets.controllers import (
    ManuallySetBeamcenterController,
    ManuallySetIntegrationRoiController,
)
from pydidas.core.utils import ShowBusyMouse
from pydidas.plugins import PluginCollection, pyFAIintegrationBase
from pydidas.gui.frames.builders import QuickIntegrationFrameBuilder

COLL = PluginCollection()


class QuickIntegrationFrame(BaseFrame):
    """
    The QuickIntegrationFrame allows to perform a quick integration without fully
    defining Scan, DiffractionExperiment and Workflow.
    """

    menu_icon = "pydidas::frame_icon_quick_integration.png"
    menu_title = "Quick integration"
    menu_entry = "Quick integration"
    default_params = get_generic_param_collection(
        "detector_pxsize",
        "beamcenter_x",
        "beamcenter_y",
        "filename",
        "hdf5_key",
        "hdf5_frame",
        "overlay_color",
        "integration_direction",
        "azi_npoint",
        "rad_npoint",
    )

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)
        self._EXP = DiffractionExperiment(detector_pxsizex=100, detector_pxsizey=100)
        self.add_params(self._EXP.params)
        self.set_default_params()
        self.__import_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="open_file",
            caption="Import diffraction experiment configuration",
            formats=DiffractionExperimentIo.get_string_of_formats(),
            qsettings_ref="QuickIntegrationFrame__diffraction_exp_import",
        )
        self.__export_dialog = PydidasFileDialog(
            parent=self,
            dialog_type="save_file",
            caption="Export experiment context file",
            formats=DiffractionExperimentIo.get_string_of_formats(),
            default_extension="yaml",
            dialog=QtWidgets.QFileDialog.getSaveFileName,
            qsettings_ref="DefineDiffractionExpFrame__export",
        )
        self._config["scroll_width"] = 350
        _generic = pyFAIintegrationBase(diffraction_exp=self._EXP)
        self._plugins = {
            "generic": _generic,
            "Azimuthal integration": COLL.get_plugin_by_name(
                "PyFAIazimuthalIntegration"
            )(_generic.params, diffraction_exp=self._EXP),
            "Radial integration": COLL.get_plugin_by_name("PyFAIradialIntegration")(
                _generic.params, diffraction_exp=self._EXP
            ),
            "2D integration": COLL.get_plugin_by_name("PyFAI2dIntegration")(
                _generic.params, diffraction_exp=self._EXP
            ),
        }

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        QuickIntegrationFrameBuilder.populate_frame(self)

    def connect_signals(self):
        """
        Connect all signals.
        """
        self._bc_controller = ManuallySetBeamcenterController(
            self,
            self._widgets["input_plot"],
            self._widgets["input_beamcenter_points"],
            selection_active=False,
        )
        self._roi_controller = ManuallySetIntegrationRoiController(
            self._widgets["roi_selector"],
            self._widgets["input_plot"],
            plugin=self._plugins["generic"],
        )
        self._roi_controller.sig_toggle_selection_mode.connect(
            self._roi_selection_toggled
        )

        self._widgets["file_selector"].sig_new_file_selection.connect(self.open_image)
        self._widgets["file_selector"].sig_file_valid.connect(self._toggle_fname_valid)

        self._widgets["but_import_exp"].clicked.connect(self._import_diffraction_exp)
        for _label in ["but_select_beamcenter_manually", "but_confirm_beamcenter"]:
            self._widgets[_label].clicked.connect(self._toggle_beamcenter_selection)
        self._widgets["but_set_beamcenter"].clicked.connect(
            self._bc_controller.set_beamcenter_from_point
        )
        self._widgets["but_fit_center_circle"].clicked.connect(
            self._bc_controller.fit_beamcenter_with_circle
        )
        self.param_widgets["overlay_color"].io_edited.connect(
            self._bc_controller.set_marker_color
        )
        self.param_widgets["detector_pxsize"].io_edited.connect(
            self._update_detector_pxsize
        )
        self.param_widgets["integration_direction"].io_edited.connect(
            self._changed_plugin_direction
        )
        self._widgets["but_run_integration"].clicked.connect(self._run_integration)

        for _section in ["exp", "integration"]:
            for _type in ["hide", "show"]:
                self._widgets[f"but_{_type}_{_section}_section"].clicked.connect(
                    partial(
                        self._widgets[f"{_section}_section"].setVisible, _type == "show"
                    )
                )
                self._widgets[f"but_{_type}_{_section}_section"].clicked.connect(
                    partial(
                        self._widgets[f"but_show_{_section}_section"].setVisible,
                        _type == "hide",
                    )
                )
        for _param_key in ["xray_energy", "xray_wavelength"]:
            _w = self.param_widgets[_param_key]
            _w.io_edited.disconnect()
            _w.io_edited.connect(partial(self._update_xray_param, _param_key, _w))
        for _param_key in ["beamcenter_x", "beamcenter_y"]:
            self.param_widgets[_param_key].io_edited.connect(self._update_beamcenter)

    @QtCore.Slot(str, object)
    def open_image(self, filename, kwargs):
        """
        Open an image with the given filename and display it in the plot.

        Parameters
        ----------
        filename : Union[str, Path]
            The filename and path.
        kwargs : dict
            Additional parameters to open a specific frame in a file.
        """
        self._image = import_data(filename, **kwargs)
        self._EXP.set_param_value("detector_npixx", self._image.shape[1])
        self._EXP.set_param_value("detector_npixy", self._image.shape[0])
        self._widgets["input_plot"].plot_pydidas_dataset(self._image)
        self._widgets["input_plot"].changeCanvasToDataAction._actionTriggered()
        self._roi_controller.show_plot_items("roi")
        for _key in [
            "beamcenter_section",
            "integration_header",
            "integration_section",
            "run_integration",
        ]:
            self._widgets[_key].setVisible(True)

    @QtCore.Slot(bool)
    def _toggle_fname_valid(self, is_valid):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        is_valid : bool
            Flag to process.
        """
        self._widgets["input_plot"].setEnabled(is_valid)
        if not is_valid:
            for _key in [
                "beamcenter_section",
                "integration_header",
                "integration_section",
                "run_integration",
            ]:
                self._widgets[_key].setVisible(False)

    def set_param_value_and_widget(self, key, value):
        """
        Update a Parameter value both in the widget and ParameterCollection.

        This method overloads the generic set_param_value_and_widget method to
        process the linked energy / wavelength parameters.

        Parameters
        ----------
        key : str
            The Parameter reference key.
        value : object
            The new Parameter value. The datatype is determined by the
            Parameter.
        """
        if key in self._EXP.params:
            self._EXP.set_param_value(key, value)
            if key in ["xray_energy", "xray_wavelength"]:
                _energy = self.get_param_value("xray_energy")
                _lambda = self.get_param_value("xray_wavelength")
                self.param_widgets["xray_energy"].set_value(_energy)
                self.param_widgets["xray_wavelength"].set_value(_lambda)
            else:
                self.param_widgets[key].set_value(value)
        else:
            BaseFrame.set_param_value_and_widget(self, key, value)

    def _update_xray_param(self, param_key, widget):
        """
        Update a value in both the Parameter and the corresponding widget.

        Parameters
        ----------
        param_key : str
            The reference key.
        widget : pydidas.widgets.parameter_config.BaseParamIoWidget
            The Parameter editing widget.
        """
        self._EXP.set_param_value(param_key, widget.get_value())
        # explicitly call update fo wavelength and energy
        if param_key == "xray_wavelength":
            _w = self.param_widgets["xray_energy"]
            _w.set_value(self._EXP.get_param_value("xray_energy"))
        elif param_key == "xray_energy":
            _w = self.param_widgets["xray_wavelength"]
            _w.set_value(self._EXP.get_param_value("xray_wavelength"))

    @QtCore.Slot(str)
    def _update_detector_pxsize(self, new_pxsize: str):
        """
        Update the detector pixel size.

        Parameters
        ----------
        new_pxsize : str
            The new pixelsize.
        """
        _pxsize = float(new_pxsize)
        self._EXP.set_param_value("detector_pxsizex", _pxsize)
        self._EXP.set_param_value("detector_pxsizey", _pxsize)

    @QtCore.Slot(str)
    def _update_beamcenter(self, _):
        """
        Update the DiffractionExperiment's stored PONI from the beamcenter.
        """
        _bx = self.get_param_value("beamcenter_x")
        _by = self.get_param_value("beamcenter_y")
        _dist = self.get_param_value("detector_dist")
        self._EXP.set_beamcenter_from_fit2d_params(_bx, _by, _dist)

    @QtCore.Slot()
    def _toggle_beamcenter_selection(self):
        """
        Toggle the manual beamcenter selection.
        """
        _active = not self._bc_controller.selection_active
        self._bc_controller.toggle_selection_active(_active)
        self._widgets["input_plot_bc_selection"].setVisible(_active)
        for _txt in ["confirm_beamcenter", "set_beamcenter", "fit_center_circle"]:
            self._widgets[f"but_{_txt}"].setVisible(_active)
        self._widgets["but_select_beamcenter_manually"].setVisible(not _active)
        self._widgets["label_overlay_color"].setVisible(not _active)
        self._roi_controller.toggle_marker_color_param_visibility(not _active)
        self._roi_controller.toggle_enable(not _active)
        if _active:
            self._bc_controller.show_plot_items("all")
            self._roi_controller.remove_plot_items("roi")
            self._widgets["tabs"].setCurrentIndex(0)
        else:
            self._bc_controller.remove_plot_items("all")
            self._roi_controller.show_plot_items("roi")
            self._update_beamcenter(None)

    @QtCore.Slot(bool)
    def _roi_selection_toggled(self, active: bool):
        """
        Handle toggling of the integration ROI selection.

        Parameters
        ----------
        active : bool
            ROI selection active flag.
        """
        self._widgets["tabs"].setCurrentIndex(0)
        self._widgets["but_import_exp"].setEnabled(not active)
        self._widgets["but_select_beamcenter_manually"].setEnabled(not active)
        for _key in [
            "xray_energy",
            "xray_wavelength",
            "detector_pxsize",
            "detector_dist",
            "detector_mask_file",
            "beamcenter_x",
            "beamcenter_y",
        ]:
            self.param_widgets[_key].setEnabled(not active)

    @QtCore.Slot(str)
    def _changed_plugin_direction(self, direction: str):
        """
        Handle the selection of a new type of plugin.

        Parameters
        ----------
        direction : str
            The integration direction.
        """
        self.toggle_param_widget_visibility(
            "azi_npoint", direction != "Azimuthal integration"
        )
        self.toggle_param_widget_visibility(
            "rad_npoint", direction != "Radial integration"
        )

    def _import_diffraction_exp(self):
        """
        Open a dialog to select a filename and load the DiffractionExperiment.

        Note: This method will overwrite all current settings.
        """
        _fname = self.__import_dialog.get_user_response()
        if _fname is not None:
            self._EXP.import_from_file(_fname)
            for _key, _param in self._EXP.params.items():
                if _key in self.param_widgets:
                    self.param_widgets[_key].set_value(_param.value)
        _cx, _cy = self._EXP.beamcenter
        self.update_widget_value("beamcenter_x", np.round(_cx, 3))
        self.update_widget_value("beamcenter_y", np.round(_cy, 3))

    @QtCore.Slot()
    def _run_integration(self):
        """
        Run the integration in the pyFAI plugin.
        """
        _dir = self.get_param_value("integration_direction")
        _plugin = self._plugins[_dir]
        if _dir != "Azimuthal integration":
            _plugin.set_param_value("azi_npoint", self.get_param_value("azi_npoint"))
        if _dir != "Radial integration":
            _plugin.set_param_value("rad_npoint", self.get_param_value("rad_npoint"))
        with ShowBusyMouse():
            _plugin.pre_execute()
            _results, _ = _plugin.execute(self._image)
            self._widgets["result_plot"].plot_data(_results)
            self._widgets["tabs"].setCurrentIndex(1)

    def export_to_file(self):
        """
        Open a dialog to select a filename and write all currrent settings
        for the DiffractionExperimentContext to file.
        """
        _fname = self.__export_dialog.get_user_response()
        if _fname is not None:
            self._EXP.export_to_file(_fname, overwrite=True)


if __name__ == "__main__":
    import pydidas

    app = pydidas.core.PydidasQApplication([])
    PC = pydidas.plugins.PluginCollection()
    EXP = pydidas.contexts.DiffractionExperimentContext()
    EXP.import_from_file("E:/MATRAC/Analysis/experiment_context.yaml")
    EXP.set_beamcenter_from_fit2d_params(
        5000, -1000, EXP.get_param_value("detector_dist")
    )
    _plugin = PC.get_plugin_by_name("PyFAIazimuthalIntegration")()
    window = QuickIntegrationFrame()
    window.frame_activated(window.frame_index)
    window.show()
    app.exec_()