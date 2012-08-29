# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak (C) 2010 - 2012
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


class _Node(object):
    headers = set()

    def __init__(self, path, parent=None):
        self._primary = ('', '')
        self._path = path
        self._parent = parent
        self._children = list()
        self.metadata = dict()
        if parent != None:
            parent.addChild(self)
        if not isinstance(self, TrackNode) and path:
            self._data = glob.glob(os.path.join(path, u'*'))
        else:
            self._data = list()

    def update(self, meta=None):
        """@todo: Docstring for update

        :meta: @todo
        :returns: @todo

        """
        if meta:
            self.metadata.update(meta)
        for i, child in enumerate(self._children):
            if not i:
                self.metadata.update(child.metadata)
                continue
            for k, v in child.metadata.iteritems():
                value = self.metadata[k]
                if value != v:
                    self.metadata[k] = u"<multiple_values>"
                    break

    def update_headers(self):
        _Node.headers |= set(self.metadata.keys())

    def canFetchMore(self):
        """Indicates if there is still some data to read from
        persistent storage.

        :returns: True or False.
        """
        return bool(len(self._data))

    def fetch(self):
        """Fetches next chunk of data from presistent storage
        and wraps it into appropriate Node type.

        @see: _Node.canFetchMore

        @note: Usually reimplemented in specific type Nodes.
        """
        ArtistNode(path=self._data.pop(), parent=self)

    def addChild(self, child):
        self._children.append(child)

    @staticmethod
    def header(section):
        """@todo: Docstring for header

        :section: @todo
        :returns: @todo
        """
        return list(_Node.headers)[section]

    def parent(self):
        return self._parent

    def row(self):
        return self._parent._children.index(self)

    def column(self):
        return 0  # FIXME

    def childCount(self):
        return len(self._children)

    def child(self, row):
        """Returns Node's child placed at specified :row:.

        :row: Row at which to get child.
        :returns: Child at given :row:.
        """
        try:
            return self._children[row]
        except IndexError:
            return None

    def children(self):
        """@todo: Docstring for children
        :returns: @todo

        """
        return self._children

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

    def __init__(self, path=None, parent=None):
        """Creates a new Artist Node.

        If :path: is specified it fetches metadata from persistent storage
        and prefetches informations about Album Nodes. Otherwise it creates
        an empty Node meant to be filled with ArtistNode.update method.

        :path: Encoded filesystem path.
        :parent: Parent Node. It's always a rootNode here.
        """
        super(ArtistNode, self).__init__(path, parent)
        self._primary = (u'album', u'year')
        if path:
            path = os.path.join(self._path, u'.meta')
            self.metadata = json.loads(open(path, 'r').read())
            self.metadata[u"artist"] = self.fn_decode(self._path)
            try:
                urls = self.metadata[u"__urls__"]
                if len(urls) > 1:
                    self.metadata[u"__urls__"] = urls[1]
                else:
                    del self.metadata[u"__urls__"]
                self.urls = urls[0]
            except KeyError:
                self.urls = dict()
            self.update_headers()
        else:
            self.metadata = dict()

    def fetch(self):
        AlbumNode(self._data.pop(), self)

    def fn_encode(self, fn):
        return u'&'.join([unicode(ord(c)) for c in fn])

    def fn_decode(self, fn):
        fn = os.path.basename(fn)
        return u''.join([unichr(int(n)) for n in fn.split(u'&')])


