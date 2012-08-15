# -*- coding: utf-8 -*-

import os
from gayeogi.db.local import BaseModel
from gayeogi.db.local import ArtistNode, AlbumNode, TrackNode


class TestUpsert(object):
    """Deeply test different kinds of inserting and updating cases."""
    def setUp(self):
        self.db = BaseModel(os.getcwd())
        self.root = self.db._rootNode

    def test_insert_to_empty_db(self):
        self.db.upsert(None, {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album',
            u'tracknumber': u'12',
            u'title': u'test_title'
        })
        artist = self.root.child(0)
        album = artist.child(0)
        track = album.child(0)
        assert album.childCount() == 1
        assert isinstance(track, TrackNode)
        assert track.metadata == {
            u'tracknumber': u'12', u'title': u'test_title'
        }
        assert artist.childCount() == 1
        assert isinstance(album, AlbumNode)
        assert album.metadata == {u'year': u'2012', u'album': u'test_album'}
        assert self.root.childCount() == 1
        assert isinstance(artist, ArtistNode)
        assert artist.metadata == {u'artist': u'test_artist'}

    def test_insert_new_artist(self):
        artist1 = ArtistNode(parent=self.root)
        artist1.metadata = {u'artist': u'test_artist1'}
        self.db.upsert(None, {
            u'artist': u'test_artist2'
        })
        assert self.root.childCount() == 2
        artist2 = self.root.child(1)
        assert isinstance(artist2, ArtistNode)
        assert artist2.metadata == {u'artist': u'test_artist2'}

    def test_insert_new_album_to_artist(self):
        artist = ArtistNode(parent=self.root)
        artist.metadata = {u'artist': u'test_artist'}
        self.db.upsert(None, {
            u'artist': u'test_artist',
            u'year': u'2012',
            u'album': u'test_album'
        })
        assert artist.childCount() == 1
        album = artist.child(0)
        assert isinstance(album, AlbumNode)
        assert album.metadata == {u'year': u'2012', u'album': u'test_album'}

    def test_insert_new_track_to_album(self):
        artist = ArtistNode(parent=self.root)
        artist.metadata = {u'artist': u'test_artist'}
        album = AlbumNode(parent=artist)
        album.metadata = {u'year': u'2012', u'album': u'test_album'}
        self.db.upsert(None, {
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

    def prepare_update(self):
        self.artist = ArtistNode(parent=self.root)
        self.artist.metadata = {u'artist': u'test_artist1'}
        self.album = AlbumNode(parent=self.artist)
        self.album.metadata = {u'year': u'2012', u'album': u'test_album1'}
        self.track = TrackNode(parent=self.album)
        self.track.metadata = {u'tracknumber': u'12', u'title': u'test_title1'}
        self.artist_index = self.db.index(0, 0)
        self.album_index = self.db.index(0, 0, self.artist_index)
        self.track_index = self.db.index(0, 0, self.album_index)

    def test_update_track_changing_title(self):
        self.prepare_update()
        self.db.upsert(self.track_index, {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title2'
        })
        assert self.album.childCount() == 1
        assert self.track.metadata == {
            u'tracknumber': u'12', u'title': u'test_title2'
        }

    def test_update_track_changing_year(self):
        self.prepare_update()
        self.db.upsert(self.track_index, {
            u'artist': u'test_artist1',
            u'year': u'2102',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        })
        assert self.artist.childCount() == 1
        album = self.artist.child(0)
        assert isinstance(album, AlbumNode)
        assert album.metadata == {u'year': u'2102', u'album': u'test_album1'}

    def test_update_track_changing_album(self):
        self.prepare_update()
        self.db.upsert(self.track_index, {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album2',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        })
        assert self.artist.childCount() == 1
        album = self.artist.child(0)
        assert isinstance(album, AlbumNode)
        assert album.metadata == {u'year': u'2012', u'album': u'test_album2'}

    def test_update_track_changing_artist(self):
        self.prepare_update()
        self.db.upsert(self.track_index, {
            u'artist': u'test_artist2',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        })
        assert self.root.childCount() == 1
        artist = self.root.child(0)
        assert artist.metadata == {u'artist': u'test_artist2'}
        assert artist.childCount() == 1

    def test_leverage_album_metadata_from_tracks(self):
        # Non-primary metadata is considered "album" when
        # it stays the same across all "tracks" in that album.
        self.prepare_update()
        album2 = AlbumNode(parent=self.artist)
        album2.metadata = {
            u'year': u'2000',
            u'album': u'test_album2',
            u'comment': u'test_comment1'
        }
        track1 = TrackNode(parent=album2)
        track1.metadata = {
            u'tracknumber': u'11',
            u'title': u'test_title2'
        }
        self.db.upsert(None, {
            u'artist': u'test_artist1',
            u'year': u'2000',
            u'album': u'test_album2',
            u'tracknumber': u'10',
            u'title': u'test_title3',
            u'comment': u'test_comment1'
        })
        assert album2.childCount() == 2
        track2 = album2.child(1)
        assert track2.metadata == {
            u'tracknumber': u'10',
            u'title': u'test_title3'
        }
        assert (u'comment', u'test_comment1') in album2.metadata.iteritems()

    def test_do_not_leverage_tracks_metadata_to_album(self):
        # See :test_leverage_album_metadata_from_tracks:.
        self.prepare_update()
        album2 = AlbumNode(parent=self.artist)
        album2.metadata = {
            u'year': u'2000',
            u'album': u'test_album2'
        }
        track1 = TrackNode(parent=album2)
        track1.metadata = {
            u'tracknumber': u'11',
            u'title': u'test_title2',
            u'comment': u'test_comment1'
        }
        self.db.upsert(None, {
            u'artist': u'test_artist1',
            u'year': u'2000',
            u'album': u'test_album2',
            u'tracknumber': u'10',
            u'title': u'test_title3',
            u'comment': u'test_comment2'
        })
        assert album2.childCount() == 2
        track2 = album2.child(1)
        assert track2.metadata == {
            u'tracknumber': u'10',
            u'title': u'test_title3',
            u'comment': u'test_comment2'
        }
        assert u'comment' not in album2.metadata

    def test_leverage_artist_metadata_from_albums(self):
        # See :test_leverage_album_metadata_from_tracks:.
        self.prepare_update()
        artist2 = ArtistNode(parent=self.root)
        artist2.metadata = {
            u'artist': u'test_artist2'
        }
        album2 = AlbumNode(parent=artist2)
        album2.metadata = {
            u'year': u'2000',
            u'album': u'test_album2',
            u'comment': u'test_comment1'
        }
        self.db.upsert(None, {
            u'artist': u'test_artist2',
            u'year': u'2001',
            u'album': u'test_album3',
            u'comment': u'test_comment1'
        })
        assert artist2.childCount() == 2
        album3 = artist2.child(1)
        assert album3.metadata == {u'year': u'2001', u'album': u'test_album3'}
        assert (u'comment', u'test_comment1') in artist2.metadata.iteritems()

    def test_do_not_leverage_albums_metadata_to_artist(self):
        # See :test_leverage_album_metadata_from_tracks:.
        self.prepare_update()
        artist2 = ArtistNode(parent=self.root)
        artist2.metadata = {
            u'artist': u'test_artist2'
        }
        album2 = AlbumNode(parent=artist2)
        album2.metadata = {
            u'year': u'2000',
            u'album': u'test_album2',
            u'comment': u'test_comment1'
        }
        self.db.upsert(None, {
            u'artist': u'test_artist2',
            u'year': u'2001',
            u'album': u'test_album3',
            u'comment': u'test_comment2'
        })
        assert artist2.childCount() == 2
        album3 = artist2.child(1)
        assert album3.metadata == {
            u'year': u'2001',
            u'album': u'test_album3',
            u'comment': u'test_comment2'
        }
        assert u'comment' not in artist2.metadata
