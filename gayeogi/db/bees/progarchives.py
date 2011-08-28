# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2011
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

from lxml import etree
from gayeogi.db.bandsensor import Bandsensor
from gayeogi.db.utils import reqread
from gayeogi.db.bees.beeexceptions import NoBandError

items = [[u'Full-length', u'Live album', u'Video'],
        [u'Best Of/Compilation', u'Single/EP']]

di = {
    u'Full-length': u'Albums',
    u'Live album': u'Live Albums',
    u'Video': u'Videos',
    u'Best Of/Compilation': u'Boxset & Compilations',
    u'Single/EP': u'Official Singles'
}

name = u'progarchives.com'

glob = dict()
def init():
    res = reqread(
        u'http://www.progarchives.com/bands-alpha.asp?letter=*'
    ).decode(u'latin-1').encode(u'utf-8')
    def __internal(context, artist, url):
        glob[str(url[0])[14:]] = artist[0].text
        return False
    root = etree.HTML(res)
    ns = etree.FunctionNamespace(u'http://fake.gayeogi/functions')
    ns.prefix = u'pa'
    ns[u'test'] = __internal
    root.xpath(u'//td/a[pa:test(strong, @href)]')

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
    res = reqread(
        u'http://www.progarchives.com/artist.asp?id=' + url
    ).decode(u'latin-1').encode(u'utf-8')
    artist = glob[url]
    def __enabled(context, element):
        for release in releases:
            if element[0].text.lower().startswith(
                artist.lower() + u' ' + di[release].lower()
            ):
                return True
        return False
    result = list()
    def __internal(context, albums, years):
        result.append((albums[0].text.strip(), years[0].text.strip()))
        return False
    root = etree.HTML(res)
    ns = etree.FunctionNamespace(u'http://fake.gayeogi/functions')
    ns.prefix = u'pa'
    ns[u'test'] = __internal
    ns[u'enabled'] = __enabled
    root.xpath(
        u'//h3[pa:enabled(.)]/following-sibling::*[1]//td[pa:test(a[2]/strong, span[3])]'
    )
    return (url, result)

def work(artist, element, urls, releases):
    """Retrieves new or updated info for specified artist.

    Also fetches a list of all bands and urls if it doesn't exist yet.

    Args:
        artist: artist to check against
        element: db element containing existing info (it is db[<artist_name>])
        urls: urls previously retrieved for given artist
        releases: types of releases to check for

    Note: Should be threaded in real application.

    """
    if urls and u'progarchives.com' in urls.keys():
        (url, albums) = __sense(urls[u'progarchives'], releases)
        return {
            u'choice': url,
            u'result': albums,
            u'errors': set(),
            u'artist': artist
        }
    artists = list()
    for (url, a) in glob.iteritems():
        if a.lower().startswith(artist.lower()):
            artists.append(url)
    if not artists:
        raise NoBandError()
    sensor = Bandsensor(__sense, artists, element, releases)
    data = sensor.run()
    if not data:
        raise NoBandError()
    return {
        u'choice': data[0],
        u'result': data[1],
        u'errors': sensor.errors
    }
