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
    errors = pyqtSignal(unicode, unicode, list, unicode)
    def __init__(self):
        QThread.__init__(self)
        self.directory = None
        self.library = []
        self.paths = []
        self.doUpdate = False
        self.exceptions = []
        #moznaby zrobic tak: aktualizujemy badz usuwamy pliki bedace w paths
        #potem "przelatujemy" caly katalog w poszukiwaniu nowosci <- to bedzie wolne pewnie ;/
    def append(self, tags, library):
        artistSem = False
        albumSem = False
        trackSem = False
        for artist in library:
            if artist[u'artist'] == tags[u'artist']:
                artistSem = True
                for album in artist[u'albums']:
                    if album[u'album'] == tags[u'album']:
                        albumSem = True
                        for track in album[u'tracks']:
                            if track[u'title'] == tags[u'title']:
                                trackSem = True
                                break
                        if not trackSem:
                            album[u'tracks'].append({
                                u'title': tags[u'title'],
                                u'tracknumber': tags[u'tracknumber'],
                                u'path': tags[u'path'],
                                u'modified': os.stat(tags[u'path']).st_mtime
                                })
                        break
                if not albumSem:
                    artist[u'albums'].append({
                        u'album': tags[u'album'],
                        u'date': tags[u'date'],
                        u'tracks': [{
                            u'title': tags[u'title'],
                            u'tracknumber': tags[u'tracknumber'],
                            u'path': tags[u'path'],
                            u'modified': os.stat(tags[u'path']).st_mtime
                            }],
                        u'digital': True,
                        u'analog': False
                        })
                break
        if not artistSem:
            library.append({
                u'artist': tags[u'artist'],
                u'albums': [{
                    u'album': tags[u'album'],
                    u'date': tags[u'date'],
                    u'tracks': [{
                        u'title': tags[u'title'],
                        u'tracknumber': tags[u'tracknumber'],
                        u'path': tags[u'path'],
                        u'modified': os.stat(tags[u'path']).st_mtime
                        }],
                    u'digital': True,
                    u'analog': False
                    }],
                u'url': None
                })
    def flyby(self, library, paths):
        for root, _, filenames in os.walk(self.directory):
            for filename in filenames:
                path = os.path.join(root, filename)
                if path not in paths:
                    tags = self.tagsread(path)
                    if tags:
                        paths.append(path)
                        self.append(tags, library)
    def tagsread(self, filepath):
        ext = os.path.splitext(filepath)[1]
        if ext == u'.mp3':
            self.stepped.emit(filepath)
            f = ID3(filepath)
            try:
                return {
                        u'artist': f[u'TPE1'].text[0],
                        u'album': f[u'TALB'].text[0],
                        u'date': str(f[u'TDRC'].text[0]),
                        u'title': f[u'TIT2'].text[0],
                        u'tracknumber': f[u'TRCK'].text[0],
                        u'path': filepath
                        }
            except KeyError:
                self.exceptions.append(filepath)
        else:
            if ext == u'.flac':
                f = FLAC(filepath)
            elif ext == u'.asf':
                f = ASF(filepath)
            elif ext == u'.wv':
                f = WavPack(filepath)
            elif ext == u'.mpc' or ext == u'.mpp' or ext == u'.mp+':
                f = Musepack(filepath)
            elif ext == u'.ogg' or ext == u'.ape': # different .ogg and .ape files
                f = File(filepath)
            else:
                return False
            self.stepped.emit(filepath)
            try:
                return {
                        u'artist': f[u'artist'][0],
                        u'album': f[u'album'][0],
                        u'date': f[u'date'][0],
                        u'title': f[u'title'][0],
                        u'tracknumber': f[u'tracknumber'][0],
                        u'path': filepath
                        }
            except KeyError:
                self.exceptions.append(filepath)
    def create(self):
        library = []
        paths = []
        self.flyby(library, paths)
        return (library, paths)
    def update(self, library, paths):
        toDelete = []
        for artist in library:
            for album in artist[u'albums']:
                for track in album[u'tracks']:
                    if os.path.exists(track[u'path']):
                        modified = os.stat(track[u'path']).st_mtime
                        if modified != track[u'modified']:
                            tags = self.tagsread(track[u'path'])
                            if tags:
                                if tags[u'artist'] != artist[u'artist']:
                                    self.append(tags, library)
                                    toDelete.append(track)
                                elif tags[u'album'] != album[u'album']:
                                    sem = False
                                    for rAlbum in artist[u'albums']:
                                        if rAlbum[u'album'] == tags[u'album']:
                                            sem = True
                                            rAlbum[u'tracks'].append({
                                                u'title': tags[u'title'],
                                                u'tracknumber': tags[u'tracknumber'],
                                                u'path': tags[u'path'],
                                                u'modified': modified
                                                })
                                            break
                                    if not sem:
                                        artist[u'albums'].append({
                                            u'album': tags[u'album'],
                                            u'date': tags[u'date'],
                                            u'tracks': [{
                                                u'title': tags[u'title'],
                                                u'tracknumber': tags[u'tracknumber'],
                                                u'path': tags[u'path'],
                                                u'modified': modified
                                                }],
                                            u'digital': True,
                                            u'analog': False
                                            })
                                    toDelete.append(track)
                                elif tags[u'title'] != track[u'title']:
                                    track[u'title'] = tags[u'title']
                                    track[u'modified'] = modified
                    else:
                        toDelete.append(track)
                for d in toDelete:
                    del album[u'tracks'][album[u'tracks'].index(d)]
                del toDelete[:]
                if not album[u'tracks']:
                    del artist[u'albums'][artist[u'albums'].index(album)]
            if not artist[u'albums']:
                del library[library.index(artist)]
        self.flyby(library, paths)
    def setDirectory(self, directory):
        self.directory = directory
    def setArgs(self, library, paths, update = False):
        self.library = library
        self.paths = paths
        self.doUpdate = update
    def run(self):
        del self.exceptions[:]
        if self.doUpdate:
            self.update(self.library, self.paths)
            self.updated.emit()
        else:
            result = self.create()
            self.created.emit(result)
        if self.exceptions:
            self.errors.emit(
                    u'local',
                    u'error',
                    self.exceptions,
                    u"You're probably missing some tags")
