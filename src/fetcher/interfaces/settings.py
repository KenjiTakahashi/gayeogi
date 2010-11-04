# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings

class Settings(QtGui.QDialog):
    __settings=QSettings(u'fetcher',u'Fetcher')
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        tabs = QtGui.QTabWidget()
        info = QtGui.QLabel()
        fsTree = QtGui.QTreeWidget()
        fsTree.setColumnCount(2)
        fsBox = QtGui.QGroupBox(u'Properties')
        fsLayout = QtGui.QVBoxLayout()
        fsLayout.setContentsMargins(0, 0, 0, 0)
        fsLayout.addWidget(fsTree)
        fsLayout.addWidget(fsBox)
        fsWidget = QtGui.QWidget()
        fsWidget.setLayout(fsLayout)
        tabs.addTab(fsWidget, self.tr(u'&Databases'))
        logsTree = QtGui.QTreeWidget()
        logsTree.setColumnCount(2)
        tabs.addTab(logsTree, self.tr(u'&Logs'))
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(info)
        self.setLayout(layout)
