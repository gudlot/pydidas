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
Package with subclassed silx widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .pydidas_plot1d import *
from .pydidas_plot2d import *
from .silx_actions import *
from .utilities import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import pydidas_plot1d

__all__.extend(pydidas_plot1d.__all__)
del pydidas_plot1d

from . import pydidas_plot2d

__all__.extend(pydidas_plot2d.__all__)
del pydidas_plot2d

from . import silx_actions

__all__.extend(silx_actions.__all__)
del silx_actions

from . import utilities

__all__.extend(utilities.__all__)
del utilities
