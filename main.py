# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/main.ui'
#
# Created: Sat Aug 21 02:09:20 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_main(object):
    def setupUi(self, main):
        main.setObjectName("main")
        main.resize(733, 242)
        self.verticalLayout = QtGui.QVBoxLayout(main)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(main)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.artists = QtGui.QTableWidget(self.widget)
        self.artists.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.artists.setAlternatingRowColors(True)
        self.artists.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.artists.setColumnCount(3)
        self.artists.setObjectName("artists")
        self.artists.setColumnCount(3)
        self.artists.setRowCount(0)
        self.artists.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.artists)
        self.albums = QtGui.QTableWidget(self.widget)
        self.albums.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.albums.setColumnCount(4)
        self.albums.setObjectName("albums")
        self.albums.setColumnCount(4)
        self.albums.setRowCount(0)
        self.albums.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.albums)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(main)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 27))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(439, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.close = QtGui.QPushButton(self.widget_2)
        self.close.setObjectName("close")
        self.horizontalLayout_2.addWidget(self.close)
        self.save = QtGui.QPushButton(self.widget_2)
        self.save.setObjectName("save")
        self.horizontalLayout_2.addWidget(self.save)
        self.refresh = QtGui.QPushButton(self.widget_2)
        self.refresh.setObjectName("refresh")
        self.horizontalLayout_2.addWidget(self.refresh)
        self.verticalLayout.addWidget(self.widget_2)

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        self.artists.setSortingEnabled(True)
        self.close.setStatusTip(QtGui.QApplication.translate("main", "Close the application", None, QtGui.QApplication.UnicodeUTF8))
        self.close.setText(QtGui.QApplication.translate("main", "&Close", None, QtGui.QApplication.UnicodeUTF8))
        self.save.setStatusTip(QtGui.QApplication.translate("main", "Save current database to disk. (Do it if you don\'t like your changes to be lost!)", None, QtGui.QApplication.UnicodeUTF8))
        self.save.setText(QtGui.QApplication.translate("main", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setStatusTip(QtGui.QApplication.translate("main", "Refresh the database (both filesystem and internet). (Not working yet! Restart app if you want to refresh)", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setText(QtGui.QApplication.translate("main", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))

