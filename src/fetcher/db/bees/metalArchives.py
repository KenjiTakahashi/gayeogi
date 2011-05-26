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

class Error(Exception):
    """General Error class."""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class NoBandError(Error):
    """Raised in case specified band has not been found in the database."""
    def __init__(self):
        self.message = u'No such band has been found.'

class ConnError(Error):
    """Raised in case an connection error appeared."""
    def __init__(self):
        self.message = u'An unknown error occurred (no internet?).'

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
                result.append((albums[i].text.encode(u'utf-8'),
                    years[i].text.encode(u'utf-8')))
        return False
    root = etree.HTML(site)
    ns = etree.FunctionNamespace(u'http://fake.fetcher/functions')
    ns.prefix = u'ma'
    ns[u'test'] = __internal
    root.xpath(u'body/table/tbody/tr[ma:test(td[1]/a, td[2], td[3])]')
    return result

#class Bandsensor(object):
#    def __init__(self, artists, albums, releases):
#        self.artists = artists
#        self.albums = albums
#        self.releases = releases
#        self.results = {}
#    def sense(self, data):
#        try:
#            soup = BeautifulSoup(urllib2.urlopen(u'http://www.metal-archives.com/' + data).read())
#        except urllib2.HTTPError:
#            pass
#        else:
#            albums = []
#            years = []
#            for release in self.releases:
#                navigation = [t for t in soup.findAll(text = re.compile(u'%s.*' % release))]
#                albums.extend([unescape(a.previous.previous.previous.previous.string)
#                    for a in navigation])
#                years.extend([unescape(y[-4:]) for y in navigation])
#            for album in albums:
#                for eAlbum in self.albums.keys():
#                    if album.lower() == eAlbum.lower():
#                        return {data: (albums, years)}
#    def finish(self, _, result):
#        if result:
#            self.results.update(result)
#    def run(self):
#        #drop threadpool here!
#        requests = threadpool.makeRequests(self.sense, self.artists, self.finish)
#        main = threadpool.ThreadPool(5)
#        for req in requests:
#            main.putRequest(req)
#        main.wait()
#        values = {}
#        for data, (albums, _) in self.results.items():
#            for album in albums:
#                for eAlbum in self.albums.keys():
#                    if album.lower() == eAlbum.lower():
#                        if data in values.keys():
#                            values[data] += 1
#                        else:
#                            values[data] = 1
#        if values.keys():
#            best = values.keys()[0]
#            for k, v in values.items():
#                if v > values[best]:
#                    best = k
#            return (best, self.results[best])

def __parse1(element, releases):
    """Retrieve updated info on an existing release.

    Arguments:
    element -- db element containing existing info (it is db[<artist_name>])
    releaseTypes -- types of releases to check for

    Note: It is meant for internal usage only!
    """
    soup = urllib2.urlopen(u'http://www.metal-archives.com/band/discography/id/' +
            element[u'url'][u'metalArchives'] +
            u'/tab/all').read().decode(u'utf-8')
    return {u'choice': element[u'url'][u'metalArchives'],
            u'artist': element,
            u'result': __getalbums(soup, releases)
            }

def __parse2(json, artist, element, releaseTypes):
    """Retrieve info on an new release and return list of results.

    Arguments:
    json -- Actually, a string retrieved from metal-archives JSON search
    artist -- artist to check against
    element -- db element containing existing info (it is db[<artist_name>])
    releaseTypes -- types of releases to check for

    Note: It is meant for internal usage only!
    """
    urls = JParse(artist).decode(json)
    try:
        sensor = Bandsensor(urls, element[u'albums'], releaseTypes)
        data = sensor.run()
    except urllib2.HTTPError:
        raise ConnError()
    else:
        if data:
            result = {
                    u'choice': data[0],
                    u'artist': artist,
                    u'albums': data[1][0],
                    u'years': data[1][1],
                    u'result': data
                    }
        else:
            raise NoBandError()
    return result

def work(artist, element, releaseTypes):
    """Retrieve new or updated info for specified artist.

    Arguments:
    artist -- artist to check against
    element -- db element containing existing info (it is db[<artist_name>])
    releaseTypes -- types of releases to check for

    Note: Should be threaded in real application.
    """
    if element[u'url'] and u'metalArchives' in element[u'url'].keys():
        result = __parse1(element, releaseTypes)
        result[u'artist'] = artist
    else:
        artist_ = urllib2.quote(artist.encode(u'latin-1')).replace(u'%20', u'+')
        try:
            json = urllib2.urlopen(
                    u'http://www.metal-archives.com/search/ajax-band-search/?field=name&query=' +
                    artist_ +
                    '&sEcho=1&iColumns=3&sColumns=&iDisplayStart=0&iDisplayLength=100&sNames=%2C%2C'
                    ).read()
        except urllib2.HTTPError:
            raise ConnError()
            #self.sleep(60) # should we sleep here or what?
        else:
            result = __parse2(json, artist, element, releaseTypes)
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
