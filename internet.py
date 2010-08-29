# -*- coding: utf-8 -*-

import urllib2
from BeautifulSoup import BeautifulSoup
import threadpool
from PyQt4.QtCore import QThread,pyqtSignal

class MetalArchives(QThread):
    paused=False
    disambiguation=pyqtSignal(str,list)
    error=pyqtSignal(str)
    nextBand=pyqtSignal(str)
    message=pyqtSignal(str)
    def __init__(self,library):
        QThread.__init__(self)
        self.library=library
        self.link=None
    def setPaused(self,state):
        self.paused=state
    def disambigue(self,link):
        self.link=link
    def parse1(self,elem):
        soup=BeautifulSoup(urllib2.urlopen('http://www.metal-archives.com/'+elem['url']).read())
        return {
                'choice':None,
                'elem':elem,
                'albums':[tag.contents[0].title() for tag in soup.findAll('a',attrs={'class':'album'})],
                'years':[tag.contents[0][-4:] for tag in soup.findAll('td',attrs={'class':'album'})]
                }
    def parse2(self,soup,elem):
        if soup.findAll('script')[0].contents:
            partial=[(elem['artist'],soup.findAll('script')[0].contents[0][18:-2])]
        else:
            partial=[(r.contents[0],r['href']) for r in soup.findAll('a') if (r.contents[0]+' (').startswith(elem['artist']+' (')]
        try:
            if len(partial)!=0:
                if len(partial)==1:
                    soup=BeautifulSoup(urllib2.urlopen('http://www.metal-archives.com/'+partial[0][1]).read())
                    self.link=partial[0][1]
                else:
                    self.disambiguation.emit(elem['artist'],partial)
                    self.setPaused(True)
                    while(self.paused):
                        pass
                    soup=BeautifulSoup(urllib2.urlopen('http://www.metal-archives.com/'+self.link).read())
                result={
                        'choice':self.link,
                        'elem':elem,
                        'albums':[tag.contents[0].title() for tag in soup.findAll('a',attrs={'class':'album'})],
                        'years':[tag.contents[0][-4:] for tag in soup.findAll('td',attrs={'class':'album'})]
                        }
            else:
                result='no_band'
        except urllib2.HTTPError:
            result='error'
        return result
    def done(self,_,result):
        def exists(a,albums):
            state=False
            for alb in albums:
                if a.lower()==alb['album'].lower():
                    state=True
                    break
            return state
        if result=='no_band':
            self.message.emit('no such band')
        elif result!='error':
            self.message.emit('success')
            elem=self.library[self.library.index(result['elem'])]
            if result['choice']:
                elem['url']=result['choice']
            for a,y in map(None,result['albums'],result['years']):
                if not exists(a,elem['albums']):
                    elem['albums'].append({'album':a,'year':y,'digital':False,'analog':False})
        else:
            self.message.emit('failed with an error')
    def work(self,elem):
        self.nextBand.emit(elem['artist'])
        if elem['url']:
            result=self.parse1(elem)
        else:
            artist=urllib2.quote(elem['artist'].replace(' ','+').encode('latin-1'))
            try:
                soup=BeautifulSoup(urllib2.urlopen(
                    'http://www.metal-archives.com/search.php?string='+artist+'&type=band').read())
            except urllib2.HTTPError:
                self.message.emit('first attempt failed, retrying')
                self.sleep(60)
                try:
                    soup=BeautifulSoup(urllib2.urlopen(
                        'http://www.metal-archives.com/search.php?string='+artist+'&type=band').read())
                except urllib2.HTTPError:
                    result='error'
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
