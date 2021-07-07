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

"""Module with the CompositeCreatorApp class which allows to combine
images to mosaics."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['MpTestApp']

import time

import numpy as np
from PyQt5 import QtCore

from pydidas.apps.base_app import BaseApp
from pydidas.core import (ParameterCollection,
                          CompositeImage, get_generic_parameter)

DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('hdf5_first_image_num'),
    get_generic_parameter('hdf5_last_image_num'),
    )


def get_image(index, **kwargs):
    _shape = kwargs.get('shape')
    return np.random.random(_shape) + 1e-5


class MpTestApp(BaseApp):
    default_params = DEFAULT_PARAMS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_params()
        self._config = {'n_image': None,
                        'datatype': None,
                        'mp_pre_run_called': False,
                        'mp_post_run_called': False,
                        'calls': 0,
                        'min_index': 0,
                        'max_index': 100
                        }

    def multiprocessing_pre_run(self):
        self._config['mp_pre_run_called'] = True
        self._config['mp_tasks'] = range(self._config['min_index'],
                                         self._config['max_index'])
        self._composite = CompositeImage(
            image_shape=(100, 100),
            composite_nx=10,
            composite_ny=int(np.ceil((self._config['max_index'])/10)),
            composite_dir='x',
            datatype=np.float64)

    def multiprocessing_get_tasks(self):
        return self._config['mp_tasks']

    def multiprocessing_carryon(self):
        self._config['calls'] += 1
        if self._config['calls'] % 2:
            time.sleep(0.01)
            return False
        return True

    def multiprocessing_func(self, index):
            _fname, _kwargs = 'dummy', {'shape': (100, 100)}
            _image = get_image(_fname, **_kwargs)
            return index, _image

    @QtCore.pyqtSlot(int, object)
    def multiprocessing_store_results(self, index, image):
        self._composite.insert_image(image, index - self._config['min_index'])

    def multiprocessing_post_run(self):
        self._config['mp_post_run_called'] = True


if __name__ == '__main__':
    from pydidas.multiprocessing.app_processor_func import app_processor
    import multiprocessing as mp
    import matplotlib.pyplot as plt
    in_queue, out_queue, stop_queue = mp.Queue(), mp.Queue(), mp.Queue()
    app = MpTestApp()
    app.multiprocessing_pre_run()
    tasks = app.multiprocessing_get_tasks()
    for task in tasks:
        in_queue.put(task)
    in_queue.put(None)
    app_processor(in_queue, out_queue, stop_queue, app.__class__, app.params.get_copy(), app._config)
    res = [out_queue.get() for i in range(100)]
    for item in res:
        app.multiprocessing_store_results(*item[1])

    plt.figure(1)
    plt.imshow(app._composite.image)
    _image1 = app._composite.image
    app.run()
    _image2 = app._composite.image
    plt.imshow(_image1 - _image2)