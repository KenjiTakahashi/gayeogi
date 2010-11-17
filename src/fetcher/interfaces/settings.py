# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, Qt, pyqtSignal, QRegExp

class Settings(QtGui.QDialog):
    dirChanged = pyqtSignal(str)
    __settings=QSettings(u'fetcher',u'Fetcher')
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        tabs = QtGui.QTabWidget()
        self.info = QtGui.QLabel()
        self.dbList = QtGui.QListWidget()
        self.dbList.currentTextChanged.connect(self.dbDisplayOptions)
        item = QtGui.QListWidgetItem(u'metal-archives.com')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'metalArchives', 0).toInt()[0])
        self.dbList.addItem(item)
        item = QtGui.QListWidgetItem(u'discogs.com')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'discogs', 0).toInt()[0])
        self.dbList.addItem(item)
        dbUp = QtGui.QPushButton(self.tr(u'&Up'))
        dbUp.clicked.connect(self.dbUp)
        dbDown = QtGui.QPushButton(self.tr(u'&Down'))
        dbDown.clicked.connect(self.dbDown)
        dbBehaviour = QtGui.QGroupBox(u'Behaviour')
        crossed = QtGui.QRadioButton(self.tr(u'C&rossed'))
        oneByOne = QtGui.QRadioButton(self.tr(u'O&ne-by-one'))
        dbBehaviourLayout = QtGui.QVBoxLayout()
        dbBehaviourLayout.addWidget(crossed)
        dbBehaviourLayout.addWidget(oneByOne)
        dbBehaviour.setLayout(dbBehaviourLayout)
        arrowsLayout = QtGui.QVBoxLayout()
        arrowsLayout.addWidget(dbUp)
        arrowsLayout.addWidget(dbDown)
        arrowsLayout.addWidget(dbBehaviour)
        arrowsLayout.addStretch()
        dbUpperLayout = QtGui.QHBoxLayout()
        dbUpperLayout.addWidget(self.dbList)
        dbUpperLayout.addLayout(arrowsLayout)
        self.dbOptions = QtGui.QGroupBox(u'Releases')
        dbOptionsLayout = QtGui.QGridLayout()
        self.dbOptions.setLayout(dbOptionsLayout)
        self.dbOptions.setVisible(False)
        dbLayout = QtGui.QVBoxLayout()
        dbLayout.addLayout(dbUpperLayout)
        dbLayout.addWidget(self.dbOptions)
        dbWidget = QtGui.QWidget()
        dbWidget.setLayout(dbLayout)
        tabs.addTab(dbWidget, self.tr(u'&Databases'))
        fsDirLabel = QtGui.QLabel(u'Directory')
        directory = self.__settings.value(u'directory', u'').toString()
        self.fsDir = QtGui.QLineEdit(directory)
        fsDirButton = QtGui.QPushButton(self.tr(u'&Browse'))
        fsDirButton.clicked.connect(self.selectDir)
        fsDirLayout = QtGui.QHBoxLayout()
        fsDirLayout.addWidget(fsDirLabel)
        fsDirLayout.addWidget(self.fsDir)
        fsDirLayout.addWidget(fsDirButton)
        fsLabel = QtGui.QLabel(u'Ignores:')
        self.fsIgnores = QtGui.QListWidget()
        ignores = self.__settings.value(u'ignores').toPyObject()
        if not ignores:
            ignores = []
        for i in ignores:
            item = QtGui.QListWidgetItem(i[0])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(i[1])
            self.fsIgnores.addItem(item)
        self.fsName = QtGui.QLineEdit()
        fsAdd = QtGui.QPushButton(self.tr(u'&Add'))
        fsAdd.clicked.connect(self.add)
        fsRemove = QtGui.QPushButton(self.tr(u'&Remove'))
        fsButtonsLayout = QtGui.QHBoxLayout()
        fsButtonsLayout.addWidget(self.fsName)
        fsButtonsLayout.addWidget(fsAdd)
        fsButtonsLayout.addWidget(fsRemove)
        fsLayout = QtGui.QVBoxLayout()
        fsLayout.addLayout(fsDirLayout)
        fsLayout.addWidget(fsLabel)
        fsLayout.addWidget(self.fsIgnores)
        fsLayout.addLayout(fsButtonsLayout)
        fsWidget = QtGui.QWidget()
        fsWidget.setLayout(fsLayout)
        tabs.addTab(fsWidget, self.tr(u'&Local'))
        self.logsList = QtGui.QListWidget()
        item = QtGui.QListWidgetItem(u'errors')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/errors', 2).toInt()[0])
        self.logsList.addItem(item)
        item = QtGui.QListWidgetItem(u'info')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/info', 0).toInt()[0])
        self.logsList.addItem(item)
        tabs.addTab(self.logsList, self.tr(u'Lo&gs'))
        ok = QtGui.QPushButton(self.tr(u'&OK'))
        ok.clicked.connect(self.save)
        cancel = QtGui.QPushButton(self.tr(u'&Cancel'))
        cancel.clicked.connect(self.close)
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(ok)
        buttonsLayout.addWidget(cancel)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(self.info)
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)
    def add(self):
        if self.fsName.text() != u'':
            item = QtGui.QListWidgetItem(self.fsName.text())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(2)
            self.fsIgnores.addItem(item)
        self.fsName.clear()
    def selectDir(self):
        dialog = QtGui.QFileDialog()
        self.fsDir.setText(dialog.getExistingDirectory())
    def save(self):
        directory = self.fsDir.text()
        if directory == u'':
            dialog = QtGui.QMessageBox()
            dialog.setText(u'Directory field cannot be empty!')
        else:
            self.__settings.setValue(u'directory', self.fsDir.text())
            self.__settings.setValue(u'metalArchives', self.dbList.item(0).checkState())
            self.__settings.setValue(u'discogs', self.dbList.item(1).checkState())
            ignores = [(str(v.text()), v.checkState()) for v
                    in self.fsIgnores.findItems(u'*', Qt.MatchWildcard)]
            self.__settings.setValue(u'ignores', ignores)
            self.__settings.setValue(u'logs/errors', self.logsList.item(0).checkState())
            self.__settings.setValue(u'logs/info', self.logsList.item(1).checkState())
            maOptions = u''
            for o in self.dbOptions.findChildren(QtGui.QCheckBox, QRegExp(u'.*')):
                maOptions += str(o.checkState())
            self.__settings.setValue(u'options/metalArchives', maOptions)
            self.close()
    def dbUp(self):
        current = self.dbList.currentRow() - 1
        if current >= 0:
            self.dbList.insertItem(current, self.dbList.takeItem(current + 1))
            self.dbList.setCurrentRow(current)
    def dbDown(self):
        current = self.dbList.currentRow() + 1
        if current < self.dbList.count():
            self.dbList.insertItem(current, self.dbList.takeItem(current - 1))
            self.dbList.setCurrentRow(current)
    def dbDisplayOptions(self, text):
        if text == u'metal-archives.com':
            self.__deleteItems()
            items = [[u'Full-length', u'Live album', u'Demo'],
                    [u'Single', u'EP', u'DVD'],
                    [u'Boxed set', u'Split', u'Video/VHS'],
                    [u'Best of/Compilation', u'Split album', u'Split DVD / Video']]
            checkStates = self.__settings.value(u'options/metalArchives').toPyObject()
            layout = self.dbOptions.layout()
            for i, item in enumerate(items):
                for j, subitem in enumerate(item):
                    widget = QtGui.QCheckBox(subitem)
                    if checkStates[i * 3 + j]:
                        widget.setCheckState(int(checkStates[i * 3 + j]))
                    layout.addWidget(widget, i, j)
            self.dbOptions.setVisible(True)
        else:
            self.dbOptions.setVisible(False)
    def __deleteItems(self):
        layout = self.dbOptions.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                child.widget().deleteLater()
