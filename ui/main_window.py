'''
mix UI classes
'''
from mix.ui import *
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as mc
import maya.api.OpenMaya as om2

# mix modules
import model_manager
import mix.ui.graph_tree_item as graph_tree_item
import mix.ui.graph_widget as graph_widget
# -------------------------------
# MAIN WINDOW
# -------------------------------
class MainWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    window_name = 'Mix'
    callback_id_list = []

    def __init__(self,
                 psd_graph_list=[graph_tree_item.GraphTreeItem('Interpolators'),
                                 graph_tree_item.GraphTreeItem('Poses')],
                 weights_graph_list=[graph_tree_item.GraphTreeItem('Deformers'),
                                     graph_tree_item.GraphTreeItem('Maps')],
                 parent=None):
        '''
        This is the main window used for mix

        :param graph: The graph which the ui will use for the setup view
        :type graph: ml_graph.MlGraph

        :param parent: The parent for the ui
        :type parent: QtGui.QWidget
        '''
        self.deleteControl(self.window_name + 'WorkspaceControl')
        super(MainWindow, self).__init__(parent)
        # load in the style sheet

        # set the window title and central widget
        self.setWindowTitle(self.window_name)
        self.setObjectName(self.window_name)
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.psdWidget = graph_widget.GraphWidget(psd_graph_list[0], psd_graph_list[1], model=model_manager.PSD_MODEL)
        #self.weightsWidget = graph_widget.GraphWidget(weights_graph_list[0], weights_graph_list[1],
        #                                              model=model_manager.WEIGHTS_MODEL)
        self.tabWidget.addTab(self.psdWidget, 'PSD')
        #self.tabWidget.addTab(self.weightsWidget, 'Weights')
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # add menu and tool bar to window
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setObjectName('MenuBar')

        # add menus to the menu bar
        fileMenu = self.menuBar.addMenu('File')
        self.mainLayout.setMenuBar(self.menuBar)
        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)
        self.resize(1200, 1200)
        '''
        id = om2.MEventMessage.addEventCallback('SelectionChanged', self.updateDeformerList)
        MainWindow.callback_id_list.append(id)
        '''

    def deleteControl(self, control):
        if mc.workspaceControl(control, q=True, exists=True):
            mc.workspaceControl(control, e=True, close=True)
            mc.deleteUI(control, control=True)
            for id in MainWindow.callback_id_list:
                MainWindow.callback_id_list.pop(MainWindow.callback_id_list.index(id))
                om2.MMessage.removeCallback(id)

    def closeEvent(self, event):
        super(MainWindow, self).closeEvent(event)
        for id in MainWindow.callback_id_list:
            MainWindow.callback_id_list.pop(MainWindow.callback_id_list.index(id))
            om2.MMessage.removeCallback(id)
    '''
    def updateDeformerList(self, *args):
        self.weightsWidget.update_primary()
    '''


def launch(psd_graph_list=[graph_tree_item.GraphTreeItem('Interpolators'), graph_tree_item.GraphTreeItem('Poses')],
           weights_graph_list=[graph_tree_item.GraphTreeItem('Deformers'), graph_tree_item.GraphTreeItem('Maps')]):
    '''
    This function will launch the window docked or undocked based on
    argument passed in.

    :param dock: Whether to dock the window to the main window.
    :type dock: bool

    :return: The instance of the window that was created.
    :rtype: QDockWidget | QMainWindow
    '''
    main_window = MainWindow(psd_graph_list, weights_graph_list)
    main_window.show(dockable=True)
    main_window.psdWidget.model.update_secondary = main_window.psdWidget.update_secondary
    main_window.psdWidget.model.update_primary = main_window.psdWidget.update_primary

    return main_window
