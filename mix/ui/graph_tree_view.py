from PySide2 import QtGui, QtCore, QtWidgets

class GraphTreeView(QtWidgets.QTreeView):
    '''
    trying to get the selectionModel to work
    '''
    selection_changed_signal = QtCore.Signal()
    def __init__(self, parent=None):
        """
        Constructor for the pTreeView class.
        """
        super(GraphTreeView, self).__init__(parent)

    def mouseReleaseEvent(self, event):
        super(GraphTreeView, self).mouseReleaseEvent(event)
        self.selection_changed_signal.emit()
        return(event)

