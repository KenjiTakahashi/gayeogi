# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2010 - 2012
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

import os
from copy import deepcopy
from fnmatch import fnmatch
from PyQt4 import QtCore
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.musepack import Musepack
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4
from mutagen import File
import logging

logger = logging.getLogger('gayeogi.local')


class Node(object):
    def __init__(self, parent=None):
        self._parent = parent
        self._children = list()
        if parent != None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)

    def parent(self):
        return self._parent

    def row(self):
        return self._parent._children.index(self)

    def childCount(self):
        return len(self._children)


class DB(QtCore.QAbstractItemModel):
    """Local filesystem watcher and DB holder/updater."""
    def __init__(self, parent=None):
        """Constructs new DB instance.

        Also sets up directories watcher.

        Note: Although not explicitly enforced, it's meant to be singleton.

        :parent: parent widget/object
        """
        super(DB, self).__init__(parent)
        self._watcher = QtCore.QFileSystemWatcher(self)
        self._rootNode = Node()

    def rowCount(self, parent):
        """Returns number of rows relative to @parent.

        Mandatory override.

        :parent: index, relative to which the rows will be counted
        :returns: number of rows relative to @parent
        """
        if parent.isValid():
            parentNode = parent.internalPointer()
        else:
            parentNode = self._rootNode
        return parentNode.childCount()

    def columnCount(self, parent):
        """Returns number of columns.

        Mandatory override.

        :parent: index, not used
        :returns: number of columns in the model
        """
        return 2  # FIXME

    def data(self, index, role):
        """Function used by view to get appropriate data to display.

        Mandatory override.

        :index: Specifies index for which to return data
        :role: Specifies role for which the data should be returned
        :returns: data for appropriate index and role
        """
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return "TEst"  # FIXME
            else:
                return "tsET"  # FIXME

    def headerData(self, section, orientation, role):
        """Function used by view to get appropriate header names.

        Override.

        :section: Specifies for which section (e.g. column) to return data
        :orientation: horizontal/vertical, not used
        :role: Specifies for which role to return data
        :returns: Appropriate column header data (e.g. name string)
        """
        if role == QtCore.Qt.DisplayRole:
            if section == 0:  # FIXME, whole if
                return "one"
            else:
                return "two"
