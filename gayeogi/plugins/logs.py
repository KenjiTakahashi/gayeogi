# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2011
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
from PyQt4.QtCore import QSettings, Qt, QObject, pyqtSignal
import logging
import re

class Handler(QObject, logging.Handler):
    """Logs handler.

    Signals:
        signal (object): propagates log to the widget.

    """
    signal = pyqtSignal(object)
    def __init__(self, update, level = logging.DEBUG):
        """Constructs new Handler instance.

        Args:
            update (function): function used to update widget
            levels (set): enabled levels list
            level (int): logging level

        """
        QObject.__init__(self)
        logging.Handler.__init__(self, level)
        self.signal.connect(update)
    def emit(self, record):
        """Emits signal.

        Args:
            record (LogRecord): log record

        """
        self.signal.emit([record.name, record.levelname] + record.msg)

class Filter(logging.Filter):
    """Logs filter."""
    __levels = {
        u'Critical': logging.CRITICAL,
        u'Error': logging.ERROR,
        u'Warning': logging.WARNING,
        u'Info': logging.INFO,
        u'Debug': logging.DEBUG
    }
    def __init__(self):
        """Construcs new Filter instance."""
        logging.Filter.__init__(self)
        self.levels = set()
    def filter(self, record):
        """Filters incoming records according to their enabled state.

        Args:
            record (LogRecord): a log record received from Logger

        """
        return record.levelno in self.levels
    def addLevel(self, level):
        """Adds specified level to enabled.

        Args:
            level (unicode): human readable level's name

        """
        self.levels.add(self.__levels[level])
    def removeLevel(self, level):
        """Removes specified level from enabled.

        Args:
            level (unicode): human readable lavel's name

        """
        self.levels.discard(self.__levels[level])

logfilter = Filter()

