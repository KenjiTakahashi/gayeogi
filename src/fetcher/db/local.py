# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import QThread, pyqtSignal
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.musepack import Musepack
from mutagen.wavpack import WavPack
from mutagen import File

class Filesystem(QThread):
    created = pyqtSignal(tuple)
    updated = pyqtSignal()
    stepped = pyqtSignal(unicode)
    def __init__(self):
        QThread.__init__(self)
        self.directory = None
        self.library = []
        self.paths = []
        self.doUpdate = False
        self.exceptions = []
    def appendToLibrary(self,
            artist,
            album,
            date,
            title,
            tracknumber,
            library,
            path,
            filename):
        artistSwitch = False
        albumSwitch = False
        trackSwitch = False
        for lib in library:
            if lib[u'artist'] == artist:
                artistSwitch = True
                for rAlbum in lib[u'albums']:
                    if rAlbum[u'album'] == album:
                        albumSwitch = True
                        rAlbum[u'digital'] = True
                        for rTitle in rAlbum[u'tracks']:
                            if rTitle[u'title'] == title:
                                trackSwitch = True
                            elif not os.path.exists(rTitle[u'path']):
                                del rAlbum[u'tracks']\
                                        [rAlbum[u'tracks'].index(rTitle)]
                        if not trackSwitch:
                            rAlbum[u'tracks'].append({
                                u'title': title,
                                u'tracknumber': tracknumber,
                                u'path': filename
                                })
                        break
                if not albumSwitch:
                    lib[u'albums'].append({
                        u'album': album,
                        u'date': date,
                        u'tracks': [{
                            u'title': title,
                            u'tracknumber': tracknumber,
                            u'path': filename
                            }],
                        u'path': path,
                        u'digital': True,
                        u'analog': False,
                        u'remote': False
                        })
                break
        if not artistSwitch:
            library.append({
                u'artist': artist,
                u'url':None,
                u'albums': [{
                    u'album': album,
                    u'date': date,
                    u'tracks': [{
                        u'title': title,
                        u'tracknumber': tracknumber,
                        u'path': filename
                        }],
                    u'path': path,
                    u'digital': True,
                    u'analog': False,
                    u'remote': False
                    }]
                })
    def appendToPaths(self, path, paths):
        paths.append((path, os.stat(path).st_mtime))
#        if not self.__exists(path, paths.keys()):
#            paths[path] = {u'modified': os.stat(path).st_mtime}
#        else:
#            for k in paths.keys():
#                prefix = os.path.commonprefix([path, k])
#                if prefix == k:
#                    self.appendToPaths(path, paths[prefix])
    def attemptToRemove(self, library, path):
        for lib in library:
            for album in lib[u'albums']:
                if album[u'path'] == path:
                    if album[u'analog'] == False and album[u'remote'] == False:
                        del lib[u'albums'][lib[u'albums'].index(album)]
            if not lib[u'albums']:
                del library[library.index(lib)]
                #can i break here? dunno now...
    def create(self, directory):
        exceptions = []
        library = []
        paths = []
        self.__traverse(directory, library, paths)
        return (library, paths)
    def update(self, library, paths):
        for (path, time) in paths:
            if os.path.exists(path):
                if os.stat(path).st_mtime != time:
                    self.__traverse(path, library, paths)
            else:
                self.attemptToRemove(library, path)
#        for k, v in paths.iteritems():
#            if os.path.exists(k):
#                if os.stat(k).st_mtime != v[u'modified']:
#                    if v.keys() == [u'modified']:
#                        self.__traverse(k, library, paths)
#                    else:
#                        v[u'modified'] = os.stat(k).st_mtime
#                        self.update(library, v)
#            else:
#                self.attemptToRemove(library, k)
    def __traverse(self, directory, library, paths):
        exceptions = []
        def __append(f, path, root):
            try:
                self.appendToLibrary(
                        f[u'artist'][0],
                        f[u'album'][0],
                        f[u'date'][0],
                        f[u'title'][0],
                        f[u'tracknumber'][0],
                        library,
                        root,
                        path)
            except KeyError:
                exceptions.append(path)
        for root, _, filenames in os.walk(directory):
            if root not in paths or\
                    os.stat(root).st_mtime != paths[paths.index(paths)][1]:
                self.appendToPaths(root, paths)
                for filename in filenames:
                    ext = os.path.splitext(filename)[1]
                    if ext == u'.mp3':
                        path = os.path.join(root, filename)
                        self.stepped.emit(path)
                        f = ID3(path)
                        try:
                            self.appendToLibrary(
                                    f[u'TPE1'].text[0],
                                    f[u'TALB'].text[0],
                                    f[u'TDRC'].text[0],
                                    f[u'TIT2'].text[0],
                                    f[u'TRCK'].text[0],
                                    library,
                                    root,
                                    path)
                        except KeyError:
                            exceptions.append(path)
                    else:
                        path = os.path.join(root, filename)
                        if ext == u'.flac':
                            f = FLAC(path)
                        elif ext == u'.asf':
                            f = ASF(path)
                        elif ext == u'.wv':
                            f = WavPack(path)
                        elif ext == u'.mpc' or ext == u'.mpp' or ext == u'.mp+':
                            f = Musepack(path)
                        elif ext == u'.ogg' or ext == u'.ape': # different .ogg and .ape files
                            f = File(path)
                        else:
                            f = None
                        if f:
                            self.stepped.emit(path)
                            __append(f, path, root)
    def __exists(self, value, keys):
        for key in keys:
            prefix = os.path.commonprefix([value, key])
            if prefix in keys:
                return True
        return False
    def setDirectory(self, directory):
        self.directory = directory
    def setArgs(self, library, paths, update = False):
        self.library = library
        self.paths = paths
        self.doUpdate = update
    def run(self):
        self.exceptions.clear()
        if self.doUpdate:
            self.update(self.library, self.paths)
            self.updated.emit()
        else:
            result = self.create(self.directory)
            self.created.emit(result)
