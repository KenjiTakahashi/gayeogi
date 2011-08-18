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

class DatabasesTab(QtGui.QWidget):
    """Databases management widget."""
    hovered = pyqtSignal(unicode)
    unhovered = pyqtSignal(int)
    def __init__(self, order, settings, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.settings = settings
        self.dbs = QtGui.QTreeWidget()
        self.dbs.setColumnCount(2)
        self.dbs.setIndentation(0)
        self.dbs.setHeaderLabels(QStringList([
            self.trUtf8('Name'), self.trUtf8('Threads')]))
        self.dbs.currentItemChanged.connect(self.displayOptions)
        from gayeogi.db.bees import __names__, __all__
        for (o, m) in zip(__names__, __all__):
            if o not in order:
                order.append(o)
            settings.setValue(o + u'/module', m)
        self.__checkStates = dict()
        for o in order:
            module = unicode(settings.value(o + u'/module', u'').toString())
            try:
                __import__(u'gayeogi.db.bees.' + module)
            except ImportError:
                pass
            else:
                item = QtGui.QTreeWidgetItem()
                item.setText(0, o)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, settings.value(
                    o + u'/Enabled', 0).toInt()[0])
                self.dbs.addTopLevelItem(item)
                spin = QtGui.QSpinBox()
                spin.setRange(1, 20)
                spin.setValue(settings.value(o + u'/size', 1).toInt()[0])
                self.dbs.setItemWidget(item, 1, spin)
                self.__checkStates[unicode(o)] = settings.value(
                        o + u'/types', {}).toPyObject()
        self.dbs.resizeColumnToContents(0)
        self.dbs.resizeColumnToContents(1)
        up = QtGui.QPushButton(self.trUtf8('&Up'))
        up.clicked.connect(self.up)
        down = QtGui.QPushButton(self.trUtf8('&Down'))
        down.clicked.connect(self.down)
        behaviour = QtGui.QGroupBox(self.trUtf8('Behaviour'))
        self.crossed = QHoveringRadioButton(0,
                self.trUtf8('Search for all bands in all enabled databases.'),
                self.trUtf8('C&rossed'))
        self.crossed.hovered.connect(self.hovered)
        self.crossed.unhovered.connect(self.unhovered)
        oneByOne = QHoveringRadioButton(0,
                self.trUtf8('Search databases in order and in every next database, search only for bands not yet found elsewhere.'),
                self.trUtf8('O&ne-by-one'))
        oneByOne.hovered.connect(self.hovered)
        oneByOne.unhovered.connect(self.unhovered)
        if not settings.value(u'behaviour', 0).toBool():
            oneByOne.setChecked(True)
        else:
            self.crossed.setChecked(True)
        behaviourL = QtGui.QVBoxLayout()
        behaviourL.addWidget(oneByOne)
        behaviourL.addWidget(self.crossed)
        behaviour.setLayout(behaviourL)
        behaviour.setFixedHeight(80)
        arrowsL = QtGui.QVBoxLayout()
        arrowsL.addWidget(up)
        arrowsL.addWidget(down)
        arrowsL.addWidget(behaviour)
        arrowsL.addStretch()
        upperL = QtGui.QHBoxLayout()
        upperL.addWidget(self.dbs)
        upperL.addLayout(arrowsL)
        self.options = QtGui.QGroupBox(self.trUtf8('Releases'))
        self.optionsL = QtGui.QGridLayout()
        self.options.setLayout(self.optionsL)
        self.options.setVisible(False)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(upperL)
        layout.addWidget(self.options)
        self.setLayout(layout)
    def displayOptions(self, item, _):
        text = item.text(0)
        module = unicode(self.settings.value(
            text + u'/module', u'').toString())
        for child in self.options.children()[1:]:
            self.optionsL.removeWidget(child)
            child.deleteLater()
        try:
            items = __import__(u'gayeogi.db.bees.' + module, globals(),
                    locals(), [u'items'], -1).items
        except TypeError:
            self.options.setVisible(False)
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
                    self.optionsL.addWidget(widget, i, j)
                    self.options.setVisible(True)
    def up(self):
        current = self.dbs.currentItem()
        oldindex = self.dbs.indexOfTopLevelItem(current)
        newindex = oldindex - 1
        if newindex >= 0:
            spin = QtGui.QSpinBox()
            spin.setRange(1, 20)
            spin.setValue(self.dbs.itemWidget(current, 1).value())
            self.dbs.insertTopLevelItem(newindex,
                    self.dbs.takeTopLevelItem(oldindex))
            self.dbs.setItemWidget(current, 1, spin)
            self.dbs.setCurrentItem(current)
    def down(self):
        current = self.dbs.currentItem()
        oldindex = self.dbs.indexOfTopLevelItem(current)
        newindex = oldindex + 1
        if newindex < self.dbs.topLevelItemCount():
            spin = QtGui.QSpinBox()
            spin.setRange(1, 20)
            spin.setValue(self.dbs.itemWidget(current, 1).value())
            self.dbs.insertTopLevelItem(newindex,
                    self.dbs.takeTopLevelItem(oldindex))
            self.dbs.setItemWidget(current, 1, spin)
            self.dbs.setCurrentItem(current)
    def changeState(self, state):
        self.__checkStates[unicode(self.dbs.currentItem().text(0))] \
                [self.sender().text()] = state
    def values(self):
        result = list()
        order = list()
        for i in range(self.dbs.count()):
            item = self.dbs.item(i)
            text = item.text(0)
            order.append(text)
            result.append((text, (
                item.checkState(0),
                self.__checkStates[unicode(text)],
                self.dbs.itemWidget(item, 1).value()
            )))
        return (self.crossed.isChecked(), result, order)

