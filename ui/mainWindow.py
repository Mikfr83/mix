'''
mix UI classes
'''

from mix.ui import *

#mix modules
from mix.ui import layerGraphModel
import mix.pGraph as pGraph
import mix.ui.uGraph as uGraph
import mix.ui.centralWidget as centralWidget
reload(centralWidget)
#-------------------------------
#MAIN WINDOW
#-------------------------------
class MainWindow(QtWidgets.QWidget):
    _initialized = None
    _instance = None
    def __new__(cls,*args,**kwargs):
        '''
        Creates a new instance of this object.
        '''
        if not MainWindow._instance:
            MainWindow._instance = QtWidgets.QWidget.__new__(cls)

        return MainWindow._instance

    def __del__(self):
        '''
        Destructor method. Restting the class attributes and destroying thte window.
        '''
        MainWindow._initialized = None
        MainWindow._instance = None

    def __init__(self, graph=uGraph.UGraph('null'), secondary_graph=uGraph.UGraph('nullGraph'), parent = None):
        '''
        This is the main window used for mix

        :param graph: The graph which the ui will use for the setup view
        :type graph: ml_graph.MlGraph
        
        :param parent: The parent for the ui
        :type parent: QtGui.QWidget
        '''
        
        if not MainWindow._initialized:
            super(MainWindow, self).__init__(parent)
            MainWindow._initialized = True
            #load in the style sheet
            
            #set the window title and central widget
            self.setWindowTitle('PUBS UI')
            self.centralWidget = centralWidget.CentralTabWidget(graph, secondary_graph)
            self.mainLayout = QtWidgets.QVBoxLayout(self)
            
            #add menu and tool bar to window
            self.menuBar = QtWidgets.QMenuBar()
            self.menuBar.setObjectName('MenuBar')
            #add menus to the menu bar
            fileMenu = self.menuBar.addMenu('File')
            self.mainLayout.setMenuBar(self.menuBar)
            self.mainLayout.addWidget(self.centralWidget)
            self.setLayout(self.mainLayout)
            #newTemplateAction = fileMenu.addAction('New Template')
            loadTemplateAction = fileMenu.addAction('Load Template')
            #saveTemplateAction = fileMenu.addAction('Save Template')
            #QtCore.QObject.connect(newTemplateAction, QtCore.SIGNAL('triggered()'), self._newTemplate)
            QtCore.QObject.connect(loadTemplateAction, QtCore.SIGNAL('triggered()'), self._loadTemplate)
            #QtCore.QObject.connect(saveTemplateAction, QtCore.SIGNAL('triggered()'), self._saveTemplate)
            self.resize(1200, 1200)
           
    @staticmethod
    def getInstance():
        '''
        '''
        return MainWindow._instance

    """
    def _newTemplate(self):
        '''
        Load all the templates into the dialog
        '''
        self.inheritTemplateDialog = widgets.InheritTemplateDialog(self)
        self.inheritTemplateDialog.show()

        self.inheritTemplateDialog.finished.connect(self.setNewTemplate)
    """

    def _loadTemplate(self, *args):
        '''
        sets the template to the template chosen in the templateDialog
        '''
        import sys
        #get the template chosen
        filepath = QtWidgets.QFileDialog.getOpenFileName(parent = self.parent(), caption ='Load Template',
                                                         directory = os.getcwd(), 
                                                         filter = '*py')
        
        #if no file name we will exit the function
        if not filepath:
            return False
        #seperate the fileName from the extension so we can attach the proper extension
        template = os.path.basename(filepath[0]).split('.')[0]
        dir = os.path.dirname(filepath[0])
        if not dir in sys.path:
            sys.path.append(dir)

        element_name, variant_name, task = template.split('_')

        #import the file and initialize
        if template != 'None':
            tabWidget = self.centralWidget
            #get data from the file
            data = dict()
            #run the data we got from file      
            className = "".join([name.title() for name in template.split('_')]) 
            exec('import {0}; graph = {0}.{1}(name="{2}")').format(template,className, element_name)
            tabWidget.setGraph(graph)
            
    def closeEvent(self, e):
        # Write window size and position to config file
        #self.settings.setValue("size", self.size())
        #self.settings.setValue("pos", self.pos())
        super(MainWindow,self).closeEvent(e)


def DockWindow(Widget):
    """Dock `Widget` into Maya
    Arguments:
        Widget (QWidget): Class
        show (bool, optional): Whether to show the resulting dock once created
    """
    name = Widget.__name__
    # get the pointer to the widget
    dockPtr = OpenMayaUI.MQtUtil.findControl(name)
    dockWidget = wrapinstance(long(dockPtr), QtWidgets.QWidget)
    # instantiate the widget
    child = Widget()
    dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    # add the widget to the dock widget
    dockWidget.layout().addWidget(child)
    return child


def launch(primary_graph=uGraph.UGraph('nullGraph'), secondary_graph=uGraph.UGraph('nullGraph')):
    '''
    This function will launch the window docked or undocked based on
    argument passed in.

    :param dock: Whether to dock the window to the main window.
    :type dock: bool

    :return: The instance of the window that was created.
    :rtype: QDockWidget | QMainWindow
    '''
    name = MainWindow.__name__

    if MAYA:
        # if the UI exists we will delete it for now. We will want.
        if mc.workspaceControl(name, q=True, exists=True):
            if MainWindow._instance:
                MainWindow.getInstance().close()
                MainWindow._instance = None
            mc.deleteUI(name)

        # Find the existing widgets
        #dockPtr = OpenMayaUI.MQtUtil.findControl(name)
        #dockWidget = wrapinstance(long(dockPtr), QtWidgets.QWidget)
        #MainWindow._instance = dockWidget.findChildren(QtWidgets.QWidget)[0]

        # get the label and create the workspaceControl
        label = getattr(MainWindow, "label", name)
        
        dockControl = mc.workspaceControl(
                name,
                tabToControl=["AttributeEditor", -1],
                initialWidth=600,
                minimumWidth=100,
                widthProperty="preferred",
                label=label,
                restore=False,
                retain=True,
                r=True,
                loadImmediately=True,
                uiScript='import mix.ui.mainWindow; mix.ui.mainWindow.DockWindow(mix.ui.mainWindow.MainWindow)',
                closeCommand='import mix.ui.mainWindow; mix.ui.mainWindow.MainWindow.getInstance().close()'
            )
        if MainWindow._instance:
            MainWindow._instance.centralWidget.set_primary_graph(primary_graph)
            MainWindow._instance.centralWidget.set_secondary_graph(secondary_graph)
    else:
        parent=None
        if getMayaWindow:
            parent = getMayaWindow()
            wnd = MainWindow(parent=parent, graph=graph)
            wnd.show()
            wnd.raise_()

    return MainWindow._instance
