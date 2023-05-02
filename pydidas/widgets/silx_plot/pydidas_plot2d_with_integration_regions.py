# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the PydidasPlot2DwithIntegrationRegions class which extends the
PydidasPlot2D with functionality to draw integration regions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasPlot2DwithIntegrationRegions"]


from typing import Literal, Tuple

import numpy as np
from qtpy import QtCore
from silx.gui.plot.items import Marker, Shape

from ...core.constants import PYDIDAS_COLORS
from ...core.utils import (
    get_chi_from_x_and_y,
    ray_from_center_intersection_with_detector,
)
from .pydidas_plot2d import PydidasPlot2D


cos_phi = np.cos(np.linspace(0, 2 * np.pi, num=145))
sin_phi = np.sin(np.linspace(0, 2 * np.pi, num=145))


class PydidasPlot2DwithIntegrationRegions(PydidasPlot2D):
    """
    An extended PydidasPlot2D which allows to show integration regions.
    """

    sig_new_point_selected = QtCore.Signal(float, float)

    def __init__(self, parent=None, backend=None, **kwargs):
        PydidasPlot2D.__init__(self, parent, backend, **kwargs)
        self._config["marker_color"] = kwargs.get(
            "marker_color", PYDIDAS_COLORS["orange"]
        )
        self._process_exp_update()
        self.sigPlotSignal.connect(self._process_plot_signal)
        self._config["diffraction_exp"].sig_params_changed.connect(
            self._process_exp_update
        )

    @QtCore.Slot()
    def _process_exp_update(self):
        """
        Process updates of the DiffractionExperiment.
        """
        self._config["beamcenter"] = self._config["diffraction_exp"].beamcenter

    @QtCore.Slot(str)
    def set_new_marker_color(self, color):
        """
        Set the new color for the markers.

        Parameters
        ----------
        color : str
            The name of the new color.
        """
        self._config["color"] = PYDIDAS_COLORS[color]
        _items = self.getItems()
        for _item in _items:
            if isinstance(_item, (Marker, Shape)):
                _item.setColor(self._config["color"])

    def remove_plot_items(
        self, *kind: Tuple[Literal["azimuthal", "radial", "roi", "all"]]
    ):
        """
        Remove the items for the given kind from the plot.

        Parameters
        ----------
        *kind : Tuple[Literal["azimuthal", "radial", "roi", "all"]]
            The kind or markers to be removed.
        """
        _entries = set(_item for _item in kind if _item != "all")
        if "all" in kind:
            _entries.update(("azimuthal", "radial", "roi"))
        for _kind in _entries:
            if _kind in ["azimuthal", "radial"]:
                self.remove(legend=f"{_kind}_lower", kind="item")
                self.remove(legend=f"{_kind}_upper", kind="item")
            self.remove(legend=_kind, kind="item")

    def draw_circle(self, radius, legend, center=None):
        """
        Draw a circle with the given radius and store it as the given legend.

        Parameters
        ----------
        radius : float
            The circle radius in pixels.
        legend : str
            The shape's legend for referencing it in the plot.
        center : Union[None, Tuple[float, float]], optional
            The center of the circle. If None, this defaults to the
            DiffractionExperiment beamcenter. The default is None.
        """
        _cx, _cy = self._config["beamcenter"] if center is None else center
        self.addShape(
            radius * cos_phi + _cx,
            radius * sin_phi + _cy,
            legend=legend,
            color=self._config["marker_color"],
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )

    def draw_line_from_beamcenter(self, chi, legend):
        """
        Draw a line from the beamcenter in the direction given by the angle chi.

        Parameters
        ----------
        chi : float
            The pointing angle, given in rad.
        legend : str
            The reference legend entry for this line.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _cx, _cy = self._config["beamcenter"]
        _xpoints, _ypoints = ray_from_center_intersection_with_detector(
            (_cx, _cy), chi, (_nx, _ny)
        )
        if len(_xpoints) == 0:
            return
        if len(_xpoints) == 1:
            _xarr = [_cx, _xpoints[0]]
            _yarr = [_cy, _ypoints[0]]
        else:
            _xarr = [_xpoints[0], _xpoints[1]]
            _yarr = [_ypoints[0], _ypoints[1]]
        self.addShape(
            _xarr,
            _yarr,
            legend=legend,
            shape="polylines",
            color=self._config["marker_color"],
            linestyle="--",
            fill=False,
            linewidth=2.0,
        )

    def draw_integration_region(self, radial, azimuthal):
        """
        Draw the given integration region.

        Parameters
        ----------
        radial : Union[None, Tuple[float, float]]
            The radial integration region. Use None for the full detector or a tuple
            with (r_inner, r_outer) in pixels to select a region.
        azimuthal : Union[None, Tuple[float, float]]
            The azimuthal integration region. Use None for the full detector or a tuple
            with (azi_start, azi_end) in radians for a region.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _cx, _cy = self._config["beamcenter"]
        _center_on_det = 0 <= _cx <= _nx and 0 <= _cy <= _ny
        if radial is None and azimuthal is None:
            _xarr = [0, 0, _nx, _nx]
            _yarr = [0, _ny, _ny, 0]
        if radial is None and azimuthal is not None:
            _x0, _y0 = ray_from_center_intersection_with_detector(
                (_cx, _cy), azimuthal[0], (_nx, _ny)
            )
            _x1, _y1 = ray_from_center_intersection_with_detector(
                (_cx, _cy), azimuthal[1], (_nx, _ny)
            )
            if _center_on_det:
                _xpoints, _ypoints = self._get_included_corners(
                    (_x0[0], _y0[0]), (_x1[0], _y1[0])
                )
                _xpoints.insert(0, _cx)
                _xpoints.append(_cx)
                _ypoints.insert(0, _cy)
                _ypoints.append(_cy)
            else:  # center off detector
                if len(_x0) == 0 and len(_x1) == 0:
                    # no intersections, i.e. either full detector or no point on
                    # detector in roi
                    _chi_det = get_chi_from_x_and_y(_nx / 2 - _cx, _ny / 2 - _cy)
                    if azimuthal[0] < _chi_det < azimuthal[1]:
                        _xpoints = [0, 0, _nx, _nx]
                        _ypoints = [0, _ny, _ny, 0]
                    else:
                        self.remove_plot_items("roi")
                        return
                elif len(_x0) == 2 and len(_x1) == 2:
                    _xpoints, _ypoints = self._get_included_corners(
                        (_x1[0], _y1[0]), (_x0[0], _y0[0])
                    )
                    _p2x, _p2y = self._get_included_corners(
                        (_x0[1], _y0[1]), (_x1[1], _y1[1])
                    )
                    _xpoints.extend(_p2x)
                    _ypoints.extend(_p2y)
                elif len(_x0) == 0 and len(_x1) == 2:
                    _xpoints, _ypoints = self._get_included_corners(
                        (_x1[0], _y1[0]), (_x1[1], _y1[1])
                    )
                elif len(_x0) == 2 and len(_x1) == 0:
                    _xpoints, _ypoints = self._get_included_corners(
                        (_x0[1], _y0[1]), (_x0[0], _y0[0])
                    )

            _xarr = np.asarray(_xpoints)
            _yarr = np.asarray(_ypoints)
        if radial is not None:
            _phi = (
                np.linspace(0, 2 * np.pi, num=145)
                if azimuthal is None
                else np.linspace(azimuthal[0], azimuthal[1], num=145)
            )
            _xarr = _cx + np.concatenate(
                (
                    radial[0] * np.cos(_phi),
                    radial[1] * np.cos(_phi[::-1]),
                    (radial[0] * np.cos(_phi[0]),),
                )
            )
            _yarr = _cy + np.concatenate(
                (
                    radial[0] * np.sin(_phi),
                    radial[1] * np.sin(_phi[::-1]),
                    (radial[0] * np.sin(_phi[0]),),
                )
            )
        self.addShape(
            _xarr,
            _yarr,
            legend="roi",
            color=self._config["marker_color"],
            linewidth=2.0,
        )

    def _get_included_corners(self, startpoint, endpoint):
        """
        Get the corners on the detector outline between startpoint and endpoint.

        Starting at the startpoint, follow the detector outline in a positive rotation
        and tag all corner points which are covered before reaching the endpoint.
        This method also includes the start- and endpoint.

        Parameters
        ----------
        startpoint : Tuple[float, float]
            The starting point (x, y)
        endpoint : Tuple[float, float]
            The endpoint (x, y)

        Returns
        -------
        corners_x : list
            The corner x positions.
        corners_y : list
            The corner y positions.
        """
        _nx = self._config["diffraction_exp"].get_param_value("detector_npixx")
        _ny = self._config["diffraction_exp"].get_param_value("detector_npixy")
        _ex, _ey = endpoint
        _c_x = [startpoint[0]]
        _c_y = [startpoint[1]]
        while True:
            if _c_y[-1] == 0 and _ey != 0:
                _c_x.append(_nx)
                _c_y.append(0)
            elif _c_y[-1] == 0:
                if _ex > _c_x[-1]:
                    break
                _c_x.append(_nx)
                _c_y.append(0)
            if _c_x[-1] == _nx and _ex != _nx:
                _c_x.append(_nx)
                _c_y.append(_ny)
            elif _c_x[-1] == _nx:
                if _ey > _c_y[-1]:
                    break
                _c_x.append(_nx)
                _c_y.append(_ny)
            if _c_y[-1] == _ny and _ey != _ny:
                _c_x.append(0)
                _c_y.append(_ny)
            elif _c_y[-1] == _ny:
                if _ex < _c_x[-1]:
                    break
                _c_x.append(0)
                _c_y.append(_ny)
            if _c_x[-1] == 0 and _ex != 0:
                _c_x.append(0)
                _c_y.append(0)
            elif _c_x[-1] == 0:
                if _ey < _c_y[-1]:
                    break
                _c_x.append(0)
                _c_y.append(0)
        _c_x.append(_ex)
        _c_y.append(_ey)
        return _c_x, _c_y

    @QtCore.Slot(dict)
    def _process_plot_signal(self, event_dict):
        """
        Process events from the plot and filter and process mouse clicks.

        Parameters
        ----------
        event_dict : dict
            The silx event dictionary.
        """
        if (
            event_dict["event"] == "mouseClicked"
            and event_dict.get("button", "None") == "left"
        ):
            _x = np.round(event_dict["x"], decimals=3)
            _y = np.round(event_dict["y"], decimals=3)
            self.sig_new_point_selected.emit(_x, _y)