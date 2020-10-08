'''
UI models 
'''
from poise.ui import *

#Japeto modules
from poise import pGraph, pNode

class LayerGraphModel(QtCore.QAbstractItemModel):
    NodeRole = QtCore.Qt.UserRole
    def __init__(self, graph, parent = None):
        super(LayerGraphModel, self).__init__(parent)
        
        self._graph = graph
        self._rootNode = pNode.PNode('root')
        self._rootNode.addChildren(graph.rootNodes())

    def itemFromIndex( self, index ):
        return index.data(self.NodeRole) if index.isValid() else self._rootNode
    
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
            
        return parentNode.childCount()
    
    def columnCount(self, parent):
        return 1
    
    def data(self, index, role):
        if not index.isValid():
            return None
        
        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.getNiceName()
        elif role == self.NodeRole:
            return node
        elif role == QtCore.Qt.ForegroundRole:#DecorationRole:
            if node.isLive():
                return QtGui.QColor("crimson")
            if node.isActive():
                if node.isEdit():
                    return QtGui.QColor("white")
                else:
                    return QtGui.QColor("lightGray")
            elif not node.isActive():
                return QtGui.QColor("gray")

        elif role == QtCore.Qt.FontRole:#FontRole:
            font = QtGui.QFont("Courier",11)
            if node.isActive():
                font.setStrikeOut(0)
            else:
                font.setStrikeOut(1)

            if node.isEdit():
                font.setBold(1)
                font.setItalic(1)
            else:
                font.setBold(0)
                font.setItalic(0)

            if node.isLive():
                font.setUnderline(1)
            else:
                font.setUnderline(0)
            return font

    def headerData(self,section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:  
            return '{0} Graph'.format(self._graph.getName())
     
        return None  
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable #| QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
    
    def parent(self, index):
        """
        :param index: Index of the node on the graph you want to get the parent
        :type index: *QModelIndex* 
        """
        node = index.internalPointer()
        parentNode = node.getParent()
        
        
        if not parentNode:
            parentNode = self._rootNode
            
        #if parent is root, return QModelIndex
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        
        #if parent isn't root node, we wrap it up in a QModel index by
        #using internal method.
        return self.createIndex(parentNode.index(), 0, parentNode)
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(str(value))
                
                return True
            
        return True
    
    def index(self, row, column,parent = QtCore.QModelIndex()):
        """
        :param row: Row index of the child node.
        :type index: *int* 
        
        :param column: Column index of the child node.
        :type column: *int* 
        
        :param parent: Parent of the child we are looking for.
        :type parent: *QModelIndex*
        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        try:
            childItem = parentNode.childAtIndex(index = row)
    
            if childItem:
                return self.createIndex(row, column, childItem)
        except:
            return QtCore.QModelIndex()
        
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode

    def supportedDropActions( self ):
        '''Items can be moved and copied (but we only provide an interface 
        or moving items in this example.'''
        return QtCore.Qt.MoveAction 

    def insertRows(self, row, count,parent = QtCore.QModelIndex(),node = None):
        '''
        Insert rows at given row index
        '''
        self.beginInsertRows(parent, row, row + count - 1)
        if node:
            if not parent.isValid():
                parentNode = self._rootNode
                graphParent = None
            else:
                parentNode = parent.internalPointer()
                graphParent = parentNode
            
            self._graph.addNode(node, graphParent, row)
            parentNode.addChild(node, row)
            
        self.endInsertRows()
        
        return True

    def removeRows( self, row, count, parentIndex ):
        '''Remove a number of rows from the model at the given row and parent.'''
        self.beginRemoveRows( parentIndex, row, row+count-1 )
        self.endRemoveRows()
        return True

    def mimeTypes(self):
        return [ "application/x-MlNodes" ]

    def mimeData(self, indices):
        mimeData = QtCore.QMimeData()
        encodedData = QtCore.QByteArray()
        stream = QtCore.QDataStream(encodedData, QtCore.QIODevice.WriteOnly)

        for index in indices:
            if not index.isValid():
                continue
            node = index.internalPointer()
        
            variant = node.getName()
        
            # add all the items into the stream
            stream << variant
        
        #print "Encoding drag with: ", "application/x-MlNodes" < --- for testing
        mimeData.setData("application/x-MlNodes", encodedData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
    
        if action == QtCore.Qt.MoveAction:
            #print "Moving" <-- for testing 
            pass
        
        # Where are we inserting?
        beginRow = 0
        if row != -1:
            #print """ROW IS NOT -1, meaning inserting inbetween,
            #       above or below an existing node""" <-- for testing
            beginRow = row
        elif parent.isValid():
            #print """PARENT IS VALID, inserting ONTO something since row was not -1, 
            #        beginRow becomes 0 because we want to insert it at the begining
            #        of this parents children"""
            parentNode = parent.internalPointer()
            beginRow = parentNode.childCount()
        else:
            #print """PARENT IS INVALID, inserting to root, can change to 0 if you want 
            #        it to appear at the top"""
            beginRow = self.rowCount(QtCore.QModelIndex())
        
        # create a read only stream to read back packed data from our QMimeData
        encodedData = data.data("application/x-MlNodes")
        
        stream = QtCore.QDataStream(encodedData, QtCore.QIODevice.ReadOnly)
    
        # decode all our data back into dropList
        dropList = []
        numDrop = 0
        
        while not stream.atEnd():
            variant = str()
            stream >> variant # extract
            name = variant
            node = None
            
            for node in self._rootNode.descendants():
                if name == node.getName():
                    node = node 
                    break
                
            if not node:
                break
            
            # add the python object that was wrapped up by a QVariant back
            #in our mimeData method
            dropList.append( node ) 
            
            # number of items to insert later
            numDrop += 1
        
            # This will insert new items, so you have to either update the
            #values after the insertion or write your own method to receive
            #our decoded dropList objects.
            self.insertRows(beginRow, numDrop, parent, node)

        return True
