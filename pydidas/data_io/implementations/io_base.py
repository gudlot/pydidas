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
Module with the IoBase class which exporters/importers using the pydidas
metaclass-based registry should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['IoBase']

import os

from ..io_master import IoMaster
from ...image_io.roi_controller import RoiController
from ..rebin_ import rebin


class IoBase(metaclass=IoMaster):
    """
    Base class for Metaclass-based importer/exporters.
    """
    extensions_export = []
    extensions_import = []
    format_name = ''
    dimensions = []

    _roi_controller = RoiController()
    _data = None

    @classmethod
    def export_to_file(cls, filename, data, **kwargs):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        **kwargs : dict
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError

    @classmethod
    def import_from_file(cls, filename, **kwargs):
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the data file to be imported.
        """
        raise NotImplementedError

    @classmethod
    def check_for_existing_file(cls, filename, **kwargs):
        """
        Check if the file exists and if yes if the overwrite flag has been
        set.

        Parameters
        ----------
        filename : str
            The full filename and path.
        **kwargs : dict
            Any keyword arguments. Supported are:
        **overwrite : bool, optional
            Flag to allow overwriting of existing files.

        Raises
        ------
        FileExistsError
            If a file with filename exists and the overwrite flag is not True.
        """
        _overwrite = kwargs.get('overwrite', False)
        if os.path.exists(filename) and not _overwrite:
            raise FileExistsError(f'The file "{filename}" exists and '
                                  'overwriting has not been confirmed.')

    @classmethod
    def return_data(cls, **kwargs):
        """
        Return the stored data.

        Parameters
        ----------
        **kwargs : dict
            A dictionary of keyword arguments. Supported keyword arguments
            are:
        **datatype : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        **binning : int, optional
            The reb-inning factor to be applied to the image. The default
            is 1.
        **roi : Union[tuple, None], optional
            A region of interest for cropping. Acceptable are both 4-tuples
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice  objects. If None, the full image
            will be returned. The default is None.

        Raises
        ------
        ValueError
            If no deata has beeen read.

        Returns
        -------
        _data : pydidas.core.Dataset
            The data in form of a pydidas Dataset (a subclassed numpy.ndarray).
        """
        _return_type = kwargs.get('datatype', 'auto')
        _local_roi = kwargs.get('roi', None)
        _binning = kwargs.get('binning', 1)
        if cls._data is None:
            raise ValueError('No image has been read.')
        _data = cls._data
        if _local_roi is not None:
            cls._roi_controller.roi = _local_roi
            _data = _data[cls._roi_controller.roi]
        if _binning != 1:
            _data = rebin(_data, int(_binning))
        if _return_type not in ('auto', _data.dtype):
            _data = _data.astype(_return_type)
        return _data
