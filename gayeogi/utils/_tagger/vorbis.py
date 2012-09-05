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
from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.wavpack import WavPack
from mutagen.musepack import Musepack
from mutagen import File


class Vorbis(object):
    def __init__(self, filename):
        self.filename = filename
        ext = os.path.splitext(filename)[1].lower()
        if ext == u'.flac':
            self.file = FLAC(filename)
        elif ext == u'.asf':
            self.file = ASF(filename)
        elif ext == u'.wv':
            self.file = WavPack(filename)
        elif ext in [u'.mpc', u'.mpp', u'.mp+']:
            self.file = Musepack(filename)
        elif ext in [u'.ogg', u'.ape']:
            self.file = File(filename)

    def readAll(self):
        data = {k: v[0] for k, v in self.file.iteritems()}
        for pkey, nkey in [(u'year', u'date'), (u'tracknumber', u'track')]:
            if pkey not in data:
                try:
                    data[pkey] = data[nkey]
                except KeyError:
                    pass
        return data
