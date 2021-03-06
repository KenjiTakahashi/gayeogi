# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak © 2010 - 2012
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
from PyQt4.QtCore import (
    QSettings, Qt, pyqtSignal, QString, QStringList, QObject
)
import gayeogi.plugins


class QHovering(QObject):
    """Class for buttons with active hovering support.
    """
    def enterEvent(self, _):
        """Emits 'hovered' signal."""
        self.hovered.emit(self.message)

    def leaveEvent(self, _):
        """Emits 'unhovered' signal."""
        self.unhovered.emit(self.tab)


class QHoveringRadioButton(QtGui.QRadioButton, QHovering):
    """RadioButton with active hovering.

    Signals:
        hovered (unicode): emitted on hover on ('message' attribute)::
            globalMessage text
        unhovered (int): emitted on hover off (supplied 'tab' attribute)::
            globalMessage number

    """
    hovered = pyqtSignal(unicode)
    unhovered = pyqtSignal(int)

    def __init__(self, tab, text, message=u'', parent=None):
        """Constructs new QHoveringRadioButton instance.

        Args:
            tab (int): tab number
            text (unicode): text to be displayed next to radio button

        Kwargs:
            message (unicode): message to be displayed
            parent (QWidget): widget's parent

        """
        super(QHoveringRadioButton, self).__init__(text, parent)
        self.message = message
        self.tab = tab


class QHoveringCheckBox(QtGui.QCheckBox, QHovering):
    """CheckBox with active hovering.

    Signals:
        hovered (unicode): emitted on hover on ('message' attribute)
        unhovered (int): emitted on hover off (supplied 'tab' attribute)

    """
    hovered = pyqtSignal(unicode)
    unhovered = pyqtSignal(int)

    def __init__(self, tab, text, message=u'', parent=None):
        """Constructs new QHoveringCheckBox instance.

        Args:
            tab (int): tab number
            text (unicode): text to be displayed next to check box

        Kwargs:
            message (unicode): message to be displayed
            parent (QWidget): widget's parent

        """
        super(QHoveringCheckBox, self).__init__(text, parent)
        self.message = message
        self.tab = tab


