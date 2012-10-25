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
_settings = QtCore.QSettings(u'gayeogi', u'Databases')


class _Node(QtCore.QObject):
    headers = set()
    staticHeaders = [u'artist', u'album']
    stats = [{u'__a__': 0, u'__d__': 0, u'__r__': 0} for _ in xrange(2)]
    artistsStatisticsChanged = QtCore.pyqtSignal(int, int, int)
    albumsStatisticsChanged = QtCore.pyqtSignal(int, int, int)

    def __init__(self, path, parent=None):
        super(_Node, self).__init__()
        self._path = path
        self._mtime = None
        if self._path:
            metapath = os.path.join(self._path, u'.meta')
            if os.path.exists(metapath):
                self._mtime = os.stat(metapath).st_mtime
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
            metapath = os.path.join(self._path, u'.meta')
            newmtime = os.stat(metapath).st_mtime
            if self._mtime == newmtime:
                os.remove(metapath)
                try:
                    os.rmdir(self._path)
                except OSError:
                    pass
        self._path = newpath

    def _fsave(self, meta):
        try:
            os.mkdir(self._path)
        except:
            pass
        path = os.path.join(self._path, u'.meta')
        open(path, u'w').write(json.dumps(meta, separators=(',', ':')))
        self._mtime = os.stat(path).st_mtime

    def updateHeaders(self):
        _Node.headers |= set(self.metadata.keys())
        for child in self._children:
            _Node.headers |= set(child.metadata.keys())
        _Node.headers -= set(_Node.staticHeaders)

    @staticmethod
    def header(section):
        """@todo: Docstring for header

        :section: @todo
        :returns: @todo
        """
        return list(_Node.headers)[section]

    @staticmethod
    def staticHeader(section):
        """@todo: Docstring for staticHeader

        :section: @todo
        :returns: @todo
        """
        try:
            return _Node.staticHeaders[section]
        except IndexError:
            return None

    def updateStatistics(self, artists, adr, value):
        """Updates global statistics count and emits appropriate singal
        for the views.

        @note: It makes sure that this method is always called on _Node
        instance, not any of the subclasses.

        :artists: True for artists stats, False for albums stats.
        :adr: __a/d/r__ key value.
        :value: -1/+1.
        """
        if not type(self) == _Node:
            self._parent.updateStatistics(artists, adr, value)
        else:
            if artists:
                _Node.stats[0][adr] += value
                if _Node.stats[0][adr] < 0:
                    _Node.stats[0][adr] = 0
                stats = _Node.stats[0]
                self.artistsStatisticsChanged.emit(
                    stats[u'__a__'], stats[u'__d__'], stats[u'__r__']
                )
            else:
                _Node.stats[1][adr] += value
                if _Node.stats[1][adr] < 0:
                    _Node.stats[1][adr] = 0
                stats = _Node.stats[1]
                self.albumsStatisticsChanged.emit(
                    stats[u'__a__'], stats[u'__d__'], stats[u'__r__']
                )

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
        while self._data:
            ArtistNode(path=self._data.pop(), parent=self).fetch()

    def addChild(self, child):
        self._children.append(child)

    def removeChild(self, child):
        self._children.remove(child)

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
        self.images = [None, None]
        self.urls = list()
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
        try:
            _ = metadata[u'__urls__']
            metadata[u'__urls__'] = [self.urls, _]
        except KeyError:
            metadata[u'__urls__'] = [self.urls]
        self._fsave(metadata)
        super(ArtistNode, self).flush()

    def updateADR(self):
        """@todo: Docstring for updateADR """
        oldadr = self.adr
        self.adr = {u'__a__': True, u'__d__': True, u'__r__': True}
        if not self._children:
            self.adr = {u'__a__': False, u'__d__': False, u'__r__': False}
        for child in self._children:
            for adr in [u'__a__', u'__d__', u'__r__']:
                if not child.adr[adr]:
                    self.adr[adr] = False
        for k, v1 in self.adr.iteritems():
            v2 = oldadr[k]
            if v1 != v2:
                if v1:
                    self.updateStatistics(True, k, 1)
                else:
                    self.updateStatistics(True, k, -1)

    def fetch(self):
        while self._data:
            AlbumNode(self._data.pop(), self).fetch()

    def fn_encode(self, fn):
        return urlsafe_b64encode(fn.encode(u'utf-8'))

    def fn_decode(self, fn):
        return unicode(
            urlsafe_b64decode(os.path.basename(fn.encode(u'utf-8')))
        )