class Main(QtGui.QWidget):
    """Logs plugin widget."""
    name = u'Logs'
    loaded = False
    depends = []
    __settings = QSettings(u'gayeogi', u'Logs')
    __levels = [u'Critical', u'Error', u'Warning', u'Info', u'Debug']
    def __init__(self, parent, ___, addWidget, removeWidget):
        """Constructs new Main instance.

        Args:
            parent: parent widget
            ___: whatever
            addWidget: function for adding widget to main window
            removeWidget: function for removing widget from main window

        """
        QtGui.QWidget.__init__(self, None)
        self.parent = parent
        self.addWidget = addWidget
        self.removeWidget = removeWidget
    def load(self):
        """Loads the plugin in.

        Also creates appropriate widgets and adds them to main window.

        """
        self.filter = QtGui.QLineEdit()
        self.filter.textEdited.connect(self.filter_)
        self.filter.setStatusTip(
            QtGui.QApplication.translate('Logs', 'Pattern: <pair>|<pair>, where <pair> is <column_name>:<searching_phrase>. Case insensitive, regexp allowed.')
        )
        self.logs = QtGui.QTreeWidget()
        self.logs.setIndentation(0)
        self.logs.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self.logs.setSortingEnabled(True)
        self.logs.setContextMenuPolicy(Qt.ActionsContextMenu)
        copy = QtGui.QAction(
            QtGui.QApplication.translate('Logs', '&Copy'),
            self.logs
        )
        copy.triggered.connect(self.copy)
        remove = QtGui.QAction(
            QtGui.QApplication.translate('Logs', '&Remove'),
            self.logs
        )
        remove.triggered.connect(self.remove)
        self.logs.addAction(copy)
        self.logs.addAction(remove)
        self.logs.setHeaderLabels([
            QtGui.QApplication.translate('Logs', 'Module'),
            QtGui.QApplication.translate('Logs', 'Type'),
            QtGui.QApplication.translate('Logs', 'File/Entry'),
            QtGui.QApplication.translate('Logs', 'Message')
        ])
        header = self.logs.header()
        header.setContextMenuPolicy(Qt.ActionsContextMenu)
        header.restoreState(self.__settings.value('state').toByteArray())
        for i, label in enumerate(['Module', 'Type', 'File/Entry', 'Message']):
            checked = self.__settings.value(label, True).toBool()
            action = QtGui.QAction(
                QtGui.QApplication.translate('Logs', label),
                self.logs
            )
            action.i = i
            action.setCheckable(True)
            action.setChecked(checked)
            action.toggled.connect(self.hideColumn)
            header.addAction(action)
            self.logs.setColumnHidden(i, not checked)
        clear = QtGui.QPushButton(QtGui.QApplication.translate(
            'Logs', 'Cle&ar'))
        clear.clicked.connect(self.logs.clear)
        save = QtGui.QPushButton(QtGui.QApplication.translate(
            'Logs', 'Sa&ve'))
        save.clicked.connect(self.save)
        buttonL = QtGui.QHBoxLayout()
        buttonL.addWidget(clear)
        buttonL.addWidget(save)
        buttonL.addStretch()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.filter)
        layout.addWidget(self.logs)
        layout.addLayout(buttonL)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.addWidget(u'horizontalLayout_2', self, 'start')
        for level in self.__levels:
            if self.__settings.value(level, 0).toInt()[0]:
                logfilter.addLevel(level)
        handler = Handler(self.update)
        handler.addFilter(logfilter)
        logger = logging.getLogger('gayeogi')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        Main.loaded = True
    def unload(self):
        """Unloads the plugin.

        Also removes appropriate widgets from main window, if needed.

        """
        self.__settings.setValue('state', self.logs.header().saveState())
        self.removeWidget(u'horizontalLayout_2', self, 'start')
        Main.loaded = False
    @staticmethod
    def QConfiguration():
        """Creates configuration widget.

        Returns:
            QWidget -- config widget used in settings dialog.

        """
        levels = QtGui.QListWidget()
        for level in Main.__levels:
            item = QtGui.QListWidgetItem(level)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Main.__settings.value(level, 0).toInt()[0])
            levels.addItem(item)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(levels)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        widget.enabled = Main.__settings.value(u'enabled', 0).toInt()[0]
        def save(x, y):
            Main.__settings.setValue(x, y)
            for i in range(levels.count()):
                item = levels.item(i)
                level = unicode(item.text())
                state = item.checkState()
                Main.__settings.setValue(level, state)
                if state:
                    logfilter.addLevel(level)
                else:
                    logfilter.removeLevel(level)
        widget.setSetting = lambda x, y : save(x, y)
        return widget
    def update(self, data):
        """Updates logs widget with new logs.

        Args:
            data (list): list of entries for appropriate columns

        """
        self.logs.addTopLevelItem(QtGui.QTreeWidgetItem(data))
    def filter_(self, text):
        """Filters log messages.

        Args:
            text (unicode): filter pattern (regexp)

        """
        columns = list()
        arguments = list()
        for a in unicode(text).split(u'|'):
            temp = a.split(u':')
            if len(temp) != 2 or temp[1] == u'':
                break
            columns.append(temp[0].lower())
            arguments.append(temp[1].lower())
        tree = self.sender().parent().children()[2]
        if len(columns) != 0 and len(columns) == len(arguments):
            header = tree.header().model()
            num_columns = [i for i in range(tree.columnCount())
                if not tree.isColumnHidden(i) and unicode(header.headerData(i,
                    Qt.Horizontal).toString()).lower() in columns]
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                hidden = list()
                for j, c in enumerate(num_columns):
                    try:
                        if item not in hidden:
                            if not re.search(arguments[j],
                            unicode(item.text(c)).lower()):
                                item.setHidden(True)
                                item.setSelected(False)
                                hidden.append(item)
                            else:
                                item.setHidden(False)
                    except:
                        pass
        else:
            for i in range(tree.topLevelItemCount()):
                tree.topLevelItem(i).setHidden(False)
    def copy(self, _):
        """Copies selected messages to the clipboard.

        Args:
            _: whatever (signal comp.)

        """
        text = ''
        for item in self.logs.selectedItems():
            for c in range(self.logs.columnCount()):
                if c != 0:
                    text += ':'
                text += item.text(c)
            text += '\n'
        QtGui.QApplication.clipboard().setText(text)
    def remove(self, _):
        """Removes selected messages from the logs.

        Args:
            _: whatever (signal comp.)

        """
        for item in self.logs.selectedItems():
            item = self.logs.takeTopLevelItem(
                self.logs.indexOfTopLevelItem(item))
    def hideColumn(self, checked):
        """Hides or reveals a column.

        Args:
            checked (bool): whether to hide or to reveal

        """
        sender = self.sender()
        self.logs.setColumnHidden(sender.i, not checked)
        self.__settings.setValue(str(sender.text()), checked)
    def save(self):
        """Saves logs to file.

        Displays dialog window asking user to choose a file.

        """
        filename = QtGui.QFileDialog().getSaveFileName()
        if filename:
            fh = open(filename, u'w')
            header = self.logs.headerItem()
            count = header.columnCount()
            for i in range(count):
                if not self.logs.isColumnHidden(i):
                    if i != 0:
                        fh.write(':')
                    fh.write(header.text(i))
            fh.write('\n')
            for i in range(self.logs.topLevelItemCount()):
                item = self.logs.topLevelItem(i)
                for c in range(count):
                    if not self.logs.isColumnHidden(i):
                        if c != 0:
                            fh.write(':')
                        fh.write(item.text(c))
                fh.write('\n')
            fh.close()
