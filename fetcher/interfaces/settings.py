# This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
# Karol "Kenji Takahashi" Wozniak (C) 2010
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, Qt, pyqtSignal, QString
import fetcher.plugins

class QHoveringRadioButton(QtGui.QRadioButton):
    hovered = pyqtSignal(unicode)
    unhovered = pyqtSignal(int)
    def __init__(self, tab, message = u'', parent = None):
        QtGui.QRadioButton.__init__(self, parent)
        self.message = message
        self.tab = tab
    def enterEvent(self, _):
        self.hovered.emit(self.message)
    def leaveEvent(self, _):
        self.unhovered.emit(self.tab)

class Settings(QtGui.QDialog):
    __settings = QSettings(u'fetcher', u'Fetcher')
    __dbsettings = QSettings(u'fetcher', u'Databases')
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.tabs = QtGui.QTabWidget()
        self.tabs.currentChanged.connect(self.globalMessage)
        self.info = QtGui.QLabel()
        self.info.setWordWrap(True)
        self.dbList = QtGui.QListWidget()
        self.dbList.currentTextChanged.connect(self.dbDisplayOptions)
        order = self.__dbsettings.value(u'order', []).toPyObject()
        dbOptionsLayout = QtGui.QGridLayout()
        for o in order:
            item = QtGui.QListWidgetItem(o)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(self.__dbsettings.value(
                o + u'/Enabled', 0).toInt()[0])
            self.dbList.addItem(item)
            checkStates = self.__dbsettings.value(
                    o + u'/types', {}).toPyObject()
            items = [[u'Full-length', u'Live album', u'Demo'],
                    [u'Single', u'EP', u'DVD'],
                    [u'Boxed set', u'Split', u'Video/VHS'],
                    [u'Best of/Compilation', u'Split album', u'Split DVD / Video']]
            for i, item in enumerate(items):
                for j, subitem in enumerate(item):
                    widget = QtGui.QCheckBox(subitem)
                    if checkStates:
                        widget.setCheckState(checkStates[QString(subitem)])
                    dbOptionsLayout.addWidget(widget, i, j)
        dbUp = QtGui.QPushButton(self.tr(u'&Up'))
        dbUp.clicked.connect(self.dbUp)
        dbDown = QtGui.QPushButton(self.tr(u'&Down'))
        dbDown.clicked.connect(self.dbDown)
        dbBehaviour = QtGui.QGroupBox(u'Behaviour')
        self.crossed = QHoveringRadioButton(
                0, u'Search for all bands in all enabled databases.',
                self.tr(u'C&rossed'))
        self.crossed.hovered.connect(self.info.setText)
        self.crossed.unhovered.connect(self.globalMessage)
        oneByOne = QHoveringRadioButton(
                0, u'Search databases in order and in every next database, search only for bands not yet found elsewhere.',
                self.tr(u'O&ne-be-one'))
        oneByOne.hovered.connect(self.info.setText)
        oneByOne.unhovered.connect(self.globalMessage)
        behaviour = self.__settings.value(u'behaviour', 0).toInt()[0]
        if behaviour == 0:
            oneByOne.setChecked(True)
        else:
            self.crossed.setChecked(True)
        dbBehaviourLayout = QtGui.QVBoxLayout()
        dbBehaviourLayout.addWidget(oneByOne)
        dbBehaviourLayout.addWidget(self.crossed)
        dbBehaviour.setLayout(dbBehaviourLayout)
        dbBehaviour.setFixedHeight(80)
        arrowsLayout = QtGui.QVBoxLayout()
        arrowsLayout.addWidget(dbUp)
        arrowsLayout.addWidget(dbDown)
        arrowsLayout.addWidget(dbBehaviour)
        arrowsLayout.addStretch()
        dbUpperLayout = QtGui.QHBoxLayout()
        dbUpperLayout.addWidget(self.dbList)
        dbUpperLayout.addLayout(arrowsLayout)
        self.dbOptions = QtGui.QGroupBox(u'Releases')
        self.dbOptions.setLayout(dbOptionsLayout)
        self.dbOptions.setVisible(False)
        ###
        dbLayout = QtGui.QVBoxLayout()
        dbLayout.addLayout(dbUpperLayout)
        dbLayout.addWidget(self.dbOptions)
        dbWidget = QtGui.QWidget()
        dbWidget.setLayout(dbLayout)
        self.tabs.addTab(dbWidget, self.tr(u'&Databases'))
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
        self.tabs.addTab(fsWidget, self.tr(u'&Local'))
        self.logsList = QtGui.QListWidget()
        item = QtGui.QListWidgetItem(u'errors')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/errors', 2).toInt()[0])
        self.logsList.addItem(item)
        item = QtGui.QListWidgetItem(u'info')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/info', 0).toInt()[0])
        self.logsList.addItem(item)
        self.tabs.addTab(self.logsList, self.tr(u'Lo&gs'))
        self.pluginsList = QtGui.QListWidget()
        self.pluginsList.currentTextChanged.connect(self.pluginsDisplayOptions)
        self.pluginsList.itemChanged.connect(self.checkDependencies)
        self.pluginsLayout = QtGui.QVBoxLayout()
        self.pluginsLayout.addWidget(self.pluginsList)
        self.__plugins = {}
        self.__depends = {}
        for plugin in fetcher.plugins.__all__:
            ref = getattr(fetcher.plugins, plugin).Main
            item = QtGui.QListWidgetItem(ref.name)
            item.depends = ref.depends
            ref2 = ref.QConfiguration()
            ref2.hide()
            self.pluginsLayout.addWidget(ref2)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(ref2.enabled)
            self.pluginsList.addItem(item)
            self.__plugins[ref.name] = ref2
            for d in ref.depends:
                try:
                    self.__depends[d].append(ref.name)
                except KeyError:
                    self.__depends[d] = [ref.name]
        pluginsWidget = QtGui.QWidget()
        pluginsWidget.setLayout(self.pluginsLayout)
        self.tabs.addTab(pluginsWidget, self.tr(u'&Plugins'))
        self.ok = QtGui.QPushButton(self.tr(u'&OK'))
        self.ok.clicked.connect(self.save)
        self.cancel = QtGui.QPushButton(self.tr(u'&Cancel'))
        self.cancel.clicked.connect(self.close)
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.ok)
        buttonsLayout.addWidget(self.cancel)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.info)
        layout.addLayout(buttonsLayout)
        self.globalMessage(0)
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
            self.__settings.setValue(u'metal-archives.com', self.dbList.item(0).checkState())
            self.__settings.setValue(u'discogs.com', self.dbList.item(1).checkState())
            ignores = [(unicode(v.text()), v.checkState()) for v
                    in self.fsIgnores.findItems(u'*', Qt.MatchWildcard)]
            self.__settings.setValue(u'ignores', ignores)
            self.__settings.setValue(u'logs/errors', self.logsList.item(0).checkState())
            self.__settings.setValue(u'logs/info', self.logsList.item(1).checkState())
            maOptions = {}
            for o in self.dbOptions.findChildren(QtGui.QCheckBox):
                maOptions[o.text()] = o.checkState()
            self.__settings.setValue(u'options/metal-archives.com', maOptions)
            if self.crossed.isChecked():
                self.__settings.setValue(u'behaviour', 1)
            else:
                self.__settings.setValue(u'behaviour', 0)
            order = []
            for item in self.dbList.findItems(u'*', Qt.MatchWildcard):
                text = unicode(item.text())
                self.__settings.setValue(text, item.checkState())
                order.append(text)
            self.__settings.setValue(u'order', order)
            for i in range(self.pluginsList.count()):
                item = self.pluginsList.item(i)
                self.__plugins[unicode(item.text())].setSetting(u'enabled', item.checkState())
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
        items = __import__(u'fetcher.db.bees.metalArchives', globals(), locals(), [u'items'], -1).items
        print items
        if text == u'metal-archives.com':
            self.dbOptions.setVisible(True)
        else:
            self.dbOptions.setVisible(False)
    def pluginsDisplayOptions(self, text):
        for k, v in self.__plugins.iteritems():
            if unicode(text) == k:
                v.show()
            else:
                v.hide()
    def checkDependencies(self, item):
        if item.checkState() != 0:
            for d in item.depends:
                for i in self.pluginsList.findItems(d, Qt.MatchFixedString):
                    i.setCheckState(2)
        else:
            try:
                for d in self.__depends[unicode(item.text()).lower()]:
                    for i in self.pluginsList.findItems(d, Qt.MatchFixedString):
                        i.setCheckState(0)
            except KeyError:
                pass
    def globalMessage(self, i):
        if i == 0:
            self.info.setText(u'Here you can choose which databases should be searched, what releases to search for and how the search should behave.')
        elif i == 1:
            self.info.setText(u"Here you can choose in which directory you files lies and which files to ignore while searching (you can use wilcards, like '*' or '?')")
        elif i == 2:
            self.info.setText(u'Here you can choose what kind of log messages should be displayed in the main window.')
        elif i == 3:
            self.info.setText(u'Here you can choose and configure additional plugins.')
