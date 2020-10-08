'''
Fields that are used in our UI

#.. todo: Make a field specifically for lists
'''
from mix.ui import *
import mix.ui.layerGraphModel as layerGraphModel
import mix.pGraph as pGraph
import mix.pNode as pNode

class BaseField(QtWidgets.QWidget):
    font = QtGui.QFont("Arial", 12)
    def __init__(self, label, value = None, description = str(), parent = None, attribute = None):
        super(BaseField, self).__init__(parent)

        self.__label = QtWidgets.QLabel(label)
        self.__label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, 
            QtWidgets.QSizePolicy.Policy.Fixed)
        self.__label.setFont(self.font)
        self.__value = value
        #self.__description = self.setAccessibleDescription(description)
        self.__attribute= attribute
        self.setContentsMargins(0,2,0,2)
    def label(self):
        return self.__label
    
    def attribute(self):
        return self.__attribute
    
    def labelText(self):
        return self.__label.text()
    
    def setLabel(self, value):
        self.__label.setText(value)
    
    def value(self):
        return self.__value
    
    def setValue(self,value):
        self.__value = value
        if self.__attribute:
            self.__attribute.setValue(value)
        
    def setDescription(self, value):
        '''
        Sets the description of the current field
        
        @param value: String describing the field
        @type value: *str* or *QString*  
        '''
        #Check type
        if not isinstance(value, basestring) and not isinstance(value, QtCore.QString):
            raise TypeError('%s must be  a string or QString' % value)
        
        #set values
        self.__description = value
        self.setDescription(value)
        
class LineEditField(BaseField):
    def __init__(self, *args, **kwargs):
        super(LineEditField, self).__init__(*args,**kwargs)
        
        self._layout = QtWidgets.QHBoxLayout()
        self._lineEdit = QtWidgets.QLineEdit()
        self._lineEdit.setFont(self.font)
        self._lineEdit.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, 
            QtWidgets.QSizePolicy.Policy.Fixed)
        #set text if any value
        if self.value():
            self.setText(self.value())
        #self._lineEdit.setMaximumHeight(20)
        self._lineEdit.setMinimumHeight(40)
        self._lineEdit.setMinimumWidth(200)
        self._lineEdit.textChanged.connect(self.setText)
        
        self._layout.addWidget(self.label())
        self._layout.addWidget(self._lineEdit)
        self._layout.addStretch()
        self.setLayout(self._layout)
        
    def setText(self, value):
        '''
        Sets the text for the QLineEdit
        '''
        if not isinstance(value, basestring) and not isinstance(value, QtCore.QString):
            raise TypeError('%s must be an string' % value)
        #get the souce of the call for setText function
        source = self.sender()
        
        #set the value on field
        self.setValue(str(value))
        #set lineEdit text
        if not source == self._lineEdit:
            self._lineEdit.setText(value)
            
    def getLineEdit(self):
        return self._lineEdit

class DirBrowserField(LineEditField):
    def __init__(self, *args, **kwargs):
        super(DirBrowserField, self).__init__(*args, **kwargs)
        self._dirBrowseButton = QtWidgets.QPushButton(QtGui.QIcon( os.path.join(os.path.dirname( __file__ ), 'icons/folder.png') ),'')
        self._dirBrowseButton.clicked.connect(self._getDir)
        self._layout.addWidget(self._dirBrowseButton)
        self._layout.setContentsMargins(0,0,0,0)
        
    def _getDir(self,index):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'open', str(os.getcwd()))
            
        self.setText(str(dir))
        
class FileBrowserField(LineEditField):
    def __init__(self, mode = 'open', filter = "", *args, **kwargs):
        super(FileBrowserField, self).__init__(*args, **kwargs)
        self.__mode = mode.lower()
        self.__filter = filter
        self._fileBrowseButton = QtWidgets.QPushButton(QtGui.QIcon( os.path.join(os.path.dirname( __file__ ), 'icons/folder.png') ),'')
        self._fileBrowseButton.clicked.connect(self._getFile)
        self._layout.addWidget(self._fileBrowseButton)
        self._layout.addStretch()
        self._layout.setContentsMargins(0,0,0,0)
        
    def _getFile(self,*args):
        if self.__mode == 'save':
            file = QtWidgets.QFileDialog.getSaveFileName(self, 'save', str(os.getcwd()), self.__filter)[0]
        else:
            file = QtWidgets.QFileDialog.getOpenFileName(self, 'open', str(os.getcwd()), self.__filter)[0]
        if file:
            self.setText(str(file))
    
