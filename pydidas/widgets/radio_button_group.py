# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the RadioButtonGroup widget which can hold multiple QadioButtons.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['RadioButtonGroup']

from PyQt5 import QtCore, QtWidgets


class RadioButtonGroup(QtWidgets.QWidget):
    """
    The RadioButtonGroup is a Widget which can hold a number of QRadioButtons
    in a QButtonGroup. Creation is automated based on the entries.
    """

    new_button = QtCore.pyqtSignal(int, str)

    def __init__(self, parent=None, entries=None, vertical=True):
        """
        Create a new RadioButtonGroup.

        Parameters
        ----------
        parent : Union[QtWidgets.QWidget, None]
            The widget's parent. The default is None.
        entries : list
            The list of entries for the QRadioButtons. The default is [].
        vertical : bool, optional
            Keyword to toggle between vertical and horizontal alignment of
            the QRadioButtons. Select True for vertical and False for
            horizontal alignment. The default is True.
        """
        super().__init__(parent)

        self._emit_signal = True
        self._active_index = 0
        self._buttons = {}
        self._button_indices = {}
        self._button_label = {}
        if entries is not None:
            self.__initUI(entries, vertical)

    def __initUI(self, entries, vertical):
        """
        Initialize the user interface with Widgets and Layout.

        Parameters
        ----------
        entries : list
            The list of entries as passed from __init__.
        vertical : bool
            The vertical flag, as passed from __init__.
        """
        self.q_button_group = QtWidgets.QButtonGroup(self)
        _layout = (QtWidgets.QVBoxLayout() if vertical
                   else QtWidgets.QHBoxLayout())

        for _index, _entry in enumerate(entries):
            _button = QtWidgets.QRadioButton(_entry, self)
            _button.toggled.connect(self.__toggled)
            self._button_indices[id(_button)] = _index
            self._button_label[_entry] = _index
            self._buttons[_index] = _button
            self.q_button_group.addButton(_button)
            _layout.addWidget(_button)

        self._buttons[0].setChecked(True)
        self.setLayout(_layout)

    @property
    def emit_signal(self):
        """
        Query whether a signal will be emitted on change.

        Returns
        -------
        bool
            Flag whether a signal will be emitted.
        """
        return self._emit_signal

    @emit_signal.setter
    def emit_signal(self, value):
        """
        Change the stored value for emit_signal.

        Parameters
        ----------
        value : bool
            The new value.
        """
        if value is True:
            self._emit_signal = True
        elif value is False:
            self._emit_signal = False
        raise ValueError('The new value must be boolean.')


    @QtCore.pyqtSlot()
    def __toggled(self):
        """
        Perform action after a button was toggled.

        This method stores the index of the active button and emits the
        signal if the "emit_signal" property is True.
        """
        _button = self.sender()
        if _button.isChecked():
            _index = self._button_indices[id(_button)]
            _entry = _button.text()
            self._active_index = _index
            if self._emit_signal:
                self.new_button.emit(_index, _entry)

    def which_is_checked(self):
        """
        Return the information about which index is checked.

        Returns
        -------
        int
            The active RadioButton's index.
        """
        return self._active_index

    def select_by_index(self, index):
        """
        Select and activate a new RadioButton based on the index.

        Parameters
        ----------
        index : int
            The new RadioButton's index.
        """
        _button = self._buttons[index]
        self.__select_new_button(_button)

    def select_by_label(self, label):
        """
        Select and activate a new RadioButton based on the text label.

        Parameters
        ----------
        label : str
            The new RadioButton's label.
        """
        _button = self._buttons[self._button_label[label]]
        self.__select_new_button(_button)

    def __select_new_button(self, button):
        """
        Toggle a new RadioButton without emitting a signal.

        Parameters
        ----------
        button : QtWidgets.QRadioButton
            The RadioButton to be checked.
        """
        _emit_enabled = self._emit_signal
        try:
            self._emit_signal = False
            button.setChecked(True)
        finally:
            self._emit_signal = _emit_enabled
