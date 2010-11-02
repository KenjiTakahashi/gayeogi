# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import QThread
from mutagen.id3 import ID3
from mutagen.flac import FLAC

class Filesystem(QThread):
    def __init__(self):
        QThread.__init__(self)
    def appendToLibrary(self, artist, album, date, title, tracknumber, library):
        artistSwitch = False
        albumSwitch = False
        trackSwitch = False
        for lib in library:
            if lib[u'artist'] == artist:
                artistSwitch = True
                for rAlbum in lib[u'albums']:
                    if rAlbum[u'album'] == album:
                        albumSwitch = True
                        for rTitle in rAlbum[u'tracks']:
                            if rTitle[u'title'] == title:
                                trackSwitch = True
                                break
                        if not trackSwitch:
                            rAlbum[u'tracks'].append({
                                u'title': title,
                                u'tracknumber': tracknumber
                                })
                        break
                if not albumSwitch:
                    lib[u'albums'].append({
                        u'album': album,
                        u'date': date,
                        u'tracks': [{
                            u'title': title,
                            u'tracknumber': tracknumber
                            }]
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
                        u'tracknumber': tracknumber
                        }]
                    }]
                })
    def appendToPaths(self, path, paths):
        if not self.__exists(path, paths.keys()):
            paths[path] = {u'modified': os.stat(path).st_mtime}
        else:
            for k in paths.keys():
                prefix = os.path.commonprefix([path, k])
                if prefix == k:
                    self.appendToPaths(path, paths[prefix])
    def create(self, directory):
        exceptions = []
        library = []
        paths = {}
        self.__traverse(directory, library, paths)
        return (library, paths)
    def update(self, library, paths):
        for k, v in paths.iteritems():
            if os.stat(k).st_mtime != v[u'modified']:
                if v.keys() == [u'modified']:
                    self.__traverse(k, library, paths)
                else:
                    k[u'modified'] = os.stat(k).st_mtime #?
                    self.update(library, v)
    def __traverse(self, directory, library, paths):
        exceptions = []
        def __append(f, path):
            try:
                self.appendToLibrary(
                        f[u'artist'][0],
                        f[u'album'][0],
                        f[u'date'][0],
                        f[u'title'][0],
                        f[u'tracknumber'][0],
                        library
                        )
            except KeyError:
                exceptions.append(path)
        for root, _, filenames in os.walk(directory):
            self.appendToPaths(root, paths)
            for filename in filenames:
                ext = os.path.splitext(filename)[1]
                if ext == u'.mp3':
                    path = os.path.join(root, filename)
                    f = ID3(path)
                    try:
                        self.appendToLibrary(
                                f[u'TPE1'].text[0],
                                f[u'TALB'].text[0],
                                f[u'TDRC'].text[0],
                                f[u'TIT2'].text[0],
                                f[u'TRCK'].text[0],
                                library
                                )
                    except KeyError:
                        exceptions.append(path)
                else:
                    if ext == u'.flac':
                        path = os.path.join(root, filename)
                        f = FLAC(path)
                        __append(f, path)
    def __exists(self, value, keys):
        for key in keys:
            prefix = os.path.commonprefix([value, key])
            if prefix in keys:
                return True
        return False
