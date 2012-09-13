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


class BaseTest(object):
    def setUp(self):
        self.path = os.path.join(__file__, u'..', u'..', u'data', u'empty')
        self.path = os.path.normpath(self.path)
        os.mkdir(self.path)
        self.db = BaseModel(self.path)
        self.root = self.db._rootNode

    def tearDown(self):
        os.rmdir(self.path)

    def prepare_update(self):
        self.artist = ArtistNode(parent=self.root)
        meta = {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        self.artist.metadata = meta.copy()
        self.album = AlbumNode(parent=self.artist)
        self.album.metadata = meta.copy()
        self.track = TrackNode(parent=self.album)
        self.track.metadata = meta.copy()
        self.artistIndex = self.db.index(0, 0)
        self.albumIndex = self.db.index(0, 0, self.artistIndex)
        self.trackIndex = self.db.index(0, 0, self.albumIndex)


class TestUpsert(BaseTest):
    """Test different kinds of inserting and updating cases."""

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

    def test_update_track_changing_title(self):
        self.prepare_update()
        result = {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title2'
        }
        self.db.upsert(self.trackIndex, result)
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
        self.db.upsert(self.trackIndex, result)
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
        self.db.upsert(self.trackIndex, result)
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
        self.db.upsert(self.trackIndex, result)
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

    def test_add_r_album(self):
        # We're testing only 'r', because 'a' is equivalent.
        self.prepare_update()
        self.db.upsert(None, (u'album', {
            u'year': u'2010',
            u'album': u'test_album2',
            u'artist': u'test_artist1',
            u'__r__': [True]
        }))
        album = self.artist.child(1)
        assert album.metadata == {
            u'year': u'2010',
            u'album': u'test_album2',
            u'artist': u'test_artist1'
        }
        assert album.adr == {u'__a__': False, u'__d__': False, u'__r__': True}
        assert self.artist.adr == {
            u'__a__': False, u'__d__': False, u'__r__': False
        }

    def test_add_r_to_album(self):
        self.prepare_update()
        self.db.upsert(None, (u'album', {
            u'year': u'2010',
            u'album': u'test_album2',
            u'artist': u'test_artist1'
        }))
        self.db.upsert(None, (u'album', {
            u'year': u'2012',
            u'album': u'test_album1',
            u'artist': u'test_artist1',
            u'__r__': [True]
        }))
        assert self.album.metadata == {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        assert self.album.adr == {
            u'__a__': False, u'__d__': False, u'__r__': True
        }
        assert self.artist.adr == {
            u'__a__': False, u'__d__': False, u'__r__': False
        }

    def test_add_r_to_album_for_known_artist_index(self):
        self.prepare_update()
        self.db.upsert(self.artistIndex, (u'album', {
            u'year': u'2012',
            u'album': u'test_album1',
            u'__r__': [True]
        }))
        assert self.album.adr[u'__r__']

    def test_add_r_to_all_albums(self):
        # This should update the artist to have 'r' too.
        self.prepare_update()
        self.db.upsert(None, (u'album', {
            u'year': u'2010',
            u'album': u'test_album2',
            u'artist': u'test_artist1',
            u'__r__': [True]
        }))
        self.db.upsert(self.albumIndex, {u'__r__': [True]})
        assert self.artist.adr == {
            u'__a__': False, u'__d__': False, u'__r__': True
        }


class TestRemove(BaseTest):
    """Test different kinds of removing cases."""

    def _add_and_remove_track(self):
        trackIndex = self.db.upsert(None, {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'11',
            u'title': u'test_title2'
        })
        self.db.remove(trackIndex)

    def test_remove_track(self):
        self.prepare_update()
        self._add_and_remove_track()
        assert self.album.childCount() == 1
        track = self.album.child(0)
        assert track.metadata == {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }

    def test_remove_album(self):
        # Album gets removed when there are no tracks and
        # it is not(a && d && r).
        self.prepare_update()
        albumIndex = self.db.upsert(None, (u'album', {
            u'artist': u'test_artist1',
            u'year': u'2010',
            u'album': u'test_album2'
        }))
        self.db.remove(albumIndex)
        assert self.artist.childCount() == 1
        album = self.artist.child(0)
        assert album.metadata == {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }

    def do_not_remove_album(self, adr):
        self.prepare_update()
        self.album.adr[adr] = True
        self.db.remove(self.trackIndex)
        assert self.album.childCount() == 0
        assert self.artist.childCount() == 1

    def test_do_not_remove_a_album(self):
        self.do_not_remove_album(u'__a__')

    def test_do_not_remove_d_album(self):
        self.do_not_remove_album(u'__d__')

    def test_do_not_remove_r_album(self):
        self.do_not_remove_album(u'__r__')

    def test_remove_artist(self):
        # Artist gets removed when there are no albums.
        self.prepare_update()
        artistIndex = self.db.upsert(None, (u'artist', {
            u'artist': u'test_artist2'
        }))
        self.db.remove(artistIndex)
        assert self.root.childCount() == 1
        artist = self.root.child(0)
        assert artist.metadata == {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
