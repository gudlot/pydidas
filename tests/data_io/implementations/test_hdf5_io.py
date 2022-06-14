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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import tempfile
import os
import shutil

import h5py
import numpy as np

from pydidas.data_io.implementations.hdf5_io import Hdf5Io
from pydidas.core.constants import HDF5_EXTENSIONS


class TestHdf5Io(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = tempfile.mkdtemp()
        cls._fname = os.path.join(cls._path, "test.h5")
        cls._data_shape = (12, 13, 14, 15)
        cls._data = np.random.random(cls._data_shape)
        with h5py.File(cls._fname, "w") as _file:
            _file["test/path"] = cls._data
            _file["entry/data/data"] = cls._data[:10, :10, :10, 0]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self):
        ...

    def test_class_extensions(self):
        for _ext in HDF5_EXTENSIONS:
            self.assertIn(_ext, Hdf5Io.extensions_export)
            self.assertIn(_ext, Hdf5Io.extensions_import)

    def test_import_from_file__default(self):
        _data = Hdf5Io.import_from_file(self._fname)
        self.assertTrue(np.allclose(_data, self._data[0, :10, :10, 0]))

    def test_import_from_file__w_int_slice(self):
        _slice = 7
        _data = Hdf5Io.import_from_file(self._fname, frame=_slice)
        self.assertTrue(np.allclose(_data, self._data[_slice, :10, :10, 0]))

    def test_import_from_file__w_list_slice(self):
        _slice = [7]
        _data = Hdf5Io.import_from_file(self._fname, frame=_slice)
        self.assertTrue(np.allclose(_data, self._data[_slice[0], :10, :10, 0]))

    def test_import_from_file__2_consecutive_slicing_axes(self):
        _slicing_axes = [0, 1]
        _slices = [0, 0]
        _data = Hdf5Io.import_from_file(
            self._fname, frame=_slices, slicing_axes=_slicing_axes
        )
        self.assertTrue(np.allclose(_data, self._data[0, 0, :10, 0]))

    def test_import_from_file__2_separate_slicing_axes(self):
        _slicing_axes = [0, 2]
        _slices = [0, 0]
        _data = Hdf5Io.import_from_file(
            self._fname, frame=_slices, slicing_axes=_slicing_axes
        )
        self.assertTrue(np.allclose(_data, self._data[0, :10, 0, 0]))

    def test_import_from_file__false_lens(self):
        _slicing_axes = [0, 1, 2]
        _slices = [0, 0]
        with self.assertRaises(ValueError):
            Hdf5Io.import_from_file(
                self._fname, frame=_slices, slicing_axes=_slicing_axes
            )

    def test_import_from_file__w_dataset(self):
        _slicing_axes = [0, 1]
        _slices = [4, 2]
        _data = Hdf5Io.import_from_file(
            self._fname, frame=_slices, slicing_axes=_slicing_axes, dataset="test/path"
        )
        self.assertTrue(np.allclose(_data, self._data[_slices[0], _slices[1]]))

    def test_import_from_file__metadata_was_copied(self):
        _data = Hdf5Io.import_from_file(self._fname)

        self.assertIn("slicing_axes", _data.metadata)
        self.assertIn("frame", _data.metadata)
        self.assertIn("dataset", _data.metadata)

    def test_export_to_file__file_exists(self):
        with self.assertRaises(FileExistsError):
            Hdf5Io.export_to_file(self._fname, self._data)

    def test_export_to_file__file_exists_and_overwrite(self):
        _fname = os.path.join(self._path, "test_new.h5")
        Hdf5Io.export_to_file(_fname, self._data)
        Hdf5Io.export_to_file(_fname, self._data[:11], overwrite=True)
        _data = Hdf5Io.import_from_file(_fname, slicing_axes=[])
        self.assertEqual(_data.shape, (11,) + self._data_shape[1:])

    def test_export_to_file__w_groupname(self):
        _fname = os.path.join(self._path, "test_gname.h5")
        Hdf5Io.export_to_file(_fname, self._data, dataset="test/new_data")
        _data = Hdf5Io.import_from_file(
            _fname, dataset="test/new_data", slicing_axes=[]
        )
        self.assertEqual(_data.shape, self._data_shape)


if __name__ == "__main__":
    unittest.main()