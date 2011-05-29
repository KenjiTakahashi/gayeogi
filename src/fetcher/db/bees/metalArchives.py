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
from bandsensor import Bandsensor
from beeexceptions import ConnError, NoBandError

class JParse(json.JSONDecoder):
    """Decode metal-archives JSON object.
    
    Note: It is meant for internal usage only!
    """
    def __init__(self, artist):
        self.artist = artist.lower() + u'('
        json.JSONDecoder.__init__(self, object_hook = self.jparse)
    def jparse(self, element):
        """Parse the given JSON element and return list of artists IDs.

        Arguments:
        element -- a JSON element given by json module default decoder
        """
        result = list()
        for e in element[u'aaData']:
            s = e[0].split(u'>', 2)
            a = s[1][0: -3]
            if (a.lower() + u'(').startswith(self.artist):
                result.append(s[0].rsplit(u'/', 1)[1][:-1])
        return result

def __getalbums(site, releases):
    """Parse discography website and return list of albums and years.

    Arguments:
    site -- string containing HTML content
    releases -- list of release types to check for

    Return value:
    a list of tuples in a form of (<album_name>, <year>)
    """
    result = list()
    def __internal(context, albums, types, years):
        for i, t in enumerate(types):
            if t.text in releases:
                result.append((albums[i].text,
                    years[i].text))
        return False
    root = etree.HTML(site)
    ns = etree.FunctionNamespace(u'http://fake.fetcher/functions')
    ns.prefix = u'ma'
    ns[u'test'] = __internal
    root.xpath(u'body/table/tbody/tr[ma:test(td[1]/a, td[2], td[3])]')
    return result

def __sense(url, releases):
    """Function injected into Bandsensor

    Arguments:
    url -- ID of the current band
    releases -- types of releases to search for

    Note: It is meant for internal usage only!
    """
    raise ConnError()
    try:
        soup = urllib2.urlopen(
                u'http://www.metal-archives.com/band/discography/id/' +
                url + u'/tab/all').read().decode(u'utf-8')
    except (urllib2.HTTPError, urllib2.URLError):
        raise ConnError()
    else:
        return (url, __getalbums(soup, releases))

def __parse1(element, url, releases):
    """Retrieve updated info on an existing release and return results.

    Arguments:
    element -- db element containing existing info (it is db[<artist_name>])
    url -- url pointing at the given artist
    releases -- types of releases to check for

    Note: It is meant for internal usage only!
    """
    try:
        soup = urllib2.urlopen(u'http://www.metal-archives.com/band/discography/id/' +
                url + u'/tab/all').read().decode(u'utf-8')
    except (urllib2.HTTPError, urllib2.URLError):
        raise ConnError()
    return {u'choice': url,
            u'artist': element,
            u'result': __getalbums(soup, releases),
            u'errors': []
            }

def __parse2(json, artist, element, releases):
    """Retrieve info on an new release and return list of results.

    Arguments:
    json -- Actually, a string retrieved from metal-archives JSON search
    artist -- artist to check against
    element -- db element containing existing info (it is db[<artist_name>])
    releases -- types of releases to check for

    Note: It is meant for internal usage only!
    """
    urls = JParse(artist).decode(json)
    try:
        sensor = Bandsensor(__sense, urls, element, releases)
        data = sensor.run()
    except (urllib2.HTTPError, urllib2.URLError):
        raise ConnError()
    else:
        if data:
            return {u'choice': data[0],
                    u'artist': artist,
                    u'result': data[1],
                    u'errors': sensor.errors
                    }
        else:
            raise NoBandError()

def work(artist, element, urls, releases):
    """Retrieve new or updated info for specified artist.

    Arguments:
    artist -- artist to check against
    element -- db element containing existing info (it is db[<artist_name>])
    urls -- urls previously retrieved for given artist
    releases -- types of releases to check for

    Note: Should be threaded in real application.
    """
    if urls and u'metalArchives' in urls.keys():
        result = __parse1(element, urls[u'metalArchives'], releases)
        result[u'artist'] = artist
    else:
        artist_ = urllib2.quote(artist.encode(u'latin-1')).replace(u'%20', u'+')
        try:
            json = urllib2.urlopen(
                    u'http://www.metal-archives.com/search/ajax-band-search/?field=name&query=' +
                    artist_ +
                    '&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=100&sNames=%2C%2C'
                    ).read()
        except (urllib2.HTTPError, urllib2.URLError):
            raise ConnError()
        else:
            result = __parse2(json, artist, element, releases)
    return result
    #def done(self,_,result):
    #        elem = self.library[result[u'artist']]
    #        elem[u'url'][u'metalArchives'] = result[u'choice']
    #        added = False
    #        toDelete = []
    #        for k, v in elem[u'albums'].iteritems():
    #            if k not in result[u'albums']:
    #                if not v[u'digital'] and not v[u'analog']:
    #                    toDelete.append(k)
    #                else:
    #                    v[u'remote'] = False
    #        for todel in toDelete:
    #            del elem[u'albums'][todel]
    #        def true(eee):
    #            for e in eee:
    #                if e[u'remote']:
    #                    return True
    #            return False
    #        if not true(elem[u'albums'].values()):
    #            del elem[u'url'][u'metalArchives']
    #        for a, y in map(None, result[u'albums'], result[u'years']):
    #            try:
    #                elem[u'albums'][a]
    #            except KeyError:
    #                added = True
    #                elem[u'albums'][a] = {
    #                        u'date': y,
    #                        u'tracks': {},
    #                        u'digital': False,
    #                        u'analog': False,
    #                        u'remote': True
    #                        }
    #            else:
    #                elem[u'albums'][a][u'remote'] = True
    #        if added and toDelete:
    #            message = u'Something has been changed'
    #        elif added:
    #            message = u'Something has been added'
    #        elif toDelete:
    #            message = u'Something has been removed'
    #        else:
    #            message = u'Nothing has been changed'
    #        self.errors.emit(u'metal-archives.com',
    #                u'info',
    #                result[u'artist'],
    #                message)
    #def run(self):
    #    if not self.behaviour:
    #        temp = {k: v for k, v in self.library.iteritems()
    #                if not v[u'url'] or u'metalArchives' in v[u'url'].keys()}
    #        if temp:
    #            requests = threadpool.makeRequests(self.work, temp, self.done)
    #        else:
    #            requests = None
    #    else:
    #        requests = threadpool.makeRequests(self.work, self.library, self.done)
    #    # metal-archives is blocking members on high load, that's why I use only 1 thread here.
    #    # (It sometimes gets blocked anyway).
    #    # If they'll ever get a pack of decent servers, this will be fixed by just changing the
    #    # number below.
    #    if requests:
    #        main = threadpool.ThreadPool(1)
    #        for req in requests:
    #            main.putRequest(req)
    #        main.wait()
