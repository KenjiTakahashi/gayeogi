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
from _tagger import ID3, MP4, Vorbis


class Tagger(object):
    """Docstring for Tag """

    def __init__(self, filename):
        """@todo: to be defined

        :filename: @todo
        """
        self.filename = filename
        ext = os.path.splitext(self.filename)[1].lower()
        if ext == u'.mp3':
            self.type = ID3
        elif ext in [u'.mp4', u'.m4a', u'.mpeg4', u'.aac']:
            self.type = MP4
        else:
            self.type = Vorbis

    def readAll(self):
        """@todo: Docstring for readAll

        :returns: @todo
        """
        try:
            meta = self.type(self.filename).readAll()
        except TypeError:
            return None
        else:
            try:
                _ = meta[u'__filename__']
            except KeyError:
                meta[u'__filename__'] = [self.filename]
            else:
                meta[u'__filename__'] = [self.filename, _]
            return meta
