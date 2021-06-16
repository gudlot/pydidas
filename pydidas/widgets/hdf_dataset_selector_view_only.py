# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with Warning class for showing notifications."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Hdf5DatasetSelectorViewOnly']


from functools import partial

import h5py
import hdf5plugin

from PyQt5 import QtWidgets, QtCore
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser

from .._exceptions import FrameConfigError
from ..utils import get_hdf5_populated_dataset_keys
from .factory import create_spin_box
from .create_widgets_mixin import CreateWidgetsMixIn

DEFAULT_FILTERS = {'/entry/instrument/detector/detectorSpecific/':
                   '"detectorSpecific"\nkeys (Eiger detector)'}


class Hdf5DatasetSelectorViewOnly(QtWidgets.QWidget, CreateWidgetsMixIn):
    """
    The Hdf5DatasetSelector is a compound widget which allows to select
    an hdf5 dataset key and the frame number. By convention, the first
    dimension of a n-dimensional (n >= 3) dataset is the frame number. Any
    2-dimensional datasets will be interpreted as single frames.
    """
    new_frame_signal = QtCore.pyqtSlot(object)

    def __init__(self, parent=None, viewWidget=None,
                 datasetKeyFilters=None):
        """
        Instanciation method.

        Setup the Hdf5DatasetSelector class with widgets and slots.

        Parameters
        ----------
        parent : Union[QWidget, None], optional
            The parent widget. The default is None.
        viewWidget : Union[QWidget, None], optional
            A widget for a full view. It can also be registered later using
            the  *register_view_widget* method. The default is None.
        datasetKeyFilters : Union[dict, None], optional
            A dictionary with dataset keys to be filtered from the list
            of displayed datasets. Entries must be in the format
            {<Key to filter>: <Descriptive text for checkbox>}.
            The default is None.
        """
        super().__init__(parent)

        self.params = dict(activeDsetFilters = [],
                           currentDset = None,
                           dsetFilterMinSize = 50,
                           dsetFilterMinDim = 3,
                           currentFname = None,
                           currentIndex = None,
                           dsetFilters = (datasetKeyFilters
                                          if datasetKeyFilters is not None
                                          else DEFAULT_FILTERS))

        self.flags = dict(slotActive = False,
                          autoUpdate = 0)
        self.w_view = viewWidget
        self._frame = None

        self.__create_widgets_and_layout()
        self.__connect_slots()

    def __create_widgets_and_layout(self):
        """
        Create all required widgets and the layout.

        This private method will create all the required and widgets and
        the layout.

        Returns
        -------
        None.
        """
        # create checkboxes and links for all filter keys:
        _w_filter_keys = []
        for key in self.params['dsetFilters']:
            _text = self.params['dsetFilters'][key]
            _widget = QtWidgets.QCheckBox(f'Ignore {_text}')
            _widget.setChecked(False)
            _widget.stateChanged.connect(
                partial(self._toggle_filter_key, _widget, key))
            _w_filter_keys.append(_widget)

        _layout = QtWidgets.QGridLayout()
        _layout.setHorizontalSpacing(15)
        self.setLayout(_layout)
        for i, widget in enumerate(_w_filter_keys):
            _layout.addWidget(widget, i // 2, i % 2, 1, 2)

        # determine the layout row offset for the other widgets based on
        # the number of filter key checkboxes:
        _row_offset = len(_w_filter_keys) // 2 + len(_w_filter_keys) % 2

        self.create_label('Min. dataset\nsize: ',
                          gridPos=(_row_offset, 0, 1, 1))
        self.create_label('Min. dataset\ndimensions: ',
                          gridPos=(_row_offset, 3, 1, 1))
        self.create_label('Filtered datasets: ',
                          gridPos=(1 + _row_offset, 0, 1, 1))

        self.w_min_datasize = self.create_spin_box(
            value=50, valueRange=(0, int(1e9)), gridPos=(_row_offset, 1, 1, 1)
            )
        self.w_min_datadim = self.create_spin_box(
            value=2, valueRange=(0, 3), gridPos=(_row_offset, 4, 1, 1)
            )

        self.w_select_dataset = QtWidgets.QComboBox()
        self.w_select_dataset.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.w_select_dataset.setMinimumContentsLength(25)
        _layout.addWidget(self.w_select_dataset, 1 + _row_offset, 1, 1, 4)

        self.w_frame_browser = HorizontalSliderWithBrowser()
        _layout.addWidget(self.w_frame_browser, 2 + _row_offset, 0, 1, 5)

        self.w_but_view = self.create_button(
            'Show full frame', gridPos=(3 + _row_offset, 3, 1, 2),
            alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop
            )

        self.w_auto_update = QtWidgets.QCheckBox('Auto update')
        _layout.addWidget(self.w_auto_update, 3 + _row_offset, 0, 1, 2)


        self.setVisible(False)

    def __connect_slots(self):
        """
        Connect all required widget slots (except for the filter keys
        which are set up dynamically along their widgets)
        """
        self.w_min_datasize.valueChanged.connect(self.__populate_dataset_list)
        self.w_min_datadim.valueChanged.connect(self.__populate_dataset_list)
        self.w_select_dataset.currentTextChanged.connect(self.__select_dataset)
        self.w_frame_browser.valueChanged.connect(self._index_changed)
        self.w_but_view.clicked.connect(self.click_view_button)
        self.w_auto_update.clicked.connect(self._toggle_auto_update)

    def register_view_widget(self, widget):
        """
        Register a view widget to be used for full visualization of data.

        This method registers an external view widget for data visualization.
        Note that the widget must accept frames through a <setData> method.

        Parameters
        ----------
        widget : QWidget
            A widget with a <setData> method to pass frames.
        """
        self.w_view = widget

    def _toggle_filter_key(self, widget, key):
        """
        Add or remove the filter key from the active dataset key filters.

        This method will add or remove the <key> which is associated with the
        checkbox widget <widget> from the active dataset filters.
        Note: This method should never be called by the user but it is
        connected to the checkboxes which activate or deactive the respective
        filters.

        Parameters
        ----------
        widget : QWidget
            The checkbox widget which is associated with enabling/disabling
            the filter key.
        key : str
            The dataset filter string.
        """
        if widget.isChecked() and key not in self.params['activeDsetFilters']:
            self.params['activeDsetFilters'].append(key)
        if not widget.isChecked() and key in self.params['activeDsetFilters']:
            self.params['activeDsetFilters'].remove(key)
        self.__populate_dataset_list()

    def _toggle_auto_update(self):
        """
        Toggle automatic updates based on the state of the checkbox widget.
        """
        self.flags['autoUpdate'] = int(self.w_auto_update.isChecked())

    def enable_signal_slot(self, enable):
        """
        Toggle the signal slot to emit the selected frame as signal for other
        widgets.

        Parameters
        ----------
        enable : bool
            Flag to enable the signal slot. If True, a signal is emitted every
            time a new frame is selected. If False, the signal slot is not
            used.
        """
        self.flags['slotActive'] = enable




    def set_filename(self, name):
        """
        Set the filename of the hdf5 file to be used.

        This method stores the filename and calls the internal method to
        populate the list of datasets included in the file.

        Parameters
        ----------
        name : str
            The full file system path to the hdf5 file.
        """
        self.params['currentFname'] = name
        self.__populate_dataset_list()

    def _index_changed(self, index):
        """
        Store the new index from the frame selector.

        This method is connected to the frame selector (slider/field) and
        calls for an update of the frame if the index has changed.

        Parameters
        ----------
        index : int
            The index in the image dataset.
        """
        self.params['currentIndex'] = index
        self.__update(True)

    def __update(self, newFrame=False):
        """
        Propagate an update to any consumers.

        This method will read a new frame from the file if any consumers
        demand it (consumers must active the signal slot or the automatic
        update). The new frame will be passed to any active view/preview
        widgets and a signal emitted if the slot is active.

        Parameters
        ----------
        newFrame : bool
            A flag to tell __updateto process a new frame, e.g. after changing
            the dataset.
        """
        if self.flags['autoUpdate'] or self.flags['slotActive'] or newFrame:
            self.__get_frame()
        if self.flags['slotActive']:
            self.new_frame_signal.emit(self._frame)
        if (self.flags['autoUpdate']
                and self.w_view is not None):
            self.w_view.setData(self._frame)

    def __populate_dataset_list(self):
        """
        Populate the dateset selection with a filtered list of datasets.

        This method reads the structure of the hdf5 file and filters the
        list of datasets according to the selected criteria. The filtered list
        is used to populate the selection drop-down menu.

        Returns
        -------
        None.
        """
        self.params['dsetFilterMinSize'] = self.w_min_datasize.value()
        self.params['dsetFilterMinDim'] = self.w_min_datadim.value()
        _datasets = get_hdf5_populated_dataset_keys(
            self.params['currentFname'],
            minDataSize=self.params['dsetFilterMinSize'],
            minDataDim=self.params['dsetFilterMinDim'],
            ignoreKeys=self.params['activeDsetFilters'])
        self.w_select_dataset.currentTextChanged.disconnect()
        self.w_select_dataset.clear()
        self.w_select_dataset.addItems(_datasets)
        self.w_select_dataset.currentTextChanged.connect(self.__select_dataset)
        if len(_datasets) > 0:
            self.__select_dataset()
        else:
            self.w_but_view.setEnabled(False)

    def __get_frame(self):
        """
        Get and store a frame.

        This internal method reads an image frame from the hdf5 dataset and
        stores it internally for further processing (passing to other widgets
        / signals)
        """
        with h5py.File(self.params['currentFname'], 'r') as f:
            _dset = f[self.params['currentDset']]
            _ndim = len(_dset.shape)
            if _ndim >= 3:
                self._frame = _dset[self.params['currentIndex']]
            elif _ndim == 2:
                self._frame = _dset[...]

    def __select_dataset(self):
        """
        Select a dataset from the drop-down list.

        This internal method is called by the Qt event system if the QComBoBox
        text has changed to notify the main program that the user has selected
        a different dataset to be visualized. This method also updates the
        accepted frame range for the sliders.
        """
        self.params['currentDset'] = self.w_select_dataset.currentText()
        with h5py.File(self.params['currentFname'], 'r') as f:
            _shape = f[self.params['currentDset']].shape
        n_frames = _shape[0] if len(_shape) >= 3 else 0
        self.w_frame_browser.setRange(0, n_frames - 1)
        self.params['currentIndex'] = 0
        self.w_but_view.setEnabled(True)
        self.__update()

    def click_view_button(self):
        """
        Process clicking the view button.

        This method is connected to the clicked event of the View button.
        """
        if not self.flags['autoUpdate']:
            self.__get_frame()
        if not isinstance(self.w_view, QtWidgets.QWidget):
            raise FrameConfigError('The reference is not a widget')
        self.w_view.setData(self._frame)