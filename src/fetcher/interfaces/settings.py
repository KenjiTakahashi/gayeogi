# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings

class Settings(QtGui.QDialog):
    __settings=QSettings(u'Fetcher',u'Fetcher')
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        tabs=QtGui.QTabWidget()
        patternList=QtGui.QListWidget()
        patternMaskLabel=QtGui.QLabel(u'Mask:')
        patternLineEdit=QtGui.QLineEdit()
        patternAdd=QtGui.QPushButton(self.tr(u'&Add'))
        patternAdd.setFixedWidth(64)
        patternRemove=QtGui.QPushButton(self.tr(u'&Remove'))
        patternRemove.setFixedWidth(64)
        patternMaskLayout=QtGui.QHBoxLayout()
        patternMaskLayout.addWidget(patternMaskLabel)
        patternMaskLayout.addWidget(patternLineEdit)
        patternMaskLayout.addWidget(patternAdd)
        patternMaskLayout.addWidget(patternRemove)
        patternLabel=QtGui.QLabel(u'some text will go here')
        pattern=QtGui.QWidget()
        patternLayout=QtGui.QVBoxLayout()
        patternLayout.addWidget(patternList)
        patternLayout.addLayout(patternMaskLayout)
        patternLayout.addWidget(patternLabel)
        pattern.setLayout(patternLayout)
        tabs.addTab(pattern,self.tr(u'Patterns'))
        layout=QtGui.QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)
        patternLineEdit.setFocus(True)
