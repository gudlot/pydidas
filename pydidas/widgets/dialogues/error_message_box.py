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
Module with ErrorMessageBox class for exception output.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ErrorMessageBox"]

import os

from qtpy import QtCore, QtWidgets, QtGui, QtSvg

from ...core.utils import (
    get_logging_dir,
    get_pydidas_error_icon_w_bg,
    get_pydidas_icon_path,
)
from ...core.constants import EXP_EXP_POLICY, PYDIDAS_FEEDBACK_URL
from ..utilities import apply_widget_properties
from ..factory import CreateWidgetsMixIn
from ..scroll_area import ScrollArea


class ErrorMessageBox(QtWidgets.QDialog, CreateWidgetsMixIn):
    """
    Show a dialogue box with exception information.

    Parameters
    ----------
    *args : tuple
        Arguments passed to QtWidgets.QDialogue instanciation.
    **kwargs : dict
        Keyword arguments passed to QtWidgets.QDialogue instanciation.
    """

    def __init__(self, *args, **kwargs):
        self._text = kwargs.pop("text", "")
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.setWindowTitle("Unhandled exception")
        self.setWindowIcon(get_pydidas_error_icon_w_bg())
        _layout = QtWidgets.QGridLayout()
        self.setLayout(_layout)

        self.create_label(
            "title",
            "An unhandled exception has occurred",
            fontsize=12,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self._widgets["label"] = QtWidgets.QLabel()
        apply_widget_properties(
            self._widgets["label"],
            textInteractionFlags=QtCore.Qt.TextSelectableByMouse,
            sizePolicy=EXP_EXP_POLICY,
            indent=8,
            fixedWidth=675,
        )

        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            widget=self._widgets["label"],
            gridPos=(1, 0, 1, 2),
        )
        self.create_button("button_okay", "OK", gridPos=(2, 3, 1, 1))
        self.create_button(
            "button_copy", "Copy to clipboard and open webpage", gridPos=(2, 0, 1, 1)
        )

        _icon_fname = os.path.join(get_pydidas_icon_path(), "pydidas_error.svg")
        self.add_any_widget(
            "icon",
            QtSvg.QSvgWidget(_icon_fname),
            fixedHeight=150,
            fixedWidth=150,
            layout_kwargs={"alignment": (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)},
            gridPos=(0, 2, 2, 2),
        )

        self._widgets["button_okay"].clicked.connect(self.close)
        self._widgets["button_copy"].clicked.connect(
            self.copy_to_clipboard_and_open_webpage
        )
        self.resize(860, self.height())
        self.set_text(self._text)

    def set_text(self, text):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        """
        _logfile = os.path.join(get_logging_dir(), "pydidas_exception.log")
        _note = (
            "Please report the bug online using the following form:\n"
            "\thttps://ms.hereon.de/pydidas\n\n"
            "You can simply use the button on the bottom left to open the\n"
            "Webpage in your default browser. The exception trace has been \n"
            "copied to your clipboard."
            f"\n\nA log has been written to:\n\t{_logfile}\n\n"
            + "-" * 20
            + "\n"
            + "Exception trace:\n\n"
        )
        self._text = text
        self._copy_trace_to_clipboard()
        self._widgets["label"].setText(_note + text)

    def copy_to_clipboard_and_open_webpage(self):
        """
        Copy the trace to the clipboard and open the URL for the pydidas
        feedback form.
        """
        self._copy_trace_to_clipboard()
        QtGui.QDesktopServices.openUrl(PYDIDAS_FEEDBACK_URL)

    def _copy_trace_to_clipboard(self):
        """
        Copy the exception trace to the system's clipboard.
        """
        _clip = QtWidgets.QApplication.clipboard()
        _clip.clear(mode=_clip.Clipboard)
        _clip.setText(self._text, mode=_clip.Clipboard)
