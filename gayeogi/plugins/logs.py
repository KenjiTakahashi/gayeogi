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
from PyQt4.QtCore import QSettings, QStringList, Qt
import logging

class Main(QtGui.QWidget):
    """Logs plugin widget."""
    name = u'Logs'
    loaded = False
    depends = []
    __settings = QSettings(u'gayeogi', u'Logs')
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
        self.logs = QtGui.QTreeWidget()
        self.logs.setHeaderLabels(QStringList([
            QtGui.QApplication.translate('Logs', 'Module'),
            QtGui.QApplication.translate('Logs', 'Type'),
            QtGui.QApplication.translate('Logs', 'File/Entry'),
            QtGui.QApplication.translate('Logs', 'Message')
        ]))
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
        layout.addWidget(self.logs)
        layout.addLayout(buttonL)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.addWidget(u'horizontalLayout_2', self, 'start')
        Main.loaded = True
    def unload(self):
        """Unloads the plugin.

        Also removes appropriate widgets from main window, if needed.

        """
        self.removeWidget(u'horizontalLayout_2', self, 'start')
        Main.loaded = False
    @staticmethod
    def QConfiguration():
        """Creates configuration widget.

        Returns:
            QWidget -- config widget used in settings dialog.

        """
        levels = QtGui.QListWidget()
        for level in [u'Critical', u'Error', u'Warning', u'Info', u'Debug']:
            item = QtGui.QListWidgetItem(level)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Main.__settings.value(level, 2).toInt()[0])
            levels.addItem(item)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(levels)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        widget.enabled = Main.__settings.value(u'enabled', 0).toInt()[0]
        widget.setSetting = lambda x, y : Main.__settings.setValue(x, y)
        return widget
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
                        if i != 0:
                            fh.write(':')
                        fh.write(item.text(c))
                fh.write('\n')
            fh.close()
