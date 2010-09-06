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

class MetalArchives(QThread):
    paused=False
    disambiguation=pyqtSignal(str,list)
    error=pyqtSignal(str)
    nextBand=pyqtSignal(str)
    message=pyqtSignal(str,str)
    def __init__(self,library):
        QThread.__init__(self)
        self.library=library
        self.link=u''
    def setPaused(self,state):
        self.paused=state
    def disambigue(self,link):
        self.link=link
    def parse1(self,elem):
        soup=BeautifulSoup(urllib2.urlopen(u'http://www.metal-archives.com/'+elem[u'url']).read())
        return {
                u'choice':u'',
                u'elem':elem,
                u'albums':[unescape(tag.contents[0]) for tag in soup.findAll(u'a',attrs={u'class':u'album'}) if len(tag.contents)!=0],
                u'years':[tag.contents[0][-4:] for tag in soup.findAll(u'td',attrs={u'class':u'album'}) if tag.contents[0][-4:]!=u'0000']
                }
    def parse2(self,soup,elem):
        if soup.findAll(u'script')[0].contents:
            partial=[(elem[u'artist'],soup.findAll(u'script')[0].contents[0][18:-2])]
        else:
            partial=[(r.contents[0],r[u'href']) for r in soup.findAll(u'a') if (r.contents[0]+u' (').startswith(elem[u'artist']+u' (')]
        try:
            if len(partial)!=0:
                if len(partial)==1:
                    soup=BeautifulSoup(urllib2.urlopen(u'http://www.metal-archives.com/'+partial[0][1]).read())
                    self.link=partial[0][1]
                else:
                    self.disambiguation.emit(elem[u'artist'],partial)
                    self.setPaused(True)
                    while(self.paused):
                        pass
                    soup=BeautifulSoup(urllib2.urlopen(u'http://www.metal-archives.com/'+self.link).read())
                result={
                        u'choice':self.link.decode('utf-8'),
                        u'elem':elem,
                        u'albums':[unescape(tag.contents[0]) for tag in soup.findAll(u'a',attrs={u'class':u'album'})],
                        u'years':[tag.contents[0][-4:] for tag in soup.findAll(u'td',attrs={u'class':u'album'})]
                        }
            else:
                result={u'choice':u'no_band',u'elem':elem[u'artist']}
        except urllib2.HTTPError:
            result={u'choice':u'error',u'elem':elem[u'artist']}
        return result
    def done(self,_,result):
        def exists(a,albums):
            state=False
            for alb in albums:
                if a.lower()==alb[u'album'].lower():
                    state=True
                    break
            return state
        if result[u'choice']==u'no_band':
            self.message.emit(result[u'elem'],u'no such band')
        elif result[u'choice']!=u'error':
            elem=self.library[self.library.index(result[u'elem'])]
            self.message.emit(elem[u'artist'],u'success')
            if result[u'choice']:
                elem[u'url']=result[u'choice']
            for a,y in map(None,result[u'albums'],result[u'years']):
                if not exists(a,elem[u'albums']):
                    elem[u'albums'].append({u'album':a,u'year':y,u'digital':False,u'analog':False})
        else:
            self.message.emit(result[u'elem'],u'failed with an error')
    def work(self,elem):
        self.nextBand.emit(elem[u'artist'])
        if elem[u'url']:
            result=self.parse1(elem)
        else:
            artist=urllib2.quote(elem[u'artist'].encode(u'latin-1')).replace(u'%20','+')
            try:
                soup=BeautifulSoup(urllib2.urlopen(
                    u'http://www.metal-archives.com/search.php?string='+artist+u'&type=band').read())
            except urllib2.HTTPError:
                self.message.emit(elem[u'artist'],u'first attempt failed, retrying')
                self.sleep(60)
                try:
                    soup=BeautifulSoup(urllib2.urlopen(
                        u'http://www.metal-archives.com/search.php?string='+artist+u'&type=band').read())
                except urllib2.HTTPError:
                    result={u'choice':u'error',u'elem':elem[u'artist']}
                else:
                    result=self.parse2(soup,elem)
            else:
                result=self.parse2(soup,elem)
        return result
    def run(self):
        requests=threadpool.makeRequests(self.work,self.library,self.done)
        # metal-archives is blocking members on high load, that's why I use only 1 thread here.
        # (It sometimes gets blocked anyway).
        # If they'll ever get a pack of decent servers, this will be fixed by just changing the
        # number below.
        main=threadpool.ThreadPool(1)
        for req in requests:
            main.putRequest(req)
        main.wait()

class Discogs(object):
    def update(self,library):
        def exists(a,lib):
            state=False
            for l in lib:
                if l['album']==a:
                    state=True
                    break
            return state
        from gzip import GzipFile
        from cStringIO import StringIO
        from xml.dom import minidom
        for l in library:
            request=urllib2.Request('http://www.discogs.com/artist/'+l['artist'].replace(' ','+')+'?f=xml&api_key=95b787be0c')
            request.add_header('Accept-Encoding','gzip')
            try:
                try:
                    data=GzipFile(fileobj=StringIO(urllib2.urlopen(request).read())).read()
                except IOError:
                    data=urllib2.urlopen(request).read()
            except urllib2.HTTPError:
                pass
            else:
                xml=minidom.parseString(data)
                releases=[]
                years=[]
                types=('CD, Album','LP, Album')
                for r in xml.getElementsByTagName('release'):
                    if r.childNodes[1].firstChild.data in types and r.firstChild.firstChild.data not in releases:
                        releases.append(r.firstChild.firstChild.data)
                        if len(r.childNodes)>3:
                            years.append(r.childNodes[3].firstChild.data)
                for a,y in map(None,releases,years):
                    if not exists(a,l['albums']):
                        l['albums'].append({'album':a,'year':y,'digital':False,'analog':False})