class ListField(BaseField):
    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self.listGraph = pGraph.PGraph('listGraph')
        
        for value in self.value():
            self.listGraph.addNode(value)
        
        self._model = layerGraphModel.LayerGraphModel(self.listGraph)
        self._layout = QtWidgets.QHBoxLayout()
        self._listView = QtWidgets.QListView()
        self._listView.setModel(self._model)
        self._listView.setMaximumHeight(100)
        #self._listView.setMaximumWidth(100)
        
        self._layout.addWidget(self.label())
        self._layout.addWidget(self._listView)
        self.setLayout(self._layout)
        self._layout.setContentsMargins(0,0,0,0)
        self._layout.addStretch()
        
        #CONTEXT MENU
        self._listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self._listView, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.showCustomContextMenu)

    
    def showCustomContextMenu(self, pos):
        '''
        Show the context menu at the position of the curser
        
        :param pos: The point where the curser is on the screen
        :type pos: QtCore.QPoint
        '''
        index = self._listView.indexAt(pos)

        if not index.isValid():
            return

        node = self._model.itemFromIndex(index)

        #If node is disabled, return
        if not node.isActive():
            return
        
        #construct menus
        mainMenu = QtWidgets.QMenu(self)

        #main menu actions
        mainMenu.addSeparator()
        addNodeAction = mainMenu.addAction('Add Item')
        removeNodeAction = mainMenu.addAction('Remove Item')
        QtCore.QObject.connect(addNodeAction, QtCore.SIGNAL('triggered()'), self.__addDialog)
        QtCore.QObject.connect(removeNodeAction, QtCore.SIGNAL('triggered()'), self._removeSelectedNode)
        
        mainMenu.popup(QtGui.QCursor.pos())     
        
    def _removeSelectedNode(self):
        index = self._listView.currentIndex()
        
        node = self._selectedNode()

        #self._model.removeRows(index.row(), 1, self._model)
        if node:
            self._model.beginRemoveRows( index.parent(), index.row(), index.row()+1-1 )
            self.listGraph.removeNode(node)
            self._model.endRemoveRows()
            del node
            self.setValue(self.listGraph.nodeNames())
            
    def _addNode(self,value):
        if not isinstance(self.value(),list):
            self.setValue([value])
        else:
            self.setValue(self.value().append(value))
            
        self.listGraph.addNode(value)
        self._model = layerGraphModel.LayerGraphModel(self.listGraph)
        self._listView.setModel(self._model)
        
    def __addDialog(self,*args):
        dialog = QtWidgets.QDialog(self)
        dialog.exec_()
        
    def _selectedNode(self):
        '''
        Returns the selected node
        '''
        index = self._listView.currentIndex()
        
        if not index.isValid():
            return None
        
        return self._model.itemFromIndex(index)

class TextEditField(BaseField):
    def __init__(self, *args, **kwargs):
        super(TextEditField, self).__init__(*args, **kwargs)
        
        self._textEdit = QtWidgets.QPlainTextEdit(self.value())
        #textEditLayout = QtWidgets.QVBoxLayout()
        #textEditLayout.addWidget(self._textEdit)
        self._textEdit.setFont(self.font)
        self.setMinimumHeight(500)
        self._layout = QtWidgets.QVBoxLayout()
        
        self._layout.addWidget(self.label())
        #self._layout.addLayout(textEditLayout)
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._textEdit)
        splitter.addWidget(QtWidgets.QLabel(""))
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, True)
        self._layout.addWidget(splitter)
        #self._layout.addStretch()
        self.setLayout(self._layout)
        self._textEdit.textChanged.connect(self.setText)
        self._layout.setContentsMargins(0,0,0,0)

    def setText(self):
        self.setValue(str(self._textEdit.toPlainText()))

class PTextEdit(QtWidgets.QPlainTextEdit):

    def __init__(self, *args, **kwargs):
        super(PTextEdit, self).__init__(*args, **kwargs)  
        self.textChanged.connect(self.changeSize)

        self.__heightMin = 500
        self.__heightMax = 65000
        self.setMinimumHeight(self.__heightMin)
        self.changeSize()

    def changeSize(self):
        height = self.size().height()
        
        #print "{} <= {} <= {}".format(self.__heightMin, height, self.__heightMax)
        if self.__heightMin <= height <= self.__heightMax:
            #print "it's working", self.document()
            self.setMinimumHeight(height)

class IntField(BaseField):
    def __init__(self, label, value = 0, description = str(), parent = None, min = -100, max = 100, **kwargs):
        super(IntField, self).__init__(label, value, description, parent, **kwargs)
        
        self._layout = QtWidgets.QHBoxLayout()
        self._intBox = QtWidgets.QSpinBox()
        self._intBox.setRange(min,max)
        self._layout.addWidget(self.label())
        if value:
            self._intBox.setValue(value)
        
        self._intBox.valueChanged.connect(self.setValue)
        self._layout.addWidget(self._intBox)
        self._layout.addStretch()
        self.setLayout(self._layout)
        self._layout.setContentsMargins(0,0,0,0)
        
        
    def setValue(self, value):
        '''
        Sets the text for the QLineEdit
        '''
        if not isinstance(value, int):
            raise TypeError('%s must be an integer' % value)
        
        #get the source of where the function is being called
        source = self.sender()
        
        #set field value
        super(IntField, self).setValue(value)
        #set spinBox value
        if not source == self._intBox:
            self._intBox.setValue(value)
        
    def value(self):
        value = self._intBox.value()
        super(IntField, self).setValue(int(value))
        
        return super(IntField,self).value()
                       
