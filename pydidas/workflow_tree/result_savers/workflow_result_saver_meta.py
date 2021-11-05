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
"""
Module with the WorkflowTreeIoMeta class which is used for creating
exporter/importer classes and registering them.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResultSaverMeta']

from pydidas.core.io import FileExtensionRegistryMetaclass


class WorkflowResultSaverMeta(FileExtensionRegistryMetaclass):
    """
    Metaclass for WorkflowTree exporters and importers which holds the
    registry with all associated file extensions for exporting WorkflowTrees.
    """
    # need to redefine the registry to have a unique registry for
    # WorkflowResultsSaverMeta
    registry = {}
    active_savers = []
    scan_title = ''

    @classmethod
    def reset(cls):
        """
        Reset the Meta registry and clear all entries.
        """
        cls.registry = {}
        cls.active_savers = []

    @classmethod
    def set_active_savers_and_title(cls, savers, title='unknown'):
        """
        Set the active savers so they do not need to be specified individually
        later on.

        Parameters
        ----------
        savers : list
            A list of the names of the savers.
        title : str, optional
            The title of the scan. If not provided, the title will default to
            "unknown".
        """
        cls.active_savers = []
        cls.scan_title = title
        for _saver in savers:
            cls.verify_extension_is_registered(_saver)
            if _saver not in cls.active_savers:
                cls.active_savers.append(_saver)

    @classmethod
    def prepare_active_savers(cls, save_dir, shapes, labels):
        """
        Prepare the active savers for storing data by creating the required
        files and directories.

        Parameters
        ----------
        save_dir : Union[pathlib.Path, str]
            The full path for the data to be saved.
        shapes : dict
            The shapes of the results in form of a dictionary with nodeID
            keys and result values.
        labels : dict
            The labels of the results in form of a dictionary with nodeID
            keys and label values.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.scan_title = cls.scan_title
            _saver.prepare_files_and_directories(save_dir, shapes, labels)

    @classmethod
    def prepare_saver(cls, extension, save_dir, shapes, labels):
        """
        Call the concrete saver associated with the extension to prepare
        all requird files and directories.

        Parameters
        ----------
        extension : str
            The extension of the saved files.
        save_dir : Union[pathlib.Path, str]
            The full path for the data to be saved.
        shapes : dict
            The shapes of the results in form of a dictionary with nodeID
            keys and result values.
        labels : dict
            The labels of the results in form of a dictionary with nodeID
            keys and label values.
        """
        cls.verify_extension_is_registered(extension)
        _saver = cls.registry[extension]
        _saver.prepare_files_and_directories(save_dir, shapes, labels)

    @classmethod
    def export_to_active_savers(cls, index, frame_result_dict, **kwargs):
        """
        Export the results of a frame to all active savers.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.export_to_file(index, frame_result_dict, **kwargs)

    @classmethod
    def export_full_data_to_active_savers(cls, data):
        """
        Export the full data to all active savers.

        Parameters
        ----------
        data : dict
            The result dictionary with nodeID keys and result values.
        """
        for _ext in cls.active_savers:
            _saver = cls.registry[_ext]
            _saver.export_full_data_to_file(data)

    @classmethod
    def export_full_data_to_file(cls, extension, data):
        """
        Export the full data to all active savers.

        Parameters
        ----------
        extension : str
            The file extension for the saver.
        data : dict
            The result dictionary with nodeID keys and result values.
        """
        cls.verify_extension_is_registered(extension)
        _saver = cls.registry[extension]
        _saver.export_full_data_to_file(data)

    @classmethod
    def export_to_file(cls, index, extension, frame_result_dict, **kwargs):
        """
        Call the concrete export_to_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        index : int
            The frame index.
        extension : str
            The file extension for the saver.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        cls.verify_extension_is_registered(extension)
        _saver = cls.registry[extension]
        _saver.export_to_file(index, frame_result_dict, **kwargs)