class AlbumNode(_Node):
    """Album node."""

    def __init__(self, path=None, parent=None):
        """@todo: Docstring for __init__

        :path: @todo
        :parent: @todo
        """
        super(AlbumNode, self).__init__(path, parent)
        self._primary = (u'track', u'title')
        if path:
            path = os.path.join(self._path, u'.meta')
            self.metadata = json.loads(open(path, 'r').read())
            (self.metadata[u"year"],
            self.metadata[u"album"]) = self.fn_decode(self._path)
            self.adr = dict()
            for adr in [u"__a__", u"__d__", u"__r__"]:
                try:
                    _ = self.metadata[adr]
                    if len(_) > 1:
                        self.metadata[adr] = _[1]
                    else:
                        del self.metadata[adr]
                    self.adr[adr] = _[0]
                except KeyError:
                    self.adr[adr] = False
            self.update_headers()
        else:
            self.metadata = dict()

    def fetch(self):
        TrackNode(self._data.pop(), self)

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

    def __init__(self, path=None, parent=None):
        """@todo: Docstring for __init__

        :path: @todo
        :parent: @todo
        """
        super(TrackNode, self).__init__(path, parent)
        if path:
            self.metadata = json.loads(open(path, 'r').read())
            (self.metadata[u"tracknumber"],
            self.metadata[u"title"]) = self.fn_decode(self._path)
            self.update_headers()
        else:
            self.metadata = dict()

    def fn_encode(self, fn):
        fn1, fn2 = fn
        n = u'&'.join([unicode(ord(c)) for c in fn1])
        t = u'&'.join([unicode(ord(c)) for c in fn2])
        return (n, t)

    def fn_decode(self, fn):
        fn = os.path.basename(fn).split(u'.')
        n = u''.join([unichr(int(n)) for n in fn[0].split(u'&')])
        t = u''.join([unichr(int(n)) for n in fn[1].split(u'&')])
        return (n, t)


