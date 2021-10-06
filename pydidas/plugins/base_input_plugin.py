# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the basic Plugin classes."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputPlugin']


from pydidas.core import get_generic_parameter
from pydidas.constants import INPUT_PLUGIN
from pydidas.apps.app_utils import ImageMetadataManager
from pydidas._exceptions import AppConfigError
from .base_plugin import BasePlugin


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """
    plugin_type = INPUT_PLUGIN
    plugin_name = 'Base input plugin'
    input_data_dim = None
    generic_params = BasePlugin.generic_params.get_copy()
    generic_params.add_params(
        get_generic_parameter('use_roi'),
        get_generic_parameter('roi_xlow'),
        get_generic_parameter('roi_xhigh'),
        get_generic_parameter('roi_ylow'),
        get_generic_parameter('roi_yhigh'),
        get_generic_parameter('binning'))
    default_params = BasePlugin.default_params.get_copy()

    def __init__(self, *args, **kwargs):
        """
        Create BasicPlugin instance.
        """
        BasePlugin.__init__(self, *args, **kwargs)
        self.__setup_image_magedata_manager()

    def __setup_image_magedata_manager(self):
        """
        Setup the ImageMetadataManager to determine the shape of the final
        image.

        The shape of the final image is required to determine the shape of
        the processed data in the WorkflowTree.

        Raises
        ------
        AppConfigError
            If neither or both "first_file" or "filename" Parameters are used
            for a non-basic plugin.
        """
        _metadata_params = [self.get_param(key)
                            for key in ['use_roi', 'roi_xlow', 'roi_xhigh',
                                        'roi_ylow', 'roi_yhigh', 'binning']]
        if 'hdf5_key' in self.params:
            _metadata_params.append(self.get_param('hdf5_key'))
        _has_first_file = 'first_file' in self.default_params
        _has_filename = 'filename' in self.default_params
        if _has_first_file and not _has_filename:
            _metadata_params.append(self.get_param('first_file'))
            _use_filename = False
        elif _has_filename and not _has_first_file:
            _metadata_params.append(self.get_param('filename'))
            _use_filename = True
        elif self.basic_plugin:
            # create some dummy value
            _use_filename = True
        else:
            raise AppConfigError('Ambiguous choice of Parameters. Use exactly'
                                 ' one of  both "first_file" and "filename".')
        self._image_metadata = ImageMetadataManager(*_metadata_params)
        self._image_metadata.set_param_value('use_filename', _use_filename)

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        self._image_metadata.update()
        self._config['result_shape'] = self._image_metadata.final_shape