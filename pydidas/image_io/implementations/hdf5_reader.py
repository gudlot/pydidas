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

"""Module with the Hdf5Reader class for reading hdf5 images."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from numpy import squeeze

from ...core import Dataset
from ..image_reader import ImageReader
from ..image_reader_factory import ImageReaderFactory
from ..low_level_readers.read_hdf5_slice import read_hdf5_slice
from ...config import HDF5_EXTENSIONS

class Hdf5Reader(ImageReader):
    """ImageReader implementation for hdf5 files."""

    def __init__(self):
        super().__init__()

    def read_image(self, filename, **kwargs):
        """
        Read an image from an hdf5 file.

        The read_image method extracts an image from a HDF file and returns
        it after processing any operations specified by the keywords
        (binning, cropping).

        The datapath, frame, axis parameters are required.

        Parameters
        ----------
        filename : str
            The full path and filename of the file to be read.
        dataset : str
            The full path to the hdf dataset within the file. The default is
            None which will raise an exception.
        frame : int
            The number of the image in the dataset. The default is 0.
        axis : int
            The number of the axis with the image. The default is 0.
        ROI : Union[tuple, None], optional
            A region of interest for cropping. Acceptable are both 4-tuples
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice  objects. If None, the full image
            will be returned. The default is None.
        returnType : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        binning : int, optional
            The reb-inning factor to be applied to the image. The default
            is 1.

        Returns
        -------
        image : pydidas.core.Dataset
            The image in form of a Dataset (with embedded metadata)
       """
        axis = kwargs.get('axis', 0)
        frame = kwargs.get('frame', 0)
        dataset = kwargs.get('dataset', None)

        self._image_metadata = {'axis': axis, 'frame': frame,
                                'dataset': dataset}
        kwargs.update(self._image_metadata)
        if dataset is None:
            raise KeyError('The hdf dataset has not been specified.')
        _img = squeeze(
            read_hdf5_slice(filename, dataset, [None] * axis + [frame])
        )
        self._image = Dataset(_img, metadata={'axis': axis,
                                              'frame': frame,
                                              'dataset': dataset}
        )
        return self.return_image(**kwargs)


reader = ImageReaderFactory()
reader.register_format('hdf5', HDF5_EXTENSIONS, Hdf5Reader)