class BaseModel(QtCore.QAbstractItemModel):
    """General model class, meant to implement basic funcionality,
    especially inserting, updating and removing items.

    Used directly by Artists view and as a source by Albums/Tracks views.
    """
    def __init__(self, dbpath, parent=None):
        """Constructs new BaseModel instance.

        :dbPath: Path to the database.
        :parent: Parent object.
        """
        super(BaseModel, self).__init__(parent)
        self._rootNode = _Node(dbpath)

    def hasChildren(self, parent):
        """Reimplemented from QAbstractItemModel.hasChildren.

        :returns: True if :parent: is a top-level node, False otherwise.
        """
        if not parent.isValid():
            return True
        return False

    def rowCount(self, parent):
        """Reimplemented from QAbstractItemModel.rowCount."""
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self._rootNode
        return node.childCount()

    def columnCount(self, parent):
        """Reimplemented from QAbstractItemModel.columnCount."""
        return len(_Node.headers)

    def canFetchMore(self, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractItemModel.canFetchMore."""
        if not parent.isValid():
            return self._rootNode.canFetchMore()
        return parent.internalPointer().canFetchMore()

    def fetchMore(self, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractItemModel.fetchMore."""
        if not parent.isValid():
            node = self._rootNode
        else:
            node = parent.internalPointer()
        self.beginInsertRows(parent, 0, 0)
        node.fetch()
        self.endInsertRows()
        count = node.childCount()
        for i in xrange(count):
            child = node.child(i)
            if child.canFetchMore():
                child.fetch()
            count = child.childCount()
            for j in xrange(count):
                child = child.child(j)
                if child.canFetchMore():
                    child.fetch()
            hlen = len(_Node.headers) - 1
            self.beginMoveColumns(parent, 0, hlen, parent, hlen + 2)
            self.endMoveColumns()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractItemModel.data."""
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            node = index.internalPointer()
            try:
                header = self.headerData(index.column())
                if header == u'#':
                    header = u'tracknumber'
                return node.metadata[header]
            except KeyError:
                return ""

    def headerData(self, section, _=None, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractItemModel.headerData.

        @note: _ (orientation) is not used, as there's only horizontal header.
        """
        if role == QtCore.Qt.DisplayRole:
            if section >= 0:
                header = _Node.header(section)
                if header == u'tracknumber':
                    return u'#'
                return header

    def parent(self, index):
        """Reimplemented from QAbstractItemModel.parent."""
        parent = self.getNode(index).parent()
        if parent == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), parent.column(), parent)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractItemModel.index."""
        if row < 0 or column < 0:
            return QtCore.QModelIndex()
        child = self.getNode(parent).child(row)
        if child:
            return self.createIndex(row, column, child)
        return QtCore.QModelIndex()

    def getNode(self, index):
        """Returns Node for specified index.

        :index: Index for which to get Node.
        :returns: Node for specified index, if exists, rootNode otherwise.
        """
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootNode

    def upsert(self, index, meta):
        """@todo: Docstring for upsert

        :index: @todo
        :meta: @todo
        :returns: @todo
        """
        def find_artist(name):
            for child in self._rootNode.children():
                if child.metadata[u'artist'] == name:
                    return child
            return None

        def find_album(index, artist, name, year):
            for child in artist.children():
                meta = child.metadata
                if meta[u'album'] == name and meta[u'year'] == year:
                    return child
            return None

        def find_track(index, album, name, number):
            for child in album.children():
                meta = child.metadata
                if meta[u'title'] == name and meta[u'tracknumber'] == number:
                    return child
            return None
        if not index:
            try:
                artist = find_artist(meta[u'artist'])
            except KeyError:
                artist = find_artist(u'unknown')
            if not artist:
                self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
                artist = ArtistNode(parent=self._rootNode)
                self.endInsertRows()
            artist_index = self.index(0, 0)
            m_album = u'unknown'
            try:
                m_album = meta[u'album']
            except KeyError:
                pass
            m_year = u'0000'
            try:
                m_year = meta[u'year']
            except KeyError:
                pass
            album = find_album(artist_index, artist, m_album, m_year)
            if not album:
                self.beginInsertRows(artist_index, 0, 0)
                album = AlbumNode(parent=artist)
                self.endInsertRows()
            album_index = self.index(0, 0, artist_index)
            self.beginInsertRows(album_index, 0, 0)
            track = TrackNode(parent=album)
            self.endInsertRows()
            track.update(meta)
            album.update()
            artist.update()
            self._rootNode.update_headers()
        else:
            index = self.index(index.row(), index.column(), index.parent())
            track = index.internalPointer()
            track.update(meta)
            album = track.parent()
            album.update()
            artist = album.parent()
            artist.update()


class Model(QtGui.QAbstractProxyModel):
    """Docstring for Model """

    def __init__(self, sourceModel, parent=None):
        """@todo: to be defined """
        super(Model, self).__init__(parent)
        self._mapper = list()
        self._selection = list()
        self.setSourceModel(sourceModel)

    def insertRows(self, parent):
        """Inserts new rows based on current _selection.
        It also triggers data fetching as needed.

        @note: To actually add data to the model use BaseModel.upsert.

        :parent: Index whose children should be inserted.
        """
        model = self.sourceModel()
        count = model.rowCount(parent)
        count_ = self.rowCount()
        end = count_ + count - 1
        self.beginInsertRows(QtCore.QModelIndex(), count_, end)
        for i in xrange(count):
            child = model.index(i, 0, parent)
            self._mapper.append(QtCore.QPersistentModelIndex(child))
        self.endInsertRows()

    def removeRows(self, parent):
        """Removes rows previously set by Model.insertRows if their :parent:
        is no longer in _selection.

        @note: To actually remove data from the model use BaseModel.remove.

        :parent: Index whose children should be removed.
        """
        model = self.sourceModel()
        count = model.rowCount(parent)
        child = self.mapFromSource(model.index(0, 0, parent))
        row = child.row()
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count)
        for i in xrange(count):
            child = model.index(i, 0, parent)
            self._mapper.remove(QtCore.QPersistentModelIndex(child))
        self.endRemoveRows()

    def setSelection(self, selected, deselected):
        """Sets new visible items, based on parent view's selections.

        :selected: Parent view's newly selected items.
        :deselected: Parent view's deselected items.
        """
        model = self.sourceModel()
        for d in deselected:
            if d.column() == 0:
                index = model.createIndex(
                    d.row(), d.column(), d.internalPointer()
                )
                self._selection.remove(index)
                self.removeRows(index)
        for s in selected:
            if s.column() == 0:
                index = model.createIndex(
                    s.row(), s.column(), s.internalPointer()
                )
                self._selection.append(index)
                self.insertRows(index)

    def hasChildren(self, parent):
        """Reimplemented from QAbstractProxyModel.hasChildren.

        Calls source implementation from BaseModel.
        """
        return self.sourceModel().hasChildren(parent)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractProxyModel.index."""
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        source = QtCore.QModelIndex(self._mapper[row])
        return self.mapFromSource(
            self.sourceModel().index(source.row(), column, source.parent())
        )

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractProxyModel.data."""
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            node = index.internalPointer()
            try:
                header = self.headerData(index.column())
                if header == u'#':
                    header = u'tracknumber'
                return node.metadata[header]
            except KeyError:
                return ""

    def headerData(self, section, _=None, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractProxyModel.headerData.

        @note: _ (orientation) is not used, as there's only horizontal header.
        """
        if role == QtCore.Qt.DisplayRole:
            if section >= 0:
                # When changing selection, the view sometimes calls this before
                # columnCount, thus trying to get headerData for columns which
                # might no longer exist.
                try:
                    header = _Node.header(section)
                    if header == u'tracknumber':
                        return u'#'
                    return header
                except IndexError:
                    pass

    def parent(self, _):
        """Reimplemented from QAbstractProxyModel.parent.

        :returns: Merely an empty index, because the proxy model is flat.
        """
        return QtCore.QModelIndex()

    def rowCount(self, _=QtCore.QModelIndex()):
        """Reimplemented from QAbstractProxyModel.rowCount.

        @note: _ (parent) parameter is not used.

        :returns: Length of the Model._mapper mapping.
        """
        return len(self._mapper)

    def columnCount(self, _=QtCore.QModelIndex()):
        """Reimplemented from QAbstractProxyModel.columnCount.

        @note: _ (parent) parameter is not used.

        :returns: Sum of the length of all rows headers data.
        """
        return len(_Node.headers)

    def mapFromSource(self, source):
        """Reimplemented from QAbstractProxyModel.mapFromSource.

        Uses _mapper object created with Model.flatten method to map
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
        """Reimplemented from QAbstractProxyModel.mapToSource.

        Uses _mapper object created with Model.flatten method to map
        flat proxy model back to tree-like source one.
        """
        if not proxy.isValid():
            return QtCore.QModelIndex()
        sourceIndex = self._mapper[proxy.row()]
        return self.sourceModel().createIndex(
            sourceIndex.row(), proxy.column(), proxy.internalPointer()
        )


class AlbumsModel(Model):
    """Docstring for AlbumsModel """


class TracksModel(Model):
    """Docstring for TracksModel """


class DB(object):
    """Local filesystem watcher and DB holder/updater."""
    __settings = QtCore.QSettings(u'gayeogi', u'db')

    def __init__(self, path):
        """@todo: to be defined """
        self.artists = BaseModel(path)
        self.albums = AlbumsModel(self.artists)
        self.tracks = TracksModel(self.artists)
        self.index = dict()

    def isIgnored(self, path, ignores):
        """Checks if specified folder is to be ignored.

        :path: Folder to check.
        :ignores: List of folders to check against.
        :returns: True if :path: should be ignored, False otherwise.
        """
        for ignore, enabled in ignores:
            if enabled and fnmatch(path, u'*' + ignore + u'*'):
                return True
        return False

    def getIndex(self, path):
        """@todo: Docstring for getIndex

        :path: @todo
        :returns: @todo

        """
        try:
            return self.index[path]
        except KeyError:
            return None

    def upsert(self, index):
        """@todo: Docstring for upsert

        :index: @todo
        :returns: @todo
        """
        def _upsert(meta):
            self.artists.upsert(index, meta)
        return _upsert

    def run(self):
        """@todo: Docstring for run"""
        directories = DB.__settings.value(u'directories', []).toPyObject()
        ignores = DB.__settings.value(u'ignores', []).toPyObject()
        if ignores == None:
            ignores = list()
        for directory, enabled in directories:
            if enabled:
                for root, _, filenames in os.walk(directory):
                    if not self.isIgnored(root, ignores):
                        for filename in filenames:
                            path = os.path.join(root, filename)
                            if not self.isIgnored(path, ignores):
                                # TODO: read real metadata
                                self.index[path] = self.upsert(
                                    self.getIndex(path)
                                )({
                                    '1': path,
                                    'test2': 2,
                                    u'artist': 't',
                                    u'album': 'dang',
                                    u'year': '200'
                                })
