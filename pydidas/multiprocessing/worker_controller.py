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

"""Module with the WorkerController class which is a subclassed QThread to
control multiprocessing of computations."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkerController']

import time
import logging
import multiprocessing as mp
from numbers import Integral
from queue import Empty

from PyQt5 import QtCore

from ._processor import processor
from pydidas.utils import get_time_string, pydidas_logger

from pydidas.multiprocessing import processor

logger = pydidas_logger(logging.DEBUG)


class WorkerController(QtCore.QThread):
    """
    The WorkerController is a QThread which can spawn a number of processes
    to perform computations in parallel.

    A function with defined args and kwargs can be called in separate
    processes with the first function argument as the variable that differs
    between function calls.
    """
    progress = QtCore.pyqtSignal(float)
    results = QtCore.pyqtSignal(int, object)
    finished = QtCore.pyqtSignal()

    def __init__(self, n_workers=None):
        """
        Create a WorkerController.

        Parameters
        ----------
        n_workers : int, optional
            The number of spawned worker processes. The default is defined
            in the global QSettings.
        """
        super().__init__()
        self._flag_running = False
        self._flag_thread_alive = True
        self._flag_active = False
        self._flag_stop_after_run = False
        if n_workers is None:
            _settings = QtCore.QSettings('Hereon', 'pydidas')
            n_workers = int(_settings.value('global/mp_n_workers'))
        self._n_workers = n_workers
        logger.debug(f'N Workers : {self._n_workers}')
        self._to_process = []
        self._write_lock = QtCore.QReadWriteLock()
        self._workers = []
        self._workers_done = 0
        self._queues = dict(send=mp.Queue(), recv=mp.Queue(), stop=mp.Queue(),
                            finished=mp.Queue())
        _worker_args = (self._queues['send'], self._queues['recv'],
                        self._queues['stop'], self._queues['finished'], None)
        self._processor = dict(func=processor, args=_worker_args, kwargs={})
        self.__progress_done = 0
        self.__progress_target = 0

    @property
    def n_workers(self):
        """
        Get the number of worker processes.

        Returns
        -------
        int
            The number of workers.
        """
        return self._n_workers

    @n_workers.setter
    def n_workers(self, number):
        """
        Change the number of worker processes.

        *Note*: This change does not take effect until the next time a new
        worker pool is created.

        Parameters
        ----------
        number : int
            The new number of workers

        Raises
        ------
        ValueError
            If number is not of type Integral.
        """
        if not isinstance(number, Integral):
            raise ValueError('The number of workers must be an integer '
                             'number.')
        self._n_workers = number

    def stop(self):
        """
        Stop the thread from running and clean up.
        """
        self.suspend()
        self.add_tasks([None] * self.n_workers)
        self.send_stop_signal()
        self._flag_thread_alive = False

    def suspend(self):
        """
        Suspend the event loop.

        This method effectively suspends the event loop and calls for the
        workers to be joined again. New calculations can be performed by
        using the :py:meth`WorkerController.restart` method.
        """
        self._flag_running = False
        self._wait_for_processes_to_finish()

    def _wait_for_processes_to_finish(self, timeout=2):
        """
        Wait for the processes to finish their calculations.

        Parameters
        ----------
        timeout : float, optional
            The maximum time to wait (in seconds). The default is 10.
        """
        _t0 = time.time()
        while self._flag_active:
            time.sleep(0.05)
            if time.time() - _t0 >= timeout:
                break

    def change_function(self, func, *args, **kwargs):
        """
        Change the function called by the workers.

        This method stops any active processing and resets the queue. Then,
        the function is changed and new workers are spawned. To run the new
        function, new tasks must be submitted.

        Parameters
        ----------
        func : object
            The function to be called by the workers.
        *args : type
            Any arguments which need to be passed to the function.
        **kwargs : kwargs
            Any keyword arguments which need to be passed to the function.
        """
        self.suspend()
        self._reset_task_list()
        self._update_function(func, *args, **kwargs)
        self.restart()

    def _reset_task_list(self):
        """
        Reset and clear the list of tasks.
        """
        self._write_lock.lockForWrite()
        self._to_process = []
        self._write_lock.unlock()

    def _update_function(self, func, *args, **kwargs):
        """
        Store the new function and its calling (keyword) arguments
        internally.

        Parameters
        ----------
        func : object
            The function.
        *args : object
            The function arguments
        **kwargs : object
            The function keyword arguments.
        """
        self._processor['args'] = (self._queues['send'],
                                   self._queues['recv'],
                                   self._queues['stop'],
                                   self._queues['finished'],
                                   func,
                                   *args)
        self._processor['kwargs'] = kwargs

    def restart(self):
        """
        Restart the event loop.

        This method allow the event loop to run and to submit tasks via the
        queue to the workers.
        """
        self._flag_running = True


    def add_task(self, task_arg):
        """
        Add a task to the worker pool.

        This will add a task to the worker pool to call the function defined
        in :py:meth`WorkerController.change_function` method. Note that the
        task_arg given here will be interpreted as the first argument
        required by the function.

        Parameters
        ----------
        task_arg : object
            The first argument for the processing function.
        """
        self._write_lock.lockForWrite()
        self._to_process.append(task_arg)
        self._write_lock.unlock()
        self.__progress_target += 1

    def add_tasks(self, task_args):
        """
        Add tasks to the worker pool.

        This will add tasks to the worker pool to call the function defined
        in :py:meth`WorkerController.change_function` method. Note that the
        task_arg given here will be interpreted as the first argument
        required by the function.

        Parameters
        ----------
        task_args : Union[list, tuple, set]
            An iterable of the first argument for the processing function.
        """
        self._write_lock.lockForWrite()
        for task in task_args:
            self._to_process.append(task)
        self._write_lock.unlock()
        self.__progress_target = len(task_args)

    def send_stop_signal(self):
        """
        Send stop signal to workers.

        This method will send stop signals to all workers.
        Note that the runtime of the workers will be determined by the runtime
        of the called function. This call will be finished before the stop
        signal will be processed.

        Parameters
        ----------
        task_args : Union[list, tuple, set]
            An iterable of the first argument for the processing function.
        """
        for worker in self._workers:
            self._queues['stop'].put(1)

    def finalize_tasks(self):
        """
        Finalize the task list.

        This will add tasks to tell the workers to shut down and set a flag
        to quit the loop once processing is done.
        """
        self._write_lock.lockForWrite()
        for task in [None] * self._n_workers:
            self._to_process.append(task)
        self._write_lock.unlock()
        self._flag_stop_after_run = True

    def run(self):
        """
        Run the thread event loop.

        This method is automatically called upon starting the thread.
        """
        logger.debug('Starting thread')
        self._workers_done = 0
        self._flag_running = True
        logger.debug('Entering thread loop')
        while self._flag_thread_alive:
            if self._flag_running and not self._flag_active:
                self._cycle_pre_run()
            while self._flag_running:
                while len(self._to_process) > 0:
                    self._put_next_task_in_queue()
                time.sleep(0.005)
                self._get_and_emit_all_queue_items()
                self._check_if_workers_done()
            if self._flag_active:
                logger.debug('Waiting for workers to join')
                self._cycle_post_run()
                logger.debug('Joined workers')
            time.sleep(0.005)
        self.finished.emit()
        logger.debug('Emitted finished signal')

    def _cycle_pre_run(self):
        """
        Perform operations before entering the main processing loop.
        """
        self._create_and_start_workers()

    def _create_and_start_workers(self):
        """
        Create and start worker processes.
        """
        logger.debug('Creating worker processes')
        self._workers = [mp.Process(target=self._processor['func'],
                                    args=self._processor['args'],
                                    kwargs=self._processor['kwargs'],
                                    daemon=True)
                         for i in range(self._n_workers)]
        logger.debug('Starting workers')
        for _worker in self._workers:
            logger.debug('Starting worker')
            _worker.start()
        logger.debug('workers running')
        self._flag_active = True
        self.__progress_done = 0

    def _put_next_task_in_queue(self):
        """
        Get the next task from the list and put it into the queue.
        """
        self._write_lock.lockForWrite()
        _arg = self._to_process.pop(0)
        self._write_lock.unlock()
        self._queues['send'].put(_arg)

    def _get_and_emit_all_queue_items(self):
        """
        Get all items from the queue and emit them as signals.
        """
        while True:
            try:
                _task, _results = self._queues['recv'].get_nowait()
                self.results.emit(_task, _results)
                self.__progress_done += 1
                self.progress.emit(self.__progress_done
                                   / self.__progress_target)
            except Empty:
                break
            time.sleep(0.001)

    def _check_if_workers_done(self):
        """
        Check if workers are all done.
        """
        for _worker in self._workers:
            try:
                self._queues['finished'].get_nowait()
                self._workers_done += 1
            except Empty:
                pass
        if self._workers_done >= len(self._workers):
            self._flag_running = False

    def _cycle_post_run(self, timeout=10):
        """
        Perform operations after the the main processing loop.

        Parameters
        ----------
        timeout : float
            The waiting time to wait on the workers to send the finished
            signal before raising a TimeoutError.
        """
        self._join_workers()
        if self._flag_stop_after_run:
            self._flag_thread_alive = False
        self._wait_for_worker_finished_signals(timeout)


    def _join_workers(self):
        """
        Join the workers back to the thread and free their resources.
        """
        logger.debug('Sending stop signals to workers')
        for _worker in self._workers:
            self._queues['send'].put(None)
            self._queues['stop'].put(1)
        logger.debug('calling join on workers')
        for _worker in self._workers:
            _worker.join()
            _worker.terminate()
        self._workers = []
        logger.debug('Joined all workers')
        self._flag_active = False

    def _wait_for_worker_finished_signals(self, timeout=10):
        """
        Wait for the worker finished signals for a maximum of "timeout"
        seconds.

        Parameters
        ----------
        timeout : float, optional
            The maximum wait time in seconds.. The default is 10.

        Raises
        ------
        TimeoutError
            If the maximum wait time is passed.
        """
        if not self._flag_running:
            return
        _tstart = time.time()
        while time.time() - _tstart <= timeout:
            self._check_if_workers_done()
            if not self._flag_running:
                return
        raise TimeoutError('Waiting too long for workers to finish.')
