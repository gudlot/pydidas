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
import shutil
import os

import numpy as np

from pydidas.image_io import ImageReaderCollection
from pydidas.image_io.implementations.numpy_reader import NumpyReader


class TestNumpyReader(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = os.path.join(self._path, 'test.npy')
        self._img_shape = (10, 10)
        self._data = np.random.random(self._img_shape)
        np.save(self._fname, self._data)

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_get_instance(self):
        obj = ImageReaderCollection().get_reader(self._fname)
        self.assertIsInstance(obj, NumpyReader)

    def test_read_image(self):
        obj = ImageReaderCollection().get_reader(self._fname)
        img = obj.read_image(self._fname)
        self.assertTrue((img == self._data).all())


if __name__ == "__main__":
    unittest.main()
