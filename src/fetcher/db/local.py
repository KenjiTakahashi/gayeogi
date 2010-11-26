# -*- coding: utf-8 -*-

import os
from fnmatch import fnmatch
from PyQt4.QtCore import QThread, pyqtSignal
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.musepack import Musepack
from mutagen.wavpack import WavPack
from mutagen import File

class Filesystem(QThread):
    u"""Create/Update local file info library"""
    created = pyqtSignal(tuple)
    updated = pyqtSignal()
    stepped = pyqtSignal(unicode)
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    def __init__(self):
        QThread.__init__(self)
        self.directory = None
        self.library = []
        self.paths = []
        self.doUpdate = False
        self.ignores = []
    def append(self, tags, library):
        u"""Append new entry to the library"""
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
                        album[u'digital'] = True
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
                u'url': {}
                })
    def ignored(self, root):
        for ignore in self.ignores:
            if fnmatch(root, u'*/' + ignore + u'/*'):
                return True
        return False
    def flyby(self, library, paths):
        u"""Create new library from scratch, going through every
        sub-directory or add new directories to an existing library"""
        for root, _, filenames in os.walk(self.directory):
            if not self.ignored(root):
                for filename in filenames:
                    path = os.path.join(root, filename)
                    if path not in paths:
                        tags = self.tagsread(path)
                        if tags:
                            paths.append(path)
                            self.append(tags, library)
    def tagsread(self, filepath):
        u"""Read needed tags (metadata/ID3) from specified file"""
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
                self.errors.emit(u'local',
                        u'errors',
                        filepath,
                        u"You're probably missing some tags")
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
                self.errors.emit(u'local',
                        u'errors',
                        filepath,
                        u"You're probably missing some tags")
    def create(self):
        u"""Create new library"""
        library = []
        paths = []
        self.flyby(library, paths)
        return (library, paths)
    def update(self, library, paths):
        u"""Check existing library entries for changes and update"""
        toDelete = []
        for artist in library:
            for album in artist[u'albums']:
                for track in album[u'tracks']:
                    if os.path.exists(track[u'path']) and not self.ignored(track[u'path']):
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
                                        rAlbum[u'digital'] = True
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
                    elif track[u'path']:
                        toDelete.append(track)
                for d in toDelete:
                    del album[u'tracks'][album[u'tracks'].index(d)]
                del toDelete[:]
                if not album[u'tracks'] and album[u'digital'] and not album[u'analog']:
                    del artist[u'albums'][artist[u'albums'].index(album)]
            if not artist[u'albums']:
                del library[library.index(artist)]
        for path in paths:
            if self.ignored(path):
                del paths[paths.index(path)]
        self.flyby(library, paths)
    def setDirectory(self, directory):
        u"""Set library directory"""
        self.directory = directory
    def setArgs(self, library, paths, ignores, update = False):
        u"""Set library object, paths list, ignores list and
        update state (whether to update or create new library)"""
        self.library = library
        self.paths = paths
        self.doUpdate = update
        self.ignores = [v for (v, _) in ignores]
    def run(self):
        u"""Run the creating/updating process (or rather a thread ;)"""
        if self.doUpdate:
            self.update(self.library, self.paths)
            self.updated.emit()
        else:
            result = self.create()
            self.created.emit(result)
