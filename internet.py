# -*- coding: utf-8 -*-

import sys
import time
import urllib2
from BeautifulSoup import BeautifulSoup
import threadpool
from PyQt4 import QtCore,QtGui

class MetalArchives(object):
    def __init__(self,library):
        self.library=library
    def parse(self,soup,elem):
        if soup.findAll('script')[0].contents:
            partial=[(elem['artist'],soup.findAll('script')[0].contents[0][18:-2])]
        else:
            partial=[(r.contents[0],r['href']) for r in soup.findAll('a') if (r.contents[0]+' (').startswith(elem['artist']+' (')]
        try:
            if len(partial)!=0:
                if len(partial)==1:
                    soup=BeautifulSoup(urllib2.urlopen('http://www.metal-archives.com/'+partial[0][1]).read())
                    result=soup
                else:
                    app=QtGui.QApplication(sys.argv) # temporary, to have ability to test from command line
                    import chooser
                    chWidget=QtGui.QDialog()
                    ch=chooser.Ui_chooser()
                    ch.setupUi(chWidget)
                    ch.label.setText(ch.label.text()+elem['artist'])
                    chWidget.exec_()
            else:
                result='no_band'
        except urllib2.HTTPError:
            result='error'
        return result
    def work(self,elem):
        try:
            soup=BeautifulSoup(urllib2.urlopen(
                'http://www.metal-archives.com/search.php?string='+elem['artist'].replace(' ','+')+'&type=band').read())
        except urllib2.HTTPError:
            print "retrying..."
            time.sleep(60)
            try:
                soup=BeautifulSoup(urllib2.urlopen(
                    'http://www.metal-archives.com/search.php?string='+elem['artist'].replace(' ','+')+'&type=band').read())
            except urllib2.HTTPError:
                result='error'
            else:
                result=self.parse(soup,elem)
        else:
            result=self.parse(soup,elem)
        return result
    def done(self,request,result):
        print "**** Results from request #%s: %r"%(request.requestID,result)
    def update(self):
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
