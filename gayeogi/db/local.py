# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak © 2010 - 2012
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
import cPickle
from base64 import urlsafe_b64encode, urlsafe_b64decode
from fnmatch import fnmatch
from PyQt4 import QtCore, QtGui
import logging
from gayeogi.utils import Tagger


class LegacyDB(object):
    def __init__(self, dbPath):
        self.dbPath = os.path.join(dbPath, u'db.pkl')

    def read(self):
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
        self._path = path
        self._mtime = self._path and os.stat(path).st_mtime or None
        self._parent = parent
        self._children = list()
        self.metadata = dict()
        if parent is not None:
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
                try:
                    value = self.metadata[k]
                except KeyError:
                    self.metadata[k] = value
                else:
                    if value != v:
                        self.metadata[k] = u"<multiple_values>"

    def flush(self):
        """@todo: Docstring for flush """
        for child in self._children:
            child.flush()

    def _fclear(self, fnd):
        newpath = os.path.join(self._parent._path, self.fn_encode(fnd))
        if self._path and self._path != newpath:
            newmtime = os.stat(newpath).st_mtime
            if self._mtime == newmtime:
                if isinstance(self, TrackNode):
                    os.remove(self._path)
                else:
                    os.remove(os.path.join(self._path, u'.meta'))
                try:
                    os.rmdir(self._path)
                except OSError:
                    pass
            self._mtime = newmtime
        self._path = newpath

    def _fsave(self, meta):
        if isinstance(self, TrackNode):
            f = open(self._path, u'w')
        else:
            try:
                os.mkdir(self._path)
            except:
                pass
            f = open(os.path.join(self._path, u'.meta'), u'w')
        f.write(json.dumps(meta, separators=(',', ':')))
        f.close()

    def updateHeaders(self):
        _Node.headers |= set(self.metadata.keys())
        for child in self._children:
            _Node.headers |= set(child.metadata.keys())

    def canFetchMore(self):
        """Indicates if there is still some data to read from
        persistent storage.

        :returns: True or False.
        """
        return bool(self._data)

    def fetch(self):
        """Fetches next chunk of data from presistent storage
        and wraps it into appropriate Node type.

        @see: _Node.canFetchMore

        @note: Usually reimplemented in specific type Nodes.
        """
        ArtistNode(path=self._data.pop(), parent=self)

    def addChild(self, child):
        self._children.append(child)

    def removeChild(self, child):
        self._children.remove(child)

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
        self.adr = {u'__a__': True, u'__d__': True, u'__r__': True}
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
            self.updateHeaders()
        else:
            self.metadata = dict()

    def update(self, meta=None):
        """@todo: Docstring for update

        :meta: @todo
        :returns: @todo

        """
        self.updateADR()
        super(ArtistNode, self).update(meta)

    def flush(self):
        """@todo: Docstring for flush
        :returns: @todo

        """
        self._fclear(self.metadata[u'artist'])
        metadata = self.metadata.copy()
        del metadata[u'artist']
        self._fsave(metadata)
        super(ArtistNode, self).flush()

    def updateADR(self):
        """@todo: Docstring for updateADR """
        self.adr = {u'__a__': True, u'__d__': True, u'__r__': True}
        for child in self._children:
            for adr in [u'__a__', u'__d__', u'__r__']:
                if not child.adr[adr]:
                    self.adr[adr] = False

    def fetch(self):
        AlbumNode(self._data.pop(), self)

    def fn_encode(self, fn):
        return urlsafe_b64encode(fn.encode(u'utf-8'))

    def fn_decode(self, fn):
        return unicode(
            urlsafe_b64decode(os.path.basename(fn.encode(u'utf-8')))
        )


