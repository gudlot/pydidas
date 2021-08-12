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

"""Module with the ImageReader base class from which all readers should
inherit."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ImageReader']

from .rebin_2d import rebin2d
from .roi_manager import RoiManager


class ImageReader:
    """Generic implementation of the image reader."""

    def __init__(self):
        """Initialization"""
        self._image = None

    def read_image(self, filename, **kwargs):
        """
        Read an image from file.

        This method must be implemented by the concrete subclasses.
        """
        raise NotImplementedError

    def return_image(self, *args, **kwargs):
        """
        Return the stored image

        Parameters
        ----------
        *args : object
            A list of arguments. Currently not used.
        **kwargs : dict
            A dictionary of keyword arguments. Supported keyword arguments
            include the following
        datatype : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        binning : int, optional
            The reb-inning factor to be applied to the image. The default
            is 1.
        ROI : Union[tuple, None], optional
            A region of interest for cropping. Acceptable are both 4-tuples
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice  objects. If None, the full image
            will be returned. The default is None.

        Raises
        ------
        ValueError
            If no image has beeen read.

        Returns
        -------
        _image : np.ndarray
            The image in form of an ndarray
        _metadata : dict
            The image metadata, as returned from the concrete reader.
        """
        _return_type = kwargs.get('datatype', 'auto')
        _roi = RoiManager(**kwargs).roi
        _binning = kwargs.get('binning', 1)
        if self._image is None:
            raise ValueError('No image has been read.')
        _image = self._image
        if _roi is not None:
            _image = _image[_roi]
        if _binning != 1:
            _image = rebin2d(_image, int(_binning))
        if _return_type not in ('auto', _image.dtype):
            _image = _image.astype(_return_type)
        return _image