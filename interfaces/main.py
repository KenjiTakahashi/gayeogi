# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui/main.ui'
#
# Created: Tue Aug 31 02:28:38 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_main(object):
    def setupUi(self, main):
        main.setObjectName("main")
        main.resize(733, 437)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(main)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widget = QtGui.QWidget(main)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtGui.QSplitter(self.widget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.artists = QtGui.QTableWidget(self.splitter)
        self.artists.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.artists.setAlternatingRowColors(True)
        self.artists.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.artists.setColumnCount(3)
        self.artists.setObjectName("artists")
        self.artists.setColumnCount(3)
        self.artists.setRowCount(0)
        self.artists.verticalHeader().setVisible(False)
        self.albums = QtGui.QTableWidget(self.splitter)
        self.albums.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.albums.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.albums.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.albums.setColumnCount(4)
        self.albums.setObjectName("albums")
        self.albums.setColumnCount(4)
        self.albums.setRowCount(0)
        self.albums.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.splitter)
        self.horizontalLayout_2.addWidget(self.widget)
        self.widget_3 = QtGui.QWidget(main)
        self.widget_3.setObjectName("widget_3")
        self.gridLayout = QtGui.QGridLayout(self.widget_3)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName("gridLayout")
        self.artistsStats = QtGui.QGroupBox(self.widget_3)
        self.artistsStats.setObjectName("artistsStats")
        self.formLayout = QtGui.QFormLayout(self.artistsStats)
        self.formLayout.setObjectName("formLayout")
        self.artistsGreen = QtGui.QLabel(self.artistsStats)
        self.artistsGreen.setObjectName("artistsGreen")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.artistsGreen)
        self.frame_2 = QtGui.QFrame(self.artistsStats)
        self.frame_2.setMinimumSize(QtCore.QSize(30, 30))
        self.frame_2.setStyleSheet("background-color: yellow;")
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.frame_2)
        self.artistsYellow = QtGui.QLabel(self.artistsStats)
        self.artistsYellow.setObjectName("artistsYellow")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.artistsYellow)
        self.frame_3 = QtGui.QFrame(self.artistsStats)
        self.frame_3.setMinimumSize(QtCore.QSize(30, 30))
        self.frame_3.setStyleSheet("background-color: red;")
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.frame_3)
        self.artistsRed = QtGui.QLabel(self.artistsStats)
        self.artistsRed.setObjectName("artistsRed")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.artistsRed)
        self.frame = QtGui.QFrame(self.artistsStats)
        self.frame.setMinimumSize(QtCore.QSize(30, 30))
        self.frame.setStyleSheet("background-color: green;")
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.frame)
        self.gridLayout.addWidget(self.artistsStats, 0, 0, 1, 2)
        self.albumsStats = QtGui.QGroupBox(self.widget_3)
        self.albumsStats.setObjectName("albumsStats")
        self.formLayout_2 = QtGui.QFormLayout(self.albumsStats)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName("formLayout_2")
        self.frame_6 = QtGui.QFrame(self.albumsStats)
        self.frame_6.setMinimumSize(QtCore.QSize(30, 30))
        self.frame_6.setStyleSheet("background-color: green;")
        self.frame_6.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.frame_6)
        self.albumsGreen = QtGui.QLabel(self.albumsStats)
        self.albumsGreen.setObjectName("albumsGreen")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.albumsGreen)
        self.frame_5 = QtGui.QFrame(self.albumsStats)
        self.frame_5.setMinimumSize(QtCore.QSize(30, 30))
        self.frame_5.setStyleSheet("background-color: yellow;")
        self.frame_5.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.frame_5)
        self.albumsYellow = QtGui.QLabel(self.albumsStats)
        self.albumsYellow.setObjectName("albumsYellow")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.albumsYellow)
        self.frame_4 = QtGui.QFrame(self.albumsStats)
        self.frame_4.setMinimumSize(QtCore.QSize(30, 30))
        self.frame_4.setStyleSheet("background-color: red;")
        self.frame_4.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.frame_4)
        self.albumsRed = QtGui.QLabel(self.albumsStats)
        self.albumsRed.setObjectName("albumsRed")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.albumsRed)
        self.gridLayout.addWidget(self.albumsStats, 1, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 62, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.refresh = QtGui.QPushButton(self.widget_3)
        self.refresh.setMaximumSize(QtCore.QSize(61, 16777215))
        self.refresh.setObjectName("refresh")
        self.gridLayout.addWidget(self.refresh, 3, 0, 1, 1)
        self.save = QtGui.QPushButton(self.widget_3)
        self.save.setMaximumSize(QtCore.QSize(61, 16777215))
        self.save.setObjectName("save")
        self.gridLayout.addWidget(self.save, 3, 1, 1, 1)
        self.log = QtGui.QPushButton(self.widget_3)
        self.log.setMaximumSize(QtCore.QSize(61, 16777215))
        self.log.setObjectName("log")
        self.gridLayout.addWidget(self.log, 4, 0, 1, 1)
        self.close = QtGui.QPushButton(self.widget_3)
        self.close.setMaximumSize(QtCore.QSize(61, 16777215))
        self.close.setObjectName("close")
        self.gridLayout.addWidget(self.close, 4, 1, 1, 1)
        self.horizontalLayout_2.addWidget(self.widget_3)

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        self.artists.setSortingEnabled(True)
        self.albums.setSortingEnabled(True)
        self.artistsStats.setTitle(QtGui.QApplication.translate("main", "Artists", None, QtGui.QApplication.UnicodeUTF8))
        self.albumsStats.setTitle(QtGui.QApplication.translate("main", "Albums", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setStatusTip(QtGui.QApplication.translate("main", "Refresh internet databases.", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setText(QtGui.QApplication.translate("main", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.save.setStatusTip(QtGui.QApplication.translate("main", "Save current database to disk. (Do it if you don\'t like your changes to be lost!)", None, QtGui.QApplication.UnicodeUTF8))
        self.save.setText(QtGui.QApplication.translate("main", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.log.setStatusTip(QtGui.QApplication.translate("main", "Access internet refreshing logs.", None, QtGui.QApplication.UnicodeUTF8))
        self.log.setText(QtGui.QApplication.translate("main", "&Logs", None, QtGui.QApplication.UnicodeUTF8))
        self.close.setStatusTip(QtGui.QApplication.translate("main", "Close the application.", None, QtGui.QApplication.UnicodeUTF8))
        self.close.setText(QtGui.QApplication.translate("main", "&Close", None, QtGui.QApplication.UnicodeUTF8))

