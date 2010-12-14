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

class Main(object):
    def __init__(self, parent):
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
        playlist = QtGui.QListWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(progress)
        layout.addWidget(playlist)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        self.parent.horizontalLayout_2.addWidget(widget)
    def unload(self):
        pass
    def QConfiguration():
        pass
    QConfiguration = staticmethod(QConfiguration)
