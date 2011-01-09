# This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
# Karol "Kenji Takahashi" Wozniak (C) 2010
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
        try:
            albums = library[tags[u'artist']][u'albums']
        except KeyError:
            library[tags[u'artist']] = {
                    u'albums': {
                        tags[u'album']: {
                            u'date': tags[u'date'],
                            u'tracks': {
                                tags[u'title']: {
                                    u'tracknumber': tags[u'tracknumber'],
                                    u'path': tags[u'path'],
                                    u'modified': os.stat(tags[u'path']).st_mtime
                                    }
                                },
                            u'digital': True,
                            u'analog': False,
                            u'remote': False
                            }
                        },
                    u'url': {}
                    }
        else:
            try:
                tracks = albums[tags[u'album']][u'tracks']
            except KeyError:
                albums[tags[u'album']] = {
                        u'date': tags[u'date'],
                        u'tracks': {
                            tags[u'title']: {
                                u'tracknumber': tags[u'tracknumber'],
                                u'path': tags[u'path'],
                                u'modified': os.stat(tags[u'path']).st_mtime
                                }
                            },
                        u'digital': True,
                        u'analog': False,
                        u'remote': False
                        }
            else:
                albums[tags[u'album']][u'digital'] = True
                try:
                    tracks[tags[u'title']]
                except KeyError:
                    tracks[tags[u'title']] = {
                            u'tracknumber': tags[u'tracknumber'],
                            u'path': tags[u'path'],
                            u'modified': os.stat(tags[u'path']).st_mtime
                            }
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
        try:
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
        except IOError:
            self.errors.emit(u'local',
                    u'errors',
                    filepath,
                    u'Cannot open file')
    def create(self):
        u"""Create new library"""
        library = {}
        paths = []
        self.flyby(library, paths)
        return (library, paths)
    def update(self, library, paths):
        u"""Check existing library entries for changes and update if necessary"""
        toTrackDelete = set()
        toAlbumDelete = set()
        toArtistDelete = set()
        toAppend = set()
        for artist, albums in library.iteritems():
            for album, tracks in albums[u'albums'].iteritems():
                for track, props in tracks[u'tracks'].iteritems():
                    if os.path.exists(props[u'path']) and not self.ignored(props[u'path']):
                        modified = os.stat(props[u'path']).st_mtime
                        if modified != props[u'modified']:
                            tags = self.tagsread(props[u'path'])
                            if tags:
                                toTrackDelete.add(track)
                                toAppend.add(tags)
                    else:
                        toTrackDelete.add(track)
                        del paths[paths.index(props[u'path'])]
                for i in range(len(toTrackDelete)):
                    del tracks[u'tracks'][toTrackDelete.pop()]
                for i in range(len(toAppend)):
                    self.append(toAppend.pop(), library)
                if not tracks[u'tracks'] and not tracks[u'remote'] and not tracks[u'analog']:
                    toAlbumDelete.add(album)
            for i in range(len(toAlbumDelete)):
                del albums[u'albums'][toAlbumDelete.pop()]
            if not albums[u'albums'] and not albums[u'url']:
                toArtistDelete.add(artist)
        for i in range(len(toArtistDelete)):
            del library[toArtistDelete.pop()]
        for path in paths:
            if self.ignored(path):
                del paths[paths.index(path)]
        self.flyby(library, paths)
    def setDirectory(self, directory):
        u"""Set library directory"""
        self.directory = directory
    def setIgnores(self, ignores):
        u"""Set ignores list"""
        self.ignores = [v for (v, _) in ignores]
    def setArgs(self, library, paths, ignores, update = False):
        u"""Set library object, paths list, ignores list and
        update state (whether to update or create new library)"""
        self.library = library
        self.paths = paths
        self.doUpdate = update
        self.ignores = [v for (v, _) in ignores]
    def run(self):
        u"""Run the creating/updating process (or rather a thread ;)"""
        self.stepped.emit(u'Working')
        if self.doUpdate:
            self.update(self.library, self.paths)
            self.updated.emit()
        else:
            result = self.create()
            self.created.emit(result)
