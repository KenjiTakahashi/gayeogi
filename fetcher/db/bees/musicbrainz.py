# This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
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
# -*- coding: utf-8 -*-

import urllib2
import json
from lxml import etree
from fetcher.db.bees.bandsensor import Bandsensor
from fetcher.db.bees.beeexceptions import ConnError, NoBandError

items = [[u'Album', u'Single', u'EP'],
        [u'Compilation', u'Soundtrack', u'Spokenword'],
        [u'Interview', u'Audiobook', u'Live'],
        [u'Remix', u'Other', u'Nat']]

name = u'musicbrainz.org'

class JParse(json.JSONDecoder):
    def __init__(self, artist):
        self.artist = artist.lower()
        json.JSONDecoder.__init__(self, object_hook = self.jparse)
    def jparse(self, element):
        try:
            if element[u'name'].lower().startswith(self.artist):
                return element[u'id']
        except KeyError:
            try:
                return element[u'artist-list']
            except KeyError:
                try:
                    return [e for e in element[u'artist'] if e is not None]
                except KeyError:
                    pass

def reqread(url):
    req = urllib2.Request(url)
    req.add_header(u'User-Agent', u'Fetcher/0.6 +')
    try:
        return urllib2.urlopen(req).read()
    except (urllib2.HTTPError, urllib2.URLError):
        raise ConnError()

def __getalbums(site):
    def __internal(context, albums, years):
        if years:
            try:
                if __internal.result[albums[0]] == u'0' \
                        or __internal.result[albums[0]] > years[0]:
                    __internal.result[albums[0]] = years[0]
            except KeyError:
                __internal.result[albums[0]] = years[0]
        else:
            try:
                __internal.result[albums[0]]
            except KeyError:
                __internal.result[albums[0]] = u'0'
        return False
    __internal.result = dict()
    ns = etree.FunctionNamespace(u'http://fake.fetcher/functions')
    ns.prefix = u'mb'
    ns[u'test'] = __internal
    root = etree.XML(site)
    root.xpath(
            u'n:release-list/n:release[mb:test(n:title/text(), n:date/text())]',
            namespaces = {u'n': u'http://musicbrainz.org/ns/mmd-2.0#'})
    count = root.xpath(u'n:release-list/@count',
            namespaces = {u'n': u'http://musicbrainz.org/ns/mmd-2.0#'})
    return (__internal.result, int(count[0]))

def __sense(url, releases):
    """Retrieve releases for specified band id.
    Injected into Bandsensor.

    Arguments:
    url -- ID of the current band (it's mbid format here)
    releases -- types of releases to search for

    Note: It is meant for internal usage only!
    """
    result = dict()
    offset = 0
    count = 100
    while count > 0:
        soup = reqread(
                u'http://www.musicbrainz.org/ws/2/release?artist=' + url
                + u'&type=' + u'|'.join(releases).lower() + u'&offset='
                + unicode(offset) + u'&limit=100')
        (partial, n) = __getalbums(soup)
        result.update(partial)
        count = n - count
        offset += 100
    return (url, list(result.iteritems()))

def work(artist, element, urls, releases):
    """Retrieve new or updated info for specified artist.

    Arguments:
    artist -- artist to check against
    element -- db element containing existing info (it is db[<artist_name>])
    urls -- urls previously retrieved for given artist
    releases -- types of releases to check for

    Note: Should be threaded in real application.
    """
    if urls and u'musicbrainz' in urls.keys():
        (url, albums) = __sense(urls[u'musicbrainz'], releases)
        return {u'choice': url,
                u'result': albums,
                u'errors': set(),
                u'artist': artist
                }
    else:
        artist_ = urllib2.quote(
                artist.replace(u'&', u'and').replace(u'/', u'').encode(
                    u'utf-8')).replace(u'%20%20', u'+')
        try:
            urls_ = reqread(
                    u'http://search.musicbrainz.org/ws/2/artist/?query=artist:'
                    + artist_ + u'*&fmt=json')
        except (urllib2.HTTPError, urllib2.URLError):
            raise ConnError()
        else:
            if not urls_:
                raise NoBandError()
            else:
                try:
                    sensor = Bandsensor(__sense, JParse(artist).decode(urls_),
                            element, releases)
                    data = sensor.run()
                except (urllib2.HTTPError, urllib2.URLError):
                    raise ConnError()
                else:
                    if data:
                        return {u'choice': data[0],
                                u'result': data[1],
                                u'errors': sensor.errors
                                }
                    else:
                        raise NoBandError()
