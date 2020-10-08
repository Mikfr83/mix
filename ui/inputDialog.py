import sys
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from poise.ui import *

class InputDialog(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InputDialog, self).__init__(parent)

    def get_text(self, title='Title', description='Enter Name:', default_text=''):
        text, ok = QtWidgets.QInputDialog.getText(self, title, description, QtWidgets.QLineEdit.Normal, default_text)

        return (text, ok)