class DatabasesTab(QtGui.QWidget):
    """Databases management widget.

    @signal:hovered: Emitted when behaviour gets hovered.
    @signal:unhovered: Emitted when behaviour gets unhovered.
    """
    hovered = pyqtSignal(unicode)
    unhovered = pyqtSignal(int)

    def __init__(self, settings, parent=None):
        """Creates new DatabasesTab instance.

        :settings: Reference to DB settings.
        :parent: Parent object.
        """
        super(DatabasesTab, self).__init__(parent)
        self.globalText = self.trUtf8(
            "Here you can choose which databases should be searched,"
            " what releases to search for and how the search should"
            "behave."
        )
        self.settings = settings
        self.dbs = QtGui.QTreeWidget()
        self.dbs.setColumnCount(1)
        self.dbs.setIndentation(0)
        self.dbs.setHeaderLabels(QStringList([self.trUtf8('Name')]))
        self.dbs.currentItemChanged.connect(self.displayOptions)
        from gayeogi.db.bees import __names__, __all__
        order = self.settings.value(u'order', []).toPyObject()
        if order is None:
            order = list()
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
                self.__checkStates[unicode(o)] = settings.value(
                        o + u'/types', {}).toPyObject()
        self.dbs.resizeColumnToContents(0)
        self.dbs.resizeColumnToContents(1)
        up = QtGui.QPushButton(self.trUtf8('&Up'))
        up.clicked.connect(self.up)
        down = QtGui.QPushButton(self.trUtf8('&Down'))
        down.clicked.connect(self.down)
        behaviour = QtGui.QGroupBox(self.trUtf8('Behaviour'))
        self.crossed = QHoveringRadioButton(0, self.trUtf8('C&rossed'),
            self.trUtf8('Search for all bands in all enabled databases.')
        )
        self.crossed.hovered.connect(self.hovered)
        self.crossed.unhovered.connect(self.unhovered)
        oneByOne = QHoveringRadioButton(0, self.trUtf8('O&ne-by-one'),
            self.trUtf8(
                "Search databases in order and in every next database"
                ", search only for bands not yet found elsewhere."
            )
        )
        oneByOne.hovered.connect(self.hovered)
        oneByOne.unhovered.connect(self.unhovered)
        if not settings.value(u'behaviour', 0).toBool():
            oneByOne.setChecked(True)
        else:
            self.crossed.setChecked(True)
        self.case = QHoveringCheckBox(0, self.trUtf8('Ignore case'),
            self.trUtf8(
                "Ignore the case of album names when merging remote with local"
                ". Note that it won't change anything until next Remote call."
            )
        )
        self.case.setCheckState(settings.value(u'case', 0).toInt()[0])
        self.case.hovered.connect(self.hovered)
        self.case.unhovered.connect(self.unhovered)
        behaviourL = QtGui.QVBoxLayout()
        behaviourL.addWidget(oneByOne)
        behaviourL.addWidget(self.crossed)
        behaviour.setLayout(behaviourL)
        behaviour.setFixedHeight(80)
        self.spin = QtGui.QSpinBox()
        self.spin.setRange(1, 20)
        self.spin.setValue(settings.value(u'threads', 1).toInt()[0])
        threadsLabel = QtGui.QLabel(self.trUtf8('Threads:'))
        threadsL = QtGui.QHBoxLayout()
        threadsL.addWidget(threadsLabel)
        threadsL.addWidget(self.spin)
        arrowsL = QtGui.QVBoxLayout()
        arrowsL.addWidget(up)
        arrowsL.addWidget(down)
        arrowsL.addLayout(threadsL)
        arrowsL.addWidget(behaviour)
        arrowsL.addWidget(self.case)
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
        """Displays options available for selected database.

        Args:
            item (QListWidgetItem): selected item
            _: whatever
        """
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
        """Shuffles selected database up."""
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
        """Shuffles selected database down."""
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
        """Changes current database's specific option state.

        :state: New state.
        """
        self.__checkStates[
            unicode(self.dbs.currentItem().text(0))
        ][self.sender().text()] = state

    def values(self):
        """Gets appropriate values (for saving).

        :returns:
            tuple. Looks like this (indices)::

                0 -- behaviour state
                1 -- main result::
                    0 -- database name
                    1 -- values::
                        0 -- check state
                        1 -- options states
                2 -- databases order
                3 -- threads number
        """
        result = list()
        order = list()
        for i in range(self.dbs.topLevelItemCount()):
            item = self.dbs.topLevelItem(i)
            text = item.text(0)
            order.append(text)
            result.append((text, (
                item.checkState(0),
                self.__checkStates[unicode(text)],
            )))
        return (
            self.crossed.isChecked(), result,
            order, self.case.checkState(), self.spin.value()
        )


class QValueWidget(QtGui.QWidget):
    """Widget used for adding values.

    Consists of QLineEdit and 2/3 QPushButtons.

    Signals:
        added (unicode, unicode): emitted when 'Add' button is clicked::
            widget's name, text to be added
        removed (unicode): emitted when 'Remove' button is clicked::
            widget's name

    """
    added = pyqtSignal(unicode, unicode)
    removed = pyqtSignal(unicode)

    def __init__(self, name, browse=False, parent=None):
        """Constructs new QValueWidget instance.

        Args:
            name (unicode): widget's name

        Kwargs:
            browse (bool): whether to draw 'Browse' button
            parent (QWidget): widget's parent

        """
        QtGui.QWidget.__init__(self, parent)
        self.name = name
        self.box = QtGui.QLineEdit()
        add = QtGui.QPushButton(self.trUtf8('&Add'))
        add.clicked.connect(self.add)
        remove = QtGui.QPushButton(self.trUtf8('&Remove'))
        remove.clicked.connect(self.remove)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.box)
        if browse:
            browse = QtGui.QPushButton(self.trUtf8('&Browse'))
            browse.clicked.connect(self.select)
            layout.addWidget(browse)
        layout.addWidget(add)
        layout.addWidget(remove)
        self.setLayout(layout)

    def add(self):
        """If text is not empty, emits added signal and clears the box."""
        text = self.box.text()
        if text != '':
            self.added.emit(self.name, text)
            self.box.clear()

    def remove(self):
        """Emits remove signal."""
        self.removed.emit(self.name)

    def select(self):
        """Opens 'Browse' dialog and passed it's result to the box."""
        dialog = QtGui.QFileDialog()
        self.box.setText(dialog.getExistingDirectory())


