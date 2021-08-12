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
Module with format_arguments functions which takes *args and **kwargs and
converts them into an argparse-compatible list.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['format_arguments']

import re


def format_arguments(*args, **kwargs):
    """Function which accepts arguments and keyword arguments and converts
    them to a argparse-compatible list.
    """
    newArgs = []
    for item, key in kwargs.items():
        if key is True:
            newArgs.append(f'--{item}')
        else:
            newArgs.append(f'-{item}')
            newArgs.append(key if isinstance(key, str) else str(key))

    for arg in args:
        arg = arg if isinstance(arg, str) else str(arg)
        if '=' in arg or ' ' in arg:
            _split_args = [item for item in re.split(' |=', arg) if item != '']
            if not _split_args[0].startswith('-'):
                _split_args[0] = f'-{_split_args[0]}'
            newArgs += _split_args
        else:
            newArgs.append(arg)

    return newArgs