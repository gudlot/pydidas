# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import os
import unittest
import tempfile
import shutil
from pathlib import Path

import numpy as np
import h5py

from pydidas.apps.app_utils import ImageMetadataManager
from pydidas.core import get_generic_parameter
from pydidas._exceptions import AppConfigError


class TestImageMetadataManager(unittest.TestCase):

    def setUp(self):
        self._dsize = 40
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path,
                                                  f'test_{i:03d}.npy'))
        self._img_shape = (32, 35)
        self._data = np.random.random((self._dsize,) + self._img_shape)
        for i in range(self._dsize):
            np.save(self._fname(i), self._data[i])
        self._hdf5_fname = Path(os.path.join(self._path, 'test_000.h5'))
        with h5py.File(self._hdf5_fname, 'w') as f:
            f['/entry/data/data'] = self._data

    def tearDown(self):
        shutil.rmtree(self._path)

    def create_second_dataset(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path,
                                                  f'test_{i:03d}.npy'))
        _img_shape = (47, 35)
        _data = np.random.random((self._dsize,) + _img_shape)
        _hdf5_fname = Path(os.path.join(self._path, 'test_001.h5'))
        with h5py.File(_hdf5_fname, 'w') as f:
            f['/entry/data/data'] = _data
        self._hdf5_fname2 = _hdf5_fname
        self._img_shape2 = _img_shape

    def test_creation(self):
        imm = ImageMetadataManager()
        self.assertIsInstance(imm, ImageMetadataManager)

    def test_creation_with_params(self):
        p = get_generic_parameter('binning')
        p.value = 4
        imm = ImageMetadataManager(p)
        self.assertIsInstance(imm, ImageMetadataManager)
        self.assertEqual(imm.get_param_value('binning'), 4)

    def test_external_param_manipulation(self):
        p = get_generic_parameter('binning')
        p.value = 4
        imm = ImageMetadataManager(p)
        p.value = 8
        self.assertEqual(imm.get_param_value('binning'), p.value)

    def test___verify_selection_range(self):
        _range = self._data.shape[0]
        _i0 = 12
        _i1 = 27
        imm = ImageMetadataManager()
        imm.set_param_value('hdf5_first_image_num', _i0)
        imm.set_param_value('hdf5_last_image_num', _i1)
        imm._ImageMetadataManager__verify_selection_range(_range)

    def test___verify_selection_range_negative_indices(self):
        _range = self._data.shape[0]
        _i0 = 12
        _i1 = -3
        imm = ImageMetadataManager()
        imm.set_param_value('hdf5_first_image_num', _i0)
        imm.set_param_value('hdf5_last_image_num', _i1)
        imm._ImageMetadataManager__verify_selection_range(_range)

    def test___verify_selection_range_no_selection(self):
        _range = self._data.shape[0]
        _i0 = 12
        _i1 = 9
        imm = ImageMetadataManager()
        imm.set_param_value('hdf5_first_image_num', _i0)
        imm.set_param_value('hdf5_last_image_num', _i1)
        with self.assertRaises(AppConfigError):
            imm._ImageMetadataManager__verify_selection_range(_range)

    def test_store_image_data(self):
        imm = ImageMetadataManager()
        imm._store_image_data(self._img_shape, self._data.dtype, self._dsize)
        self.assertEqual(imm._config['datatype'], self._data.dtype)
        self.assertEqual(imm._config['raw_img_shape_x'], self._img_shape[1])
        self.assertEqual(imm._config['raw_img_shape_y'], self._img_shape[0])
        self.assertEqual(imm._config['images_per_file'], self._dsize)

    def test_store_image_data_from_single_image(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._fname(0))
        imm._store_image_data_from_single_image()
        self.assertEqual(imm._config['datatype'], self._data.dtype)
        self.assertEqual(imm._config['raw_img_shape_x'], self._img_shape[1])
        self.assertEqual(imm._config['raw_img_shape_y'], self._img_shape[0])
        self.assertEqual(imm._config['numbers'], [0])
        self.assertEqual(imm._config['images_per_file'], 1)

    def test_store_image_data_from_single_image_no_file(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._fname(90))
        with self.assertRaises(FileNotFoundError):
            imm._store_image_data_from_single_image()
        self.assertEqual(imm._config['datatype'], None)
        self.assertEqual(imm._config['raw_img_shape_x'], None)
        self.assertEqual(imm._config['raw_img_shape_y'], None)

    def test_store_image_data_from_hdf5(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm._store_image_data_from_hdf5_file()
        self.assertEqual(imm._config['datatype'], self._data.dtype)
        self.assertEqual(imm._config['raw_img_shape_x'], self._img_shape[1])
        self.assertEqual(imm._config['raw_img_shape_y'], self._img_shape[0])
        self.assertEqual(imm._config['numbers'], range(self._dsize))
        self.assertEqual(imm._config['images_per_file'], self._dsize)

    def test_store_image_data_from_hdf5_wrong_key(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.set_param_value('hdf5_key', 'foo/bar')
        with self.assertRaises(AppConfigError):
            imm._store_image_data_from_hdf5_file()

    def test_store_image_data_from_hdf5_stepping(self):
        _step = 3
        imm = ImageMetadataManager()
        imm.set_param_value('hdf5_stepping', _step)
        imm.set_param_value('first_file', self._hdf5_fname)
        imm._store_image_data_from_hdf5_file()
        self.assertEqual(imm._config['images_per_file'],
                         self._dsize // _step + 1)
        self.assertEqual(imm._config['numbers'], range(0, self._dsize, _step))

    def test___check_roi_for_consistency(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        imm.set_param_value('use_roi', True)
        imm._ImageMetadataManager__check_roi_for_consistency()

    def test___check_roi_for_consistency_wrong_range(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        imm.set_param_value('use_roi', True)
        imm.set_param_value('roi_xlow', 12)
        imm.set_param_value('roi_xhigh', 9)
        imm.set_param_value('roi_ylow', 12)
        imm.set_param_value('roi_yhigh', 9)
        with self.assertRaises(AppConfigError):
            imm._ImageMetadataManager__check_roi_for_consistency()

    def test_calculate_final_image_shape(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        imm.set_param_value('use_roi', False)
        imm.set_param_value('binning', 1)
        imm._calculate_final_image_shape()
        self.assertIsNone(imm.roi)
        self.assertEqual(imm.final_shape, self._img_shape)

    def test_calculate_final_image_shape_with_binning(self):
        _bin = 3
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        imm.set_param_value('use_roi', False)
        imm.set_param_value('binning', _bin)
        imm._calculate_final_image_shape()
        self.assertIsNone(imm.roi)
        _shape = (self._img_shape[0] // _bin, self._img_shape[1] // _bin)
        self.assertEqual(imm.final_shape, _shape)

    def test_calculate_final_image_shape_with_roi(self):
        _xlow =7
        _xhigh = 17
        _ylow = 2
        _yhigh = 22
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        imm.set_param_value('use_roi', True)
        imm.set_param_value('roi_xlow', _xlow)
        imm.set_param_value('roi_xhigh', _xhigh)
        imm.set_param_value('roi_ylow', _ylow)
        imm.set_param_value('roi_yhigh', _yhigh)
        imm.set_param_value('binning', 1)
        imm._calculate_final_image_shape()
        self.assertEqual(imm.roi, (slice(_ylow, _yhigh),
                                   slice(_xlow, _xhigh)))
        self.assertEqual(imm.final_shape, (_yhigh - _ylow, _xhigh - _xlow))

    def test_calculate_final_image_shape_with_roi_and_binning(self):
        _xlow =7
        _xhigh = 17
        _ylow = 2
        _yhigh = 22
        _bin = 3
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        imm.set_param_value('use_roi', True)
        imm.set_param_value('roi_xlow', _xlow)
        imm.set_param_value('roi_xhigh', _xhigh)
        imm.set_param_value('roi_ylow', _ylow)
        imm.set_param_value('roi_yhigh', _yhigh)
        imm.set_param_value('binning', _bin)
        imm._calculate_final_image_shape()
        self.assertEqual(imm.roi, (slice(_ylow, _yhigh),
                                   slice(_xlow, _xhigh)))
        self.assertEqual(imm.final_shape, ((_yhigh - _ylow) // _bin,
                                           (_xhigh - _xlow) // _bin))

    def test_update(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        self.assertEqual(imm._config['images_per_file'], self._dsize)
        self.assertEqual(imm._config['numbers'], range(self._dsize))

    def test_update_single_file(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._fname(0))
        imm.update_input_data()
        self.assertEqual(imm._config['images_per_file'], 1)
        self.assertEqual(imm._config['numbers'], [0])

    def test_update_new_data(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update()
        self.create_second_dataset()
        imm.set_param_value('first_file', self._hdf5_fname2)
        imm.update()
        self.assertEqual(imm.final_shape, self._img_shape2)

    def test_update_new_data_with_roi(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.set_param_value('roi_xlow', 5)
        imm.update()
        self.create_second_dataset()
        imm.set_param_value('first_file', self._hdf5_fname2)
        imm.update()
        self.assertEqual(imm.final_shape, self._img_shape2)

    def test_property_sizex(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        self.assertEqual(imm.raw_size_x, self._img_shape[1])

    def test_property_sizey(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        self.assertEqual(imm.raw_size_y, self._img_shape[0])

    def test_property_numbers(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        _n = imm.numbers
        self.assertEqual(_n, range(self._dsize))

    def test_property_datatype(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        self.assertEqual(imm.datatype, self._data.dtype)

    def test_property_roi(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.set_param_value('use_roi', True)
        imm.update()
        self.assertEqual(imm.roi, (slice(0, self._img_shape[0]),
                                   slice(0, self._img_shape[1])))

    def test_property_final_shape(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update()
        self.assertEqual(imm.final_shape, self._img_shape)

    def test_property_images_per_file(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update()
        self.assertEqual(imm.images_per_file, self._dsize)

    def test_property_hdf5_dset_shape(self):
        imm = ImageMetadataManager()
        imm.set_param_value('first_file', self._hdf5_fname)
        imm.update_input_data()
        self.assertEqual(imm.hdf5_dset_shape, (self._dsize,) + self._img_shape)


if __name__ == "__main__":
    unittest.main()