class QValueWidget(QtGui.QWidget):
    added = pyqtSignal(unicode, unicode)
    removed = pyqtSignal(unicode)
    def __init__(self, name, browse = False, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.name = name
        self.box = QtGui.QLineEdit()
        add = QtGui.QPushButton(self.trUtf8('&Add'))
        add.clicked.connect(self.add)
        remove = QtGui.QPushButton(self.trUtf8('&Remove'))
        remove.clicked.connect(self.remove)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.box)
        if browse:
            browse = QtGui.QPushButton(self.trUtf8('&Browse'))
            browse.clicked.connect(self.select)
            layout.addWidget(browse)
        layout.addWidget(add)
        layout.addWidget(remove)
        self.setLayout(layout)
    def add(self):
        text = self.box.text()
        if text != '':
            self.added.emit(self.name, text)
            self.box.clear()
    def remove(self):
        self.removed.emit(self.name)
    def select(self):
        dialog = QtGui.QFileDialog()
        self.box.setText(dialog.getExistingDirectory())

class LocalTab(QtGui.QWidget):
    def __init__(self, directories, ignores, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.directories = QtGui.QListWidget()
        self.directories.setSelectionMode(QtGui.QListWidget.ExtendedSelection)
        for d in directories:
            item = QtGui.QListWidgetItem(d[0])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(d[1])
            self.directories.addItem(item)
        self.ignores = QtGui.QListWidget()
        self.ignores.setSelectionMode(QtGui.QListWidget.ExtendedSelection)
        for i in ignores:
            item = QtGui.QListWidgetItem(i[0])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(i[1])
            self.ignores.addItem(item)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel(self.trUtf8('Directories:')))
        layout.addWidget(self.directories)
        value = QValueWidget('directories', True)
        value.added.connect(self.add)
        value.removed.connect(self.remove)
        layout.addWidget(value)
        layout.addWidget(QtGui.QLabel(self.trUtf8('Ignores:')))
        layout.addWidget(self.ignores)
        value = QValueWidget('ignores')
        value.added.connect(self.add)
        value.removed.connect(self.remove)
        layout.addWidget(value)
        self.setLayout(layout)
    def add(self, name, text):
        item = QtGui.QListWidgetItem(self.fsName.text())
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(2)
        if name == 'directories':
            self.directories.addItem(item)
        else:
            self.ignores.addItem(item)
    def remove(self, name):
        if name == 'directories':
            widget = self.directories
        else:
            widget = self.ignores
        for item in widget.selectedItems():
            item.deleteLater()
    def isEmpty(self):
        return bool(self.directories.count())
    def values(self):
        return (
            [unicode(self.directories.item(i).text())
            for i in range(self.directories.count())],
            [unicode(self.ignores.item(i).text())
            for i in range(self.directories.count())]
        )

