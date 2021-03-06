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


from mutagen import id3


class ID3(object):
    def __init__(self, filename):
        self.filename = filename
        self.file = id3.ID3(filename)
        self._ids = {
            "TIT1": "grouping",
            "TIT2": "title",
            "TIT3": "version",
            "TPE1": "artist",
            "TPE2": "performer",
            "TPE3": "conductor",
            "TPE4": "arranger",
            "TEXT": "lyricist",
            "TCOM": "composer",
            "TENC": "encodedby",
            "TALB": "album",
            "TRCK": "tracknumber",
            "TPOS": "discnumber",
            "TSRC": "isrc",
            "TCOP": "copyright",
            "TPUB": "organization",
            "TSST": "discsubtitle",
            "TOLY": "author",
            "TMOO": "mood",
            "TBPM": "bpm",
            "TDRC": "date",
            "TDOR": "originaldate",
            "TOAL": "originalalbum",
            "TOPE": "originalartist",
            "WOAR": "website",
            "TSOP": "artistsort",
            "TSOA": "albumsort",
            "TSOT": "titlesort",
            "TSO2": "albumartistsort",
            "TSOC": "composersort",
            "TMED": "media",
            "TCMP": "compilation",
            # TLAN requires an ISO 639-2 language code, check manually
            #"TLAN": "language"
        }

    def readAll(self):
        return {self._ids[k]: unicode(v.text[0])
                for k, v in self.file.iteritems()}