class VectorField(BaseField):
    def __init__(self, *args, **kwargs):
        super(VectorField, self).__init__(*args,**kwargs)
        
        #create layouts
        self._layout = QtWidgets.QHBoxLayout()
        self._valueLayout = QtWidgets.QVBoxLayout()
        
        #create widgets
        self._xField = LineEditField(label = 'X')
        self._xField.setFont(self.font)
        self._yField = LineEditField(label = 'Y')
        self._yField.setFont(self.font)
        self._zField = LineEditField(label = 'Z')
        self._zField.setFont(self.font)
        
        #set line edit widths
        self._xField.getLineEdit().setMaximumWidth(55)
        self._xField.getLineEdit().setMinimumWidth(55)
        self._xField.getLineEdit().setMaximumHeight(20)
        self._xField.getLineEdit().setMinimumHeight(20)
        self._yField.getLineEdit().setMaximumWidth(55)
        self._yField.getLineEdit().setMinimumWidth(55)
        self._yField.getLineEdit().setMaximumHeight(20)
        self._yField.getLineEdit().setMinimumHeight(20)
        self._zField.getLineEdit().setMaximumWidth(55)
        self._zField.getLineEdit().setMinimumWidth(55)
        self._zField.getLineEdit().setMaximumHeight(20)
        self._zField.getLineEdit().setMinimumHeight(20)
        
        #set validators for line edits
        self._xField.getLineEdit().setValidator(QtGui.QDoubleValidator())
        self._yField.getLineEdit().setValidator(QtGui.QDoubleValidator())
        self._zField.getLineEdit().setValidator(QtGui.QDoubleValidator())
        
        #connect line edits to set value methods
        self._xField.getLineEdit().editingFinished.connect(self._setValue)
        self._yField.getLineEdit().editingFinished.connect(self._setValue)
        self._zField.getLineEdit().editingFinished.connect(self._setValue)
        
        #add widgets to the layout
        self._valueLayout.addWidget(self._xField)
        self._valueLayout.addWidget(self._yField)
        self._valueLayout.addWidget(self._zField)
        
        #self._valueLayout.addStretch()
        self._layout.addWidget(self.label())
        self._layout.addLayout(self._valueLayout)
        self._valueLayout.setContentsMargins(0,0,0,0)
        self._layout.setContentsMargins(0,0,0,0)

        #set text if any value
        if self.value():
            if isinstance(self.value(), list) or isinstance(self.value(), tuple):
                if len(self.value()) < 3 or len(self.value()) > 3:
                    raise TypeError('%s must be a list of 3 values' % self.value())

                #set the values on the individual fields
                self._xField.getLineEdit().setText('%.4f' % float(self.value()[0]))
                self._yField.getLineEdit().setText('%.4f' % float(self.value()[1]))  
                self._zField.getLineEdit().setText('%.4f' % float(self.value()[2]))
            else:
                raise TypeError('%s must be a list of 3 values' % self.value())
        else:
            self.setValue(['%.4f' % float(0.0),'%.4f' % float(0.0),'%.4f' % float(0.0)])
        
        self.setLayout(self._layout)
        self._layout.addStretch()

    
    def setValue(self, value):
        self._xField.getLineEdit().setText('%.4f' % float(value[0]))
        self._yField.getLineEdit().setText('%.4f' % float(value[1]))
        self._zField.getLineEdit().setText('%.4f' % float(value[2]))
        super(VectorField, self).setValue(*value)
        
    def _setValue(self, *args):
        sender = self.sender()
        if sender == self._xField.getLineEdit():
            value = self._xField.getLineEdit().text()
            self._xField.getLineEdit().setText('%.4f' % float(value))
            super(VectorField, self).setValue((float(value),self.value()[1],self.value()[2]))
        if sender == self._yField.getLineEdit():
            value = self._yField.getLineEdit().text()
            self._yField.getLineEdit().setText('%.4f' % float(value))
            super(VectorField, self).setValue((self.value()[0], float(value), self.value()[2]))
        if sender == self._zField.getLineEdit():
            value = self._zField.getLineEdit().text()
            self._zField.getLineEdit().setText('%.4f' % float(value))
            super(VectorField, self).setValue((self.value()[0],self.value()[1], float(value)))
    
class BooleanField(BaseField):
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        self._layout = QtWidgets.QHBoxLayout()
        self._checkBox = QtWidgets.QCheckBox()
        self._checkBox.toggled.connect(self.setValue)
        self._layout.addWidget(self.label())
        #self._layout.addStretch()
        self._layout.addWidget(self._checkBox)
        self._layout.addStretch()
        self.setValue(self.value())
        self._layout.setContentsMargins(0,0,0,0)
        self.setLayout(self._layout)

    def setValue(self, value):
        super(BooleanField, self).setValue(value)
        self._checkBox.blockSignals(True)
        if value:
            self._checkBox.setCheckState(QtCore.Qt.Checked)
        else:
            self._checkBox.setCheckState(QtCore.Qt.Unchecked)
            
        self._checkBox.blockSignals(False)

