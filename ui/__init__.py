'''
Currently this is only setup to be used with pyside. We may
want to change this to use QT5 at some point.
'''
#sip module
import os
from PySide2 import QtGui, QtCore, QtWidgets
import shiboken2
try:
    from maya import OpenMaya
    from maya import OpenMayaAnim
    from maya import OpenMayaUI 
    import maya.cmds as mc
    from maya import mel
    MAYA = True
except:
    MAYA = False

def wrapinstance(ptr, base=None):
    """
    Utility to convert a pointer to a Qt class instance (PySide2/PyQt compatible)
    :param ptr: Pointer to QObject in memory
    :type ptr: long or Swig instance
    :param base: (Optional) Base class to wrap with (Defaults to QObject, which should handle anything)
    :type base: QtGui.QWidget
    :return: QWidget or subclass instance
    :rtype: QtGui.QWidget
    """
    if ptr is None:
        return None
    ptr = long(ptr) #Ensure type
    if globals().has_key('shiboken2'):
        if base is None:
            qObj = shiboken2.wrapInstance(long(ptr), QtCore.QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtWidgets, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtWidgets, superCls):
                base = getattr(QtWidgets, superCls)
            else:
                base = QtWidgets.QWidget
        return shiboken2.wrapInstance(long(ptr), base)
    else:
        return None

getMayaWindow = None

def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapinstance(long(ptr), QtWidgets.QMainWindow)
