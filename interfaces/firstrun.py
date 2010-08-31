# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui/firstrun.ui'
#
# Created: Tue Aug 31 02:28:51 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_firstRun(object):
    def setupUi(self, firstRun):
        firstRun.setObjectName("firstRun")
        firstRun.resize(553, 171)
        self.verticalLayout = QtGui.QVBoxLayout(firstRun)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(firstRun)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.widget = QtGui.QWidget(firstRun)
        self.widget.setMaximumSize(QtCore.QSize(16777215, 27))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.directory = QtGui.QLineEdit(self.widget)
        self.directory.setObjectName("directory")
        self.horizontalLayout.addWidget(self.directory)
        self.browse = QtGui.QPushButton(self.widget)
        self.browse.setObjectName("browse")
        self.horizontalLayout.addWidget(self.browse)
        self.verticalLayout.addWidget(self.widget)
        self.widget_3 = QtGui.QWidget(firstRun)
        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 46))
        self.widget_3.setObjectName("widget_3")
        self.gridLayout = QtGui.QGridLayout(self.widget_3)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(self.widget_3)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 3)
        self.metalArchives = QtGui.QCheckBox(self.widget_3)
        self.metalArchives.setObjectName("metalArchives")
        self.gridLayout.addWidget(self.metalArchives, 1, 0, 1, 1)
        self.discogs = QtGui.QCheckBox(self.widget_3)
        self.discogs.setObjectName("discogs")
        self.gridLayout.addWidget(self.discogs, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(257, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.widget_3)
        self.widget_2 = QtGui.QWidget(firstRun)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 27))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtGui.QSpacerItem(350, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.cancel = QtGui.QPushButton(self.widget_2)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout_2.addWidget(self.cancel)
        self.ok = QtGui.QPushButton(self.widget_2)
        self.ok.setObjectName("ok")
        self.horizontalLayout_2.addWidget(self.ok)
        self.verticalLayout.addWidget(self.widget_2)

        self.retranslateUi(firstRun)
        QtCore.QMetaObject.connectSlotsByName(firstRun)

    def retranslateUi(self, firstRun):
        firstRun.setWindowTitle(QtGui.QApplication.translate("firstRun", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("firstRun", "It seems that it\'s first time you run our app, so we need you to sell your soul to us. Err, I mean we need your music directory to create new database.", None, QtGui.QApplication.UnicodeUTF8))
        self.browse.setText(QtGui.QApplication.translate("firstRun", "&Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("firstRun", "We need you to choose also internet databases you want to use: ", None, QtGui.QApplication.UnicodeUTF8))
        self.metalArchives.setText(QtGui.QApplication.translate("firstRun", "&metal-archives.com", None, QtGui.QApplication.UnicodeUTF8))
        self.discogs.setText(QtGui.QApplication.translate("firstRun", "&discogs.com", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("firstRun", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok.setText(QtGui.QApplication.translate("firstRun", "&OK", None, QtGui.QApplication.UnicodeUTF8))

