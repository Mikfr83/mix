import sys
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
import maya.cmds as mc
from mix.ui import *
class InputDialog(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InputDialog, self).__init__(parent)

    def get_text(self, title='Title', description='Enter Name:', default_text=''):
        text, ok = QtWidgets.QInputDialog.getText(self, title, description, QtWidgets.QLineEdit.Normal, default_text)

        return (text, ok)

    def get_item(self, title='Title', description='Enter Name:', default_items=[], default_index=0):
        item, ok =  QtWidgets.QInputDialog.getItem(self, title, description, default_items, default_index, False)

        return (item, ok)

class TwistTableDialog(MayaQWidgetBaseMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(TwistTableDialog, self).__init__(parent)
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setGeometry(QtCore.QRect(220, 100, 411, 392))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['Drivers', 'Twist Axis'])
        self.combo_list = list()
        self.__twist_value_list = ['X', 'Y', 'Z']
        self.interp = None
        okay_button = QtWidgets.QPushButton('OK')
        okay_button.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tableWidget)
        layout.addWidget(okay_button)
        self.setLayout(layout)

    def set_twist(self, title='Title', interp=None):
        self.setWindowTitle(title)
        driver_list = mc.poseInterpolator(interp, q=1, drivers=1)
        self.tableWidget.setRowCount(len(driver_list))
        self.interp = interp
        for i, item in enumerate(driver_list):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(item))
            comboBox = QtWidgets.QComboBox()
            comboBox.addItems(self.__twist_value_list)
            comboBox.setCurrentIndex(mc.getAttr('{}.driver[{}].driverTwistAxis'.format(interp, i)))
            self.combo_list.append(comboBox)
            self.tableWidget.setCellWidget(i, 1, comboBox)
        self.open()

    def accept(self):
        super(TwistTableDialog, self).accept()

        for i, combo_box in enumerate(self.combo_list):
            mc.setAttr('{}.driver[{}].driverTwistAxis'.format(self.interp, i),
                       self.__twist_value_list.index(combo_box.currentText()))