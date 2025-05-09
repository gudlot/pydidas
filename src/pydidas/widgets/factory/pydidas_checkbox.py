# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
The PydidasCheckBox is a QCheckBox with font formatting and sizeHint adjustment.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasCheckBox"]


from qtpy import QtWidgets

from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


class PydidasCheckBox(PydidasWidgetMixin, QtWidgets.QCheckBox):
    """
    Create a QCheckBox with automatic font formatting.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        kwargs["font_metric_height_factor"] = kwargs.get("font_metric_height_factor", 1)
        QtWidgets.QCheckBox.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)
