# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2010 - 2011
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
from gayeogi.db.bandsensor import Bandsensor
from gayeogi.db.utils import reqread
from gayeogi.db.bees.beeexceptions import NoBandError

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

        Args:
            artist (str): artist name

        """
        self.artist = artist.lower().replace(u' ', u'')
        json.JSONDecoder.__init__(self, object_hook = self.jparse)
    def jparse(self, element):
        """Parses the given JSON element and return list of artists IDs.

        Args:
            element (dict): a JSON element given by json module default decoder

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

    Args:
        site: string containing HTML content
        releases: list of release types to check for

    Returns:
        list -- of tuples in a form of (<album_name>, <year>)

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

def __sense(url, releases):
    """Retrieves releases for specified band id.

    Injected into Bandsensor.

    Args:
        url: ID of the current band
        releases: types of releases to search for

    Returns:
        tuple -- (<url>, <list-of-tuples> -- (<album>, <year>))

    Note: It is meant for internal usage only!

    """
    soup = reqread(u'http://www.metal-archives.com/band/discography/id/' +
        url + u'/tab/all').decode(u'utf-8')
    return (url, __getalbums(soup, releases))

def __parse2(json, artist, element, releases):
    """Retrieves info on an new release for a list of results.

    Args:
        json: Actually, a string retrieved from metal-archives JSON search
        artist: artist to check against
        element: db element containing existing info (it is db[<artist_name>])
        releases: types of releases to check for

    Note: It is meant for internal usage only!

    """
    urls = JParse(artist).decode(json)
    if not urls:
        raise NoBandError()
    sensor = Bandsensor(__sense, urls, element, releases)
    data = sensor.run()
    if not data:
        raise NoBandError()
    return {
        u'choice': data[0],
        u'result': data[1],
        u'errors': sensor.errors
    }

def work(artist, element, urls, releases):
    """Retrieves new or updated info for specified artist.

    Args:
        artist: artist to check against
        element: db element containing existing info (it is db[<artist_name>])
        urls: urls previously retrieved for given artist
        releases: types of releases to check for

    Note: Should be threaded in real application.

    """
    if urls and u'metalArchives' in urls.keys():
        (url, albums) = __sense(urls[u'metalArchives'], releases)
        return {
            u'choice': url,
            u'result': albums,
            u'errors': set(),
            u'artist': artist
        }
    artist_ = urllib2.quote(
        artist.replace(u'&', u'and').replace(u'/', u'').encode(u'utf-8')
    ).replace(u'%20', u'+')
    json = reqread(
        u'http://www.metal-archives.com/search/ajax-band-search/?field=name&query=' +
        artist_ +
        '&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=100&sNames=%2C%2C'
    )
    return __parse2(json, artist, element, releases)
