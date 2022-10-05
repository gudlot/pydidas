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
Module with the SetupExperimentIoBase class which exporters/importers for
SetupExperiment should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SetupExperimentIoBase"]

from ...core.io_registry import GenericIoBase
from ...core import UserConfigError
from .setup_experiment_io_meta import SetupExperimentIoMeta
from .setup_experiment import SetupExperiment


EXP_SETUP = SetupExperiment()


class SetupExperimentIoBase(GenericIoBase, metaclass=SetupExperimentIoMeta):
    """
    Base class for SetupExperiment importer/exporters.
    """

    extensions = []
    format_name = "unknown"
    imported_params = {}

    @classmethod
    def _verify_all_entries_present(cls):
        """
        Verify that the tmp_params dictionary holds all keys from the
        SetupExperiment.
        """
        _missing_entries = []
        for _key in EXP_SETUP.params:
            if _key not in cls.imported_params:
                _missing_entries.append(_key)
        if len(_missing_entries) > 0:
            _text = (
                "The following SetupExperiment Parameters are missing:\n - "
                + "\n - ".join(_missing_entries)
            )
            raise UserConfigError(_text)

    @classmethod
    def _write_to_exp_settings(cls):
        """
        Write the loaded (temporary) Parameters to the SetupExperiment.
        """
        for key in cls.imported_params:
            EXP_SETUP.set_param_value(key, cls.imported_params[key])
        cls.imported_params = {}
