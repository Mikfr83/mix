'''
mix central widget
'''
from mix.ui import *

#mix modules
import mix.mix_graph as mix_graph
import mix.ui.graph_model as graph_model
import mix.ui.graph_tree_view as graph_tree_view
import mix.ui.graph_tree_item as graph_tree_item
import mix.ui.radial_menu

class GraphWidget(QtWidgets.QWidget):
    def __init__(self, primary_graph = graph_tree_item.GraphTreeItem('null'), secondary_graph=graph_tree_item.GraphTreeItem('null'), model=graph_model, parent=None):
        super(GraphWidget, self).__init__(parent)
        # ------------------------------------------------
        # Primary Tree
        # ------------------------------------------------
        self.mainLayout = QtWidgets.QVBoxLayout()
        self._setupTreeFilter = QtWidgets.QLineEdit()
        self._setupTreeView = graph_tree_view.GraphTreeView()
        self._setupTreeView.setAlternatingRowColors(True)
        self._setupTreeView.setDragEnabled(True)
        self._setupTreeView.setAcceptDrops(True)
        self._setupTreeView.setDropIndicatorShown(True)
        self._setupTreeView.setExpandsOnDoubleClick(True)
        self._setupTreeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # ------------------------------------------------
        # Secondary Tree
        # ------------------------------------------------
        self._secondary_setupTreeView = graph_tree_view.GraphTreeView()
        self._secondary_setupTreeView.setAlternatingRowColors(True)
        self._secondary_setupTreeView.setDragEnabled(True)
        self._secondary_setupTreeView.setExpandsOnDoubleClick(True)
        self._secondary_setupTreeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.model = model
        # Graphs
        self.set_primary_graph(primary_graph)
        self.set_secondary_graph(secondary_graph)

        # ------------------------------------------------
        # bring it all together
        # ------------------------------------------------
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._setupTreeView)
        splitter.addWidget(self._secondary_setupTreeView)
        self.mainLayout.addWidget(splitter)
        self.setLayout(self.mainLayout)

        # Tree
        # Connect the primary treeView selectionChange signal to the secondaryTreeUpdate
        self._setupTreeView.selection_changed_signal.connect(self._primary_tree_selection_change)
        self._secondary_setupTreeView.selection_changed_signal.connect(self._secondary_tree_selection_change)

        self._setupTreeView.expandAll()

    def _toggleActive(self, graph):
        '''
        '''
        nodes = graph.getSelectedNodes()

        if nodes:
            state = not(nodes[0].isActive())
        for node in nodes:
            if state:
                node.enable()
            else:
                node.disable()

    def _selectedNode(self):
        '''
        Returns the selected node
        '''
        index = self._setupTreeView.currentIndex()

        if not index.isValid():
            return None

        return self._primary_graph_model.itemFromIndex(index)

    def _selectedNodeList(self, tree, model):
        '''
        Returns the selected nodes
        '''
        selected_index_list = tree.selectedIndexes()

        valid_node_list = []
        for index in selected_index_list:
            if index.isValid():
                valid_node_list.append(model.itemFromIndex(index))

        return valid_node_list

    def _removeSelectedNode(self):
        index = self._setupTreeView.currentIndex()

        node = self._selectedNode()

        #self._model.removeRows(index.row(), 1, self._model)
        if node:
            self._primary_graph_model.beginRemoveRows( index.parent(), index.row(), index.row()+1-1 )
            self.primary_graph.removeNode(node)
            #node.parent().removeChild(node)
            self._primary_graph_model.endRemoveRows()
            del node

    def _copyNodePath(self):
        """
        This will copy the path to a clipboard.

        :: note..
            Currently we're going to print it until we decide how we want to
            copy it to the clipboard.
        """
        node = self._selectedNode()
        clipboard = QtWidgets.QApplication.clipboard()
        originalText = clipboard.setText("|".join(node.getFullPath().split("|root|")))

    def _addNode(self,*args):
        '''
        '''
        self._primary_graph.addNode('null')

    def set_primary_graph(self, graph=graph_tree_item.GraphTreeItem('null')):
        '''
        Set the primary graph with the passed graph
        '''

        self._primary_graph = graph or graph_tree_item.GraphTreeItem('null')
        self.model.init_primary_graph(self._primary_graph)
        self._primary_graph_model = self.model.GraphModel(self._primary_graph)
        self._setupTreeView.setModel(self._primary_graph_model)

        # clicked func
        self._setupTreeView.clicked.connect(self.primary_tree_clicked)

        radial_menu_list = self._primary_graph.getRadialMenuList()
        self.buildRadialContextMenu(self._setupTreeView, radial_menu_list)

    def set_secondary_graph(self, graph=mix_graph.MixGraph('null')):
        '''
        Set the primary graph with the passed graph
        '''

        self._secondary_graph = graph
        self.model.init_secondary_graph(self._primary_graph, self._secondary_graph)
        self._secondary_graph_model = self.model.GraphModel(graph)
        self._secondary_setupTreeView.setModel(self._secondary_graph_model)

        # clicked func
        self._secondary_setupTreeView.clicked.connect(self.secondary_tree_clicked)
        # double click
        self._secondary_setupTreeView.doubleClicked.connect(self.secondary_tree_double_clicked)

        # Radial menu
        #
        #default_items = [{'position': 'W', 'text': 'Toggle Enabled', 'func': partial(self._toggleActive, graph)}]
        #menu = self.buildRadialContextMenu(self._secondary_setupTreeView, default_items)
        # Add or replace radial items from the graph

        radial_menu_list = self._secondary_graph.getRadialMenuList()
        self.buildRadialContextMenu(self._secondary_setupTreeView, radial_menu_list)

    def update_primary_graph(self):
        '''
        Slot for external graph update
        :return:
        '''
        self.model.update_primary_graph(self._primary_graph)

    def update_secondary_graph(self):
        '''
        Slot for external graph update
        :return:
        '''
        self.model.update_secondary_graph(self._primary_graph, self._secondary_graph)

    def refresh_secondary_graph(self):
        '''
        Slot for when the selection of the secondary tree changes
        :return:
        '''
        self.model.refresh_secondary_graph(self._secondary_graph)

    def _update_primary_tree(self, index, old_indexes):
        '''
        Populates the primary tree
        '''

        # Update the graph with the external call
        self.update_primary_graph()
        # Build model
        self._primary_graph_model = self.model.GraphModel(self._primary_graph)
        # Set model to the tree
        self._setupTreeView.setModel(self._primary_graph_model)

    def update_secondary(self, indexes=None):
        '''
        Populate secondary tree
        :return:
        '''
        indexes = self._secondary_setupTreeView.selectedIndexes()
        seleced_indexes = []
        row = None
        column = None
        if indexes:
            row = indexes[0].row()
            column = indexes[0].column()
        for index in indexes:
            row = index.row()
            column = index.column()
            seleced_indexes.append((row, column))

        # Update the graph with the external call
        self.update_secondary_graph()

        # Build model
        # Build model
        self._secondary_graph_model = self.model.GraphModel(self._secondary_graph)
        # Set model to the tree
        self._secondary_setupTreeView.setModel(self._secondary_graph_model)

        # Reselected the previously selected nodes if the row and column are still valid
        sel_model = self._secondary_setupTreeView.selectionModel()
        for index_data in seleced_indexes:
            row, column = index_data
            index = self._secondary_graph_model.index(row, column)
            if index:
                sel_model.select(index, QtCore.QItemSelectionModel.Select)

    def update_primary(self):
        '''
        '''
        indexes = self._setupTreeView.selectedIndexes()
        selected_indexes = []
        row = None
        column = None
        if indexes:
            row = indexes[0].row()
            column = indexes[0].column()
        for index in indexes:
            row = index.row()
            column = index.column()
            selected_indexes.append((row, column))

        # Update the graph with the external call
        self.update_primary_graph()

        # Build model
        self._primary_graph_model = self.model.GraphModel(self._primary_graph)
        # Set model to the tree
        self._setupTreeView.setModel(self._primary_graph_model)

        # Reselected the previously selected nodes if the row and column are still valid
        sel_model = self._setupTreeView.selectionModel()
        for index_data in selected_indexes:
            row, column = index_data
            index = self._primary_graph_model.index(row, column)
            if index:
                sel_model.select(index, QtCore.QItemSelectionModel.Select)

        self._setupTreeView.expandAll()

    def _iterItems(self, root):
        if root is not None:
            stack = [root]
            while stack:
                parent = stack.pop(0)
                for row in range(parent.rowCount()):
                    for column in range(parent.columnCount()):
                        child = parent.child(row, column)
                        yield child
                        if child.hasChildren():
                            stack.append(child)

    def _primary_tree_selection_change(self):
        '''
        Populates the secondary tree
        '''
        # Update the graph
        nodes = self._selectedNodeList(self._setupTreeView, self._primary_graph_model)
        self._primary_graph.setSelectedNodes(nodes)
        self.update_secondary_graph()
        if not self._secondary_graph:
            return

        # Build the model
        self._secondary_graph_model = self.model.GraphModel(self._secondary_graph)

        # Set the model to the tree
        self._secondary_setupTreeView.setModel(self._secondary_graph_model)

    def _secondary_tree_selection_change(self):
        # Update selected nodes on primary graph
        nodes = self._selectedNodeList(self._secondary_setupTreeView, self._secondary_graph_model)
        self._secondary_graph.setSelectedNodes(nodes)
        self.refresh_secondary_graph()

    def secondary_tree_clicked(self):
        clicked = self._secondary_graph.getClicked()
        if clicked:
            clicked()

    def primary_tree_clicked(self):
        # Update selected nodes on primary graph
        clicked = self._primary_graph.getClicked()
        nodes = self._selectedNodeList(self._setupTreeView, self._primary_graph_model)
        self._primary_graph.setSelectedNodes(nodes)
        if clicked:
            clicked()

    def secondary_tree_double_clicked(self):
        if self._secondary_graph.getDoubleClicked():
            double_clicked = self._secondary_graph.getDoubleClicked()
            double_clicked()

    def buildRadialContextMenu(self, parentWidget, item_list, menu=None):
        '''
        :param parentWidget: Widget that the radial menu is attached to
        :param item_list: List of dicts
               [{'position': 'N', 'text': 'North', 'func': 'run_it', 'checkbox': False},
                {'position': 'S', 'text': 'South', 'func': 'slap_it', 'checkbox': True}]
        :return: radial menu object
        '''

        # Initialize menu if one is not passed
        if not menu:
            menu = mix.ui.radial_menu.RadialMenu()
            menu.rightClickConnect(parentWidget)

        for n in item_list:
            item = mix.ui.radial_menu.RadialMenuItem(position=n['position'], text=n['text'])
            item.connect(n['func'])
            menu.addItem(item)

        return(menu)