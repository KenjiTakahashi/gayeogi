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
from gayeogi.utils import Tagger


class TestTagger(object):
    def setUp(self):
        self.path = os.path.join(__file__, u'..', u'..', u'data')
        self.path = os.path.normpath(self.path)
        self.result = {
            u'artist': u'test_artist1',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }
        self.result2 = {
            u'artist': u'test_artist1',
            u'date': u'2012',
            u'year': u'2012',
            u'album': u'test_album1',
            u'tracknumber': u'12',
            u'title': u'test_title1'
        }

    def readAllTest(self, ext, result):
        path = os.path.join(self.path, u'test.{0}'.format(ext))
        tag = Tagger(path)
        result[u'__filename__'] = [path]
        assert tag.readAll() == result

    def test_readAll_flac(self):
        self.readAllTest(u'flac', self.result2)

    def test_readAll_asf(self):
        self.readAllTest(u'wma', self.result)

    def test_readAll_wavpack(self):
        result = self.result.copy()
        result[u'track'] = u'12'
        self.readAllTest(u'wv', result)

    def test_readAll_musepack(self):
        result = self.result.copy()
        result[u'track'] = u'12'
        self.readAllTest(u'mpc', result)

    def test_readAll_ogg(self):
        self.readAllTest(u'ogg', self.result2)

    def test_readAll_ape(self):
        result = self.result.copy()
        result[u'track'] = u'12'
        self.readAllTest(u'ape', result)

    def test_readAll_mp3(self):
        self.readAllTest(u'mp3', self.result2)

    def test_readAll_mp4(self):
        self.readAllTest(u'mp4', self.result2)
