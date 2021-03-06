from PySide import QtGui
from shiboken import wrapInstance

import maya.OpenMayaUI as omui

from . import tools
from . import character


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class Window(QtGui.QDialog):

    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)

        self.modify_dialog()

        self.create_connections()

    def modify_dialog(self):

        self.setWindowTitle('Animation')

        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.main_tabs = QtGui.QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.main_tabs.addTab(tools.Window(), 'Tools')
        self.main_tabs.addTab(character.Window(), 'Character')

    def create_connections(self):

        pass
