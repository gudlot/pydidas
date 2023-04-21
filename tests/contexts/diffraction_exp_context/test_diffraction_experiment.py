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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import logging
import unittest
from numbers import Real

import numpy as np
import pyFAI

from pydidas.contexts.diffraction_exp_context import (
    DiffractionExperiment,
    DiffractionExperimentContext,
)
from pydidas.core import UserConfigError


logger = logging.getLogger("pyFAI.detectors._common")
logger.setLevel(logging.CRITICAL)


class TestDiffractionExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._xpos = 1623.546
        cls._ypos = 459.765
        cls._det_dist = 0.12
        cls._beamcenter = (cls._xpos, cls._ypos, cls._det_dist)
        cls._xpos_abs = cls._xpos * 75e-6
        cls._ypos_abs = cls._ypos * 75e-6

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def prepare_context_with_Eiger(self):
        obj = DiffractionExperiment()
        obj.set_detector_params_from_name("Eiger 9M")
        return obj

    def assert_beamcenter_okay(self, obj, accuracy=8):
        _rot1 = obj.get_param_value("detector_rot1")
        _rot2 = obj.get_param_value("detector_rot2")
        _poni1 = obj.get_param_value("detector_poni1")
        _poni2 = obj.get_param_value("detector_poni2")
        _z = obj.get_param_value("detector_dist")
        _beam_center_x = (_poni2 - _z * np.tan(_rot1)) / 75e-6
        _beam_center_y = (_poni1 + _z * np.tan(_rot2) / np.cos(_rot1)) / 75e-6
        self.assertAlmostEqual(_beam_center_y, self._ypos, accuracy)
        self.assertAlmostEqual(_beam_center_x, self._xpos, accuracy)

    def test_set_param_energy(self):
        _new_E = 15.7
        obj = DiffractionExperimentContext()
        obj.set_param_value("xray_energy", _new_E)
        self.assertEqual(obj.get_param_value("xray_energy"), _new_E)
        self.assertAlmostEqual(
            obj.get_param_value("xray_wavelength"), 0.78970806, delta=0.00005
        )

    def test_set_param_wavelength(self):
        _new_lambda = 0.98765
        obj = DiffractionExperimentContext()
        obj.set_param_value("xray_wavelength", _new_lambda)
        self.assertEqual(obj.get_param_value("xray_wavelength"), _new_lambda)
        self.assertAlmostEqual(
            obj.get_param_value("xray_energy"), 12.5534517, delta=0.0005
        )

    def test_get_detector__from_param_name(self):
        _shape = (1000, 1000)
        obj = DiffractionExperimentContext()
        obj.set_param_value("detector_name", "Eiger 9M")
        obj.set_param_value("detector_npixy", _shape[0])
        obj.set_param_value("detector_npixx", _shape[1])
        _det = obj.get_detector()
        self.assertIsInstance(_det, pyFAI.detectors.Detector)
        self.assertEqual(_det.max_shape, _shape)

    def test_get_detector__new_name(self):
        _shape = (1000, 1000)
        _pixelsize = 100
        obj = DiffractionExperimentContext()
        obj.set_param_value("detector_name", "No Eiger")
        obj.set_param_value("detector_npixy", _shape[0])
        obj.set_param_value("detector_npixx", _shape[1])
        obj.set_param_value("detector_pxsizey", _pixelsize)
        obj.set_param_value("detector_pxsizex", _pixelsize)
        _det = obj.get_detector()
        self.assertIsInstance(_det, pyFAI.detectors.Detector)
        self.assertEqual(_det.max_shape, _shape)
        self.assertEqual(_det.pixel1, 1e-6 * _pixelsize)
        self.assertEqual(_det.pixel2, 1e-6 * _pixelsize)

    def test_set_detector_params_from_name__wrong_name(self):
        obj = DiffractionExperimentContext()
        with self.assertRaises(UserConfigError):
            obj.set_detector_params_from_name("no such detector")

    def test_update_from_diffraction_exp(self):
        obj = DiffractionExperimentContext()
        obj.set_param_value("detector_name", "Eiger 9M")
        _exp = DiffractionExperiment()
        _exp.update_from_diffraction_exp(obj)
        for _key, _val in obj.get_param_values_as_dict().items():
            if isinstance(_val, Real):
                self.assertAlmostEqual(_val, _exp.get_param_value(_key), delta=0.000001)
            else:
                self.assertEqual(_val, _exp.get_param_value(_key))

    def test_set_detector_params_from_name(self):
        _det = {"name": "Pilatus 300k", "pixsize": 172, "npixx": 487, "npixy": 619}
        obj = DiffractionExperimentContext()
        obj.set_detector_params_from_name(_det["name"])
        self.assertEqual(obj.get_param_value("detector_name"), _det["name"])
        self.assertEqual(obj.get_param_value("detector_pxsizex"), _det["pixsize"])
        self.assertEqual(obj.get_param_value("detector_pxsizey"), _det["pixsize"])
        self.assertEqual(obj.get_param_value("detector_npixy"), _det["npixy"])
        self.assertEqual(obj.get_param_value("detector_npixx"), _det["npixx"])

    def test_set_beamcenter_from_fit2d_params__no_rot(self):
        obj = self.prepare_context_with_Eiger()
        obj.set_beamcenter_from_fit2d_params(*self._beamcenter)
        self.assert_beamcenter_okay(obj)

    def test_set_beamcenter_from_fit2d_params__full_rot_degree(self):
        obj = self.prepare_context_with_Eiger()
        obj.set_beamcenter_from_fit2d_params(
            *self._beamcenter, tilt=5, tilt_plane=270, rot_unit="degree"
        )
        self.assert_beamcenter_okay(obj)

    def test_set_beamcenter_from_fit2d_params_full_rot_rad(self):
        obj = self.prepare_context_with_Eiger()
        obj.set_beamcenter_from_fit2d_params(
            *self._beamcenter, tilt=0.5, tilt_plane=1, rot_unit="rad"
        )
        self.assert_beamcenter_okay(obj)

    def test_set_beamcenter_from_points_on_circle(self):
        obj = self.prepare_context_with_Eiger()
        r = 300
        _dist = 0.234
        phi = np.r_[[0, 1, 3, 5]]
        _xpoints = self._xpos + r * np.cos(phi)
        _ypoints = self._ypos + r * np.sin(phi)
        obj.set_beamcenter_from_points_on_circle(_xpoints, _ypoints, _dist)
        self.assertAlmostEqual(obj.get_param_value("detector_poni1"), self._ypos_abs, 3)
        self.assertAlmostEqual(obj.get_param_value("detector_poni2"), self._xpos_abs, 3)
        self.assertAlmostEqual(obj.get_param_value("detector_dist"), _dist, 6)


if __name__ == "__main__":
    unittest.main()
