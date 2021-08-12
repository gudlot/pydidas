# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with a factory function to create formatted lines as a formatted
QFrame."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_button']

from PyQt5.QtWidgets import QPushButton

from ..utilities import apply_widget_properties


def create_button(text, **kwargs):
    """
    Create a button.

    Parameters
    ----------
    text : str
        The button text.
    **kwargs : dict
        Any supported keyword arguments.

    Supported keyword arguments
    ---------------------------
    *Qt settings : any
        Any supported Qt settings for button (for example, icon, visible,
        enabled, fixedWidth)

    Returns
    -------
    button : QtWidgets.QPushButton
        The instantiated button widget.
    """
    _button = QPushButton(text)
    apply_widget_properties(_button, **kwargs)
    return _button