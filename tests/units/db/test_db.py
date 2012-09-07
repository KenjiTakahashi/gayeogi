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
from gayeogi.db.local import DB
from PyQt4.QtCore import QSettings


class TestRun(object):
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

    def tearDown(self):
        os.rmdir(self.path)

    def test_add_files(self):
        self.db.run()
        root = self.db.artists._rootNode
        assert root.childCount() == 1
        artist = root.child(0)
        assert artist.childCount() == 1
        album = artist.child(0)
        assert album.childCount() == 4
