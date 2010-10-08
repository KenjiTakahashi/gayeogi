# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import QStringList

class ErrorDialog(QtGui.QDialog):
    def __init__(self,errors,parent=None):
        QtGui.QDialog.__init__(self,parent)
        label=QtGui.QLabel(u'Following directories do not match with any of the specified patterns:')
        errorList=QtGui.QListWidget()
        errorList.addItems(QStringList(errors))
        ok=QtGui.QPushButton(self.tr(u'&OK'))
        ok.clicked.connect(self.close)
        layout=QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(errorList)
        layout.addWidget(ok)
        self.setLayout(layout)