class AlbumNode(_Node):
    """Album node."""

    def __init__(self, path=None, parent=None):
        """@todo: Docstring for __init__

        :path: @todo
        :parent: @todo
        """
        super(AlbumNode, self).__init__(path, parent)
        self.adr = {u'__a__': False, u'__d__': False, u'__r__': False}
        if path:
            path = os.path.join(self._path, u'.meta')
            self.metadata = json.loads(open(path, 'r').read())
            (self.metadata[u"year"],
            self.metadata[u"album"]) = self.fn_decode(self._path)
            for adr in [u"__a__", u"__d__", u"__r__"]:
                try:
                    _ = self.metadata[adr]
                    if len(_) > 1:
                        self.metadata[adr] = _[1]
                    else:
                        del self.metadata[adr]
                    self.adr[adr] = _[0]
                    if not self.adr[adr]:
                        self.parent().adr[adr] = False
                except KeyError:
                    pass
            self.updateHeaders()
        else:
            self.metadata = dict()

    def update(self, meta=None):
        """@todo: Docstring for update

        :meta: @todo
        :returns: @todo

        """
        if meta:
            for adr in [u"__a__", u"__d__", u"__r__"]:
                try:
                    _ = meta[adr]
                    self.adr[adr] = _[0]
                    if len(_) > 1:
                        meta[adr] = _[1]
                    else:
                        del meta[adr]
                except KeyError:
                    pass
        super(AlbumNode, self).update(meta)

    def flush(self):
        """@todo: Docstring for flush
        :returns: @todo

        """
        self._fclear((self.metadata[u'year'], self.metadata[u'album']))
        metadata = self.metadata.copy()
        del metadata[u'year']
        del metadata[u'album']
        for adr in [u'__a__', u'__d__', u'__r__']:
            try:
                _ = metadata[adr]
                metadata[adr] = [self.adr[adr], _]
            except KeyError:
                metadata[adr] = [self.adr[adr]]
        self._fsave(metadata)
        super(AlbumNode, self).flush()

    def fetch(self):
        TrackNode(self._data.pop(), self)

    def fn_encode(self, fn):
        fn1, fn2 = fn
        return urlsafe_b64encode("{0}.{1}".format(fn1, fn2))

    def fn_decode(self, fn):
        fn = unicode(
            urlsafe_b64decode(os.path.basename(fn.encode(u'utf-8'))
        )).split(u'.')
        return (fn[0], fn[1])


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
            self.updateHeaders()
        else:
            self.metadata = dict()

    def flush(self):
        """@todo: Docstring for flush
        :returns: @todo

        """
        self._fclear((self.metadata[u'tracknumber'], self.metadata[u'title']))
        metadata = self.metadata.copy()
        del metadata[u'tracknumber']
        del metadata[u'title']
        self._fsave(metadata)

    def fn_encode(self, fn):
        fn1, fn2 = fn
        return urlsafe_b64encode("{0}.{1}".format(fn1, fn2))

    def fn_decode(self, fn):
        fn = unicode(
            urlsafe_b64decode(os.path.basename(fn.encode(u'utf-8'))
        )).split(u'.')
        return (fn[0], fn[1])


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
        if parent.column() > 0:
            return 0
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self._rootNode
        return node.childCount()

    def columnCount(self, parent):
        """Reimplemented from QAbstractItemModel.columnCount."""
        if parent.column() > 0:
            return 0
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
            while child.canFetchMore():
                child.fetch()
            count = child.childCount()
            for j in xrange(count):
                child_ = child.child(j)
                while child_.canFetchMore():
                    child_.fetch()
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
                header = _Node.header(index.column())
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
        if not parent or parent == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), parent.column(), parent)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractItemModel.index."""
        if row < 0 or column < 0 or parent.column() > 0:
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
        """Inserts or updates an entry in the database.

        When :index: is None metadata should also tell what to update, e.g.:
        (u'track', {}) will pass the metadata dict to the track,
        (u'album', {}) will pass the metadata dict to the album,
        (u'artist', {}) will pass the metadata dict to the artist.

        For specified :index:, it's derived from it.

        It's created that way to allow passing ADR directly to the albums,
        without messing with it's tracks.

        @note: For convenience, it's assumed that passing a single dict is
        meant to be passed to the track.

        :index: Persistent index pointing at entry to update. None for insert.
        :meta: Metadata to put into the database.
        :returns: New persistent index pointing at inserted/updated entry.
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
        if isinstance(meta, tuple):
            place, meta = meta
        else:
            place = None
        if not index:
            # TODO: deal with adr
            try:
                artist = find_artist(meta[u'artist'])
            except KeyError:
                artist = find_artist(u'unknown')
            artistPosition = self._rootNode.childCount()
            if not artist:
                self.beginInsertRows(
                    QtCore.QModelIndex(), artistPosition, artistPosition
                )
                artist = ArtistNode(parent=self._rootNode)
                self.endInsertRows()
            else:
                artistPosition -= 1
            index = self.index(artistPosition, 0)
            if not place or place == u'album' or place == u'track':
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
                album = find_album(index, artist, m_album, m_year)
                albumPosition = artist.childCount()
                if not album:
                    self.beginInsertRows(
                        index, albumPosition, albumPosition
                    )
                    album = AlbumNode(parent=artist)
                    self.endInsertRows()
                else:
                    albumPosition -= 1
                index = self.index(albumPosition, 0, index)
                if not place or place == u'track':
                    trackPosition = album.childCount()
                    self.beginInsertRows(
                        index, trackPosition, trackPosition
                    )
                    track = TrackNode(parent=album)
                    self.endInsertRows()
                    track.update(meta)
                    album.update()
                    artist.update()
                    self._rootNode.updateHeaders()
                    index = self.index(trackPosition, 0, index)
                else:
                    album.update(meta)
                    artist.update()
                    self._rootNode.updateHeaders()
            else:
                artist.update(meta)
                self._rootNode.updateHeaders()
        else:
            index = self.index(index.row(), index.column(), index.parent())
            track = index.internalPointer()
            track.update(meta)
            album = track.parent()
            album.update()
            artist = album.parent()
            artist.update()
        return QtCore.QPersistentModelIndex(index)

    def remove(self, index):
        """Removes specified track's index and it's parents, as needed.

        :index: Track's index.
        """
        index = self.index(index.row(), index.column(), index.parent())
        albumIndex = self.parent(index)
        album = albumIndex.internalPointer()
        album.removeChild(index.internalPointer())
        if not album.childCount():
            artistIndex = self.parent(albumIndex)
            artist = artistIndex.internalPointer()
            if album.adr[u'__a__'] or album.adr[u'__r__']:
                album.adr[u'__d__'] = False
                album.update()
            else:
                artist.removeChild(album)
                if not artist.childCount():
                    self._rootNode.removeChild(artist)
                else:
                    artist.update()
            artist.updateADR()
        else:
            album.update()
        self._rootNode.updateHeaders()

    def flush(self):
        """@todo: Docstring for flush """
        # TODO: remove old files (needs adjusts in remove and upsert methods)
        self._rootNode.flush()


