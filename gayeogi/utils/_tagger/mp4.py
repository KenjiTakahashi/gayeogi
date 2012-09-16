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


from mutagen import mp4


class MP4(object):
    def __init__(self, filename):
        self.filename = filename
        self.file = mp4.MP4(filename)
        self._ids = {
            "\xa9nam": "title",
            "\xa9alb": "album",
            "\xa9ART": "artist",
            "aART": "albumartist",
            "\xa9wrt": "composer",
            "\xa9day": "date",
            "\xa9cmt": "comment",
            "\xa9grp": "grouping",
            "\xa9gen": "genre",
            "tmpo": "bpm",
            "\xa9too": "encodedby",
            "cprt": "copyright",
            "soal": "albumsort",
            "soaa": "albumartistsort",
            "soar": "artistsort",
            "sonm": "titlesort",
            "soco": "composersort"
        }
        self._tupleids = {
            "disk": "discnumber",
            "trkn": "tracknumber"
        }

    def readAll(self):
        meta = dict()
        for k, v in self.file.iteritems():
            if k in self._tupleids:
                current, total = v[0]
                if total:
                    meta[self._tupleids[k]] = "{0}/{1}".format(current, total)
                else:
                    meta[self._tupleids[k]] = unicode(current)
            else:
                meta[self._ids[k]] = unicode(v[0])
        return meta
