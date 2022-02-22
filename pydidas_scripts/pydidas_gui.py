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
The main_gui module includes a function to run the GUI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['run_gui']

import sys

from qtpy import QtWidgets

from pydidas.gui import (
    DataBrowsingFrame,  WorkflowEditFrame, PyfaiCalibFrame, HomeFrame,
    ExperimentalSetupFrame, ScanSetupFrame, ExecuteWorkflowFrame,
    CompositeCreatorFrame, get_pyfai_calib_icon, MainWindow)
from pydidas.widgets import BaseFrame


class ProcessingFrame(BaseFrame):
    show_frame = False
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)


class ToolsFrame(BaseFrame):
    show_frame = False
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super().__init__(parent)


def run_gui():
    """
    Run the GUI application with the generic pydidas layout.
    """
    app = QtWidgets.QApplication(sys.argv)
    gui = MainWindow()
    gui.register_frame(HomeFrame, 'Home','Home', 'qta::mdi.home')
    gui.register_frame(DataBrowsingFrame, 'Data browsing', 'Data browsing',
                        'qta::mdi.image-search-outline')
    gui.register_frame(PyfaiCalibFrame, 'pyFAI calibration',
                       'pyFAI calibration', get_pyfai_calib_icon())
    gui.register_frame(CompositeCreatorFrame, 'Composite image creator',
                       'Composite image creator', 'qta::mdi.view-comfy')
    gui.register_frame(ProcessingFrame, 'Workflow processing',
                       'Workflow processing', 'qta::mdi.cogs')
    gui.register_frame(ExperimentalSetupFrame, 'Experimental settings',
                       'Workflow processing/Experimental settings',
                       'qta::mdi.card-bulleted-settings-outline')
    gui.register_frame(ScanSetupFrame, 'Scan settings',
                       'Workflow processing/Scan settings', 'qta::ei.move')
    gui.register_frame(WorkflowEditFrame, 'Workflow editing',
                       'Workflow processing/Workflow editing',
                       'qta::mdi.clipboard-flow-outline')
    gui.register_frame(ExecuteWorkflowFrame, 'Run full processing',
                   'Workflow processing/Run full procesing', 'qta::mdi.sync')
    # gui.register_frame(ResultVisualizationFrame, 'Result visualization',
    #                    'Result visualization', 'qta::mdi.monitor-eye')
    gui.show()
    gui.raise_()
    _ = app.exec_()
    gui.deleteLater()
    app.deleteLater()
    sys.exit()


if __name__ == '__main__':
    run_gui()