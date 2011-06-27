# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2010 - 2011
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
from copy import deepcopy
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
    updated = pyqtSignal()
    stepped = pyqtSignal(unicode)
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    def __init__(self, directory, library, ignores):
        QThread.__init__(self)
        self.directory = directory
        self.library = library[1]
        self.paths = library[2]
        self.avai = library[4]
        self.ignores = [v for (v, _) in ignores]
        self.toremove = set()
    def append(self, path, existing = False):
        u"""Append new entry to the library.
        
        Arguments:
        path -- path to the file one wants to append
        existing -- (bool) whether path points to completely new entry
        or an changed one
        """
        tags = self.tagsread(path)
        if tags:
            if existing:
                self.toremove.add(self.remove(path))
            item = {tags[u'date']: {
                        tags[u'album']: {
                            tags[u'tracknumber']: {
                                tags[u'title']: {
                                    u'path': path
                                    }
                                }
                            }
                        }
                    }
            try:
                partial = self.library[tags[u'artist']]
            except KeyError:
                self.library[tags[u'artist']] = item
            else:
                item = item[tags[u'date']]
                try:
                    partial = partial[tags[u'date']]
                except KeyError:
                    partial[tags[u'date']] = item
                else:
                    item = item[tags[u'album']]
                    try:
                        partial = partial[tags[u'album']]
                    except KeyError:
                        partial[tags[u'album']] = item
                    else:
                        item = item[tags[u'tracknumber']]
                        try:
                            partial = partial[tags[u'tracknumber']]
                        except KeyError:
                            partial[tags[u'tracknumber']] = item
                        else:
                            item = item[tags[u'title']]
                            try:
                                partial = partial[tags[u'tracknumber']]
                            except KeyError:
                                partial[tags[u'tracknumber']] = item
                            else:
                                item = item[tags[u'title']]
                                try:
                                    partial = partial[tags[u'title']]
                                except KeyError:
                                    partial[tags[u'title']] = item
            self.paths[path] = tags
            self.paths[path][u'modified'] = os.stat(path).st_mtime
            key = tags[u'artist'] + tags[u'date'] + tags[u'album']
            try:
                self.avai[key][u'digital'] = True
            except KeyError:
                self.avai[key] = {
                        u'digital': True,
                        u'analog': False,
                        u'remote': False
                        }
    def remove(self, path):
        u"""Remove specified item from the library.

        Arguments:
        path -- path to the file one wants to remove

        Return value:
        artist who can probably be removed completely
        """
        result = None
        path_ = self.paths[path]
        item = self.library[path_[u'artist']][path_[u'date']] \
                [path_[u'album']][path_[u'tracknumber']]
        del item[path_[u'title']]
        if not item:
            item = self.library[path_[u'artist']][path_[u'date']] \
                    [path_[u'album']]
            del item[path_[u'tracknumber']]
            key = path_[u'artist'] + path_[u'date'] + path_[u'album']
            if not item:
                result = path_[u'artist']
                if not self.avai[key][u'analog'] and \
                        not self.avai[key][u'remote']:
                    item = self.library[path_[u'artist']][path_[u'date']]
                    del item[path_[u'album']]
                    del self.avai[key]
                    if not item:
                        item = self.library[path_[u'artist']]
                        del item[path_[u'date']]
                        if not item:
                            del self.library[path_[u'artist']]
                else:
                    self.avai[key][u'digital'] = False
        del self.paths[path]
        return result
    def ignored(self, root):
        u"""Check if specified folder is on list to ignore.

        Arguments:
        root -- folder to check against
        """
        for ignore in self.ignores:
            if fnmatch(root, u'*/' + ignore + u'/*'):
                return True
        return False
    def tagsread(self, filepath):
        u"""Read needed tags (metadata/ID3) from specified file.
        
        Arguments:
        filepath --  path to the files one wants to read

        Return value:
        a dictionary of tags
        """
        ext = os.path.splitext(filepath)[1]
        try:
            if ext == u'.mp3':
                self.stepped.emit(filepath)
                f = ID3(filepath)
                try:
                    return {u'artist': f[u'TPE1'].text[0],
                            u'album': f[u'TALB'].text[0],
                            u'date': unicode(f[u'TDRC'].text[0]),
                            u'title': f[u'TIT2'].text[0],
                            u'tracknumber': f[u'TRCK'].text[0],
                            }
                except KeyError:
                    self.errors.emit(u'local',
                            u'errors',
                            filepath,
                            self.trUtf8("You're probably missing some tags."))
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
                    return {u'artist': f[u'artist'][0],
                            u'album': f[u'album'][0],
                            u'date': f[u'date'][0],
                            u'title': f[u'title'][0],
                            u'tracknumber': f[u'tracknumber'][0]
                            }
                except KeyError:
                    self.errors.emit(u'local',
                            u'errors',
                            filepath,
                            self.trUtf8("You're probably missing some tags."))
        except IOError:
            self.errors.emit(u'local',
                    u'errors',
                    filepath,
                    u'Cannot open file')
    def actualize(self, directory, ignores):
        u"""Actualize directory and ignores list.

        Arguments:
        directory -- new directory
        ignores -- new ignores list

        Note: This is executed after settings changes.
        """
        self.directory = directory
        self.ignores = [v for (v, _) in ignores]
    def run(self):
        u"""Run the creating/updating process (or rather a thread ;).
        
        Note: Should be called using start() method.
        """
        self.stepped.emit(self.trUtf8('Working'))
        tfiles = deepcopy(self.paths)
        for root, _, filenames in os.walk(self.directory):
            for filename in filenames:
                path = os.path.join(root, filename)
                if not self.ignored(root):
                    try:
                        modified = self.paths[path][u'modified']
                    except KeyError:
                        self.append(path)
                    else:
                        if os.stat(path).st_mtime != modified:
                            self.append(path, True)
                        try:
                            del tfiles[path]
                        except KeyError:
                            pass
                elif path in self.paths.keys():
                    self.toremove.add(self.remove(path))
        for tf in tfiles:
            self.toremove.add(self.remove(tf))
        for tr in self.toremove:
            if tr:
                remove = True
                try:
                    for year, albums in self.library[tr].iteritems():
                        for tracks in albums.values():
                            if tracks:
                                remove = False
                                break
                        if not remove:
                            break
                except KeyError:
                    pass
                else:
                    if remove:
                        del self.library[tr]
        self.updated.emit()
