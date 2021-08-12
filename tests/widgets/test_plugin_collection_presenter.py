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

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import random
import sys
import itertools

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtTest, QtGui

from pydidas.widgets.plugin_collection_presenter import (
    PluginCollectionPresenter, _PluginCollectionTreeWidget)
from pydidas.test_objects.dummy_plugins import DummyPluginCollection

_typemap = {0: 'input', 1: 'proc', 2: 'output'}


class TestPluginCollectionPresenter(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication(sys.argv)
        self.num = 21
        self.pcoll = DummyPluginCollection
        self.widgets = []

    def tearDown(self):
        self.q_app.deleteLater()
        self.q_app.quit()

    def tree_click_test(self, double):
        obj = _PluginCollectionTreeWidget(None, self.pcoll)
        spy = QtTest.QSignalSpy(obj.selection_changed)
        self.click_index(obj, double)
        _index = obj.selectedIndexes()[0]
        _name = obj.model().itemFromIndex(_index).text()
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], _name)

    @staticmethod
    def click_index(obj, double=False):
        model = obj.model()
        _type = random.choice([0, 1, 2])
        _num_plugins = len(DummyPluginCollection.plugins[_typemap[_type]])
        _num = random.choice(np.arange(_num_plugins))
        _item = model.item(_type).child(_num)
        index = model.indexFromItem(_item)
        obj.scrollTo(index)
        item_rect = obj.visualRect(index)
        QtTest.QTest.mouseClick(obj.viewport(), QtCore.Qt.LeftButton,
                                QtCore.Qt.NoModifier, item_rect.center())
        if double:
            QtTest.QTest.mouseDClick(obj.viewport(), QtCore.Qt.LeftButton,
                                     QtCore.Qt.NoModifier, item_rect.center())
        return _item

    def test_PluginCollectionTreeWidget_init(self):
        obj = _PluginCollectionTreeWidget(None, self.pcoll)
        self.assertIsInstance(obj, QtWidgets.QTreeView)
        self.assertEqual(obj.width(), 493)

    def test_PluginCollectionTreeWidget__create_tree_model(self):
        obj = _PluginCollectionTreeWidget(None, self.pcoll)
        _root, _model = obj._PluginCollectionTreeWidget__create_tree_model()
        self.assertIsInstance(_root, QtGui.QStandardItem)
        self.assertIsInstance(_model, QtGui.QStandardItemModel)
        self.assertEqual(_model.rowCount(), 3)
        for _num, _ptype in enumerate(['input', 'proc', 'output']):
            self.assertEqual(_model.item(_num).rowCount(),
                             len(self.pcoll.plugins[_ptype]))

    def test_PluginCollectionTreeWidget_single_click(self):
        self.tree_click_test(False)

    def test_PluginCollectionTreeWidget_double_click(self):
        self.tree_click_test(True)

    def test_PluginCollectionPresenter_init(self):
        obj = PluginCollectionPresenter(None, self.pcoll)
        self.assertIsInstance(obj, QtWidgets.QWidget)

    def test_PluginCollectionPresenter_confirm_selection(self):
        obj = PluginCollectionPresenter(None, self.pcoll)
        spy = QtTest.QSignalSpy(obj.selection_confirmed)
        _item = self.click_index(obj._widgets['plugin_treeview'], double=True)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], _item.text())

    def test_PluginCollectionPresenter_preview_plugin(self):
        obj = PluginCollectionPresenter(None, self.pcoll)
        _item = self.click_index(obj._widgets['plugin_treeview'])
        _plugin = DummyPluginCollection.get_plugin_by_name(_item.text())
        _text = obj._widgets['plugin_description'].toPlainText()
        _desc = _plugin.get_class_description(return_list=True)
        for item in list(itertools.chain.from_iterable(_desc)):
            self.assertTrue(_text.find(item) >= 0)


if __name__ == "__main__":
    unittest.main()