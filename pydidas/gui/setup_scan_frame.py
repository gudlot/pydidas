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

"""
Module with the SetupScanFrame which is used to manage and modify the scan
settings like dimensionality, number of points and labels.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SetupScanFrame"]

import sys

from qtpy import QtWidgets

from ..experiment import SetupScan, SetupScanIoMeta
from ..widgets import gui_excepthook
from .builders import SetupScanFrameBuilder


SCAN_SETTINGS = SetupScan()


class SetupScanFrame(SetupScanFrameBuilder):
    """
    Frame for managing the global scan settings.
    """

    menu_icon = "qta::ei.move"
    menu_title = "Scan settings"
    menu_entry = "Workflow processing/Scan settings"

    def __init__(self, parent=None, **kwargs):
        SetupScanFrameBuilder.__init__(self, parent, **kwargs)

    def connect_signals(self):
        """
        Connect all required signals and slots.
        """
        self._widgets["but_save"].clicked.connect(self.export_to_file)
        self._widgets["but_load"].clicked.connect(self.load_from_file)
        self._widgets["but_reset"].clicked.connect(self.reset_entries)
        self.param_widgets["scan_dim"].currentTextChanged.connect(
            self.update_dim_visibility
        )

    def finalize_ui(self):
        """
        Finalize the UI initialization.
        """
        self.update_dim_visibility()
        for param in SCAN_SETTINGS.params.values():
            self.param_widgets[param.refkey].set_value(param.value)

    def update_dim_visibility(self):
        """
        Update the visibility of dimensions based on the selected number
        of scan dimensions.
        """
        _prefixes = [
            "scan_label_{n}",
            "n_points_{n}",
            "delta_{n}",
            "unit_{n}",
            "offset_{n}",
        ]
        _dim = int(self.param_widgets["scan_dim"].currentText())
        for i in range(1, 5):
            _toggle = i <= _dim
            self._widgets[f"title_{i}"].setVisible(_toggle)
            for _pre in _prefixes:
                self.toggle_param_widget_visibility(_pre.format(n=i), _toggle)

    def update_param(self, param_ref, widget):
        """
        Overload the update of a parameter method to handle the linked
        X-ray energy / X-ray wavelength variables.

        Parameters
        ----------
        param_ref : str
            The Parameter reference key
        widget : pydidas.widgets.parameter_config.BaseParamIoWidget
            The widget used for the I/O of the Parameter value.
        """
        try:
            SCAN_SETTINGS.set(param_ref, widget.get_value())
        except Exception:
            widget.set_value(SCAN_SETTINGS.get(param_ref))
            gui_excepthook(*sys.exc_info())
        # explicitly call update fo wavelength and energy
        if param_ref == "xray_wavelength":
            _w = self.param_widgets["xray_energy"]
            _w.set_value(SCAN_SETTINGS.get("xray_energy"))
        elif param_ref == "xray_energy":
            _w = self.param_widgets["xray_wavelength"]
            _w.set_value(SCAN_SETTINGS.get("xray_wavelength") * 1e10)

    def load_from_file(self):
        """
        Load SetupScan from a file.

        This method will open a QFileDialog to select the file to be read.
        """
        _formats = SetupScanIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, "Name of file", None, _formats
        )[0]
        if fname != "":
            SCAN_SETTINGS.import_from_file(fname)
            for param in SCAN_SETTINGS.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    def export_to_file(self):
        """
        Save SetupScan to a file.

        This method will open a QFileDialog to select a filename for the
        file in which the information shall be written.
        """
        _formats = SetupScanIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self, "Name of file", None, _formats
        )[0]
        if fname != "":
            SCAN_SETTINGS.export_to_file(fname, overwrite=True)

    def reset_entries(self):
        """
        Reset all ScanSetting entries to their default values.
        """
        SCAN_SETTINGS.restore_all_defaults(True)
        for param in SCAN_SETTINGS.params.values():
            self.param_widgets[param.refkey].set_value(param.value)