class LocalTab(QtGui.QWidget):
    """Local options management widget."""
    def __init__(self, directories, ignores, images, parent=None):
        """Creates new LocalTab instance.

        :directories: Directories already present in settings.
        :ignores: Patterns to ignore.
        :images: Images names.
        :parent: Parent object.
        """
        super(LocalTab, self).__init__(parent)
        self.globalText = self.trUtf8(
            "Here you can choose in which directories your files lie and"
            " which files to ignore while searching (you can use wilcards,"
            " like '*' or '?')"
        )
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
        layout.addWidget(QtGui.QLabel(self.trUtf8('Image files:')))
        l = QtGui.QFormLayout()
        self.images = list()
        for label in [u'Album:', u'Artist:']:
            state, img = images[label[:-1]]
            box = QtGui.QCheckBox(label)
            box.setCheckState(state)
            line = QtGui.QLineEdit(",".join([unicode(i) for i in img]))
            self.images.append((box, line))
            l.addRow(box, line)
        layout.addLayout(l)
        self.precedence = QtGui.QCheckBox(self.trUtf8(
            'Files take precedence over in-file image tags.'
        ))
        self.precedence.setCheckState(images[u'p'])
        layout.addWidget(self.precedence)
        self.setLayout(layout)

    def add(self, name, text):
        """Adds new entry to directories/ignores list.

        :name: Sender's name ('directories'/'ignores').
        :text: Text to add.
        """
        item = QtGui.QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(2)
        if name == 'directories':
            self.directories.addItem(item)
        else:
            self.ignores.addItem(item)

    def remove(self, name):
        """Removes selected entries from directories/ignores list.

        :name: Sender's name ('directories'/'ignores').
        """
        if name == 'directories':
            widget = self.directories
        else:
            widget = self.ignores
        for item in widget.selectedItems():
            row = widget.row(item)
            widget.takeItem(row)
            item = None

    def isEmpty(self):
        """Checks whether there are some directories present.

        :returns: True if there are no directories specified, False otherwise.
        """
        return not bool(self.directories.count())

    def values(self):
        """Gets appropriate values (for saving).

        :returns: Tuple in form of (directories, ignores, image names).
        """
        directories = list()
        ignores = list()
        for i in xrange(self.directories.count()):
            item = self.directories.item(i)
            directories.append((unicode(item.text()), item.checkState()))
        for i in xrange(self.ignores.count()):
            item = self.ignores.item(i)
            ignores.append((unicode(item.text()), item.checkState()))
        images = {
            u'Album': (
                self.images[0][0].checkState(),
                self.images[0][1].text().split(u',')
            ),
            u'Artist': (
                self.images[1][0].checkState(),
                self.images[1][1].text().split(u',')
            ),
            u'p': self.precedence.checkState()
        }
        return (directories, ignores, images)


class PluginsTab(QtGui.QWidget):
    """Plugins management widget."""
    selected = pyqtSignal(unicode, QtGui.QWidget)

    def __init__(self, parent=None):
        """Creates new PluginsTab instance.

        :parent: Parent object.
        """
        super(PluginsTab, self).__init__(parent)
        self.globalText = self.trUtf8(
            "Here you can choose additional plugins."
        )
        self.parent = parent
        self.plugins = QtGui.QListWidget()
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
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(ref2.enabled)
            if ref2.enabled and ref2.children():
                self.parent.addTab(ref2, ref.name)
            self.plugins.addItem(item)
            self.__plugins[ref.name] = ref2
            for d in ref.depends:
                self.__depends.setdefault(d, set([ref.name])).add(ref.name)
        self.setLayout(self.layout)

    def checkDependencies(self, item):
        """Checks whether selected plugin's dependencies are available.

        If they are, they are automatically selected.
        If an dependant is being deselected, it's parent(s) will be
        deselected as well.

        Also adds/removes appropriate settings tabs.

        :item: Selected item.
        """
        if item.checkState() != 0:
            ref = self.__plugins[unicode(item.text())]
            if ref.children():
                self.parent.addTab(ref, item.text())
            for d in item.depends:
                for i in self.plugins.findItems(d, Qt.MatchFixedString):
                    i.setCheckState(2)
                    ref = self.__plugins[unicode(i.text())]
                    if ref.children():
                        self.parent.addTab(ref, i.text())
        else:
            self.parent.removeTab(self.parent.indexOf(
                self.__plugins[unicode(item.text())]))
            try:
                for d in self.__depends[unicode(item.text()).lower()]:
                    for i in self.plugins.findItems(d, Qt.MatchFixedString):
                        i.setCheckState(0)
                        self.parent.removeTab(self.parent.indexOf(
                            self.__plugins[unicode(i.text())]))
            except KeyError:
                pass

    def save(self):
        """Save plugins options.

        It doesn't return anything, instead it just sets plugin
        enabled/disabled and relies on specific plugin's internal
        saving methods.

        """
        for i in range(self.plugins.count()):
            item = self.plugins.item(i)
            self.__plugins[unicode(item.text())].save(item.checkState())


