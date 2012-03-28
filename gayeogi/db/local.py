# -*- coding: utf-8 -*-
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

import os
from copy import deepcopy
from fnmatch import fnmatch
from PyQt4.QtCore import QThread, pyqtSignal
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.musepack import Musepack
from mutagen.wavpack import WavPack
from mutagen.mp4 import MP4
from mutagen import File
import logging

logger = logging.getLogger('gayeogi.local')

class Filesystem(QThread):
    """Create/Update local file info library.

    Signals:
        updated (void): emitted at the end
        stepped (unicode): emitted after each file (filename)

    """
    updated = pyqtSignal()
    stepped = pyqtSignal(unicode)
    def __init__(self, directory, library, ignores):
        """Constructs new Filesystem instance.

        Args:
            directory (list): list of directories to search in
            library (tuple): library object
            ignores (list): list of patterns to ignore

        """
        QThread.__init__(self)
        self.directories = directory
        self.library = library[1]
        self.paths = library[2]
        self.avai = library[4]
        self.modified = library[5]
        self.ignores = ignores
        self.toremove = set()
        self.logged = set()
        self.__messages = {
            u'added': self.trUtf8('Something has been added.'),
            u'changed': self.trUtf8('Something has been changed.'),
            u'removed': self.trUtf8('Something has been removed.'),
            u'missing': self.trUtf8("You're probably missing some tags."),
            u'cannot': self.trUtf8('Cannot open file.')
        }
    def log(self, level, element, message):
        """Sends specified message to logger if element wasn't logged already.

        Args:
            level (unicode): log severity level
            element (unicode): file/entry
            message (unicode): message to log

        """
        if element not in self.logged:
            getattr(logger, level)([element, self.__messages[message]])
            self.logged.add(element)
    def append(self, path, existing = False):
        """Appends new entry to the library.

        Ars:
            path (unicode): path to the file one wants to append

        Kwargs:
            existing (bool): whether path points to completely new entry
            or an changed one

        """
        tags = self.tagsread(path)
        if tags:
            if existing:
                self.log(u'info', tags[u'artist'], u'changed')
                self.toremove.add(self.remove(path))
            else:
                self.log(u'info', tags[u'artist'], u'added')
            partial = self.library.setdefault(tags[u'artist'], {})
            for tag in [u'date', u'album', u'tracknumber', u'title']:
                partial = partial.setdefault(tags[tag], {})
            partial[u'path'] = path
            self.paths[path] = tags
            self.paths[path][u'modified'] = os.stat(path).st_mtime
            key = tags[u'artist'] + tags[u'date'] + tags[u'album']
            self.avai.setdefault(key,
                {
                    u'digital': True,
                    u'analog': False,
                    u'remote': set()
                }
            )[u'digital'] = True
    def remove(self, path):
        """Remove specified item from the library.

        Args:
            path (unicode): path to the file one wants to remove

        Returns:
            unicode -- artist who can probably be removed completely

        """
        result = None
        path_ = self.paths[path]
        item = self.library[path_[u'artist']][path_[u'date']]\
            [path_[u'album']][path_[u'tracknumber']]
        if item[path_[u'title']][u'path'] == path:
            del item[path_[u'title']]
            if not item:
                item = self.library[path_[u'artist']]\
                    [path_[u'date']][path_[u'album']]
                del item[path_[u'tracknumber']]
                key = path_[u'artist'] + path_[u'date'] + path_[u'album']
                if not item:
                    result = path_[u'artist']
                    if (not self.avai[key][u'analog'] and
                    not self.avai[key][u'remote']):
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
        self.log(u'info', path_[u'artist'], u'removed')
        return result
    def ignored(self, root):
        """Check if specified folder is on list to ignore.

        Args:
            root (unicode): folder to check against

        Returns:
            bool -- True if root is in ignores, False otherwise

        """
        for (ignore, enabled) in self.ignores:
            if enabled and fnmatch(root, u'*' + ignore + u'*'):
                return True
        return False
    def tagsread(self, filepath):
        """Read needed tags (metadata/ID3) from specified file.
        
        Args:
            filepath (unicode): path to the files one wants to read

        Returns:
            dict -- a dictionary of tags

        """
        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == u'.mp3':
                self.stepped.emit(filepath)
                f = ID3(filepath)
                try:
                    return {
                        u'artist': f[u'TPE1'].text[0],
                        u'album': f[u'TALB'].text[0],
                        u'date': unicode(f[u'TDRC'].text[0]),
                        u'title': f[u'TIT2'].text[0],
                        u'tracknumber': f[u'TRCK'].text[0],
                    }
                except KeyError:
                    self.log(u'warning', filepath, u'missing')
            elif ext in [u'.mp4', u'.m4a', u'.mpeg4', u'.aac']:
                f = MP4(filepath)
                try:
                    return {
                        u'artist': f['\xa9ART'][0],
                        u'album': f['\xa9alb'][0],
                        u'date': f['\xa9day'][0],
                        u'title': f['\xa9nam'][0],
                        u'tracknumber': unicode(f['trkn'][0][0])
                    }
                except KeyError:
                    self.log(u'warning', filepath, u'missing')
            else:
                if ext == u'.flac':
                    f = FLAC(filepath)
                elif ext == u'.asf':
                    f = ASF(filepath)
                elif ext == u'.wv':
                    f = WavPack(filepath)
                elif ext in [u'.mpc', u'.mpp', u'.mp+']:
                    f = Musepack(filepath)
                elif ext in [u'.ogg', u'.ape']:
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
                        u'tracknumber': f[u'tracknumber'][0]
                    }
                except KeyError:
                    self.log(u'warning', filepath, u'missing')
        except IOError:
            self.log(u'error', filepath, u'cannot')
    def actualize(self, directory = None, ignores = None):
        """Actualize directory and ignores list.

        Kwargs:
            directory (list): new directories list
            ignores (list): new ignores list

        Note: This is executed after settings changes.

        """
        if directory != None:
            self.directories = directory
        if ignores != None:
            self.ignores = ignores
    def run(self):
        """Run the creating/updating process (or rather a thread ;).
        
        Note: Should be called using start() method.

        """
        self.stepped.emit(self.trUtf8('Working'))
        tfiles = deepcopy(self.paths)
        for (directory, enabled) in self.directories:
            if enabled:
                for root, _, filenames in os.walk(directory):
                    for filename in filenames:
                        path = os.path.join(root, filename)
                        if not self.ignored(root):
                            try:
                                modified = self.paths[path][u'modified']
                            except KeyError:
                                self.append(path)
                                self.modified[0] = True
                            else:
                                if os.stat(path).st_mtime != modified:
                                    self.append(path, True)
                                    self.modified[0] = True
                                try:
                                    del tfiles[path]
                                except KeyError:
                                    pass
                        elif path in self.paths.keys():
                            self.toremove.add(self.remove(path))
                            del tfiles[path]
        if tfiles:
            self.modified[0] = True
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
                        self.log(u'info', tr, u'removed')
        self.logged.clear()
        self.updated.emit()
