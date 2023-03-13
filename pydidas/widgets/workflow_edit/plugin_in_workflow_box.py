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
Module with the PluginInWorkflowBox which is a subclassed QLabel and used
to display plugin processing steps in the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PluginInWorkflowBox"]

from functools import partial

from qtpy import QtWidgets, QtCore, QtGui

from ...core import constants
from ...core.utils import apply_qt_properties
from ...workflow import WorkflowTree

TREE = WorkflowTree()


class PluginInWorkflowBox(QtWidgets.QLabel):
    """
    Widget with title and delete button for every selected plugin
    in the processing chain.

    Parameters
    ----------
    plugin_name : str
        The name of the Plugin class.
    widget_id : int
        The widget ID. This is the same as the corresponding node ID.
    parent : Union[QtWidgets.QWidget, None], optional
        The widget's parent. The default is None.
    """

    widget_width = constants.GENERIC_PLUGIN_WIDGET_WIDTH
    widget_height = constants.GENERIC_PLUGIN_WIDGET_HEIGHT
    sig_widget_activated = QtCore.Signal(int)
    sig_widget_delete_branch_request = QtCore.Signal(int)
    sig_widget_delete_request = QtCore.Signal(int)
    sig_new_node_parent_request = QtCore.Signal(int, int)
    sig_create_copy_request = QtCore.Signal(int, int)

    def __init__(self, plugin_name, widget_id, parent=None, **kwargs):
        super().__init__(parent)
        self.setAcceptDrops(True)
        apply_qt_properties(self, **kwargs)
        self._flag_active = False
        self._flag_inconsistent = False
        self.widget_id = widget_id
        self._label = kwargs.get("label", "")

        self.setFixedSize(self.widget_width, self.widget_height)

        self.setAutoFillBackground(True)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.id_label = QtWidgets.QLabel(self)
        self.id_label.setGeometry(3, 3, self.widget_width - 25, 20)

        self.setStyleSheet(self.__get_stylesheet())

        if kwargs.get("deletable", True):
            self.del_button = QtWidgets.QPushButton(self)
            self.del_button.setIcon(self.style().standardIcon(3))
            self.del_button.setGeometry(self.widget_width - 18, 3, 16, 16)
            self.del_button.setStyleSheet(self.__get_stylesheet())
            self.__create_menu()

        self.id_label.setStyleSheet(self.__get_stylesheet(border=False))

        _font = self.font()
        _font.setPointSize(constants.STANDARD_FONT_SIZE + 2)
        self.setFont(_font)
        _font.setBold(True)
        self.id_label.setFont(_font)

        self.update_text(widget_id, self._label)
        self.setText(plugin_name)

    def __create_menu(self):
        """
        Create the custom context menu for adding an replacing nodes.
        """
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._menu_item_context = QtWidgets.QMenu(self)
        self.customContextMenuRequested.connect(self._open_context_menu)

        self._menu_move = QtWidgets.QMenu("Move to a new parent", self)
        self._menu_append = QtWidgets.QMenu(
            "Append a plugin copy to specific node", self
        )
        self._menu_item_context.addMenu(self._menu_move)
        self._menu_item_context.addMenu(self._menu_append)

        self._delete_node_context = QtWidgets.QMenu(self)

        self._del_actions = {
            "delete": QtWidgets.QAction("Delete this node", self),
            "delete_branch": QtWidgets.QAction("Delete this branch", self),
        }
        self._del_actions["delete"].triggered.connect(
            partial(self.sig_widget_delete_request.emit, self.widget_id)
        )
        self._del_actions["delete_branch"].triggered.connect(
            partial(self.sig_widget_delete_branch_request.emit, self.widget_id)
        )
        self._delete_node_context.addAction(self._del_actions["delete"])
        self._delete_node_context.addAction(self._del_actions["delete_branch"])
        self.del_button.setMenu(self._delete_node_context)

    def __get_stylesheet(self, border=True):
        """
        Get the stylesheet based on the active and consistent flags.

        Parameters
        ----------
        border : bool, optional
            Flag to set the border. The default is True.

        Returns
        -------
        QtWidgets.QStylesheet
            The stylesheet for this box.
        """
        _border = (3 if self._flag_active else 1) if border else 0
        if self._flag_inconsistent:
            _bg_color = "rgb(255, 225, 225)"
        elif self._flag_active:
            _bg_color = "rgb(225, 225, 255)"
        else:
            _bg_color = "rgb(225, 225, 225)"
        _style = (
            "QPushButton{ border: 0px; }"
            "QPushButton::menu-indicator { image: none; }"
            "QLabel{font-size: " + f"{constants.STANDARD_FONT_SIZE + 2}px; "
            f"border: {_border}px solid;"
            "border-color: rgb(60, 60, 60);"
            "border-radius: 3px;"
            f"background: {_bg_color};"
            "margin-left: 2px;"
            "margin-bottom: 2px;}"
        )
        return _style

    def mousePressEvent(self, event):
        """
        Extend the generic mousePressEvent by an activation signal.

        Parameters
        ----------
        event : QtCore.QEvent
            The original event.
        """
        event.accept()
        if not self._flag_active:
            self.sig_widget_activated.emit(self.widget_id)

    def delete(self):
        """
        Reimplement the generic delete method and send it to the
        WorkflowTreeEditManager.
        """
        self.sig_widget_delete_request.emit(self.widget_id)

    @QtCore.Slot(int)
    def new_widget_selected(self, selection):
        """
        Select or deselect the widget.

        Parameters
        ----------
        selection : bool
            Flag whether the widget has been selected (True) or deselected
            (False).
        """
        self._flag_active = self.widget_id == selection
        self._update_stylesheets()

    def _update_stylesheets(self):
        """
        Update the stylesheets based on the active and consistent flags.
        """
        self.setStyleSheet(self.__get_stylesheet())
        self.id_label.setStyleSheet(self.__get_stylesheet(border=False))

    @QtCore.Slot(list)
    def receive_inconsistent_signal(self, widget_ids):
        """
        Receive the signal that the given node ID is inconsistent and set the
        stylesheets.

        Parameters
        ----------
        *widget_ids : int
            The widget node ID.
        """
        if self.widget_id in widget_ids and not self._flag_inconsistent:
            self._flag_inconsistent = True
            self._update_stylesheets()

    @QtCore.Slot(list)
    def receive_consistent_signal(self, widget_ids):
        """
        Receive the signal that the given node ID is not inconsistent any more

        Parameters
        ----------
        widget_id : int
            The widget node ID.
        """
        if self.widget_id in widget_ids and self._flag_inconsistent:
            self._flag_inconsistent = False
            self._update_stylesheets()

    def update_text(self, node_id, label=""):
        """
        Update the text for node label.

        Parameters
        ----------
        node_id : int
            The unique node ID.
        label : str, optional
            The new label for the workflow node.
        """
        _txt = f"node {node_id:d}"
        if len(label) > 0:
            self._label = label
            _txt += f": {label}"
        self.id_label.setText(_txt)

    def mouseMoveEvent(self, event):
        """
        Implement a mouse move event to drag the plugins to a new position in the
        WorkflowTree.
        """
        if event.buttons() == QtCore.Qt.LeftButton:
            _drag = QtGui.QDrag(self)
            _mime = QtCore.QMimeData()
            _drag.setMimeData(_mime)

            _pixmap = QtGui.QPixmap(self.size())
            self.render(_pixmap)
            _drag.setPixmap(_pixmap)
            _drag.exec_(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event):
        """
        Enable dragging of this widget.

        Parameters
        ----------
        event : QtCore.QEvent
            The drag event.
        """
        event.accept()

    def dropEvent(self, event):
        """
        Allow dropping the widget on other WorkflowNode widgets.

        Parameters
        ----------
        event : QtCore.QEvent
            The drop event.
        """
        _source_widget = event.source()
        event.accept()
        self.sig_new_node_parent_request.emit(_source_widget.widget_id, self.widget_id)

    @QtCore.Slot(QtCore.QPoint)
    def _open_context_menu(self, point):
        """
        Open the context menu after updating the menu entries based on the
        current WorkflowTree.
        """
        self.__update_menus()
        self._menu_item_context.exec(self.mapToGlobal(point))

    def __update_menus(self):
        """
        Update the menus to move and to append a copy based on the nodes in the Tree.
        """
        self._menu_move.clear()
        self._menu_append.clear()
        self._menu_move_actions = {}
        self._menu_append_actions = {}
        for _id in TREE.node_ids:
            if _id == self.widget_id:
                continue

            _plugin = TREE.nodes[_id].plugin
            _label = _plugin.get_param_value("label")
            _plugin_type = _plugin.plugin_name
            _name = (
                f"{_id}: {_label} [{_plugin_type}]"
                if len(_label) > 0
                else f"{_id} [{_plugin_type}]"
            )
            self._menu_move_actions[_id] = QtWidgets.QAction(_name)
            self._menu_move.addAction(self._menu_move_actions[_id])
            self._menu_move_actions[_id].triggered.connect(
                partial(self._emit_new_parent_signal, _id)
            )
            self._menu_append_actions[_id] = QtWidgets.QAction(_name)
            self._menu_append.addAction(self._menu_append_actions[_id])
            self._menu_append_actions[_id].triggered.connect(
                partial(self._emit_create_copy_signal, _id)
            )

    @QtCore.Slot(int)
    def _emit_new_parent_signal(self, new_parent_id):
        """
        Emit the signal to move the node to a new parent.

        Parameters
        ----------
        new_parent_id: int
            The id of the new parent node.
        """
        self.sig_new_node_parent_request.emit(self.widget_id, new_parent_id)

    @QtCore.Slot(int)
    def _emit_create_copy_signal(self, new_parent_id):
        """
        Emit the signal to move the node to a new parent.

        Parameters
        ----------
        new_parent_id: int
            The id of the new parent node.
        """
        self.sig_create_copy_request.emit(self.widget_id, new_parent_id)
