# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings

class Settings(QtGui.QDialog):
    __settings=QSettings(u'fetcher',u'Fetcher')
    __patterns=[]
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.__patterns=list(self.__settings.value(u'patterns',[]).toPyObject())
        tabs=QtGui.QTabWidget()
        self.patternList=QtGui.QListWidget()
        self.patternList.addItems(self.__patterns)
        patternMaskLabel=QtGui.QLabel(u'Mask:')
        self.patternLineEdit=QtGui.QLineEdit()
        patternAdd=QtGui.QPushButton(self.tr(u'&Add'))
        patternAdd.setFixedWidth(64)
        patternAdd.clicked.connect(self.add)
        patternRemove=QtGui.QPushButton(self.tr(u'&Remove'))
        patternRemove.setFixedWidth(64)
        patternRemove.clicked.connect(self.remove)
        patternMaskLayout=QtGui.QHBoxLayout()
        patternMaskLayout.addWidget(patternMaskLabel)
        patternMaskLayout.addWidget(self.patternLineEdit)
        patternMaskLayout.addWidget(patternAdd)
        patternMaskLayout.addWidget(patternRemove)
        patternLabel=QtGui.QLabel(u'some text will go here')
        pattern=QtGui.QWidget()
        self.patternError=QtGui.QLabel()
        self.patternError.setVisible(False)
        self.patternError.setWordWrap(True)
        self.patternError.setStyleSheet(u'border:2px groove red;background:#ffc8c8')
        patternLayout=QtGui.QVBoxLayout()
        patternLayout.addWidget(self.patternError)
        patternLayout.addWidget(self.patternList)
        patternLayout.addLayout(patternMaskLayout)
        patternLayout.addWidget(patternLabel)
        pattern.setLayout(patternLayout)
        tabs.addTab(pattern,self.tr(u'Patterns'))
        layout=QtGui.QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.patternLineEdit.setFocus(True)
    def error(self,text,widget):
        self.patternError.setText(text)
        self.patternError.setVisible(True)
#        palette=widget.palette()
#        palette.setColor(11,Qt.red)
#        widget.setPalette(palette)
    def remove(self):
        item=self.patternList.currentItem()
        if not item:
            self.error(u'Item selection should not be empty',self.patternList)
        else:
            del self.__patterns[self.__patterns.index(item.text())]
            i=self.patternList.takeItem(self.patternList.row(item))
            del i
        self.__settings.setValue(u'patterns',self.__patterns)
    def add(self):
        mask=self.patternLineEdit.text()
        if mask==u'':
            self.error(u'Mask should not be empty.',self.patternLineEdit)
        else:
            masks=[]
            for m in [u'<artist>',u'<album>',u'<year>']:
                if m not in mask:
                    masks.append(m)
            if masks:
                text=u'Mask should contain '
                for i,m in enumerate(masks):
                    text+=m
                    if i+1<len(masks):
                        text+=u', '
                text+=u' variables.'
                self.error(text,self.patternLineEdit)
            else:
                self.patternError.setVisible(False)
                self.patternList.addItem(mask)
                self.__patterns.append(mask)
                self.patternLineEdit.clear()
                self.__settings.setValue(u'patterns',self.__patterns)
