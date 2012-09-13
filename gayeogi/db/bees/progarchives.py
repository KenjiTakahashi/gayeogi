# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak © 2011 - 2012
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
from gayeogi.utils import reqread

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


def sense(url, releases):
    """Retrieves releases for specified band id.

    Injected into Bandsensor.

    :url: ID of the current band (it is mbid format here).
    :releases: Types of releases to search for.
    :returns: Tuple in form of (url, [(album, year)]).
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
        u"//h3[pa:enabled(.)]/following-sibling::*[1]"
        u"//td[pa:test(a[2]/strong, span[3])]"
    )
    return (url, result)


def urls(artist):
    """Retrieves all possibly correct urls for specified :artist:.

    :artist: Artist to search for.
    :returns: List of urls.
    """
    urls = list()
    for url, a in glob.iteritems():
        if a.lower().startswith(artist.lower()):
            urls.append(url)
    return urls
