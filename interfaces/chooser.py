# -*- coding: utf-8 -*-

from PyQt4 import QtGui

class Chooser(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        ok=QtGui.QPushButton(self.tr('&OK'))
        ok.clicked.connect(self.close)
        layoutBottom=QtGui.QHBoxLayout()
        layoutBottom.addWidget(ok)
        self.label=QtGui.QLabel('It seems that there are more bands coming by the name: ')
        label2=QtGui.QLabel('Please choose the one you are looking for:')
        self.buttonGroup=QtGui.QButtonGroup()
        self.buttons=QtGui.QVBoxLayout()
        buttons=QtGui.QWidget()
        buttons.setLayout(self.buttons)
        layout=QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(label2)
        layout.addWidget(buttons)
        layout.addLayout(layoutBottom)
        self.setLayout(layout)
    def setArtist(self,artist):
        self.label.setText(self.label.text()+artist)
    def addButton(self,(name,link)):
        button=QtGui.QRadioButton(name)
        button.link=link
        button.setChecked(True)
        self.buttonGroup.addButton(button)
        self.buttons.addWidget(button)
    def getChoice(self):
        return self.buttonGroup.checkedButton().link