class PluginsTab(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.plugins = QtGui.QListWidget()
        self.plugins.currentTextChanged.connect(self.displayOptions)
        self.plugins.itemChanged.connect(self.checkDependencies)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.plugins)
        self.__plugins = dict()
        self.__depends = dict()
        for plugin in gayeogi.plugins.__all__:
            ref = getattr(gayeogi.plugins, plugin).Main
            item = QtGui.QListWidgetItem(ref.name)
            item.depends = ref.depends
            ref2 = ref.QConfiguration()
            ref2.hide()
            self.layout.addWidget(ref2)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(ref2.enabled)
            self.plugins.addItem(item)
            self.__plugins[ref.name] = ref2
            for d in ref.depends:
                self.__depends.setdefault(d, [ref.name]).append(ref.name)
        self.setLayout(self.layout)
    def displayOptions(self, text):
        for k, v in self.__plugins.iteritems():
            if unicode(text) == k:
                v.show()
            else:
                v.hide()
    def checkDependencies(self, item):
        if item.checkState() != 0:
            for d in item.depends:
                for i in self.plugins.findItems(d, Qt.MatchFixedString):
                    i.setCheckState(2)
        else:
            try:
                for d in self.__depends[unicode(item.text()).lower()]:
                    for i in self.plugins.findItems(d, Qt.MatchFixedString):
                        i.setCheckState(0)
            except KeyError:
                pass
    def save(self):
        for i in range(self.plugins.count()):
            item = self.plugins.item(i)
            self.__plugins[unicode(item.text())].setSetting(
                u'enabled', item.checkState())

class Settings(QtGui.QDialog):
    """Main settings dialog window."""
    __settings = QSettings(u'gayeogi', u'gayeogi')
    __dbsettings = QSettings(u'gayeogi', u'Databases')
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.info = QtGui.QLabel()
        self.info.setWordWrap(True)
        # Logs - start
        self.logsList = QtGui.QListWidget()
        item = QtGui.QListWidgetItem(u'errors')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/errors', 2).toInt()[0])
        self.logsList.addItem(item)
        item = QtGui.QListWidgetItem(u'info')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.__settings.value(u'logs/info', 0).toInt()[0])
        self.logsList.addItem(item)
        # Logs - end
        self.tabs = QtGui.QTabWidget()
        self.tabs.currentChanged.connect(self.globalMessage)
        # Databases
        order = self.__settings.value(u'order', []).toPyObject()
        if order == None:
            order = []
        self.dbs = DatabasesTab(order, self.__dbsettings)
        self.dbs.hovered.connect(self.info.setText)
        self.dbs.unhovered.connect(self.globalMessage)
        self.tabs.addTab(self.dbs, self.trUtf8('&Databases'))
        # Local
        directory = self.__settings.value(u'directory', '').toPyObject()
        directory = type(directory) == list and directory or [(directory, 2)]
        self.directories = LocalTab(directory,
                self.__settings.value('ignores', []).toPyObject())
        self.tabs.addTab(self.directories, self.trUtf8('&Local'))
        # Logs
        self.tabs.addTab(self.logsList, self.trUtf8('Lo&gs'))
        # Plugins
        self.plugins = PluginsTab()
        self.tabs.addTab(self.plugins, self.trUtf8('&Plugins'))
        # Main
        self.globalMessage(0)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.info)
        self.ok = QtGui.QPushButton(self.trUtf8('&OK'))
        self.ok.clicked.connect(self.save)
        cancel = QtGui.QPushButton(self.trUtf8('&Cancel'))
        cancel.clicked.connect(self.close)
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.ok)
        buttonsLayout.addWidget(cancel)
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)
    def save(self):
        if self.directories.isEmpty():
            dialog = QtGui.QMessageBox()
            dialog.setText(self.trUtf8('There should be at least one directory supplied!'))
            dialog.exec_()
        else:
            (directories, ignores) = self.directories.values()
            self.__settings.setValue(u'directory', directories)
            self.__settings.setValue(u'ignores', ignores)
            self.__settings.setValue(u'logs/errors',
                    self.logsList.item(0).checkState())
            self.__settings.setValue(u'logs/info',
                    self.logsList.item(1).checkState())
            (checked, data, order) = self.dbs.values()
            self.__dbsettings.setValue(u'behaviour', checked)
            self.__dbsettings.setValue(u'order', order)
            for (text, (checkState, __checkState, itemWidget)) in data:
                self.__dbsettings.setValue(text + u'/Enabled', checkState)
                self.__dbsettings.setValue(text + u'/types', __checkState)
                self.__dbsettings.setValue(text + u'/size', itemWidget)
            self.plugins.save()
            self.close()
    def globalMessage(self, i):
        if i == 0:
            self.info.setText(self.trUtf8('Here you can choose which databases should be searched, what releases to search for and how the search should behave.'))
        elif i == 1:
            self.info.setText(self.trUtf8("Here you can choose in which directory you files lies and which files to ignore while searching (you can use wilcards, like '*' or '?')"))
        elif i == 2:
            self.info.setText(self.trUtf8('Here you can choose what kind of log messages should be displayed in the main window.'))
        elif i == 3:
            self.info.setText(self.trUtf8('Here you can choose and configure additional plugins.'))
