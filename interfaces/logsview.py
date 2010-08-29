# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import QStringList

class LogsView(QtGui.QDialog):
    def __init__(self,logs,parent=None):
        QtGui.QDialog.__init__(self,parent)
        table=QtGui.QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(QStringList(['Artist','Message']))
        table.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        table.setRowCount(len(logs))
        for i,(a,m) in enumerate(logs):
            table.setItem(i,0,QtGui.QTableWidgetItem(a))
            table.setItem(i,1,QtGui.QTableWidgetItem(m))
        table.resizeColumnsToContents()
        close=QtGui.QPushButton(self.tr('&Close'))
        close.clicked.connect(self.close)
        layout=QtGui.QVBoxLayout()
        layout.addWidget(table)
        layout.addWidget(close)
        self.setLayout(layout)
        self.setMinimumHeight(500)
