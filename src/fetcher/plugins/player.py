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

from PyQt4.phonon import Phonon
from PyQt4 import QtGui
from PyQt4.QtCore import QSize, Qt
from copy import deepcopy

class PlayerItemDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        start = deepcopy(option.rect)
        size = option.font.pointSize()
        start.setLeft(start.left() + 5)
        start.setTop(start.top() + 20)
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        painter.drawText(start, Qt.AlignLeft, index.data(668).toString() + u' (' +
                index.data(669).toString() + u')')
        start.setY(start.y() - (size + 6))
        painter.drawText(start, Qt.AlignLeft, index.data(666).toString() + u'. ' +
                index.data(667).toString())
        start = deepcopy(option.rect)
        start.setRight(start.right() - 5)
        painter.save()
        font = option.font
        font.setPointSize(16)
        painter.setFont(font)
        painter.drawText(start, Qt.AlignRight | Qt.AlignVCenter,
                index.data(670).toString() + u'/' + index.data(671).toString())
        font.setPointSize(10)
        painter.restore()
    def sizeHint(self, option, index):
        return QSize(0, 18 + option.font.pointSize() * 2)

class Main(QtGui.QWidget):
    loaded = False
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, None)
        self.parent = parent
    def load(self):
        previous = QtGui.QPushButton(u'Previous')
        play = QtGui.QPushButton(u'Play')
        stop = QtGui.QPushButton(u'Stop')
        next_ = QtGui.QPushButton(u'Next')
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.setContentsMargins(0, 0, 0, 0)
        buttonsLayout.addWidget(previous)
        buttonsLayout.addWidget(play)
        buttonsLayout.addWidget(stop)
        buttonsLayout.addWidget(next_)
        buttons = QtGui.QWidget()
        progress = QtGui.QProgressBar()
        buttons.setLayout(buttonsLayout)
        delegate = PlayerItemDelegate()
        self.playlist = QtGui.QListWidget()
        self.playlist.setItemDelegate(delegate)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(progress)
        layout.addWidget(self.playlist)
        self.setLayout(layout)
        self.parent.tracks.itemActivated.connect(self.addItem)
        self.parent.horizontalLayout_2.addWidget(self)
        Main.loaded = True
    def unload(self):
        Main.loaded = False
    def QConfiguration():
        pass
    QConfiguration = staticmethod(QConfiguration)
    def addItem(self, item, _):
        item_ = QtGui.QListWidgetItem()
        item_.setData(666, item.text(0))
        item_.setData(667, item.text(1))
        item_.setData(668, item.artist)
        item_.setData(669, item.album)
        self.playlist.addItem(item_)
