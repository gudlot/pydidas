# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The pydidas_widget_mixin module includes the PydidasWidgetMixin class to add additional
functionality implemented in PydidasQApplication.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasWidgetMixin"]


from qtpy import QtCore
from qtpy.QtWidgets import QApplication

from ...core.utils import apply_qt_properties, update_qobject_font


class PydidasWidgetMixin:
    """
    Mixin class to handle automatic font updated from the QApplication.

    This class allows to use custom font settings (different sizes, bold etc) and
    still update them automatically.
    """

    init_kwargs = [
        "size_offset",
        "bold",
        "italic",
        "underline",
        "font_metric_width_factor",
    ]

    def __init__(self, **kwargs: dict):
        """
        Set up the class instance of the subclassed QWidget.

        Parameters
        ----------
        **kwargs : dict
            Any kwargs for setting the font or other Qt parameters.
        """
        apply_qt_properties(self, **kwargs)
        self.__font_config = {
            "size_offset": kwargs.get("fontsize_offset", 0),
            "bold": kwargs.get("bold", False),
            "italic": kwargs.get("italic", False),
            "underline": kwargs.get("underline", False),
        }
        self._qtapp = QApplication.instance()
        self.update_fontsize(self._qtapp.standard_font_size)
        self.update_font_family(self._qtapp.standard_font_family)
        self._qtapp.sig_new_fontsize.connect(self.update_fontsize)
        self._qtapp.sig_new_font_family.connect(self.update_font_family)
        if True in self.__font_config.values():
            update_qobject_font(self, **self.__font_config)
        if "font_metric_width_factor" in kwargs:
            self.__font_metric_width_factor = kwargs.get("font_metric_width_factor")
            self.set_dynamic_width_from_font(self._qtapp.standard_font_height)
            self._qtapp.sig_new_font_height.connect(self.set_dynamic_width_from_font)

    @QtCore.Slot(float)
    def update_fontsize(self, new_fontsize: float):
        """
        Update the fontsize with the new global default.

        Parameters
        ----------
        new_fontsize : float
            The new font size.
        """
        _font = self.font()
        _font.setPointSizeF(new_fontsize + self.__font_config["size_offset"])
        self.setFont(_font)

    @QtCore.Slot(str)
    def update_font_family(self, new_family: str):
        """
        Update the font family.

        Parameters
        ----------
        new_family : str
            The name of the new font family.
        """
        _font = self.font()
        _font.setFamily(new_family)
        self.setFont(_font)

    @QtCore.Slot(float)
    def set_dynamic_width_from_font(self, font_height: float):
        """
        Set the fixed width of the widget dynamically from the font height metric.

        Parameters
        ----------
        font_height : float
            The font height in pixels.
        """
        self.setFixedWidth(int(self.__font_metric_width_factor * font_height))