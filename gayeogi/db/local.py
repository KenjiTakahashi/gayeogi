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

import json
import os
import glob
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

logger = logging.getLogger('gayeogi.local')


class Columner(object):
    """Docstring for Columner """

    artists = set()
    albums = set(["album", "year", "__a__", "comment"])  # FIXME

    @staticmethod
    def artist(index):
        """@todo: Docstring for artist

        :index: @todo
        :returns: @todo
        """
        return list(Columner.artists)[index]

    @staticmethod
    def album(index):
        """@todo: Docstring for album

        :index: @todo
        :returns: @todo
        """
        return list(Columner.albums)[index]


class _Node(object):
    def __init__(self, parent=None):
        self._parent = parent
        self._children = list()
        self.metadata = dict()
        if parent != None:
            parent.addChild(self)

    def setPath(self, dbPath):
        """@todo: Docstring for setPath

        :dbPath: @todo
        :returns: @todo
        """
        self._data = glob.glob(os.path.join(dbPath, u'*'))

    def canFetchMore(self):
        """@todo: Docstring for canFetchMore

        :returns: @todo
        """
        return bool(len(self._data))

    def fetch(self, dbpath=None):
        ArtistNode(self._data.pop(), self)

    def addChild(self, child):
        self._children.append(child)

    def parent(self):
        return self._parent

    def row(self):
        return self._parent._children.index(self)

    def column(self):
        return 0

    def childCount(self):
        return len(self._children)

    def child(self, row):
        """Returns Node's child placed at specified :row:.

        :row: Row at which to get child.
        :returns: Child at given :row:.
        """
        return self._children[row]

    def fn_encode(self, fn):
        """Encodes filename into format passable by filesystem(s).

        @note: Implemented in specific Node types.

        :fn: Human-readable filename string.
        :returns: Encoded :fn:.
        """
        raise NotImplemented

    def fn_decode(self, fn):
        """Decodes filename into human-readable string.

        :fn: Encoded filename string.
        :returns: Human-readable form of :fn:.
        """
        raise NotImplemented


class ArtistNode(_Node):
    """Artist node."""

    def __init__(self, path, parent=None):
        """@todo: Docstring for __init__

        :filename: @todo
        :parent: @todo
        :returns: @todo
        """
        super(ArtistNode, self).__init__(parent)
        self._path = path
        path = os.path.join(self._path, u'.meta')
        self.metadata = json.loads(open(path, 'r').read())
        self.metadata[u"artist"] = self.fn_decode(self._path)
        Columner.artists |= set(self.metadata.keys())
        self._data = glob.glob(os.path.join(self._path, u'*'))
        # TODO: deal with __urls__

    def fetch(self):
        AlbumNode(self._data.pop(), self)

    def fn_encode(self, fn):
        return u'&'.join([unicode(ord(c)) for c in fn])

    def fn_decode(self, fn):
        fn = os.path.basename(fn)
        return u''.join([unichr(int(n)) for n in fn.split(u'&')])


class AlbumNode(_Node):
    """Album node."""

    def __init__(self, path, parent=None):
        """@todo: Docstring for __init__

        :path: @todo
        :parent: @todo
        :returns: @todo
        """
        super(AlbumNode, self).__init__(parent)
        self._path = path
        path = os.path.join(self._path, u'.meta')
        self.metadata = json.loads(open(path, 'r').read())
        self.metadata[u"year"], self.metadata[u"album"] = self.fn_decode(
            self._path
        )
        # TODO: deal with a/d/r
        # TODO: fetch tracks
        # TODO: deal with columns

    def fn_encode(self, fn):
        fn1, fn2 = fn
        y = u'&'.join([unicode(ord(c)) for c in fn1])
        a = u'&'.join([unicode(ord(c)) for c in fn2])
        return "{0}.{1}".format(y, a)

    def fn_decode(self, fn):
        fn = os.path.basename(fn).split(u'.')
        y = u''.join([unichr(int(n)) for n in fn[0].split(u'&')])
        a = u''.join([unichr(int(n)) for n in fn[1].split(u'&')])
        return (y, a)


class TrackNode(_Node):
    """Track node."""


