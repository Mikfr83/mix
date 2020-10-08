'''
mix central widget
'''
from mix.ui import *

#mix modules
from mix.ui import layerGraphModel, layerGraphTreeView, fields
import mix.pGraph as pGraph
import mix.pNode as pNode
import mix.ui.radialMenu
reload(mix.ui.radialMenu)

class CentralTabWidget(QtWidgets.QTabWidget):
    def __init__(self, primary_graph = pGraph.PGraph('null'), secondary_graph=pGraph.PGraph('null'), parent=None, tab_name='Main'):
        super(CentralTabWidget, self).__init__(parent)
        self._primary_graph = primary_graph
        self._secondary_graph = secondary_graph
        
        # -------------------------------------------------
        # SETUP TAB
        # -------------------------------------------------
        setupWidget = QtWidgets.QWidget()

        # ------------------------------------------------
        # Primary Tree
        # ------------------------------------------------
        self._setupWidgetLayout = QtWidgets.QHBoxLayout()
        self._setupTreeFilter = QtWidgets.QLineEdit()
        self._setupTreeView = layerGraphTreeView.LayerGraphTreeView()
        self._setupTreeView.setAlternatingRowColors(True)
        self._setupTreeView.setDragEnabled(True)
        self._setupTreeView.setAcceptDrops(True)
        self._setupTreeView.setDropIndicatorShown(True)
        self._setupTreeView.setExpandsOnDoubleClick(True)
        self._setupTreeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # ------------------------------------------------
        # Secondary Tree
        # ------------------------------------------------
        secondary_setupWidget = QtWidgets.QWidget()
        self._secondary_setupWidgetLayout = QtWidgets.QHBoxLayout()
        self._secondary_setupTreeFilter = QtWidgets.QLineEdit()
        self._secondary_setupTreeView = layerGraphTreeView.LayerGraphTreeView()
        self._secondary_setupTreeView.setAlternatingRowColors(True)
        self._secondary_setupTreeView.setDragEnabled(True)
        self._secondary_setupTreeView.setExpandsOnDoubleClick(True)
        self._secondary_setupTreeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        #file view
        #self._fileView = widgets.FileView()
        
        #fields
        # self._setupAttrsWidget = QtWidgets.QFrame()
        # self._setupAttrsLayout = QtWidgets.QVBoxLayout(self._setupAttrsWidget)
        # scrollAreaAttrs = QtWidgets.QScrollArea()
        # scrollAreaAttrs.setWidget(self._setupAttrsWidget)
        # scrollAreaAttrs.setWidgetResizable(True)
        # self._setupAttrsWidget.setFrameShape(QtWidgets.QFrame.Panel)
        # self._setupAttrsWidget.setFrameShadow(QtWidgets.QFrame.Sunken)
        # #self._setupAttrsWidget.setMaximumWidth(200)
        # self._setupAttrsWidget.setMinimumWidth(200)

        # ------------------------------------------------
        # bring it all together
        # ------------------------------------------------
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._setupTreeView)
        splitter.addWidget(self._secondary_setupTreeView)
        self._setupWidgetLayout.addWidget(splitter)
        setupWidget.setLayout(self._setupWidgetLayout)

        # Graphs
        self._model = layerGraphModel.LayerGraphModel(self._primary_graph)
        self._secondary_model = layerGraphModel.LayerGraphModel(self._secondary_graph)

        # Models
        self._setupTreeView.setModel(self._model)
        self._secondary_setupTreeView.setModel(self._secondary_model)

        # Tree
        # Connect the primary treeView selectionChange signal to the secondaryTreeUpdate
        self._setupTreeView.pSelectionChanged = self._primary_tree_selection_change
        self._secondary_setupTreeView.pSelectionChanged = self._secondary_tree_selection_change

        # Tab
        self.addTab(setupWidget, tab_name)
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

    def _executeSelectedNode(self, *args):
        '''
        Runs the selected item in the setup view
        '''
        node = self._selectedNode()
        attributes = dict()

        if node:
            node.execute()

    def _executeAllNodes(self, *args):
        '''
        Will execute the entire graph.
        '''
        nodeList = self._primary_graph.getNodes()

        self._executeFromNode(nodeList[0])

    def _executeFromNode(self, *args):
        '''
        Will execute the current node and every node that is a descendant of that node
        '''
        node = self._selectedNode()
        if args:
            if isinstance(args[0], pNode.PNode):
                node = args[0]
        node.execute()
        nodeList = list(node.descendants())

        for node in nodeList:
            if not node.isActive():
                nodeIndex = nodeList.index(node)
                childList = node.descendants()
                for child in childList:
                    nodeList.pop(nodeIndex+1)
                nodeList.pop(nodeIndex)

        for node in nodeList:
            if node.isActive():
                node.execute()

    def _selectedNode(self):
        '''
        Returns the selected node
        '''
        index = self._setupTreeView.currentIndex()

        if not index.isValid():
            return None
        
        return self._model.itemFromIndex(index)

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
            self._model.beginRemoveRows( index.parent(), index.row(), index.row()+1-1 )
            self.primary_graph.removeNode(node)
            #node.parent().removeChild(node)
            self._model.endRemoveRows()
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

    def _populateSetupAttrsLayout(self, index):
        '''
        Populates the attributes for the given node
        
        :param index: QModelIndex of the node you want to get attributes for
        :type index: QtCore.QModelIndex
        '''
        #Check if there are any items in the layout
        #if self._setupAttrsLayout.count():
        #    self.clearLayout(self._setupAttrsLayout)

        #check to see if the index passed is valid
        if not index.isValid():
            return None
        
        #get the node
        node = self._model.itemFromIndex(index)

        #go through the attributes on the node and create appropriate field
        labelWidth = 150
        for attr in node.getAttributes():
            if attr.getName() == 'position':
                field = fields.VectorField('{0}:'.format(attr.getName()), value = attr.getValue(), attribute = attr)
            elif attr.getType() == "str":
                field = fields.LineEditField('{0}:'.format(attr.getName()), value = str(attr.getValue()), attribute = attr)
            elif attr.getType() == "bool":
                field = fields.BooleanField('{0}:'.format(attr.getName()), value = attr.getValue(), attribute = attr)
            elif attr.getType() == "int":
                field = fields.IntField('{0}:'.format(attr.getName()), value = attr.getValue(), attribute = attr)
            elif attr.getType() == "float":
                field = fields.IntField('{0}:'.format(attr.getName()), value = attr.getValue(), attribute = attr)
            elif attr.getType() == "list":
                field = fields.ListField('{0}:'.format(attr.getName()), value = attr.getValue(), attribute = attr)
            elif attr.getType() == "code":
                field = fields.TextEditField('{0}:'.format(attr.getName()), value = attr.getValue(), attribute = attr)
            elif attr.getType() == "file":
                field = fields.FileBrowserField(label = '{0}:'.format(attr.getName()), filter = "",value = attr.getValue(), attribute = attr)
            elif attr.getType() == "dir":
                field = fields.DirBrowserField(label = '{0}:'.format(attr.getName()), value = attr.getValue(), attribute = attr)
            
            #add the field to the layout
            field.label().setMinimumWidth(labelWidth)
            field.label().setMaximumWidth(labelWidth)
            field.label().setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            self._setupAttrsLayout.addWidget(field)

    def _addNode(self,*args):
        '''
        '''
        self._primary_graph.addNode('null')
     
    def clearLayout(self, layout):
        '''
        Clears a layout of any items with in the layout
        
        :param layout: Layout that you wish to clear
        :type layout: QtGui.QLayout
        '''
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
    
            if isinstance(item, QtWidgets.QWidgetItem):
                item.widget().close()
                # or
                # item.widget().setParent(None)
            elif isinstance(item, QtWidgets.QSpacerItem):
                pass
                # no need to do extra stuff
            else:
                self.clearLayout(item.layout())
    
            # remove the item from layout
            layout.removeItem(item)  
            
    def getAttrFieldValues(self):
        for i in reversed(range(self._setupAttrsLayout.count())):
            item = self._setupAttrsLayout.itemAt(i)
            if isinstance(item, QtWidgets.QWidgetItem):
                item.widget().value()

    def set_primary_graph(self, graph=pGraph.PGraph('null')):
        '''
        Set the primary graph with the passed graph
        '''

        self._primary_graph = graph
        self._model = layerGraphModel.LayerGraphModel(self._primary_graph)
        self._setupTreeView.setModel(self._model)

    def set_secondary_graph(self, graph=pGraph.PGraph('null')):
        '''
        Set the primary graph with the passed graph
        '''

        self._secondary_graph = graph
        self._secondary_model = layerGraphModel.LayerGraphModel(graph)
        self._secondary_setupTreeView.setModel(self._secondary_model)

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
        pass

    def update_secondary_graph(self):
        '''
        Slot for external graph update
        :return:
        '''
        pass

    def update_secondary_graph_slot(self):
        '''
        Slot for external graph update
        :return:
        '''
        pass


    def refresh_secondary_graph(self):
        '''
        Slot for when the selection of the secondary tree changes
        :return:
        '''
        pass

    def _update_primary_tree(self, index, old_indexes):
        '''
        Populates the primary tree
        '''

        # Update the graph with the external call
        primary_graph = self.update_primary_graph()
        self._primary_graph = primary_graph
        if not primary_graph:
            return

        # Build model
        self._model = layerGraphModel.LayerGraphModel(self._primary_graph)
        # Set model to the tree
        self._setupTreeView.setModel(self._model)

    def update_secondary(self, indexes=None):
        '''
        Populate secondary tree
        :return:
        '''

        indexes = self._secondary_setupTreeView.selectedIndexes()
        row = None
        column = None
        if indexes:
            row = indexes[0].row()
            column = indexes[0].column()

        # Update the graph with the external call
        secondary_graph = self.update_secondary_graph()
        self._secondary_graph = secondary_graph
        if not secondary_graph:
            return

        # Build model
        self._secondary_model = layerGraphModel.LayerGraphModel(self._secondary_graph)
        # Set model to the tree
        self._secondary_setupTreeView.setModel(self._secondary_model)

        sel_model = self._secondary_setupTreeView.selectionModel()
        index = self._secondary_model.index(row, column)
        if index:
            sel_model.select(index, QtCore.QItemSelectionModel.Select)


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

        # Update selected nodes on primary graph
        nodes = self._selectedNodeList(self._setupTreeView, self._model)
        self._primary_graph.setSelectedNodes(nodes)

        # Update the graph
        self.update_secondary_graph()
        if not self._secondary_graph:
            return

        # Build the model
        self._secondary_model = layerGraphModel.LayerGraphModel(self._secondary_graph)
        # Set the model to the tree
        self._secondary_setupTreeView.setModel(self._secondary_model)

    def _secondary_tree_selection_change(self):
        # Update selected nodes on primary graph
        nodes = self._selectedNodeList(self._secondary_setupTreeView, self._secondary_model)
        self._secondary_graph.setSelectedNodes(nodes)
        self.refresh_secondary_graph()

    def secondary_tree_clicked(self):
        if self._secondary_graph.getClicked():
            clicked = self._secondary_graph.getClicked()
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
            #menu = RadialMenu()
            menu = rigrepo.ui.radialMenu.RadialMenu()
            menu.rightClickConnect(parentWidget)

        for n in item_list:
            #item = RadialMenuItem(position=n['position'], text=n['text'])
            item = rigrepo.ui.radialMenu.RadialMenuItem(position=n['position'], text=n['text'])
            item.connect(n['func'])
            menu.addItem(item)

        return(menu)

