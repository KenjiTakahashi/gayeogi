# -*- coding: utf-8 -*-

import urllib2
import threadpool
from gzip import GzipFile
from cStringIO import StringIO
from xml.dom import minidom
from PyQt4.QtCore import QThread,pyqtSignal

class Discogs(QThread):
    paused=False
    disambiguation=pyqtSignal(str,list)
    error=pyqtSignal(str)
    nextBand=pyqtSignal(str)
    message=pyqtSignal(str,str)
    def __init__(self,library):
        QThread.__init__(self)
        self.library=library
    def parse(self,elem,data=None):
        if data:
            artist=urllib2.quote(elem[u'artist'].encode(u'latin-1')).replace(u'%20',u'+')
            url=u'http://www.discogs.com/artist/'+artist+u'?f=xml&api_key=95b787be0c'
        else:
            url=elem[u'url']
        request=urllib2.Request(url)
        request.add_header(u'Accept-Encoding',u'gzip')
        try:
            temp=urllib2.urlopen(request).read()
            try:
                data=GzipFile(fileobj=StringIO(temp)).read()
            except IOError:
                data=temp
        except urllib2.HTTPError:
            result={u'choice':u'error',u'elem':elem}
        else:
            xml=minidom.parseString(data)
            releases=[]
            years=[]
            types=[u'CD, Album',u'LP, Album']
            for r in xml.getElementsByTagName(u'release'):
                if r.childNodes[1].firstChild.data in types and r.firstChild.firstChild.data not in releases:
                    releases.append(r.firstChild.firstChild.data)
                    if len(r.childNodes)>3:
                        years.append(r.childNodes[3].firstChild.data)
            result={
                    u'choice':u'',
                    u'elem':elem,
                    u'albums':releases,
                    u'years':years
                    }
            if data:
                result[u'choice']=url
        return result
    def work(self,elem):
        self.nextBand.emit(elem[u'artist'])
        if elem[u'url']:
            result=self.parse(elem)
        else:
            artist=urllib2.quote(elem[u'artist'].encode(u'latin-1')).replace(u'%20',u'+')
            request=urllib2.Request(u'http://www.discogs.com/search?type=all&q='+artist+u'&f=xml&api_key=95b787be0c')
            request.add_header(u'Accept-Encoding',u'gzip')
            try:
                temp=urllib2.urlopen(request).read()
                try:
                    data=GzipFile(fileobj=StringIO(temp)).read()
                except IOError:
                    data=temp
            except urllib2.HTTPError:
                result={u'choice':u'error',u'elem':elem[u'artist']}
            else:
                xml=minidom.parseString(data)
                tag=xml.firstChild.firstChild
                if tag.tagName==u'exactresults':
                    data=tag.firstChild.firstChild.firstChild.data
                elif tag.tagName.attributes[u'numResults'].value!=0:
                    artists=[]
                    for t in tag.getElementsByTagName(u'title'):
                        if elem[u'artist'] in t.firstChild.data:
                            artists.append(t.firstChild.data)
                    self.disambiguation.emit(elem[u'artist'],artists)
                    self.setPaused(True)
                    while(self.paused):
                        pass
                else:
                    result={u'choice':u'no_band',u'elem':elem[u'artist']}
                result=self.parse(elem,data)
        return result
    def done(self,_,result):
        def exists(a,albums):
            for alb in albums:
                if a.lower()==alb[u'album'].lower():
                    return True
            return False
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
    def run(self):
        requests=threadpool.makeRequests(self.work,self.library,self.done)
        main=threadpool.ThreadPool(1)
        for req in requests:
            main.putRequest(req)
        main.wait()