class BaseModel(QtCore.QAbstractItemModel):
    """General model class, meant to implement basic funcionality.

    Used directly by Artists view and as a source by Albums/Tracks views.
    """
    def __init__(self, dbpath, parent=None):
        """Constructs new BaseModel instance.

        :parent: parent object
        """
        super(BaseModel, self).__init__(parent)
        self._rootNode = _Node()
        self._rootNode.setPath(dbpath)

    def hasChildren(self, parent):
        """Tells if given :parent: has children.

        Returns true only for top-level node as our views are flat.

        @note: Override.

        :parent: Parent node.
        :returns: Boolean value, depending on children availability.
        """
        if not parent.isValid():
            return True
        return False

    def rowCount(self, parent):
        """Returns number of rows relative to @parent.

        @note: Mandatory override.

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

        :parent: Index, not used.
        :returns: Number of columns in the model.
        """
        return len(Columner.artists)

    def canFetchMore(self, parent):
        """@todo: Docstring for canFetchMore

        :parent: @todo
        :returns: @todo
        """
        return self._rootNode.canFetchMore()

    def fetchMore(self, parent):
        """@todo: Docstring for fetchMore

        :parent: @todo
        :returns: @todo
        """
        self._rootNode.fetch()

    def data(self, index, role):
        """Reimplemented from QAbstractItemModel.data().

        :index: Specifies index for which to return data.
        :role: Specifies role for which the data should be returned.
        :returns: Data for appropriate index and role.
        """
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            node = index.internalPointer()
            return node.metadata[self.headerData(index.column())]

    def headerData(self, section, _=None, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractItemModel.headerData().

        :section: Specifies for which section (e.g. column) to return data.
        :_: Normally used for orientation, but there's no use for it here.
        :role: Specifies for which role to return data.
        :returns: Appropriate column header data (e.g. name string).
        """
        if role == QtCore.Qt.DisplayRole:
            if section >= 0:
                return Columner.artist(section)

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

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Returns index placed at specified row and column,
        relatively to parent.

        Mandatory override.

        :row: Specifies row at which to look for index
        :column: Specifies column at which to look for index
        :parent: Specifies parent index to which to relate
        :returns: index placed at specified positions
        """
        if row < 0 or column < 0:
            return QtCore.QModelIndex()
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


class Model(QtGui.QAbstractProxyModel):
    """Docstring for Model """

    def __init__(self, sourceModel, parent=None):
        """@todo: to be defined """
        super(Model, self).__init__(parent)
        self._mapper = list()
        self._selection = list()
        self.setSourceModel(sourceModel)
        self.flatten()

    def flatten(self, root=None):
        """@todo: Docstring for flatten

        :root: @todo
        """
        self._mapper = list()
        model = self.sourceModel()
        if not root:
            root = model.index(-1, -1)

        def _flatten(_root):
            if _root.isValid() and _root in self._selection:
                for i in xrange(model.rowCount(_root)):
                    child = model.index(i, 0, _root)
                    self._mapper.append(QtCore.QPersistentModelIndex(child))
                    _flatten(child)
            else:
                for i in xrange(model.rowCount(_root)):
                    child = model.index(i, 0, _root)
                    _flatten(child)
        _flatten(root)

    def setSelection(self, selected, deselected):
        """@todo: Docstring for setSelection

        :selected: @todo
        :deselected: @todo
        """
        model = self.sourceModel()
        for s in selected.indexes():
            if s.column() == 0:
                index = model.createIndex(
                    s.row(), s.column(), s.internalPointer()
                )
                self._selection.append(index)
        for d in deselected.indexes():
            if d.column() == 0:
                index = model.createIndex(
                    d.row(), d.column(), d.internalPointer()
                )
                self._selection.remove(index)
        self.flatten()
        self.reset()

    def canFetchMore(self, parent):
        """@todo: Docstring for canFetchMore

        :parent: @todo
        :returns: @todo
        """
        for s in self._selection:
            node = s.internalPointer()
            if node.canFetchMore():
                return True
        return False

    def fetchMore(self, parent):
        """@todo: Docstring for fetchMore

        :parent: @todo
        :returns: @todo
        """
        for s in self._selection:
            node = s.internalPointer()
            if node.canFetchMore():
                node.fetch()
                break
        self.flatten()

    def hasChildren(self, parent):
        """Reimplemented from QAbstractProxyModel.hasChildren().

        Calls source implementation from BaseModel.
        """
        return self.sourceModel().hasChildren(parent)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractProxyModel.index()."""
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        source = QtCore.QModelIndex(self._mapper[row])
        return self.mapFromSource(
            self.sourceModel().index(source.row(), column, source.parent())
        )

    def data(self, index, role):
        """Reimplemented from QAbstractProxyModel.data().

        :index: Specifies index for which to return data.
        :role: Specifies role for which the data should be returned.
        :returns: Data for appropriate index and role.
        """
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            node = index.internalPointer()
            return node.metadata[self.headerData(index.column())]

    def headerData(self, section, _=None, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractProxyModel.headerData().

        :section: Specifies for which section (e.g. column) to return data.
        :_: Normally used for orientation, but there's no use for it here.
        :role: Specifies for which role to return data.
        :returns: Appropriate column header data (e.g. name string).
        """
        if role == QtCore.Qt.DisplayRole:
            if section >= 0:
                return Columner.album(section)

    def parent(self, _):
        """Reimplemented from QAbstractProxyModel.parent().

        Merely returns empty index, because the proxy model is flat.
        """
        return QtCore.QModelIndex()

    def rowCount(self, parent):
        """@todo: Docstring for rowCount

        :parent: @todo
        :returns: @todo
        """
        return len(self._mapper)

    def columnCount(self, parent):
        """@todo: Docstring for columnCount

        :parent: @todo
        :returns: @todo
        """
        return len(Columner.albums)  # FIXME

    def mapFromSource(self, source):
        """Reimplemented from QAbstractProxyModel.mapFromSource().

        Uses _mapper object created with Model.flatten() method to map
        tree-like source model to a flat one.
        """
        if not source.isValid():
            return QtCore.QModelIndex()
        source0 = self.sourceModel().createIndex(
            source.row(), 0, source.internalPointer()
        )
        i = self._mapper.index(source0)
        index = self.createIndex(i, source.column(), source.internalPointer())
        return index

    def mapToSource(self, proxy):
        """Reimplemented from QAbstractProxyModel.mapToSource().

        Uses _mapper object created with Model.flatten() method to map
        flat proxy model back to tree-like source one.
        """
        if not proxy.isValid():
            return QtCore.QModelIndex()
        sourceIndex = self._mapper[proxy.row()]
        return self.sourceModel().createIndex(
            sourceIndex.row(), proxy.column(), proxy.internalPointer()
        )


class DB(object):
    """Local filesystem watcher and DB holder/updater."""
    __settings = QtCore.QSettings(u'gayeogi', u'db')

    def __init__(self):
        """@todo: to be defined """
        self.artists = BaseModel(unicode(
            DB.__settings.value(u'path').toString()
        ))
        self.albums = Model(self.artists)
        self.tracks = Model(self.artists)
