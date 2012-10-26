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
from gayeogi.db import local
from PyQt4.QtCore import QSettings


class TestRun(object):
    def setUp(self):
        self.path = os.path.join(__file__, u'..', u'..', u'data', u'empty')
        self.path = os.path.normpath(self.path)
        os.mkdir(self.path)
        self.db = local.DB(self.path)
        self.rpath = os.path.abspath(
            os.path.join(os.path.dirname(__file__), u'..', u'data')
        )
        local._settings = QSettings(
            os.path.join(self.rpath, u'db.conf'), QSettings.NativeFormat
        )
        local._settings.setValue(u'directories', [(self.rpath, True)])

    def tearDown(self):
        os.rmdir(self.path)
        try:
            shutil.move(
                os.path.abspath(os.path.join(self.rpath, u'..', u'test.mp3')),
                os.path.join(self.rpath, u'test.mp3')
            )
        except IOError:
            pass

    def check_db(self):
        root = self.db.artists._rootNode
        assert root.childCount() == 1
        artist = root.child(0)
        assert artist.childCount() == 1
        album = artist.child(0)
        length = len([
            n for n in os.listdir(self.rpath)
            if os.path.isfile(os.path.join(self.rpath, n)) and
            n != u'db.conf'
        ])
        assert album.childCount() == length
        assert len(self.db.index) == length

    def test_add_files(self):
        self.db.run()
        self.check_db()

    def test_remove_files(self):
        self.db.run()
        shutil.move(
            os.path.join(self.rpath, u'test.mp3'),
            os.path.abspath(os.path.join(self.rpath, u'..', u'test.mp3'))
        )
        self.db.run()
        self.check_db()

    def test_files_not_changed(self):
        # Will implement those when logging is in place.
        raise NotImplementedError

    def test_files_changed(self):
        raise NotImplementedError
