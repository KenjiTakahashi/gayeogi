# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi
# Karol "Kenji Takahashi" Woźniak © 2012
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
import shutil
from gayeogi.db.local import _Node, ArtistNode, AlbumNode, TrackNode


class Test_fclear(object):
    # It is same for artist, album and track,
    # so we'll test ArtistNode here.
    def setUp(self):
        self.path = os.path.join(__file__, u'..', u'..', u'data', u'empty')
        self.path = os.path.normpath(self.path)
        os.mkdir(self.path)
        self.meta = {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        self.root = _Node(self.path)
        self.artist = ArtistNode(parent=self.root)
        self.artist.update(self.meta.copy())
        self.artist._path = os.path.join(
            self.path, self.artist.fn_encode(self.meta[u'artist'])
        )
        metadata = self.meta.copy()
        del metadata[u'artist']
        self.artist._fsave(metadata)
        self.artist._mtime = os.stat(os.path.join(
            self.artist._path, u'.meta'
        )).st_mtime

    def tearDown(self):
        shutil.rmtree(self.path)

    def test_do_not_remove_unchanged(self):
        self.artist._fclear(self.meta[u'artist'])
        assert os.path.exists(self.artist._path)

    def test_do_not_remove_changed_file(self):
        # It means that somebody already overwritten this entry
        # (e.g. File has been moved without metadata change).
        path = os.path.join(
            self.path, self.artist.fn_encode(u'test_artist2')
        )
        os.mkdir(path)
        open(os.path.join(path, u'.meta'), u'w')
        oldpath = self.artist._path
        stat = os.stat(oldpath)
        os.utime(
            os.path.join(oldpath, u'.meta'),
            (stat.st_atime, stat.st_mtime + 10)
        )
        self.artist._fclear(u'test_artist2')
        assert os.path.exists(oldpath)

    def test_remove_changed_with_unchanged_file(self):
        path = os.path.join(
            self.path, self.artist.fn_encode(u'test_artist2')
        )
        os.mkdir(path)
        open(os.path.join(path, u'.meta'), u'w')
        oldpath = self.artist._path
        self.artist._fclear(u'test_artist2')
        assert not os.path.exists(oldpath)


class Test_fsave(object):
    def test_save_artist(self):
        pass

    def test_save_album(self):
        pass

    def test_save_track(self):
        pass