class Model(QtGui.QAbstractProxyModel):
    """Docstring for Model """

    def __init__(self, sourceModel, parent=None):
        """@todo: to be defined """
        super(Model, self).__init__(parent)
        self._mapper = list()
        self._rmapper = dict()
        self._selection = list()
        self.setSourceModel(sourceModel)
        self.sourceModel = sourceModel

    def insertRows(self, parent):
        """Inserts new rows based on current _selection.

        @note: To actually add data to the model use BaseModel.upsert.

        :parent: Index whose children should be inserted.
        """
        model = self.sourceModel
        count = model.rowCount(parent)
        count_ = self.rowCount()
        end = count_ + count - 1
        self.beginInsertRows(QtCore.QModelIndex(), count_, end)
        for i in xrange(count):
            child = model.index(i, 0, parent)
            pindex = QtCore.QPersistentModelIndex(child)
            self._mapper.append(pindex)
            self._rmapper[pindex] = len(self._mapper) - 1
        self.endInsertRows()

    def removeRows(self, parent):
        """Removes rows previously set by Model.insertRows if their :parent:
        is no longer in _selection.

        @note: To actually remove data from the model use BaseModel.remove.

        :parent: Index whose children should be removed.
        """
        model = self.sourceModel
        count = model.rowCount(parent)
        child = self.mapFromSource(model.index(0, 0, parent))
        row = child.row()
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count)
        for i in xrange(count):
            child = model.index(i, 0, parent)
            pindex = QtCore.QPersistentModelIndex(child)
            self._mapper.remove(pindex)
            del self._rmapper[pindex]
        for k, v in self._rmapper.iteritems():
            if v > row:
                self._rmapper[k] -= count
        self.endRemoveRows()

    def setSelection(self, selected, deselected):
        """Sets new visible items, based on parent view's selections.

        :selected: Parent view's newly selected items.
        :deselected: Parent view's deselected items.
        """
        model = self.sourceModel
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

        It returns True for top-level, because otherwise the model would
        ignore AlbumNodes, as they're root's children.

        :returns: True for top-level Node, False otherwise.
        """
        if not parent.isValid():
            return True
        return False

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractProxyModel.index."""
        if not self.hasIndex(row, column, parent) or parent.column() > 0:
            return QtCore.QModelIndex()
        source = QtCore.QModelIndex(self._mapper[row])
        return self.mapFromSource(
            self.sourceModel.index(source.row(), column, source.parent())
        )

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractProxyModel.data."""
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            node = index.internalPointer()
            try:
                header = _Node.header(index.column())
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
        source0 = self.sourceModel.createIndex(
            source.row(), 0, source.internalPointer()
        )
        i = self._rmapper[QtCore.QPersistentModelIndex(source0)]
        return self.createIndex(i, source.column(), source.internalPointer())

    def mapToSource(self, proxy):
        """Reimplemented from QAbstractProxyModel.mapToSource.

        Uses _mapper object created with Model.flatten method to map
        flat proxy model back to tree-like source one.
        """
        if not proxy.isValid():
            return QtCore.QModelIndex()
        sourceIndex = self._mapper[proxy.row()]
        return self.sourceModel.createIndex(
            sourceIndex.row(), proxy.column(), proxy.internalPointer()
        )


class AlbumsModel(Model):
    """Docstring for AlbumsModel """


class TracksModel(Model):
    """Docstring for TracksModel """


class DB(QtCore.QThread):
    """Local filesystem watcher and DB holder/updater."""
    __settings = QtCore.QSettings(u'gayeogi', u'db')
    finished = QtCore.pyqtSignal()

    def __init__(self, path):
        """@todo: to be defined """
        super(DB, self).__init__()
        self.artists = BaseModel(path)
        self.path = os.path.join(os.path.dirname(path), u'index.db')
        self.albums = AlbumsModel(self.artists)
        self.tracks = TracksModel(self.artists)
        self.index = None

    def save(self):
        """@todo: Docstring for save """
        cPickle.dump(self.index, open(self.path, u'wb'), -1)
        self.artists.flush()

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
        if ignores is None:
            ignores = list()
        if self.index is None:
            if os.path.exists(self.path):
                self.index = cPickle.load(open(self.path, u'rb'))
            else:
                self.index = dict()
        for path, index in self.index.copy().iteritems():
            if not os.path.exists(path):
                self.artists.remove(index)
                del self.index[path]
        for directory, enabled in directories:
            if enabled:
                for root, _, filenames in os.walk(directory):
                    if not self.isIgnored(root, ignores):
                        for filename in filenames:
                            path = os.path.join(root, filename)
                            if not self.isIgnored(path, ignores):
                                tag = Tagger(path).readAll()
                                if tag is not None:
                                    self.index[path] = self.upsert(
                                        self.getIndex(path)
                                    )(tag)
        self.finished.emit()
