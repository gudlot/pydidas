# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the WorkflowRunFrameBuilder class which is used to
populate the WorkflowRunFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkflowRunFrameBuilder"]

from ....core import constants
from ....core.constants import (
    CONFIG_WIDGET_WIDTH,
    DEFAULT_TWO_LINE_PARAM_CONFIG,
    FIX_EXP_POLICY,
)
from ....widgets import BaseFrameWithApp, ScrollArea
from ....widgets.parameter_config import ParameterEditCanvas
from ....widgets.selection import ResultSelectionWidget
from ....widgets.silx_plot import create_silx_plot_stack


class WorkflowRunFrameBuilder(BaseFrameWithApp):
    """
    Mix-in class which includes the build_frame method to populate the
    base class's UI and initialize all widgets.
    """

    def __init__(self, parent=None, **kwargs):
        BaseFrameWithApp.__init__(self, parent, **kwargs)
        _layout = self.layout()
        _layout.setHorizontalSpacing(10)
        _layout.setVerticalSpacing(5)

    def __param_widget_config(self, param_key):
        """
        Get Formatting options for create_param_widget calls.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.

        Returns
        -------
        dict :
            The dictionary with the formatting options.
        """
        if param_key in ["autosave_directory", "selected_results"]:
            _dict = DEFAULT_TWO_LINE_PARAM_CONFIG.copy()
            _dict.update(
                {
                    "parent_widget": self._widgets["config"],
                }
            )
        else:
            _dict = dict(
                parent_widget=self._widgets["config"],
                width_io=100,
                width_unit=0,
                width_text=CONFIG_WIDGET_WIDTH - 100,
                width_total=CONFIG_WIDGET_WIDTH,
            )
        if param_key in ["autosave_directory", "autosave_format"]:
            _dict["visible"] = False
        return _dict

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "title",
            "Run full workflow processing",
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 5),
        )

        self.create_spacer("title_spacer", height=20, gridPos=(1, 0, 1, 1))

        self._widgets["config"] = ParameterEditCanvas(
            parent=None, init_layout=True, lineWidth=5, sizePolicy=FIX_EXP_POLICY
        )
        self.create_spacer(
            "spacer1", gridPos=(-1, 0, 1, 2), parent_widget=self._widgets["config"]
        )
        self.create_any_widget(
            "config_area",
            ScrollArea,
            widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH + 40,
            sizePolicy=FIX_EXP_POLICY,
            gridPos=(-1, 0, 1, 1),
            stretch=(1, 0),
            layout_kwargs={"alignment": None},
        )
        for _param in ["autosave_results", "autosave_directory", "autosave_format"]:
            self.create_param_widget(
                self.get_param(_param), **self.__param_widget_config(_param)
            )

        self.create_line(
            "line_autosave",
            gridPos=(-1, 0, 1, 1),
            parent_widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH,
        )
        self.create_button(
            "but_exec",
            "Start processing",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
            icon=self.style().standardIcon(61),
        )
        self.create_progress_bar(
            "progress",
            gridPos=(-1, 0, 1, 1),
            visible=False,
            minimum=0,
            maximum=100,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
        )
        self.create_button(
            "but_abort",
            "Abort processing",
            gridPos=(-1, 0, 1, 1),
            enabled=True,
            visible=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
            icon=self.style().standardIcon(60),
        )
        self.create_line(
            "line_results",
            gridPos=(-1, 0, 1, 1),
            parent_widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH,
        )
        self.create_any_widget(
            "result_selector",
            ResultSelectionWidget,
            parent_widget=self._widgets["config"],
            gridpos=(-1, 0, 1, 1),
            select_results_param=self.get_param("selected_results"),
            fixedWidth=CONFIG_WIDGET_WIDTH,
        )
        self.create_line(
            "line_export",
            gridPos=(-1, 0, 1, 1),
            parent_widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH,
        )
        self.create_param_widget(
            self.get_param("saving_format"),
            **self.__param_widget_config("saving_format"),
        )
        self.create_param_widget(
            self.get_param("enable_overwrite"),
            **self.__param_widget_config("enable_overwrite"),
        )
        self.create_button(
            "but_export_current",
            "Export current node results",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
            enabled=False,
            icon=self.style().standardIcon(25),
            toolTip=(
                "Export the current node's results to file. Note that "
                "the filenames are pre-determined based on node ID "
                "and node label."
            ),
        )
        self.create_button(
            "but_export_all",
            "Export all results",
            enabled=False,
            gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["config"],
            tooltip=("Export all results. Note that the directory must be empty."),
            icon=self.style().standardIcon(43),
        )
        self.create_spacer(
            "config_terminal_spacer",
            height=20,
            gridPos=(-1, 0, 1, 1),
            parent_widget=self._widgets["config"],
        )
        self.create_spacer("menu_bottom_spacer", height=20, gridPos=(-1, 0, 1, 1))

        create_silx_plot_stack(self, gridPos=(0, 1, 3, 1), use_data_info_action=True)
