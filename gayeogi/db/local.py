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
from fnmatch import fnmatch
from PyQt4 import QtCore, QtGui
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.musepack import Musepack
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4
from mutagen import File
import logging

logger = logging.getLogger('gayeogi.local')


class LegacyDB(object):
    def __init__(self, dbPath):
        self.dbPath = os.path.join(dbPath, u'db.pkl')

    def read(self):
        import cPickle
        handler = open(self.dbPath, u'rb')
        result = cPickle.load(handler)
        handler.close()
        if result[0] == u'0.6':
            self.convert3(result[3], result[4])
            return (u'0.6.1',) + result[1:] + ([False],)
        else:
            return result

    def convert3(self, urls, avai):
        import re
        for key in avai.keys():
            if avai[key][u'remote']:
                avai[key][u'remote'] = set()
                artist = re.findall(u'\d*\D+', key)[0]
                try:
                    u = urls[artist]
                except KeyError:
                    pass
                else:
                    for uu in u.keys():
                        avai[key][u'remote'].add(uu)
            else:
                avai[key][u'remote'] = set()


class _Node(object):
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

    def column(self):
        """@todo: Docstring for column

        :returns: @todo
        """
        return 0  # FIXME

    def childCount(self):
        return len(self._children)

    def child(self, row):
        """Returns Node's child placed at specified @row.

        :row: @todo
        :returns: @todo
        """
        return self._children[row]


class ArtistNode(_Node):
    def __init__(self, name, parent=None):
        super(ArtistNode, self).__init__(parent)
        self.name = name


class AlbumNode(_Node):
    """Album node."""
    def __init__(self, parent=None):
        """@todo: to be defined

        :parent: @todo
        """
        super(AlbumNode, self).__init__(parent)


class TrackNode(_Node):
    """Track node."""
    def __init__(self, parent=None):
        """@todo: to be defined

        :parent: @todo
        """
        super(TrackNode, self).__init__()


class _Model(QtCore.QAbstractItemModel):
    """General model class, meant to implement basic funcionality."""
    def __init__(self, parent=None):
        """Constructs new _Model instance.

        :parent: parent widget/object
        """
        super(_Model, self).__init__(parent)
        self._rootNode = _Node()
        # FIXME : remove things below
        node = ArtistNode("b", self._rootNode)
        ArtistNode("a", self._rootNode)
        AlbumNode(node)
        node3 = AlbumNode(node)
        TrackNode(node3)

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
            # FIXME: whole if
            if index.column() == 0:
                if isinstance(node, ArtistNode):
                    return node.name
                else:
                    return "alaow"
            else:
                return "tsET"

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

    def parent(self, index):
        """Returns parent index for given Node index.

        Mandatory override.

        :index: Specifies index for which to get parent
        :returns: parent of the given index
        """
        parent = self.getNode(index).parent()
        if parent == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), parent.column(), parent)

    def index(self, row, column, parent):
        """Returns index placed at specified row and column,
        relatively to parent.

        Mandatory override.

        :row: Specifies row at which to look for index
        :column: Specifies column at which to look for index
        :parent: Specifies parent index to which to relate
        :returns: index placed at specified positions
        """
        child = self.getNode(parent).child(row)
        if child:
            return self.createIndex(row, column, child)
        return QtCore.QModelIndex()

    def getNode(self, index):
        """Returns Node for specified index.

        If no Node exists for such index, returns rootNode.

        :index: Specifies index for which to get Node
        :returns: Node for specified index, if exists, rootNode otherwise
        """
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootNode


class ArtistsModel(_Model):
    """Docstring for ArtistsModel """
    def __init__(self):
        """@todo: to be defined """
        super(ArtistsModel, self).__init__()

    def hasChildren(self, parent):
        """@todo: Docstring for hasChildren

        :parent: @todo
        :returns: @todo
        """
        if self.getNode(parent) == self._rootNode:
            return True
        return False


class AlbumsModel(QtGui.QAbstractProxyModel):
    """Docstring for AlbumsModel """
    def __init__(self):
        """@todo: to be defined """
        super(AlbumsModel, self).__init__()

    def index(self, row, column, parent):
        """@todo: Docstring for index

        :row: @todo
        :column: @todo
        :parent: @todo
        :returns: @todo
        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        source = self.mapToSource(parent)
        return self.mapFromSource(
            self.sourceModel().index(row, column, source)
        )

    def parent(self, child):
        """@todo: Docstring for parent

        :child: @todo
        :returns: @todo
        """
        return self.mapFromSource(self.mapToSource(child).parent())

    def rowCount(self, parent):
        """@todo: Docstring for rowCount

        :parent: @todo
        :returns: @todo
        """
        source = self.sourceModel()
        return source.rowCount(parent)

    def columnCount(self, parent):
        """@todo: Docstring for columnCount

        :parent: @todo
        :returns: @todo
        """
        return self.sourceModel().columnCount(parent)

    def mapFromSource(self, source):
        """@todo: Docstring for mapFromSource

        :source: @todo
        :returns: @todo
        """
        if not source.isValid():
            return QtCore.QModelIndex()
        return self.createIndex(
            source.row(), source.column(), source.internalPointer()
        )

    def mapToSource(self, proxy):
        """@todo: Docstring for mapToSource

        :proxy: @todo
        :returns: @todo
        """
        if not proxy.isValid():
            return QtCore.QModelIndex()
        return self.sourceModel().createIndex(
            proxy.row(), proxy.column(), proxy.internalPointer()
        )


class DB(object):
    """Local filesystem watcher and DB holder/updater."""
    def __init__(self):
        """@todo: to be defined """
        self._model = _Model()
        self.artists = ArtistsModel()
        #self.artists.setSourceModel(self._model)
        self.albums = AlbumsModel()
        self.albums.setSourceModel(self._model)
