# -*- coding: utf-8 -*-

import os
from gayeogi.db.local import BaseModel
from gayeogi.db.local import ArtistNode, AlbumNode, TrackNode


class TestUpsert(object):
    """Deeply test different kinds of inserting and updating cases."""
    def setUp(self):
        self.artists = BaseModel(os.getcwd())
        self.root = self.artists._rootNode

    def test_insert_to_empty_db(self):
        self.artists.upsert(None, {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album',
            u'tracknumber': u'12',
            u'title': u'test_title'
        })
        assert self.root.childCount() == 1
        artist = self.root.child(0)
        assert isinstance(artist, ArtistNode)
        assert artist.metadata == {u'artist': u'test_artist'}
        assert artist.childCount() == 1
        album = artist.child(0)
        assert isinstance(album, AlbumNode)
        assert album.metadata == {u'year': u'2012', u'album': u'test_album'}
        assert album.childCount() == 1
        track = album.child(0)
        assert isinstance(track, TrackNode)
        assert track.metadata == {
            u'tracknumber': u'12', u'title': u'test_title'
        }

    def test_insert_new_artist(self):
        artist1 = ArtistNode(parent=self.root)
        artist1.metadata = {u'artist': u'test_artist1'}
        self.artists.upsert(None, {
            u'artist': u'test_artist2'
        })
        assert self.root.childCount() == 2
        artist2 = self.root.child(1)
        assert isinstance(artist2, ArtistNode)
        assert artist2.metadata == {u'artist': u'test_artist2'}

    def test_insert_new_album_to_artist(self):
        artist = ArtistNode(parent=self.root)
        artist.metadata = {u'artist': u'test_artist'}
        self.artists.upsert(None, {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album'
        })
        assert artist.childCount() == 1
        album = artist.child(0)
        assert isinstance(album, AlbumNode)
        assert album.metadata == {u'year': u'2o12', u'album': u'test_album'}

    def test_insert_new_track_to_album(self):
        artist = ArtistNode(parent=self.root)
        artist.metadata = {u'artist': u'test_artist'}
        album = AlbumNode(parent=artist)
        album.metadata = {u'year': u'2012', u'album': u'test_album'}
        self.artists.upsert(None, {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album',
            u'tracknumber': u'12',
            u'title': u'test_title'
        })
        assert album.childCount() == 1
        track = album.child(0)
        assert isinstance(track, TrackNode)
        assert track.metadata == {
            u'tracknumber': u'12', u'title': u'test_title'
        }

    def test_update_track_without_changing_artist_and_album_and_title(self):
        assert False

    def test_update_track_changing_only_title(self):
        assert False

    def test_update_track_changing_only_album(self):
        assert False

    def test_update_track_changing_only_artist(self):
        assert False

    def test_update_track_changing_title_and_album(self):
        assert False

    def test_update_track_changing_title_and_artist(self):
        assert False

    def test_update_track_changing_artist_and_album(self):
        assert False

    def test_update_track_changing_artist_and_album_and_title(self):
        assert False
