import sys
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
import maya.cmds as mc
import showtools.maya.common as common
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
        self.combo_dict = {}
        self.__twist_value_list = ['X', 'Y', 'Z']
        self.interp_list = []
        okay_button = QtWidgets.QPushButton('OK')
        okay_button.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tableWidget)
        layout.addWidget(okay_button)
        self.setLayout(layout)

    def set_twist(self, interp=None):
        self.interp_list = common.toList(interp)
        self.combo_dict={}
        row_index = 0
        total_driver_list = self.__get_driver_list(self.interp_list)
        self.tableWidget.setRowCount(len(total_driver_list))
        for interp in self.interp_list:
            self.combo_dict[interp] = list()
            driver_list = mc.poseInterpolator(interp, q=1, drivers=1)
            for i, item in enumerate(driver_list):
                self.tableWidget.setItem(row_index, 0, QtWidgets.QTableWidgetItem(item))
                comboBox = QtWidgets.QComboBox()
                comboBox.addItems(self.__twist_value_list)
                comboBox.wheelEvent = self._combo_box_wheel_event
                comboBox.setCurrentIndex(mc.getAttr('{}.driver[{}].driverTwistAxis'.format(interp, i)))
                self.combo_dict[interp].append(comboBox)
                self.tableWidget.setCellWidget(row_index, 1, comboBox)
                row_index += 1

    def accept(self):
        super(TwistTableDialog, self).accept()
        for interp in self.interp_list:
            for i, combo_box in enumerate(self.combo_dict[interp]):
                mc.setAttr('{}.driver[{}].driverTwistAxis'.format(interp, i),
                           self.__twist_value_list.index(combo_box.currentText()))

    def __get_driver_list(self, interp_list):
        driver_list = []
        for interp in self.interp_list:
            driver_list.extend(mc.poseInterpolator(interp, q=1, drivers=1))

        return driver_list

    def _combo_box_wheel_event(self, event):
        return