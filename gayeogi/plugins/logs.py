# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak © 2011 - 2012
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
from gayeogi.interfaces import TableView
from gayeogi.utils import Filter


class Handler(QObject, logging.Handler):
    """Logs handler.

    @signal: signal (object): propagates log to the widget.

    """

    signal = pyqtSignal(object)

    def __init__(self, update, level=logging.DEBUG):
        """Constructs new Handler instance.

        :update: Function used to update widget.
        :levels: Enabled levels list.
        :level: Logging level.

        """
        QObject.__init__(self)
        logging.Handler.__init__(self, level)
        self.signal.connect(update)

    def emit(self, record):
        """Emits signal.

        :record: Log record.

        """
        self.signal.emit([record.name, record.levelname] + record.msg)


class LogFilter(logging.Filter):
    """Logs filter."""
    ADDED = 60
    REMOVED = 70
    allLevels = {
        u'Error': logging.ERROR,
        u'Debug': logging.DEBUG,
        u'Added': ADDED,
        u'Removed': REMOVED
    }

    def __init__(self):
        """Construcs new LogFilter instance."""
        super(LogFilter, self).__init__()
        self.levels = set()
        for name in [u'added', u'removed']:
            level = LogFilter.allLevels[name.capitalize()]
            logging.addLevelName(level, name.upper())

            def func(self, msg, *args, **kwargs):
                self._log(level, msg, args, **kwargs)
            setattr(logging.Logger, name, func)

    def filter(self, record):
        """Filters incoming records according to their enabled state.

        :record: Log record received from Logger.

        """
        return record.levelno in self.levels

    def addLevel(self, level):
        """Enabled specified level.

        :level: Human readable level's name.

        """
        self.levels.add(self.allLevels[level])

    def removeLevel(self, level):
        """Disables specified level.

        :level: Human readable level's name.

        """
        self.levels.discard(self.allLevels[level])


logfilter = LogFilter()


class Main(QtGui.QWidget):
    """Logs plugin widget."""
    name = u'Logs'
    loaded = False
    depends = []
    __settings = QSettings(u'gayeogi', u'Logs')

    def __init__(self, parent, ___, addWidget, removeWidget):
        """Constructs new Main instance.

        :parent: Parent widget.
        :___: Whatever.
        :addWidget: Function used to add widget to main window.
        :removeWidget: Function used to remove widget from main window.

        """
        QtGui.QWidget.__init__(self, None)
        self.parent = parent
        self.addWidget = addWidget
        self.removeWidget = removeWidget

    def load(self):
        """Loads the plugin in.

        Also creates appropriate widgets and adds them to main window.

        """
        self.logs = QtGui.QStandardItemModel(0, 4)
        self.logs.setHorizontalHeaderLabels([
            QtGui.QApplication.translate('Logs', 'Module'),
            QtGui.QApplication.translate('Logs', 'Type'),
            QtGui.QApplication.translate('Logs', 'File/Entry'),
            QtGui.QApplication.translate('Logs', 'Message')
        ])
        self.view = TableView(None)  # TODO: provide state
        self.view.setContextMenuPolicy(Qt.ActionsContextMenu)
        copy = QtGui.QAction(
            QtGui.QApplication.translate('Logs', '&Copy'), self.view
        )
        copy.triggered.connect(self.copy)
        remove = QtGui.QAction(
            QtGui.QApplication.translate('Logs', '&Remove'), self.view
        )
        remove.triggered.connect(self.remove)
        self.view.addAction(copy)
        self.view.addAction(remove)
        clear = QtGui.QPushButton(QtGui.QApplication.translate(
            'Logs', 'Cle&ar'))
        clear.clicked.connect(self.logs.clear)
        save = QtGui.QPushButton(QtGui.QApplication.translate(
            'Logs', 'Sa&ve'))
        save.clicked.connect(self.save)
        self.filter = QtGui.QLineEdit()
        self.filter.setStatusTip(QtGui.QApplication.translate(
            'Logs',
            "Pattern: <pair>|<pair>, where <pair> is <column_name>"
            ":<searching_phrase>. Case insensitive, regexp allowed."
        ))
        f = Filter(self.logs)
        self.filter.textEdited.connect(f.setFilter)
        self.view.setModel(f)
        buttonL = QtGui.QHBoxLayout()
        buttonL.addWidget(clear)
        buttonL.addWidget(save)
        buttonL.addStretch()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.filter)
        layout.addWidget(self.view)
        layout.addLayout(buttonL)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.addWidget(u'horizontalLayout_2', self, 'start')
        for level in LogFilter.allLevels.keys():
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
        self.__settings.setValue(
            'state', self.view.horizontalHeader().saveState()
        )
        self.removeWidget(u'horizontalLayout_2', self, 'start')
        Main.loaded = False

    @staticmethod
    def QConfiguration():
        """Creates configuration widget.

        :returns: Config widget used in settings dialog.

        """
        levels = QtGui.QListWidget()
        for level in LogFilter.allLevels.keys():
            item = QtGui.QListWidgetItem(level)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Main.__settings.value(level, 0).toInt()[0])
            levels.addItem(item)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(levels)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        widget.enabled = Main.__settings.value(u'enabled', 0).toInt()[0]

        def save(y):
            Main.__settings.setValue(u'enabled', y)
            for i in range(levels.count()):
                item = levels.item(i)
                level = unicode(item.text())
                state = item.checkState()
                Main.__settings.setValue(level, state)
                if state:
                    logfilter.addLevel(level)
                else:
                    logfilter.removeLevel(level)
        widget.save = save
        widget.globalText = QtGui.QApplication.translate(
            'Logs',
            "Here you can choose what kind of log messages"
            " should be displayed in the main window."
        )
        return widget

    def update(self, data):
        """Updates logs widget with new logs.

        :data: List of entries for appropriate columns.

        """
        self.logs.appendRow([QtGui.QStandardItem(d) for d in data])

    def copy(self, _):
        """Copies selected messages to the clipboard.

        :_: whatever (signal compatibility).

        """
        text = ''
        for index in self.view.selectedIndexes():
            for c in range(self.logs.columnCount()):
                if c != 0:
                    text += ':'
                text += index.data(c)
            text += '\n'
        QtGui.QApplication.clipboard().setText(text)

    def remove(self, _):
        """Removes selected messages from the logs.

        :_: whatever (signal compatibility).

        """
        for index in self.view.selectedIndexes():
            self.logs.takeRow(index.row())

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
