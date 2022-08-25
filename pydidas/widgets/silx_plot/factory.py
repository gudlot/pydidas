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
Module with a function to create a QStackedWidget with 1d and 2d plots.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_silx_plot_stack"]

from functools import partial

from qtpy import QtWidgets

from ...core.constants import EXP_EXP_POLICY
from .pydidas_plot1d import PydidasPlot1D
from .pydidas_plot2d import PydidasPlot2D


def create_silx_plot_stack(frame, gridPos=None):
    """
    Create a QStackedWidget with 1D and 2D plot widgets in the input frame.


    Parameters
    ----------
    frame : pydidas.core.BaseFrame
        The input frame.
    gridPos : Union[tuple, None], optional
        The gridPos for the new widget. The default is None.

    Returns
    -------
    frame : pydidas.core.BaseFrame
        The updated frame.
    """
    frame._widgets["plot1d"] = PydidasPlot1D()
    frame._widgets["plot2d"] = PydidasPlot2D()
    if hasattr(frame, "sig_this_frame_activated"):
        frame.sig_this_frame_activated.connect(
            partial(frame._widgets["plot2d"].cs_transform.check_detector_is_set, True)
        )
    if hasattr(frame, "sig_this_frame_activated"):
        frame.sig_this_frame_activated.connect(
            frame._widgets["plot2d"].cs_transform.set_beam_center_from_exp_setup
        )
    frame.add_any_widget(
        "plot_stack",
        QtWidgets.QStackedWidget(),
        alignment=None,
        gridPos=gridPos,
        visible=True,
        stretch=(1, 1),
        sizePolicy=EXP_EXP_POLICY,
    )
    frame._widgets["plot_stack"].addWidget(frame._widgets["plot1d"])
    frame._widgets["plot_stack"].addWidget(frame._widgets["plot2d"])