class AlbumNode(_Node):
    """Album node."""

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, value):
        self._images[0] = value
        if self._images[0] is not None:
            self._parent.images[0] = self._images[0][:]

    def __init__(self, path=None, parent=None):
        """Creates a new Album Node.

        If :path: is specified it fetches metadata from persistent storage
        and prefetches informations about Track Nodes. Otherwise it creates
        an empty Node meant to be filled with AlbumNode.update method.

        Also updates adr information for it's parent Node.

        :path: Encoded filesystem path.
        :parent: Parent Node.
        """
        super(AlbumNode, self).__init__(path, parent)
        self.adr = {u'__a__': False, u'__d__': False, u'__r__': False}
        self._images = [None, None]
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
                    if self.adr[adr]:
                        self.updateStatistics(False, adr, 1)
                    if not self.adr[adr]:
                        self._parent.adr[adr] = False
                except KeyError:
                    pass
            for adr in [u'__a__', u'__d__', u'__r__']:
                if self._parent.adr[adr]:
                    self._parent.updateStatistics(True, adr, 1)
            self.updateHeaders()
        else:
            self.metadata = dict()

    def update(self, meta=None):
        """@todo: Docstring for update

        :meta: @todo
        """
        if meta:
            for adr in [u"__a__", u"__d__", u"__r__"]:
                try:
                    _ = meta[adr]
                    if self.adr[adr] != _[0]:
                        if not self.adr[adr]:
                            self.updateStatistics(False, adr, 1)
                        else:
                            self.updateStatistics(False, adr, -1)
                    self.adr[adr] = _[0]
                    if len(_) > 1:
                        meta[adr] = _[1]
                    else:
                        del meta[adr]
                except KeyError:
                    pass
            if self._images[0] is not None:
                self._parent.images[0] = self._images[0][:]
        super(AlbumNode, self).update(meta)

    def flush(self):
        """@todo: Docstring for flush."""
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
        while self._data:
            TrackNode(self._data.pop(), self).fetch()

    def fn_encode(self, fn):
        fn1, fn2 = fn
        return urlsafe_b64encode("{0}.{1}".format(fn1, fn2))

    def fn_decode(self, fn):
        fn = unicode(
            urlsafe_b64decode(os.path.basename(fn.encode(u'utf-8')))
        ).split(u'.')
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
            path = os.path.join(self._path, u'.meta')
            self.metadata = json.loads(open(path, 'r').read())
            (self.metadata[u"tracknumber"],
             self.metadata[u"title"]) = self.fn_decode(self._path)
            _ = self.metadata[u'__filename__']
            if len(_) > 1:
                self.metadata[u'__filename__'] = _[1]
            else:
                del self.metadata[u'__filename__']
            self.filename = _[0]
            self._parent.images = os.path.dirname(self.filename)
            self.updateHeaders()
        else:
            self.metadata = dict()

    def update(self, meta=None):
        """@todo: Docstring for update

        :meta: @todo
        """
        if meta:
            try:
                _ = meta[u'__filename__']
                if len(_) > 1:
                    meta[u'__filename__'] = _[1]
                else:
                    del meta[u'__filename__']
                self.filename = _[0]
                self._parent.images = os.path.dirname(self.filename)
            except KeyError:
                pass
        super(TrackNode, self).update(meta)

    def flush(self):
        """@todo: Docstring for flush."""
        self._fclear((self.metadata[u'tracknumber'], self.metadata[u'title']))
        metadata = self.metadata.copy()
        del metadata[u'tracknumber']
        del metadata[u'title']
        try:
            _ = metadata[u'__filename__']
            metadata[u'__filename__'] = [self.filename, _]
        except KeyError:
            metadata[u'__filename__'] = [self.filename]
        self._fsave(metadata)

    def fn_encode(self, fn):
        fn1, fn2 = fn
        return urlsafe_b64encode("{0}.{1}".format(fn1, fn2))

    def fn_decode(self, fn):
        fn = unicode(
            urlsafe_b64decode(os.path.basename(fn.encode(u'utf-8')))
        ).split(u'.')
        return (fn[0], fn[1])


