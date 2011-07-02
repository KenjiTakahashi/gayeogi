# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2010 - 2011
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

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, Qt, pyqtSignal, QString, QStringList
import gayeogi.plugins

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
    __settings = QSettings(u'gayeogi', u'gayeogi')
    __dbsettings = QSettings(u'gayeogi', u'Databases')
    __checkStates = dict()
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.tabs = QtGui.QTabWidget()
        self.tabs.currentChanged.connect(self.globalMessage)
        self.info = QtGui.QLabel()
        self.info.setWordWrap(True)
        self.dbList = QtGui.QTreeWidget()
        self.dbList.setColumnCount(2)
        self.dbList.setIndentation(0)
        self.dbList.setHeaderLabels(QStringList([
            self.trUtf8('Name'), self.trUtf8('Threads')]))
        self.dbList.currentItemChanged.connect(self.dbDisplayOptions)
        order = self.__dbsettings.value(u'order', []).toPyObject()
        self.dbOptionsLayout = QtGui.QGridLayout()
        from gayeogi.db.bees import __names__, __all__
        if order == None:
            order = []
        for (o, m) in zip(__names__, __all__):
            if o not in order:
                order.append(o)
            self.__dbsettings.setValue(o + u'/module', m)
        for o in order:
            module = unicode(
                    self.__dbsettings.value(o + u'/module', u'').toString())
            try:
                __import__(u'gayeogi.db.bees.' + module)
            except ImportError:
                pass
            else:
                item = QtGui.QTreeWidgetItem()
                item.setText(0, o)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, self.__dbsettings.value(
                    o + u'/Enabled', 0).toInt()[0])
                self.dbList.addTopLevelItem(item)
                spin = QtGui.QSpinBox()
                spin.setRange(1, 20)
                spin.setValue(self.__dbsettings.value(
                    o + u'/size', 1).toInt()[0])
                self.dbList.setItemWidget(item, 1, spin)
                self.__checkStates[unicode(o)] = self.__dbsettings.value(o +
                        u'/types', {}).toPyObject()
        self.dbList.resizeColumnToContents(0)
        self.dbList.resizeColumnToContents(1)
        dbUp = QtGui.QPushButton(self.trUtf8('&Up'))
        dbUp.clicked.connect(self.dbUp)
        dbDown = QtGui.QPushButton(self.trUtf8('&Down'))
        dbDown.clicked.connect(self.dbDown)
        dbBehaviour = QtGui.QGroupBox(self.trUtf8('Behaviour'))
        self.crossed = QHoveringRadioButton(0,
                self.trUtf8('Search for all bands in all enabled databases.'),
                self.trUtf8('C&rossed'))
        self.crossed.hovered.connect(self.info.setText)
        self.crossed.unhovered.connect(self.globalMessage)
        oneByOne = QHoveringRadioButton(0,
                self.trUtf8('Search databases in order and in every next database, search only for bands not yet found elsewhere.'),
                self.trUtf8('O&ne-by-one'))
        oneByOne.hovered.connect(self.info.setText)
        oneByOne.unhovered.connect(self.globalMessage)
        behaviour = self.__dbsettings.value(u'behaviour', 0).toBool()
        if not behaviour:
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
        self.dbOptions = QtGui.QGroupBox(self.trUtf8('Releases'))
        self.dbOptions.setLayout(self.dbOptionsLayout)
        self.dbOptions.setVisible(False)
        dbLayout = QtGui.QVBoxLayout()
        dbLayout.addLayout(dbUpperLayout)
        dbLayout.addWidget(self.dbOptions)
        dbWidget = QtGui.QWidget()
        dbWidget.setLayout(dbLayout)
        self.tabs.addTab(dbWidget, self.trUtf8('&Databases'))
        fsDirLabel = QtGui.QLabel(self.trUtf8('Directory'))
        directory = self.__settings.value(u'directory', u'').toString()
        self.fsDir = QtGui.QLineEdit(directory)
        fsDirButton = QtGui.QPushButton(self.trUtf8('&Browse'))
        fsDirButton.clicked.connect(self.selectDir)
        fsDirLayout = QtGui.QHBoxLayout()
        fsDirLayout.addWidget(fsDirLabel)
        fsDirLayout.addWidget(self.fsDir)
        fsDirLayout.addWidget(fsDirButton)
        fsLabel = QtGui.QLabel(self.trUtf8('Ignores:'))
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
        fsAdd = QtGui.QPushButton(self.trUtf8('&Add'))
        fsAdd.clicked.connect(self.add)
        fsRemove = QtGui.QPushButton(self.trUtf8('&Remove'))
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
        self.tabs.addTab(fsWidget, self.trUtf8('&Local'))
        self.logsList = QtGui.QListWidget()
        item = QtGui.QListWidgetItem(u'errors')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/errors', 2).toInt()[0])
        self.logsList.addItem(item)
        item = QtGui.QListWidgetItem(u'info')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/info', 0).toInt()[0])
        self.logsList.addItem(item)
        self.tabs.addTab(self.logsList, self.trUtf8('Lo&gs'))
        self.pluginsList = QtGui.QListWidget()
        self.pluginsList.currentTextChanged.connect(self.pluginsDisplayOptions)
        self.pluginsList.itemChanged.connect(self.checkDependencies)
        self.pluginsLayout = QtGui.QVBoxLayout()
        self.pluginsLayout.addWidget(self.pluginsList)
        self.__plugins = {}
        self.__depends = {}
        for plugin in gayeogi.plugins.__all__:
            ref = getattr(gayeogi.plugins, plugin).Main
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
        self.tabs.addTab(pluginsWidget, self.trUtf8('&Plugins'))
        self.ok = QtGui.QPushButton(self.trUtf8('&OK'))
        self.ok.clicked.connect(self.save)
        self.cancel = QtGui.QPushButton(self.trUtf8('&Cancel'))
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
            dialog.setText(self.trUtf8('Directory field cannot be empty!'))
            dialog.exec_()
        else:
            self.__settings.setValue(u'directory', self.fsDir.text())
            ignores = [(unicode(v.text()), v.checkState()) for v
                    in self.fsIgnores.findItems(u'*', Qt.MatchWildcard)]
            self.__settings.setValue(u'ignores', ignores)
            self.__settings.setValue(u'logs/errors',
                    self.logsList.item(0).checkState())
            self.__settings.setValue(u'logs/info',
                    self.logsList.item(1).checkState())
            self.__dbsettings.setValue(u'behaviour', self.crossed.isChecked())
            order = []
            for item in self.dbList.findItems(u'*', Qt.MatchWildcard):
                text = item.text(0)
                self.__dbsettings.setValue(
                        text + u'/Enabled', item.checkState(0))
                order.append(text)
                self.__dbsettings.setValue(text + u'/types',
                        self.__checkStates[unicode(text)])
                self.__dbsettings.setValue(text + u'/size',
                        self.dbList.itemWidget(item, 1).value())
            self.__dbsettings.setValue(u'order', order)
            for i in range(self.pluginsList.count()):
                item = self.pluginsList.item(i)
                self.__plugins[unicode(item.text())].setSetting(u'enabled',
                        item.checkState())
            self.close()
    def dbUp(self):
        current = self.dbList.currentItem()
        oldindex = self.dbList.indexOfTopLevelItem(current)
        newindex = oldindex - 1
        if newindex >= 0:
            spin = QtGui.QSpinBox()
            spin.setRange(1, 20)
            spin.setValue(self.dbList.itemWidget(current, 1).value())
            self.dbList.insertTopLevelItem(newindex,
                    self.dbList.takeTopLevelItem(oldindex))
            self.dbList.setItemWidget(current, 1, spin)
            self.dbList.setCurrentItem(current)
    def dbDown(self):
        current = self.dbList.currentItem()
        oldindex = self.dbList.indexOfTopLevelItem(current)
        newindex = oldindex + 1
        if newindex < self.dbList.topLevelItemCount():
            spin = QtGui.QSpinBox()
            spin.setRange(1, 20)
            spin.setValue(self.dbList.itemWidget(current, 1).value())
            self.dbList.insertTopLevelItem(newindex,
                    self.dbList.takeTopLevelItem(oldindex))
            self.dbList.setItemWidget(current, 1, spin)
            self.dbList.setCurrentItem(current)
    def changeState(self, state):
        self.__checkStates[unicode(self.dbList.currentItem().text(0))] \
                [self.sender().text()] = state
    def dbDisplayOptions(self, item, _):
        text = item.text(0)
        module = unicode(self.__dbsettings.value(
            text + u'/module', u'').toString())
        for child in self.dbOptions.children()[1:]:
            self.dbOptionsLayout.removeWidget(child)
            child.deleteLater()
        try:
            items = __import__(u'gayeogi.db.bees.' + module, globals(),
                    locals(), [u'items'], -1).items
        except TypeError:
            self.dbOptions.setVisible(False)
        else:
            checkStates = self.__checkStates[unicode(text)]
            for i, item in enumerate(items):
                for j, subitem in enumerate(item):
                    widget = QtGui.QCheckBox(subitem)
                    widget.stateChanged.connect(self.changeState)
                    if checkStates:
                        try:
                            widget.setCheckState(checkStates[QString(subitem)])
                        except KeyError:
                            pass
                    self.dbOptionsLayout.addWidget(widget, i, j)
                    self.dbOptions.setVisible(True)
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
            self.info.setText(self.trUtf8('Here you can choose which databases should be searched, what releases to search for and how the search should behave.'))
        elif i == 1:
            self.info.setText(self.trUtf8("Here you can choose in which directory you files lies and which files to ignore while searching (you can use wilcards, like '*' or '?')"))
        elif i == 2:
            self.info.setText(self.trUtf8('Here you can choose what kind of log messages should be displayed in the main window.'))
        elif i == 3:
            self.info.setText(self.trUtf8('Here you can choose and configure additional plugins.'))
