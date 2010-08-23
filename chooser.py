# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/chooser.ui'
#
# Created: Mon Aug 23 20:45:17 2010
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_chooser(object):
    def setupUi(self, chooser):
        chooser.setObjectName("chooser")
        chooser.resize(572, 206)
        self.verticalLayout = QtGui.QVBoxLayout(chooser)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(chooser)
        self.label.setMaximumSize(QtCore.QSize(16777215, 17))
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(chooser)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 17))
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.widget = QtGui.QWidget(chooser)
        self.widget.setObjectName("widget")
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(chooser)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 27))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(460, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ok = QtGui.QPushButton(self.widget_2)
        self.ok.setObjectName("ok")
        self.horizontalLayout.addWidget(self.ok)
        self.verticalLayout.addWidget(self.widget_2)

        self.retranslateUi(chooser)
        QtCore.QMetaObject.connectSlotsByName(chooser)

    def retranslateUi(self, chooser):
        chooser.setWindowTitle(QtGui.QApplication.translate("chooser", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("chooser", "It seems that there are more bands coming by the name: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("chooser", "Please choose the one you are looking for:", None, QtGui.QApplication.UnicodeUTF8))
        self.ok.setText(QtGui.QApplication.translate("chooser", "OK", None, QtGui.QApplication.UnicodeUTF8))

