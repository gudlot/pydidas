#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the PluginParamConfig class used to edit plugin parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['IOwidget_file']

import pathlib

from PyQt5 import QtWidgets, QtCore
from .io_widget import IOwidget

class IOwidget_file(IOwidget):
    """
    Widgets for I/O during plugin parameter for filepaths.
    (Includes a small button to select a filepath from a dialogue.)
     """
    #for some reason, inhering the signal from the base class does not work
    io_edited = QtCore.pyqtSignal(str)

    def __init__(self, parent, param, width=255):
        """
        Setup the widget.

        Init method to setup the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        parent : QWidget
            A QWidget instance.
        param : Parameter
            A Parameter instance.
        width : int, optional
            The width of the IOwidget.

        Returns
        -------
        None.
        """
        super().__init__(parent, param, width)
        self.ledit = QtWidgets.QLineEdit()
        self.ledit.setFixedWidth(width - 25)
        self.ledit.setFixedHeight(25)

        fbutton = QtWidgets.QPushButton(self.style().standardIcon(42), '')
        fbutton.setFixedWidth(25)
        self.ledit.setFixedHeight(25)
        _layout = QtWidgets.QHBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self.ledit)
        _layout.addWidget(fbutton)
        self.setLayout(_layout)

        self.ledit.editingFinished.connect(self.emit_signal)
        fbutton.clicked.connect(self.button)

    def button(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.

        Returns
        -------
        None.
        """
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Name of file', None,
            ('All files (*.*);;HDF5 files (*.nxs *.hdf *.h5)'
             ';;TIFF files (*.tif, *.tiff)')
        )[0]
        if fname:
            self.setText(fname)
            self.emit_signal()

    def emit_signal(self):
        """
        Emit a signal that the value has been edited.

        This method emits a signal that the combobox selection has been
        changed and the Parameter value needs to be updated.

        Returns
        -------
        None.
        """
        self.io_edited.emit(self.ledit.text())

    def get_value(self):
        """
        Get the current value from the combobox to update the Parameter value.

        Returns
        -------
        Path
            The text converted to a pathlib.Path to update the Parameter value.
        """
        text = self.ledit.text()
        return pathlib.Path(self.get_value_from_text(text))

    def set_value(self, value):
        """
        Set the input field's value.

        This method changes the combobox selection to the specified value.

        Returns
        -------
        None.
        """
        self.ledit.setText(f'{value}')

    def setText(self, text):
        """
        Set the line edit text to the input.

        This method will call the line edit setText method to update the
        displayed text.

        Parameters
        ----------
        text : object
            Any object, the object's str representation will be used.

        Returns
        -------
        None.
        """
        self.ledit.setText(str(text))
