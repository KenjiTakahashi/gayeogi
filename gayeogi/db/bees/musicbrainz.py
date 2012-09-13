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

items = [[u'Album', u'Single', u'EP'],
        [u'Compilation', u'Soundtrack', u'Spokenword'],
        [u'Interview', u'Audiobook', u'Live'],
        [u'Remix', u'Other', u'Nat']]

name = u'musicbrainz.org'


class JParse(json.JSONDecoder):
    def __init__(self, artist):
        self.artist = artist.lower().strip().replace(u' ', u'')
        json.JSONDecoder.__init__(self, object_hook=self.jparse)

    def jparse(self, element):
        try:
            if element[u'name'].lower().replace(u' ',
            u'').startswith(self.artist):
                return element[u'id']
        except KeyError:
            try:
                return element[u'artist-list']
            except KeyError:
                try:
                    return [e for e in element[u'artist'] if e is not None]
                except KeyError:
                    pass


def __getalbums(site, existing):
    """Parses site for albums.

    :site: Site's XML to parse.
    :existing: Results already received from previous part.
    :returns: A tuple in form of (results, result_count).
              where results -> [album_name] = year
    """
    def __internal(context, albums, years):
        albums = albums[0].text
        try:
            years = years[0].text
        except IndexError:
            years = u'0'
        try:
            if (__internal.result[albums] == u'0' or
            __internal.result[albums] > years):
                __internal.result[albums] = years
        except KeyError:
            __internal.result[albums] = years
        return False
    __internal.result = existing
    ns = etree.FunctionNamespace(u'http://fake.gayeogi/functions')
    ns.prefix = u'mb'
    ns[u'test'] = __internal
    root = etree.XML(site)
    root.xpath(
        u'n:release-list/n:release[mb:test(n:title, n:date)]',
        namespaces={u'n': u'http://musicbrainz.org/ns/mmd-2.0#'})
    count = root.xpath(u'n:release-list/@count',
        namespaces={u'n': u'http://musicbrainz.org/ns/mmd-2.0#'})
    return (__internal.result, int(count[0]))


def sense(url, releases):
    """Retrieves releases for specified band id.

    Injected into Bandsensor.

    :url: ID of the current band (it is mbid format here).
    :releases: Types of releases to search for.
    :returns: Tuple in form of (url, [(album, year)]).
    """
    result = dict()
    offset = 0
    count = 100
    partial = dict()
    while count > 0:
        soup = reqread(
            u'http://www.musicbrainz.org/ws/2/release?artist=' + url
            + u'&type=' + u'|'.join(releases).lower() + u'&offset='
            + unicode(offset) + u'&limit=100')
        (partial, n) = __getalbums(soup, partial)
        result.update(partial)
        count = n - count - offset
        offset += 100
    return (url, list(result.iteritems()))


def urls(artist):
    """Retrieves all possibly correct urls for specified :artist:.

    :artist: Artist to search for.
    :returns: List of urls.
    """
    artist_ = urllib2.quote(artist.replace(u'/', u'').encode(
                u'utf-8')).replace(u'%20', u'+')
    return reqread(
            u'http://search.musicbrainz.org/ws/2/artist/?query=artist:'
            + artist_ + u'*&fmt=json')
