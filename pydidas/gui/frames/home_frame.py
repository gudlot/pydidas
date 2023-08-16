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
Module with the HomeFrame which acts as a starting and reference point when
opening pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["HomeFrame"]


from qtpy import QtCore, QtGui, QtWidgets

from ...core import constants
from ...core.utils import DOC_HOME_ADDRESS
from ...resources import logos
from ...widgets import ScrollArea
from ...widgets.framework import BaseFrame


_GENERIC_INTRO = (
    "- The pydidas GUI is organized in 'frames' with individual functionalities.\n"
    "- The help is available as webpages either through the menu or by pressing 'F1'\n"
    "  to open the specific help for the current frame directly.\n"
    "- The configuration and inputs can be stored and restored using the File->GUI\n"
    "  state menu entries."
)

_TOOOLBAR_USER_TEXT = (
    "Use the menu toolbar on the left to switch between different frames. Some menu "
    "toolbars will open an additional submenu on  the left. The active frame is "
    "highlighted."
)

_HELP_TEXT = (
    "Documentation is available in the html format. You can open the documentation "
    "from any frame using the 'Help' menu entry to either open it in the system's "
    f'web browser. <br>Or follow this link to <a href="{DOC_HOME_ADDRESS}">open the '
    "documentation in a browser</a>."
)

_PROC_SETUP_TEXT = (
    "Setting up a processing job requires three different object to be set: "
    "\n  1. The experimental setup. This includes values such as the beamline "
    "energy, \n      detector and detector geometry. \n      "
    "It is modified in the 'Workflow processing'->'Experimental Setup' frame."
    "\n  2. The scan setup. This includes the number of scan dimensions and "
    "number\n      of scan points per dimension."
    "\n  3. The processing workflow. The workflow must includes all the "
    "plugins \n      which should be executed."
    "\n\nEach object has its own dedicated setup frame with importers and "
    "exporters for the various supported formats."
)

_processing_recipe_link = DOC_HOME_ADDRESS.replace(
    "index.html", "/manuals/gui/recipes/pydidas_processing.html"
)
_PROC_TEXT = (
    "The processing can be started for a single datapoint using the 'Test Workflow' "
    "frame (in the 'Workflow Processing' submenu). The test also allows to view all "
    "intermediate results.<br>"
    "The full automatic processing can be started using the 'Run Full Processing' "
    "frame.<br>"
    "The full processing will run in separate processes and the GUI will stay "
    "responsive. <br>"
    "Results can be visualized on the fly while the processing is still running by "
    "selecting the desired node and axes.<br>"
    "For a full tutorial, please visit the corresponding help page: "
    f'<a href="{_processing_recipe_link}">open the processing documentation'
    " in a browser</a>."
)


class HomeFrame(BaseFrame):
    """The pydidas start-up/home frame with generic information."""

    menu_icon = "qta::mdi.home"
    menu_title = "Home"
    menu_entry = "Home"

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent)

    def build_frame(self):
        """Build the frame and add all widgets."""
        self.create_empty_widget("canvas", parent_widget=None)

        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            widget=self._widgets["canvas"],
            fixedWidth=650,
            sizePolicy=constants.POLICY_FIX_EXP,
            gridPos=(0, 0, 2, 1),
            stretch=(1, 0),
            layout_kwargs={"alignment": None},
        )

        self.create_label(
            "label_welcome",
            "Welcome to pydidas",
            fontsize_offset=4,
            bold=True,
            fixedWidth=400,
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "label_full_name",
            "- the python Diffraction Data Analysis Suite.",
            fontsize_offset=3,
            bold=True,
            fixedWidth=400,
            parent_widget=self._widgets["canvas"],
        )
        self.create_spacer(None, parent_widget=self._widgets["canvas"])
        self.create_label(
            "label_quickstart",
            "Quickstart hints:",
            fontsize_offset=2,
            bold=True,
            underline=True,
            fixedWidth=400,
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "label_quickstart_info",
            _GENERIC_INTRO,
            weight=QtGui.QFont.DemiBold,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )
        self.create_spacer(None, parent_widget=self._widgets["canvas"])
        self.create_label(
            "label_toolbar",
            "Menu toolbar:",
            fontsize_offset=1,
            underline=True,
            bold=True,
            fixedWidth=400,
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "label_toolbar_use",
            _TOOOLBAR_USER_TEXT,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )
        self.create_spacer(None, parent_widget=self._widgets["canvas"])

        self.create_label(
            "label_help_header",
            "Online help:",
            fontsize_offset=1,
            underline=True,
            bold=True,
            fixedWidth=400,
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "label_help",
            _HELP_TEXT,
            fixedWidth=600,
            openExternalLinks=True,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            textFormat=QtCore.Qt.RichText,
            parent_widget=self._widgets["canvas"],
        )
        self.create_spacer(None, parent_widget=self._widgets["canvas"])
        self.create_label(
            "label_proc_setup",
            "Workflow processing setup:",
            fontsize_offset=1,
            underline=True,
            bold=True,
            fixedWidth=400,
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "label_processing_setup",
            _PROC_SETUP_TEXT,
            fixedWidth=600,
            parent_widget=self._widgets["canvas"],
        )
        self.create_spacer(None, parent_widget=self._widgets["canvas"])
        self.create_label(
            "label_proc",
            "Running processing:",
            fontsize_offset=1,
            underline=True,
            bold=True,
            fixedWidth=400,
            parent_widget=self._widgets["canvas"],
        )
        self.create_label(
            "label_processing",
            _PROC_TEXT,
            fixedWidth=600,
            openExternalLinks=True,
            textFormat=QtCore.Qt.RichText,
            textInteractionFlags=QtCore.Qt.LinksAccessibleByMouse,
            parent_widget=self._widgets["canvas"],
        )

        self.create_spacer(
            None,
            gridPos=(0, 1, 1, 1),
            stretch=(1, 1),
            policy=QtWidgets.QSizePolicy.Expanding,
        )
        self.add_any_widget(
            "svg_logo",
            logos.pydidas_logo_svg(),
            gridPos=(0, 2, 1, 1),
            fixedHeight=300,
            fixedWidth=300,
            layout_kwargs={"alignment": (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)},
        )
