'''
mix UI classes
'''
from mix.ui import *
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as mc
import maya.api.OpenMaya as om2
import maya.api.OpenMayaUI as omui2

# mix modules
import model_manager
import mix.ui.graph_tree_item as graph_tree_item
import mix.ui.graph_widget as graph_widget

ICONPATH = os.path.join(os.path.dirname(__file__), 'icons')
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
        self.delete_control(self.window_name + 'WorkspaceControl')
        super(MainWindow, self).__init__(parent)
        # set the window title and central widget
        self.setWindowTitle(self.window_name)
        self.setObjectName(self.window_name)
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICONPATH, 'mix_blue_icon.png')))
        self.psdWidget = graph_widget.GraphWidget(psd_graph_list[0], psd_graph_list[1], model=model_manager.PSD_MODEL)
        self.weightsWidget = graph_widget.GraphWidget(weights_graph_list[0], weights_graph_list[1],
                                                      model=model_manager.WEIGHTS_MODEL)
        self.tabWidget.addTab(self.psdWidget, 'PSD')
        self.tabWidget.addTab(self.weightsWidget, 'Weights')
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # add menu and tool bar to window
        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setObjectName('MenuBar')
        toolBar = QtWidgets.QToolBar()
        refreshAction = toolBar.addAction(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "icons/refresh.png")),
                                          'Refresh')
        refreshAction.triggered.connect(self.update_widgets)

        # add menus to the menu bar
        fileMenu = self.menuBar.addMenu('File')
        self.mainLayout.setMenuBar(self.menuBar)
        self.mainLayout.addWidget(toolBar)
        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)
        self.resize(1200, 1200)
        id = om2.MEventMessage.addEventCallback('SelectionChanged', self.update_deformer_list)
        MainWindow.callback_id_list.append(id)
        id = om2.MEventMessage.addEventCallback('SceneOpened', self.update_widgets)
        MainWindow.callback_id_list.append(id)

    def delete_control(self, control):
        if mc.workspaceControl(control, q=True, exists=True):
            mc.workspaceControl(control, e=True, close=True)
            mc.deleteUI(control, control=True)
            self.delete_callbacks()

    def closeEvent(self, event):
        super(MainWindow, self).closeEvent(event)
        self.delete_callbacks()

    def update_deformer_list(self, *args):
        self.weightsWidget.update_primary()

    def update_psd_widget(self, *args):
        '''
        This method will update psd widget
        :param args:
        :return:
        '''
        self.psdWidget.update_primary()
        self.psdWidget.update_secondary()

    def update_widgets(self, *args):
        '''
        This will update all widgets that need to be updated when starting a new session.
        :param args:
        :return:
        '''
        self.update_psd_widget()
        self.update_deformer_list()

    @staticmethod
    def delete_callbacks():
        '''
        This method will ensure all callbacks are deleted.
        '''

        if MainWindow.callback_id_list:
            for id in MainWindow.callback_id_list:
                om2.MMessage.removeCallback(id)
            MainWindow.callback_id_list = []

def launch(psd_graph_list=[graph_tree_item.GraphTreeItem('Interpolators'), graph_tree_item.GraphTreeItem('Poses')],
           weights_graph_list=[graph_tree_item.GraphTreeItem('Deformers'), graph_tree_item.GraphTreeItem('Maps')],
           dock=False):
    '''
    This function will launch the window docked or undocked based on
    argument passed in.

    :param dock: Whether to dock the window to the main window.
    :type dock: bool

    :return: The instance of the window that was created.
    :rtype: QDockWidget | QMainWindow
    '''
    # get the latest mix version and set the title
    import mix
    import os
    import json
    from collections import OrderedDict
    VERSIONPATH = os.path.join(os.path.dirname(mix.__file__), 'version.json')
    f = open(VERSIONPATH, 'r')
    version_data = json.loads(f.read().decode('utf-8'), object_pairs_hook=OrderedDict)
    MainWindow.window_name='Mix - v{}.{}.{}'.format(version_data['MIX']['MAJOR'],
                                                    version_data['MIX']['MINOR'],
                                                    version_data['MIX']['PATCH'])
    f.close()

    # Create a workspace control for the mixin widget by passing all the needed parameters.
    # See workspaceControl command documentation for all available flags.
    main_window = MainWindow(psd_graph_list=[graph_tree_item.GraphTreeItem('Interpolators'),
                                                  graph_tree_item.GraphTreeItem('Poses')],
                                  weights_graph_list=[graph_tree_item.GraphTreeItem('Deformers'),
                                                      graph_tree_item.GraphTreeItem('Maps')])

    main_window.show(dockable=dock, area='right', floating=True)
    if dock:
        mc.workspaceControl('{}WorkspaceControl'.format(main_window.window_name), e=True)

    main_window.psdWidget.model.update_secondary = main_window.psdWidget.update_secondary
    main_window.psdWidget.model.update_primary = main_window.psdWidget.update_primary

    return main_window