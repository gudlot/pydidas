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
Module with the create_workflow_edit_frame_widgets_and_layout function
which is used to populate the WorkflowEditFrame with widgets.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['create_workflow_edit_frame_widgets_and_layout']

from PyQt5 import QtWidgets

from pydidas.widgets import ScrollArea
from pydidas.widgets.parameter_config import PluginParameterConfigWidget
from pydidas.widgets.workflow_edit import (WorkflowTreeCanvas,
                                           PluginCollectionPresenter)

def create_workflow_edit_frame_widgets_and_layout(frame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    frame : pydidas.gui.WorkflowditFrame
        The WorkflowditFrame instance.
    """
    frame._widgets = {}
    frame.layout().setContentsMargins(0, 0, 0, 0)

    frame._widgets['workflow_canvas'] = WorkflowTreeCanvas(frame)
    frame._widgets['plugin_edit_canvas'] = PluginParameterConfigWidget(
        frame)
    frame.create_any_widget(
        'workflow_area', ScrollArea, minimumHeight=500,
        widget=frame._widgets['workflow_canvas'], gridPos=(0, 0, 1, 1))
    frame.create_any_widget('plugin_collection',
                              PluginCollectionPresenter,
                              gridPos=(1, 0, 3, 1))
    frame.create_any_widget(
        'plugin_edit_area', ScrollArea, minimumHeight=500,
        widget=frame._widgets['plugin_edit_canvas'], fixedWidth=400,
        sizePolicy=(QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Expanding),
        gridPos=(0, 1, 2, 1))
    frame.create_button('but_load', 'Load workflow from file',
                          gridPos=(2, 1, 1, 1))
    frame.create_button('but_save', 'Save workflow to file',
                          gridPos=(3, 1, 1, 1))