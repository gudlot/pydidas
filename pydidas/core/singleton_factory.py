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
Module with the SingletonFactory class which is used to create Singleton
instances of classes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL 3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SingletonFactory"]


from qtpy import QtCore


class SingletonFactory:
    """
    Factory to create a Singleton. This factory also handles QObjects and removes
    the instance if the corresponding QObject has been destroyed.

    Parameters
    ----------
    cls : class
        The Python class which should be managed by the SingletonFactory.
    unreference_deleted_qt_object : bool
        Flag to unreference the associated QObject if a deletion request has been
        sent. This must be True unless the QObject handles its own deletion differently
        from generic objects. If the QObject overwrites delete requests, set to False
        to keep the reference intact. The default is True
    """

    def __init__(self, cls, **permanent_kwargs):
        """
        Setup method.
        """
        self.__instance = None
        self.__class = cls
        self.__permanent_kwargs = permanent_kwargs

    def __call__(self, *args, **kwargs):
        """
        Get the instance of the Singleton.

        Parameters
        ----------
        args : tuple
            Any args to be passed to the class. Note that this is only used
            if no instance exists yet.
        kwargs : dict
            Any kwargs which should be passed. Note that this is only used
            if no instance exists yet.

        Returns
        -------
        object
            The instance of the Singleton class.
        """
        if self.__instance is None:
            self.__instance = self.__class(*args, **(kwargs | self.__permanent_kwargs))
            if isinstance(self.__instance, QtCore.QObject):
                self.__instance.destroyed.connect(self._clear_instance)
        return self.__instance

    def _reset_instance(self, *args, **kwargs):
        """
        Reset the Singleton instance and create a new one.

         Parameters
        ----------
        args : tuple
            Any args to be passed to the class. Note that this is only used
            if no instance exists yet.
        kwargs : dict
            Any kwargs which should be passed. Note that this is only used
            if no instance exists yet.
        """
        self.__instance = self.__class(*args, **(kwargs | self.__permanent_kwargs))

    def _clear_instance(self):
        """
        Clear the instance and reset it with None.
        """
        self.__instance = None

    @property
    def instance(self, **kwargs):
        """
        Get the instance. A wrapper for __call__

        Parameters
        ----------
        kwargs : dict
            Any kwargs which should be passed. Note that this is only used
            if no instance exists yet.
        """
        return self.__call__(**kwargs)
