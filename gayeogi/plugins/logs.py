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
from PyQt4.QtCore import QSettings, QStringList

class Main(QtGui.QWidget):
    name = u'Logs'
    loaded = False
    depends = []
    __settings = QSettings(u'gayeogi', u'Logs')
    def __init__(self, parent, ___, addWidget, removeWidget):
        QtGui.QWidget.__init__(self, None)
        self.parent = parent
        self.addWidget = addWidget
        self.removeWidget = removeWidget
    def load(self):
        logs = QtGui.QTreeWidget()
        logs.setHeaderLabels(QStringList([
            QtGui.QApplication.translate('Logs', 'Module'),
            QtGui.QApplication.translate('Logs', 'Type'),
            QtGui.QApplication.translate('Logs', 'File/Entry'),
            QtGui.QApplication.translate('Logs', 'Message')
        ]))
        clear = QtGui.QPushButton(QtGui.QApplication.translate(
            'Logs', 'Cle&ar'))
        save = QtGui.QPushButton(QtGui.QApplication.translate(
            'Logs', 'Sa&ve'))
        buttonL = QtGui.QHBoxLayout()
        buttonL.addWidget(clear)
        buttonL.addWidget(save)
        buttonL.addStretch()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(logs)
        layout.addLayout(buttonL)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.addWidget(u'horizontalLayout_2', self, 'start')
        Main.loaded = True
    def unload(self):
        self.removeWidget(u'horizontalLayout_2', self, 'start')
        Main.loaded = False
    @staticmethod
    def QConfiguration():
        widget = QtGui.QWidget()
        widget.enabled = Main.__settings.value(u'enabled', 0).toInt()[0]
        widget.setSetting = lambda x, y : Main.__settings.setValue(x, y)
        return widget
