from PySide2 import QtGui, QtCore, QtWidgets

class LayerGraphTreeView(QtWidgets.QTreeView):
    '''
    trying to get the selectionModel to work
    '''

    def __init__(self, parent=None):
        """
        Constructor for the pTreeView class.
        """
        super(LayerGraphTreeView, self).__init__(parent)

    #def setModel(self, model):
    #    super(LayerGraphTreeView, self).setModel(model)
    #    self.connect(self.selectionModel(),
    #                 QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
    #                 self.pSelectionChanged)


    #def pSelectionChanged(self, newSelection, oldSelection):
    #    '''
    #    Pass through method so the selectionChanged signal gets emitted when
    #    using the layerGraphModel objects with a treeView
    #    '''
    #    pass

    def pSelectionChanged(self):
        pass

    def mouseReleaseEvent(self, event):
        super(LayerGraphTreeView, self).mouseReleaseEvent(event)
        self.pSelectionChanged()
        return(event)

