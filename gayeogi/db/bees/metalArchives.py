# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak © 2010 - 2012
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


import urllib2
import json
from lxml import etree
from gayeogi.utils import reqread

items = [[u'Full-length', u'Live album', u'Demo'],
        [u'Single', u'EP', u'DVD'],
        [u'Boxed set', u'Split', u'Video/VHS'],
        [u'Best of/Compilation', u'Split album', u'Split DVD / Video']]

name = u'metal-archives.com'


class JParse(json.JSONDecoder):
    """Decode metal-archives JSON object.

    Note: It is meant for internal usage only!
    """
    def __init__(self, artist):
        """Constructs new JParse instance.

        :artist: artist name
        """
        self.artist = artist.lower().replace(u' ', u'')
        json.JSONDecoder.__init__(self, object_hook=self.jparse)

    def jparse(self, element):
        """Parses the given JSON element and return list of artists IDs.

        :element: a JSON element given by json module default decoder
        """
        result = list()
        for e in element[u'aaData']:
            s = e[0].split(u'>', 2)
            a = s[1][0: -3]
            if a.lower().replace(u' ', u'').startswith(self.artist):
                result.append(s[0].rsplit(u'/', 1)[1][:-1])
        return result


def __getalbums(site, releases):
    """Parses discography website for a list of albums and years.

    :site: String containing HTML content.
    :releases: List of release types to check for.
    :returns: List of tuples in form of (album_name, year).
    """
    def __internal(context, albums, types, years):
        for i, t in enumerate(types):
            if t.text in releases:
                __internal.result.append((albums[i].text,
                    years[i].text))
        return False
    __internal.result = list()
    root = etree.HTML(site)
    ns = etree.FunctionNamespace(u'http://fake.gayeogi/functions')
    ns.prefix = u'ma'
    ns[u'test'] = __internal
    root.xpath(u'body/table/tbody/tr[ma:test(td[1]/a, td[2], td[3])]')
    return __internal.result


def sense(url, releases):
    """Retrieves releases for specified band id.

    Injected into Bandsensor.

    :url: ID of the current band.
    :releases: Types of releases to search for.
    :returns: Tuple in form of (url, [(album, year)]).
    """
    soup = reqread(u'http://www.metal-archives.com/band/discography/id/' +
        url + u'/tab/all').decode(u'utf-8')
    return (url, __getalbums(soup, releases))


def urls(artist):
    """Retrieves all possibly correct urls for specified :artist:.

    :artist: Artist to search for.
    :returns: List of urls.
    """
    artist_ = urllib2.quote(
        artist.replace(u'&', u'and').replace(u'/', u'').encode(u'utf-8')
    ).replace(u'%20', u'+')
    json = reqread(
        u"http://www.metal-archives.com/search/ajax-band-search"
        u"/?field=name&query={0}&sEcho=1&iColumns=3&sColumns=&"
        u"iDisplayStart=0&iDisplayLength=100&sNames=%2C%2C".format(artist_)
    )
    return JParse(artist).decode(json)
