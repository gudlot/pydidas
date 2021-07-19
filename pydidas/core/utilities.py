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

"""Module with generic utiliy functions."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import time
import os
import sys
import tempfile
from os.path import join as osjoin
from os.path import dirname, isfile

from numpy import floor

def update_separators(path):
    """
    Check the separators and update to os.sep if required.

    Parameters
    ----------
    path : str
        The file path to be checked

    Returns
    -------
    str
        The path with separators updated to os.sep standard.
    """
    if sys.platform in ['win32', 'win64']:
        return path.replace('/', os.sep)
    return path.replace('\\', os.sep)


def get_pydidas_module_dir(path):
    """
    Function to find the pydidas module directory from the input directory.

    Parameters
    ----------
    filename : str
        The filename of the file to be checked.
    overwrite : bool
        Keyword to allow overwriting of existing files. Default: False

    Returns
    -------
    bool
        True if file exists and overwrite or directory is writable.
        False in other cases.
    """
    path = update_separators(os.path.dirname(path) if isfile(path) else path)
    p = path.split(os.sep)
    if len(p) == 0:
        raise IOError('No path given')
    for i in range(1, len(p)):
        _p = os.sep.join(p[:-i])
        if p[-i] == 'tests':
            if isfile(osjoin(_p, 'pydidas', '__init__.py')):
                return _p
        elif p[-i] == 'pydidas' or 'pydidas' in os.listdir(_p):
            if isfile(osjoin(_p, '__init__.py')):
                return dirname(_p)
            if isfile(osjoin(_p, 'pydidas', 'pydidas', '__init__.py')):
                return osjoin(_p, 'pydidas')
    raise FileNotFoundError('Could not locate pydidas init file.')


def create_temp_file():
    """
    Create a temporary file and close the file handle.

    Returns
    -------
    str
        The full path to the temporary file.
    """
    _handle, _filename = tempfile.mkstemp()
    os.close(_handle)
    return _filename

def get_time_string(epoch=None, humanReadable=False):
    """
    Get a formatted time string.

    This function creates a readable time string from an epoch time. If no
    epoch time is specified, the current time will be used.
    By using the "skipSpecChars" flag, the output can be formatted without
    any separators and special characters, for example for using it for
    file names.

    Parameter
    ---------
    epoch : Union[None, float]
        The time in epoch. If None, the current system time will be used.
        The default is None.
    humanReadable : bool, optional
        Flag to create human-readable format with special separation characters
        (":" and "/"). If False, the output items will not be separated by
        separators (e.g. for filenames). The default is True.

    Returns
    -------
    str
        Formatted date and time string
        (if humanReadable: YYYY/MM/DD HH:MM:ss.sss;
         else: YYYYMMDD__HHMMss)
    """
    if epoch is None:
        epoch = time.time()
    _time = time.localtime(epoch)
    _sec = _time[5] + epoch - floor(epoch)
    if humanReadable:
        return ('{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:06.3f}'
                ''.format(_time[0], _time[1], _time[2], _time[3], _time[4],
                          _sec))
    return ('{:04d}{:02d}{:02d}_{:02d}{:02d}{:02.0f}'
            ''.format(_time[0], _time[1], _time[2], _time[3], _time[4], _sec))
