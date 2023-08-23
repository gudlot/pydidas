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
Module with the ParameterEditCanvas class which is a subclassed QFrame updated
with the ParameterWidgetsMixIn.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterEditCanvas"]


from typing import Union

from qtpy import QtWidgets

from ...core.constants import POLICY_MIN_MIN
from ...core.utils import apply_qt_properties
from ..factory import PydidasWidgetWithGridLayout
from .parameter_widgets_mixin import ParameterWidgetsMixIn


class ParameterEditCanvas(ParameterWidgetsMixIn, PydidasWidgetWithGridLayout):
    """
    The ParameterEditCanvas is widget for handling Parameter edit widgets.

    Parameters
    ----------
    parent : Union[QtWidgets.QtWidget, None], optional
        The parent widget. The default is None.
    **kwargs : dict
        Additional keyword arguments
    """

    def __init__(self, parent: Union[QtWidgets.QWidget, None] = None, **kwargs: dict):
        PydidasWidgetWithGridLayout.__init__(self, parent)
        ParameterWidgetsMixIn.__init__(self)
        apply_qt_properties(self, **kwargs)
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.setSizePolicy(*POLICY_MIN_MIN)
