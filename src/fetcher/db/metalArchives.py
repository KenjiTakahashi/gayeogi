# -*- coding: utf-8 -*-

import urllib2
from BeautifulSoup import BeautifulSoup
import threadpool
from PyQt4.QtCore import QThread,pyqtSignal
from re import sub
from htmlentitydefs import name2codepoint

def unescape(text):
    """Removes HTML or XML character references 
      and entities from a text string.
      keep &amp;, &gt;, &lt; in the source code.
   from Fredrik Lundh
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                print "erreur de valeur"
        else:
            # named entity
            try:
                if text[1:-1] == "amp":
                    text = "&amp;amp;"
                elif text[1:-1] == "gt":
                    text = "&amp;gt;"
                elif text[1:-1] == "lt":
                    text = "&amp;lt;"
                else:
                    text = unichr(name2codepoint[text[1:-1]])
            except KeyError:
                print "keyerror"
        return text # leave as is
    return sub("&#?\w+;", fixup, text)

class Bandsensor(object):
    def __init__(self, artists, albums):
        self.artists = artists
        self.albums = albums
        self.results = {}
    def sense(self, data):
        soup = BeautifulSoup(urllib2.urlopen(u'http://www.metal-archives.com/' + data).read())
        albums = [unescape(tag.contents[0])
                for tag in soup.findAll(u'a', attrs = {u'class': u'album'})]
        years = [tag.contents[0][-4:]
                for tag in soup.findAll(u'td', attrs={u'class': u'album'})]
        for album in albums:
            for eAlbum in self.albums:
                if album.lower() == eAlbum[u'album'].lower():
                    return {data: (albums, years)}
    def finish(self, _, result):
        if result:
            self.results[result.keys()[0]] = result.values()[0]
    def run(self):
        requests = threadpool.makeRequests(self.sense, self.artists, self.finish)
        main = threadpool.ThreadPool(3)
        for req in requests:
            main.putRequest(req)
        main.wait()
        values = {}
        for data, (albums, _) in self.results.items():
            for album in albums:
                for eAlbum in self.albums:
                    if album.lower() == eAlbum[u'album'].lower():
                        if data in values.keys():
                            values[data] += 1
                        else:
                            values[data] = 1
        if values.keys():
            best = values.keys()[0]
            for k, v in values.items():
                if v > values[best]:
                    best = k
            return (best, self.results[best])

class MetalArchives(QThread):
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    stepped = pyqtSignal(unicode)
    def __init__(self,library):
        QThread.__init__(self)
        self.library=library
    def parse1(self,elem):
        soup=BeautifulSoup(urllib2.urlopen(u'http://www.metal-archives.com/'+elem[u'url']).read())
        return {
                u'choice':u'',
                u'elem':elem,
                u'albums':[unescape(tag.contents[0].replace('/',' ')) for tag in soup.findAll(u'a',attrs={u'class':u'album'}) if len(tag.contents)!=0],
                u'years':[tag.contents[0][-4:] for tag in soup.findAll(u'td',attrs={u'class':u'album'}) if tag.contents[0][-4:]!=u'0000']
                }
    def parse2(self,soup,elem):
        if soup.findAll(u'script')[0].contents:
            partial=[soup.findAll(u'script')[0].contents[0][18:-2]]
        else:
            partial=[r[u'href'] for r in soup.findAll(u'a') if (r.contents[0]+u' (').startswith(elem[u'artist']+u' (')]
        try:
            sensor = Bandsensor(partial, elem[u'albums'])
            data = sensor.run()
            if data:
                result = {
                        u'choice': data[0],
                        u'elem': elem,
                        u'albums': data[1][0],
                        u'years': data[1][1]
                        }
            else:
                result = {u'choice': u'no_band', u'elem': elem[u'artist']}
        except urllib2.HTTPError:
            result={u'choice':u'error',u'elem':elem[u'artist']}
        return result
    def done(self,_,result):
        def exists(a,albums):
            for alb in albums:
                if a.lower()==alb[u'album'].lower():
                    return True
            return False
        def exists2(a, albums):
            for album in albums:
                if a.lower() == album.lower():
                    return True
            return False
        if result[u'choice']==u'no_band':
            self.errors.emit(u'metal-archives.com',
                    u'errors',
                    result[u'elem'],
                    u'No such band has been found')
        elif result[u'choice'] == u'error':
            self.errors.emit(u'metal-archives.com',
                    u'errors',
                    result[u'elem'],
                    u'An unknown error occured (no internet?)')
        elif result[u'choice'] != u'block':
            elem=self.library[self.library.index(result[u'elem'])]
            self.errors.emit(u'metal-archives.com',
                    u'info',
                    elem[u'artist'],
                    u'Successfully retrieved band contents')
            if result[u'choice']:
                elem[u'url']=result[u'choice']
            for a,y in map(None,result[u'albums'],result[u'years']):
                for album in elem[u'albums']:
                    if not album[u'digital'] and not album[u'analog']\
                            and not exists2(album[u'album'], result[u'albums']):
                        del elem[u'albums'][elem[u'albums'].index(album)]
                if not exists(a,elem[u'albums']):
                    elem[u'albums'].append({
                        u'album': a,
                        u'date': y,
                        u'tracks': [],
                        u'digital': False,
                        u'analog': False
                        })
    def work(self,elem):
        self.stepped.emit(elem[u'artist'])
        if elem[u'url']:
            result=self.parse1(elem)
        else:
            artist=urllib2.quote(elem[u'artist'].encode(u'latin-1')).replace(u'%20','+')
            try:
                soup=BeautifulSoup(urllib2.urlopen(
                    u'http://www.metal-archives.com/search.php?string='+artist+u'&type=band').read())
            except urllib2.HTTPError:
                result = {u'choice': u'block', u'elem': elem[u'artist']}
                self.errors.emit(u'metal-archives.com',
                        u'errors',
                        result[u'elem'],
                        u'No internet or blocked by upstream (Delaying for 60 secs)')
                self.stepped.emit(u'Waiting...')
                self.sleep(60)
            else:
                result=self.parse2(soup,elem)
        return result
    def run(self):
        requests = threadpool.makeRequests(self.work, self.library, self.done)
        # metal-archives is blocking members on high load, that's why I use only 1 thread here.
        # (It sometimes gets blocked anyway).
        # If they'll ever get a pack of decent servers, this will be fixed by just changing the
        # number below.
        main = threadpool.ThreadPool(1)
        for req in requests:
            main.putRequest(req)
        main.wait()
