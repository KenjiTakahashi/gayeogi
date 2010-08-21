# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/firstrun.ui'
#
# Created: Fri Aug 20 20:58:17 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_firstRun(object):
    def setupUi(self, firstRun):
        firstRun.setObjectName("firstRun")
        firstRun.resize(553, 126)
        self.verticalLayout = QtGui.QVBoxLayout(firstRun)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(firstRun)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.widget = QtGui.QWidget(firstRun)
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
        self.widget_2 = QtGui.QWidget(firstRun)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(350, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
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
        self.browse.setText(QtGui.QApplication.translate("firstRun", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("firstRun", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok.setText(QtGui.QApplication.translate("firstRun", "OK", None, QtGui.QApplication.UnicodeUTF8))