class Settings(QtGui.QDialog):
    """Main settings dialog window.

    @attr:__settings: Reference to the main settings.
    @attr:__dbsettings: Reference to the DB settings.
    """
    __settings = QSettings(u'gayeogi', u'gayeogi')
    __dbsettings = QSettings(u'gayeogi', u'Databases')

    def __init__(self, parent=None):
        """Creates new Settings instance.

        :parent: Parent object.
        """
        QtGui.QDialog.__init__(self, parent)
        self.info = QtGui.QLabel()
        self.info.setWordWrap(True)
        self.tabs = QtGui.QTabWidget()
        self.tabs.currentChanged.connect(self.globalMessage)
        # Local
        directories = self.__dbsettings.value(u'directories', []).toPyObject()
        if not isinstance(directories, list):
            directories = [(unicode(directories), 2)]
        ignores = self.__settings.value(u'ignores', []).toPyObject()
        if ignores is None:
            ignores = list()
        images = {
            u'Album': (
                Settings.__settings.value(
                    u'image/album/enabled', 2
                ).toInt()[0],
                Settings.__settings.value(
                    u'image/album', [u'Folder.jpg']
                ).toPyObject()
            ),
            u'Artist': (
                Settings.__settings.value(
                    u'image/artist/enabled', 2
                ).toInt()[0],
                Settings.__settings.value(
                    u'image/artist', [u'Artist.jpg']
                ).toPyObject()
            ),
            u'p': self.__settings.value(u'image/precedence', 2).toInt()[0]
        }
        self.directories = LocalTab(directories, ignores, images)
        self.tabs.addTab(self.directories, self.trUtf8('&Local'))
        # Databases
        self.dbs = DatabasesTab(self.__dbsettings)
        self.dbs.hovered.connect(self.info.setText)
        self.dbs.unhovered.connect(self.globalMessage)
        self.tabs.addTab(self.dbs, self.trUtf8('&Databases'))
        # Plugins
        self.plugins = PluginsTab(self.tabs)
        self.tabs.insertTab(2, self.plugins, self.trUtf8('&Plugins'))
        # Main
        self.globalMessage()
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
        """Saves settings to file."""
        if self.directories.isEmpty():
            dialog = QtGui.QMessageBox()
            dialog.setText(self.trUtf8(
                "There should be at least one directory supplied!"
            ))
            dialog.exec_()
        else:
            directories, ignores, images = self.directories.values()
            self.__dbsettings.setValue(u'directories', directories)
            self.__dbsettings.setValue(u'ignores', ignores)
            for k in [u'Album', u'Artist']:
                enabled, v = images[k]
                k = k.lower()
                self.__dbsettings.setValue(u'image/{0}'.format(k), list(v))
                self.__dbsettings.setValue(
                    u'image/{0}/enabled'.format(k), enabled
                )
            self.__dbsettings.setValue(u'image/precedence', images[u'p'])
            checked, data, order, case, threads = self.dbs.values()
            self.__dbsettings.setValue(u'behaviour', checked)
            self.__dbsettings.setValue(u'order', order)
            self.__dbsettings.setValue(u'case', case)
            for text, (checkState, __checkState) in data:
                self.__dbsettings.setValue(text + u'/Enabled', checkState)
                self.__dbsettings.setValue(text + u'/types', __checkState)
            self.__dbsettings.setValue(u'threads', threads)
            self.plugins.save()
            self.close()

    def globalMessage(self, i=0):
        """Displays global help message.

        :i: Current tab number.
        """
        try:
            self.info.setText(self.tabs.widget(i).globalText)
        except AttributeError:
            self.info.clear()
