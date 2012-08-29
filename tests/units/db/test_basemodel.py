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
from gayeogi.db.local import BaseModel
from gayeogi.db.local import ArtistNode, AlbumNode, TrackNode


class TestUpsert(object):
    """Deeply test different kinds of inserting and updating cases."""
    def setUp(self):
        self.db = BaseModel("{0}/non_existing".format(os.getcwd()))
        self.root = self.db._rootNode

    def test_insert_to_empty_db(self):
        result = {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album',
            u'tracknumber': u'12',
            u'title': u'test_title'
        }
        self.db.upsert(None, result)
        artist = self.root.child(0)
        album = artist.child(0)
        track = album.child(0)
        assert track.metadata == result
        assert album.metadata == result
        assert artist.metadata == result

    def test_insert_new_artist(self):
        artist1 = ArtistNode(parent=self.root)
        artist1.metadata = {u'artist': u'test_artist1'}
        self.db.upsert(None, {
            u'artist': u'test_artist2'
        })
        artist2 = self.root.child(1)
        assert artist2.metadata == {u'artist': u'test_artist2'}

    def test_insert_new_album_to_artist(self):
        artist = ArtistNode(parent=self.root)
        artist.metadata = {u'artist': u'test_artist'}
        result = {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album'
        }
        self.db.upsert(None, result)
        album = artist.child(0)
        assert album.metadata == result
        assert artist.metadata == result

    def test_insert_new_track_to_album(self):
        artist = ArtistNode(parent=self.root)
        artist.metadata = {u'artist': u'test_artist'}
        album = AlbumNode(parent=artist)
        album.metadata = {u'year': u'2012', u'album': u'test_album'}
        result = {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album',
            u'tracknumber': u'12',
            u'title': u'test_title'
        }
        self.db.upsert(None, result)
        track = album.child(0)
        assert track.metadata == result
        assert album.metadata == result
        assert artist.metadata == result

    def prepare_update(self):
        self.artist = ArtistNode(parent=self.root)
        meta = {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        self.artist.metadata = meta
        self.album = AlbumNode(parent=self.artist)
        self.album.metadata = meta
        self.track = TrackNode(parent=self.album)
        self.track.metadata = meta
        self.artist_index = self.db.index(0, 0)
        self.album_index = self.db.index(0, 0, self.artist_index)
        self.track_index = self.db.index(0, 0, self.album_index)

    def test_update_track_changing_title(self):
        self.prepare_update()
        result = {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title2'
        }
        self.db.upsert(self.track_index, result)
        assert self.track.metadata == result
        assert self.album.metadata == result
        assert self.artist.metadata == result

    def test_update_track_changing_year(self):
        self.prepare_update()
        result = {
            u'artist': u'test_artist1',
            u'year': u'2102',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        self.db.upsert(self.track_index, result)
        assert self.track.metadata == result
        assert self.album.metadata == result
        assert self.artist.metadata == result

    def test_update_track_changing_album(self):
        self.prepare_update()
        result = {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album2',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        self.db.upsert(self.track_index, result)
        assert self.track.metadata == result
        assert self.album.metadata == result
        assert self.artist.metadata == result

    def test_update_track_changing_artist(self):
        self.prepare_update()
        result = {
            u'artist': u'test_artist2',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        self.db.upsert(self.track_index, result)
        assert self.track.metadata == result
        assert self.album.metadata == result
        assert self.artist.metadata == result

    def test_add_second_track_to_album(self):
        self.prepare_update()
        result = {
            u'title': u'test_title2',
            u'tracknumber': u'11',
            u'year': u'2012',
            u'album': u'test_album1',
            u'artist': u'test_artist1'
        }
        self.db.upsert(None, result)
        track = self.album.child(1)
        assert track.metadata == result
        result[u'title'] = u'<multiple_values>'
        result[u'tracknumber'] = u'<multiple_values>'
        assert self.album.metadata == result
        assert self.artist.metadata == result

    def test_add_second_album_to_artist(self):
        self.prepare_update()
        result = {
            u'title': u'test_title1',
            u'tracknumber': u'12',
            u'year': u'2010',
            u'album': u'test_album2',
            u'artist': u'test_artist1'
        }
        self.db.upsert(None, result)
        album = self.artist.child(1)
        track = album.child(0)
        assert track.metadata == result
        assert album.metadata == result
        result[u'year'] = u'<multiple_values>'
        result[u'album'] = u'<multiple_values>'
        assert self.artist.metadata == result