class BaseModel(QtCore.QAbstractItemModel):
    """General model class, meant to implement basic funcionality,
    especially inserting, updating and removing items.

    Used directly by Artists view and as a source by Albums/Tracks views.
    """

    artistsStatisticsChanged = QtCore.pyqtSignal(int, int, int)
    albumsStatisticsChanged = QtCore.pyqtSignal(int, int, int)

    def __init__(self, dbpath, parent=None):
        """Constructs new BaseModel instance.

        :dbPath: Path to the database.
        :parent: Parent object.
        """
        super(BaseModel, self).__init__(parent)
        self._rootNode = _Node(dbpath)
        self._rootNode.artistsStatisticsChanged.connect(
            self.artistsStatisticsChanged
        )
        self._rootNode.albumsStatisticsChanged.connect(
            self.albumsStatisticsChanged
        )

    def hasChildren(self, parent):
        """Reimplemented from QAbstractItemModel.hasChildren.

        :returns: True if :parent: is a top-level node, False otherwise.
        """
        if not parent.isValid():
            return True
        return False

    def rowCount(self, parent=QtCore.QModelIndex()):
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
        length = len(_Node.headers)
        if length:
            return length + len(_Node.staticHeaders)
        return 0

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

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractItemModel.data."""
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            column = index.column()
            try:
                header = _Node.staticHeader(column)
                if header is None:
                    header = _Node.header(column - len(_Node.staticHeaders))
                return node.metadata[header]
            except KeyError:
                return ""
        elif role == 123:  # a
            return node.adr[u'__a__']
        elif role == 234:  # d
            return node.adr[u'__d__']
        elif role == 345:  # r
            return node.adr[u'__r__']
        elif role == 666:
            try:
                images = node.images
                if _settings.value('image/precedence', 2).toBool():
                    k = index.column() and u'image/album' or u'image/artist'
                    enabled = _settings.value(
                        u'{0}/enabled'.format(k), 2
                    ).toBool()
                    names = _settings.value(k, [u'Folder.jpg']).toPyObject()
                    if enabled and names and images[0] is not None:
                        for name in names:
                            img = QtGui.QPixmap(os.path.join(
                                unicode(images[0]), unicode(name)
                            ))
                            if not img.isNull():
                                return img.scaledToHeight(80)
                return None  # try internal images
            except AttributeError:
                return None

    def setData(self, index, value):
        """@todo: Docstring for setData

        :index: @todo
        :value: @todo
        :returns: @todo
        """
        self.upsert(index, (u'album', {u'__a__': [value]}))
        return True

    def headerData(
        self, section,
        o=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole
    ):
        """Reimplemented from QAbstractItemModel.headerData."""
        if role == QtCore.Qt.DisplayRole and o == QtCore.Qt.Horizontal:
            header = _Node.staticHeader(section)
            if header is None:
                header = _Node.header(section - len(_Node.staticHeaders))
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

        For specified :index::
            if :meta: is a tuple, as described above, it will update matching
            children[*] of :index:.
            if :meta: is a dict it will pass the specified meta to :index:.

        [*] That also (possibly) counts grand children.

        It's created that way to allow passing ADR to the albums using artist's
        index and without messing with it's tracks.

        @note: For convenience, it's assumed that passing a single dict is
        equivalent to (u'track', {}).

        :index: Persistent index pointing at entry to update. None for insert.
        :meta: Metadata to put into the database.
        :returns: New persistent index pointing at inserted/updated entry.
        """
        def find(node, values):
            for child in node.children():
                truth = True
                for k, v in values.iteritems():
                    if child.metadata[k] != v:
                        truth = False
                        break
                if truth:
                    return child
            return None
        if isinstance(meta, tuple):
            place, meta = meta
        else:
            place = None
        self.layoutAboutToBeChanged.emit()
        if not index:
            def _update_(node, values, Class):
                newNode = find(node, values)
                position = node.childCount()
                if not newNode:
                    self.beginInsertRows(
                        QtCore.QModelIndex(), position, position
                    )
                    newNode = Class(parent=node)
                    self.endInsertRows()
                else:
                    position -= 1
                return (newNode, position)
            artist, artistPosition = _update_(self._rootNode, {
                u'artist': meta.get(u'artist') or u'unknown'
            }, ArtistNode)
            index = self.index(artistPosition, 0)
            if not place or place == u'album' or place == u'track':
                album, albumPosition = _update_(artist, {
                    u'album': meta.get(u'album') or u'unknown',
                    u'year': meta.get(u'year') or u'0000'
                }, AlbumNode)
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
                    index = self.index(trackPosition, 0, index)
                else:
                    album.update(meta)
                    artist.update()
            else:
                artist.update(meta)
        else:
            def _update(item, node, parent):
                if not item:
                    item = node(parent=parent)
                item.update(meta)
                self.remove(item)
                parent.update()
            index = self.index(index.row(), index.column(), index.parent())
            pointer = index.internalPointer()
            if isinstance(pointer, ArtistNode):
                if place == u'album':
                    album = find(pointer, {
                        u'album': meta[u'album'],
                        u'year': meta[u'year']
                    })
                    _update(album, AlbumNode, pointer)
                elif place == u'track':
                    for album in pointer.children():
                        track = find(album, {
                            u'title': meta[u'title'],
                            u'tracknumber': meta[u'tracknumber']
                        })
                        _update(track, TrackNode, album)
                    pointer.update()
                else:
                    pointer.update(meta)
            elif isinstance(pointer, AlbumNode):
                if place == u'track':
                    track = find(pointer, {
                        u'title': meta[u'title'],
                        u'tracknumber': meta[u'tracknumber']
                    })
                    _update(track, TrackNode, pointer)
                else:
                    pointer.update(meta)
                pointer.parent().update()
            else:
                if place == u'album':
                    pointer = pointer.parent()
                    pointer.update(meta)
                    pointer.parent().update()
                else:
                    pointer.update(meta)
                    album = pointer.parent()
                    album.update()
                    album.parent().update()
        self._rootNode.updateHeaders()
        self.layoutChanged.emit()
        #hlen = len(_Node.headers) - 1
        #self.beginMoveColumns(parent, 0, hlen, parent, hlen + 2)
        #self.endMoveColumns()
        return QtCore.QPersistentModelIndex(index)

    def remove(self, index):
        """Removes specified index and it's parents, if applicable.

        It is considered "secure", which means it will not remove album's
        index if it has tracks or a or d or r. Same applies to artists.

        @note: To erase adr state, use appropriate BaseModel.upsert call.
        @see: BaseModel.removeByFilename.

        :index: Index to remove. It can also be an internalPointer.
        """
        def _remove(item):
            parent = item.parent()
            parent.removeChild(pointer)
            parent.update()
            return parent
        if not isinstance(index, _Node):
            index = self.index(index.row(), index.column(), index.parent())
            pointer = index.internalPointer()
        else:
            pointer = index
        if isinstance(pointer, TrackNode):
            pointer = _remove(pointer)

        def _remove_(item):
            adr = item.adr
            parent = item.parent()
            if(not pointer.childCount()
               and not adr[u'__a__']
               and not adr[u'__d__']
               and not adr[u'__r__']):
                _remove(item)
            return parent
        if isinstance(pointer, AlbumNode):
            pointer = _remove_(pointer)
            pointer.updateADR()
        if isinstance(pointer, ArtistNode):
            _remove_(pointer)
        self._rootNode.updateHeaders()

    def removeByFilename(self, filename):
        """Removes Model entry pointing at :filename:.

        @see: BaseModel.remove.

        :filename: @todo
        """
        index = self._indexByFilename(filename)
        if index is not None:
            self.remove(index)

    def upsertByFilename(self, filename, meta):
        """@todo: Docstring for upsertByFilename

        @see: BaseModel.upsert.

        :filename: @todo
        :meta: @todo
        :returns: @todo
        """
        return self.upsert(self._indexByFilename(filename), meta)

    def _indexByFilename(self, filename):
        """@todo: Docstring for _indexByFilename

        :filename: @todo
        :returns: @todo
        """
        def startswith(row):
            pointer = row.internalPointer()
            try:
                return filename.startswith(pointer.filename)
            except AttributeError:
                fn = pointer.images[0]
                if fn is not None:
                    return filename.startswith(fn)
                return False
        empty = QtCore.QModelIndex()
        for rowi in xrange(self.rowCount(empty)):
            row = self.index(rowi, 0, empty)
            if startswith(row):
                for row2i in xrange(self.rowCount(row)):
                    row2 = self.index(row2i, 0, row)
                    if startswith(row2):
                        for row3i in xrange(self.rowCount(row2)):
                            row3 = self.index(row3i, 0, row2)
                            if row3.internalPointer().filename == filename:
                                return row3
        return None

    def flush(self):
        """Starts flushing db to permanent storage."""
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

        :returns: False.
        """
        return False

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Reimplemented from QAbstractProxyModel.index."""
        if parent.column() > 0:
            return QtCore.QModelIndex()
        source = self._mapper[row]
        return self.mapFromSource(
            self.sourceModel.index(source.row(), column, source.parent())
        )

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Reimplemented from QAbstractProxyModel.data."""
        return self.sourceModel.data(self.mapToSource(index), role)

    def setData(self, index, value, role):
        """Reimplemented from QAbstractProxyModel.setData."""
        return self.sourceModel.setData(self.mapToSource(index), value)

    def headerData(
        self, section,
        o=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole
    ):
        """Reimplemented from QAbstractProxyModel.headerData."""
        return self.sourceModel.headerData(section, o, role)

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
        """Reimplemented from QAbstractProxyModel.columnCount."""
        return self.sourceModel.columnCount(_)

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
    finished = QtCore.pyqtSignal()
    artistsStatisticsChanged = QtCore.pyqtSignal(int, int, int)
    albumsStatisticsChanged = QtCore.pyqtSignal(int, int, int)

    def __init__(self, path):
        """Creates new DB instance.

        @note: Although not explicitly stated, it is meant to be singleton.

        :path: Path to the root of database's storage.
        """
        super(DB, self).__init__()
        self.modified = False
        self.artists = BaseModel(path)
        self.path = os.path.join(os.path.dirname(path), u'index.db')
        self.albums = AlbumsModel(self.artists)
        self.tracks = TracksModel(self.artists)
        self.index = None
        self.artists.artistsStatisticsChanged.connect(
            self.artistsStatisticsChanged
        )
        self.artists.albumsStatisticsChanged.connect(
            self.albumsStatisticsChanged
        )

    def save(self):
        """Save database and index to permanent storage."""
        cPickle.dump(self.index, open(self.path, u'wb'), -1)
        self.artists.flush()
        self.modified = False

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

    def iterator(self):
        """Returns an iterator over the library, suitable for remote updating.

        Provides artist name for lookup, an upsert closure for that artist,
        artist's albums (for sensors) and existing urls to remote databases.

        :returns: An iterator yielding a tuple in form of
                  (artist name, albums, urls, upsert)
        """
        for i in xrange(self.artists.rowCount()):
            index = self.artists.index(i, 0)
            node = index.internalPointer()
            albums = list()
            for j in xrange(self.artists.rowCount(index)):
                _ = self.artists.index(j, 0, index)
                albumNode = _.internalPointer()
                metadata = albumNode.metadata
                albums.append((metadata[u'album'], metadata[u'year']))
            yield (
                node.metadata[u'artist'],
                node.urls,
                albums,
                self.upsert(index)
            )

    def upsert(self, index):
        """Creates an BaseModel.upsert closure.

        :index: Index or path at which to point the closure.
        :returns: A closure with metadata as parameter and :index: as internal.
        """
        def _upsert(meta):
            self.modified = True
            if isinstance(index, basestring):
                return self.artists.upsertByFilename(index, meta)
            else:
                return self.artists.upsert(index, meta)
        return _upsert

    def run(self):
        """@todo: Docstring for run"""
        directories = _settings.value(u'directories', []).toPyObject()
        ignores = _settings.value(u'ignores', []).toPyObject()
        if ignores is None:
            ignores = list()
        if self.index is None:
            if os.path.exists(self.path):
                self.index = cPickle.load(open(self.path, u'rb'))
            else:
                self.index = set()
        for path in self.index.copy():
            if not os.path.exists(path):
                self.artists.removeByFilename(path)
                self.index.remove(path)
        for directory, enabled in directories:
            if enabled:
                for root, _, filenames in os.walk(directory):
                    if not self.isIgnored(root, ignores):
                        for filename in filenames:
                            path = os.path.join(root, filename)
                            if not self.isIgnored(path, ignores):
                                tag = Tagger(path).readAll()
                                if tag is not None:
                                    index = self.upsert(path)(tag)
                                    self.upsert(index)(
                                        (u'album', {u'__d__': [True]})
                                    )
                                    self.index.add(path)
        self.finished.emit()
