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

"""Module with the BaseApp from which all apps should inherit.."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParameterCollectionMixIn', 'ObjectWithParameterCollection']

from numbers import Integral
from PyQt5 import QtCore
from numpy import mod

from pydidas.core.parameter import Parameter
from .parameter_collection import ParameterCollection


class ParameterCollectionMixIn:
    """
    MixIn class with ParameterCollection convenience methods.
    If the MixIn is used, the subclass is responsible for creating a
    ParameterCollection instance as self.params attribute.
    """

    default_params = ParameterCollection()

    @classmethod
    def get_default_params_copy(cls):
        """
        Get a copy of the default ParameterCollection.

        Returns
        -------
        ParameterCollection
            A copy of the default ParameterCollection.
        """
        return cls.default_params.get_copy()

    def add_param(self, param):
        """
        Add a parameter to the ParameterCollection.

        This is a wrapper for the ParameterCollection.add_parameter method.

        Parameters
        ----------
        param : Parameter
            An instance of a Parameter object.
        """
        self.params.add_param(param)

    def add_params(self, *params, **kwed_params):
        """
        Add parameters to the object.

        This method adds Parameters to the ParameterCollection of the object.
        Parameters can be either supplies as args or a ParameterCollection
        or dictionary in the form of <ref_key>: <Parameter>.
        This method is explicitly separate from the __init__ method to allow
        subclasses full control over args and kwargs.

        Parameters
        ----------
        *params : Union[Parameter, dict, ParameterCollection]
            Any Parameter or ParameterCollection
        **kwed_params : dict
            A dictionary with Parameters. Note that the dictionary keys will
            be ignored and only the Parameter.refkey attributes will be used.
        """
        for _param in (params + tuple(kwed_params.values())):
            if isinstance(_param, Parameter):
                self.add_param(_param)
            elif isinstance(_param, ParameterCollection):
                self.params.update(_param)
            else:
                raise TypeError(
                    f'Cannot add object of type "{_param.__class__}" '
                    'to ParameterCollection.')

    def set_default_params(self, defaults):
        """
        Set default entries.

        This method will go through the supplied defaults iterable.
        If there are no entries for the Parameter keys, it will add a
        Parameter with default value.

        Parameters
        ----------
        defaults : Union[dict, ParameterCollection, list, tuple, set]
            An iterable with default Parameters.
        """
        if isinstance(defaults, ParameterCollection):
            defaults = defaults.values()
        for _param in defaults:
            if _param.refkey not in self.params:
                self.params.add_param(Parameter(*_param.dump()))

    def get_param_value(self, param_key):
        """
        Get a parameter value.

        Parameters
        ----------
        param_key : str
            The key name of the Parameter.

        Returns
        -------
        object
            The value of the Parameter.
        """
        if not param_key in self.params:
            raise KeyError(f'No parameter with the name "{param_key}" '
                           'has been registered.')
        return self.params.get_value(param_key)

    def get_param(self, param_key):
        """
        Get a parameter.

        *Note*: This method returns the Parameter itself, *not* a copy.

        Parameters
        ----------
        param_key : str
            The key name of the Parameter.

        Returns
        -------
        Parameter
            The Parameter object.
        """
        if not param_key in self.params:
            raise KeyError(f'No parameter with the name "{param_key}" '
                           'has been registered.')
        return self.params[param_key]

    def set_param_value(self, param_key, value):
        """
        Set a parameter value.

        Parameters
        ----------
        param_key : str
            The key name of the Parameter.
        value : *
            The value to be set. This has to be the datatype associated with
            the Parameter.
        """
        if not param_key in self.params:
            raise KeyError(f'No parameter with the name "{param_key}" '
                           'has been registered.')
        self.params.set_value(param_key, value)

    def get_param_values_as_dict(self):
        """
        Get a dictionary with Parameter names and values only.

        Returns
        -------
        name_val_pairs : dict
            The dictionary with Parameter <name>: <value> pairs.
        """
        name_val_pairs = {}
        for _key in self.params:
            name_val_pairs[self.params[_key].name] = self.params[_key].value
        return name_val_pairs

    def print_param_values(self):
        """
        Print the name and value of all Parameters.
        None.
        """
        _config = self.get_param_values_as_dict()
        for _key in _config:
            print(f'{_key}: {_config[_key]}')

    def _apply_param_modulo(self, param_refkey, modulo):
        """
        Apply a modulo to a Parameter.

        This method applies a modulo to a Parameter, referenced by its
        refkey, for example for converting image sizes of -1 to the actual
        detector dimensions.

        Parameters
        ----------
        param_refkey : str
            The reference key for the selected Parameter.
        modulo : int
            The mathematical modulo to be applied.

        Raises
        ------
        ValueError
            If the datatype of the selected Parameter is not integer.

        Returns
        -------
        _val : int
            The modulated Parameter value
        """
        _param = self.params[param_refkey]
        if _param.type is not Integral:
            raise ValueError(f'The datatype of Parameter "{_param.refkey}"'
                             ' is not integer.')
        if _param.value == modulo:
            return _param.value
        _val = mod(_param.value, modulo)
        # create offset for negative indices to capture the whole array
        _offset = 1 if _param.value < 0 else 0
        _param.value = _val + _offset
        return _val + _offset

    def restore_all_defaults(self, confirm=False):
        """
        Restore the default values to all entries.

        Parameters
        ----------
        confirm : bool
            Confirmation flag as safety feature.
        """
        if not confirm == True:
            return
        for _key in self.params.keys():
            self.params[_key].restore_default()

    def _check_key(self, key):
        """
        Check a key exists.

        Parameters
        ----------
        key : str
            The name of the Parameter reference key.

        Raises
        ------
        KeyError
            If the key does not exist.
        """
        if key not in self.params:
            raise KeyError(f'The key {key} is not registered with '
                           f'{self.__class__.__name__}!')


class ObjectWithParameterCollection(QtCore.QObject, ParameterCollectionMixIn):
    """
    An object with a ParameterCollection.

    This class can be inherited by any class which requires a
    ParameterCollection and access methods for it.
    """
    def __init__(self, *args, **kwargs):
        """
        Create a Base instance.

        Parameters
        ----------
        *args : list
            Any arguments. Defined by the concrete
            subclass..
        **kwargs : dict
            A dictionary of keyword arguments. Defined by the concrete
            subclass.
        """
        super().__init__()
        self.params = ParameterCollection()
