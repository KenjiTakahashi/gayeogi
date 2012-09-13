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
from gayeogi.db.distributor import Distributor, Bee
from gayeogi.db.local import DB
from threading import RLock
from Queue import Queue
from PyQt4.QtCore import QSettings


class Mockup(object):
    def __init__(self, work):
        self.sense = work


def work1(url, types):
    """Artificial worker function 1."""
    return (None, [(u'test_album1', u'2012')])


def work2(url, types):
    """Artificial worker function 2."""
    return (None, [(u'test_album2', u'2010')])


class TestBeeRun(object):
    def setUp(self):
        self.path = os.path.join(__file__, u'..', u'..', u'data', u'empty')
        self.path = os.path.normpath(self.path)
        os.mkdir(self.path)
        self.db = DB(self.path)
        path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), u'..', u'data')
        )
        DB._DB__settings = QSettings(
            os.path.join(path, u'db.conf'), QSettings.NativeFormat
        )
        DB._DB__settings.setValue(u'directories', [(path, True)])
        self.db.run()
        self.queue = Queue(2)

    def tearDown(self):
        os.rmdir(self.path)

    def work(self, work):
        instance = list(self.db.iterator())[0]
        instance = (instance[0], {u'mock': True}, instance[2], instance[3])
        self.queue.put(([(Mockup(work), [])], True, instance))
        self.queue.put((None, None, (None, None, None, None)))
        self.bee = Bee(self.queue, RLock(), False)
        self.bee.wait()

    def test_add_r_for_fetched_album(self):
        self.work(work1)
        node = self.db.artists._rootNode.child(0).child(0)
        assert node.adr[u'__r__']

    def test_do_not_add_r_for_not_fetched_album(self):
        self.db.artists.upsert(self.db.artists.index(0, 0), (u'album', {
            u'album': u'test_album2',
            u'year': u'2010',
            u'__d__': [True],
            u'__r__': [False]
        }))
        self.work(work1)
        node = self.db.artists._rootNode.child(0).child(1)
        assert not node.adr[u'__r__']

    def test_remove_r_from_not_fetched_album(self):
        self.db.artists.upsert(self.db.artists.index(0, 0), (u'album', {
            u'album': u'test_album2',
            u'year': u'2010',
            u'__d__': [True],
            u'__r__': [True]
        }))
        self.work(work1)
        node = self.db.artists._rootNode.child(0).child(1)
        assert not node.adr[u'__r__']

    def test_keep_r_of_previously_fetched_album(self):
        node = self.db.artists._rootNode.child(0).child(0)
        node.adr[u'__r__'] = True
        self.work(work1)
        assert node.adr[u'__r__']

    def test_add_r_only_album(self):
        self.work(work2)
        node = self.db.artists._rootNode.child(0)
        assert node.childCount() == 2
        album = node.child(1)
        assert album.adr[u'__r__']
        assert album.metadata == {u'album': u'test_album2', u'year': u'2010'}

    def test_remove_non_adr_album(self):
        # Should happen if not(a && d && r)
        self.db.artists.upsert(self.db.artists.index(0, 0), (u'album', {
            u'album': u'test_album2',
            u'year': u'2010',
            u'__r__': [True]
        }))
        self.work(work1)
        node = self.db.artists._rootNode.child(0)
        assert node.childCount() == 1
        album = node.child(0)
        assert album.metadata[u'album'] == u'test_album1'
        assert album.metadata[u'year'] == u'2012'
