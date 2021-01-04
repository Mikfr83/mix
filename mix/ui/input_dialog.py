from mix.ui import *
import openrig.shared.common as common
import model_manager
import fields

class InputDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InputDialog, self).__init__(parent)

    def get_text(self, title='Title', description='Enter Name:', default_text=''):
        text, ok = QtWidgets.QInputDialog.getText(self, title, description, QtWidgets.QLineEdit.Normal, default_text)

        return (text, ok)

    def get_item(self, title='Title', description='Enter Name:', default_items=[], default_index=0):
        item, ok =  QtWidgets.QInputDialog.getItem(self, title, description, default_items, default_index, False)

        return (item, ok)

class TwistTableDialog(QtWidgets.QDialog):

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
            driver_list = model_manager.PSD_MODEL.get_drivers(interp)
            for i, item in enumerate(driver_list):
                self.tableWidget.setItem(row_index, 0, QtWidgets.QTableWidgetItem(item))
                comboBox = QtWidgets.QComboBox()
                comboBox.addItems(self.__twist_value_list)
                comboBox.wheelEvent = self._combo_box_wheel_event
                comboBox.setCurrentIndex(model_manager.PSD_MODEL.get_current_twist_value(interp, i))
                self.combo_dict[interp].append(comboBox)
                self.tableWidget.setCellWidget(row_index, 1, comboBox)
                row_index += 1

    def accept(self):
        for interp in self.interp_list:
            for i, combo_box in enumerate(self.combo_dict[interp]):
                model_manager.PSD_MODEL.set_driver_twist_value(interp, i, combo_box.currentIndex())
        self.close()

    def __get_driver_list(self, interp_list):
        driver_list = []
        for interp in interp_list:
            driver_list.extend(model_manager.PSD_MODEL.get_drivers(interp))

        return driver_list

    def _combo_box_wheel_event(self, event):
        return

class InterpolationDialog(QtWidgets.QDialog):
    accept_signal = QtCore.Signal()
    def __init__(self, parent=None):
        super(InterpolationDialog, self).__init__(parent)
        self.interp_list = list()
        self.widget = QtWidgets.QWidget()
        self.widget.setGeometry(QtCore.QRect(220, 100, 411, 392))
        widget_layout = QtWidgets.QGridLayout()
        self.regularization_field = fields.FloatField('Regularization: ', 0.0000)
        self.regularization_field.setText(0.0000)
        self.smoothing_field = fields.FloatField('Output Smoothing: ', 0.0000)
        self.smoothing_field.setText(0.0000)
        self.negative_weights_field = fields.BooleanField('Allow Negative Weights:', 1)
        self.track_rotation_field = fields.BooleanField('Track Rotation:', 1)
        self.track_translation_field = fields.BooleanField('Track Translation:', 0)
        self.interpolation_combo_box = QtWidgets.QComboBox()
        #interpolation_layout = QtWidgets.QHBoxLayout()
        interpolation_label = QtWidgets.QLabel('Interpolation: ')
        interpolation_label.setFont(fields.BaseField.font)
        self.interpolation_combo_box.addItems(['Linear', 'Gaussian'])
        self.interpolation_combo_box.wheelEvent = self._combo_box_wheel_event
        self.interpolation_combo_box.setCurrentIndex(0)
        self.interpolation_combo_box.setFont(fields.BaseField.font)
        #interpolation_layout.addWidget(interpolation_label)
        #interpolation_layout.addWidget(self.interpolation_combo_box)
        '''
        widget_layout.addStretch()
        widget_layout.addWidget(self.regularization_field)
        widget_layout.addWidget(self.smoothing_field)
        widget_layout.addLayout(interpolation_layout)
        widget_layout.addWidget(self.negative_weights_field)
        widget_layout.addWidget(self.track_rotation_field)
        widget_layout.addWidget(self.track_translation_field)
        widget_layout.setAlignment(QtCore.Qt.AlignLeft)
        widget_layout.addStretch()
        '''
        widget_layout.addWidget(self.regularization_field.label(), 0, 0, QtCore.Qt.AlignRight)
        widget_layout.addWidget(self.regularization_field._lineEdit, 0, 1, QtCore.Qt.AlignLeft)
        widget_layout.addWidget(self.smoothing_field.label(), 1, 0, QtCore.Qt.AlignRight)
        widget_layout.addWidget(self.smoothing_field._lineEdit, 1, 1, QtCore.Qt.AlignLeft)
        widget_layout.addWidget(interpolation_label, 2, 0, QtCore.Qt.AlignRight)
        widget_layout.addWidget(self.interpolation_combo_box, 2, 1, QtCore.Qt.AlignLeft)
        widget_layout.addWidget(self.negative_weights_field.label(), 3, 0, QtCore.Qt.AlignRight)
        widget_layout.addWidget(self.negative_weights_field._checkBox, 3, 1, QtCore.Qt.AlignLeft)
        widget_layout.addWidget(self.track_rotation_field.label(), 4, 0, QtCore.Qt.AlignRight)
        widget_layout.addWidget(self.track_rotation_field._checkBox, 4, 1, QtCore.Qt.AlignLeft)
        widget_layout.addWidget(self.track_translation_field.label(), 5, 0, QtCore.Qt.AlignRight)
        widget_layout.addWidget(self.track_translation_field._checkBox, 5, 1, QtCore.Qt.AlignLeft)


        self.widget.setLayout(widget_layout)
        okay_button = QtWidgets.QPushButton('OK')
        okay_button.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.widget)
        layout.addWidget(okay_button)
        self.setLayout(layout)

    def set_interps(self, interp_list):
        self.interp_list = interp_list

    def accept(self):
        model_manager.PSD_MODEL.set_interpolation(self.interp_list)
        self.close()

    def _combo_box_wheel_event(self, event):
        return