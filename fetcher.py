# -*- coding: utf-8 -*-

import sys
import os
import sqlite3
from PyQt4 import QtGui
from PyQt4.QtCore import QStringList,Qt

class Sqlite(object):
    def __init__(self):
        self.__connector=sqlite3.connect(os.path.expanduser('~/.config/fetcher/db.sqlite3'))
        self.cursor=self.__connector.cursor()
        self.cursor.execute("create table if not exists settings(main_path text)")
        self.cursor.execute("""create table if not exists artists(
                artist text primary key,
                path text,
                modified float)""")
        self.cursor.execute("""create table if not exists albums(
                artist text,
                album text,
                year text,
                digital boolean,
                analog boolean, primary key(album,year))""")
    def setMainPath(self,path):
        self.cursor.execute("insert into settings values(?)",(path,))
        self.__connector.commit()
    def getMainPath(self):
        return self.cursor.execute("select main_path from settings").fetchone()[0]
    def read(self):
        def __getAlbums(artist):
            albums=self.cursor.execute("select album,year,digital,analog from albums where artist=?",(artist,))
            return [{'album':a,'year':y,'digital':d,'analog':anal} for a,y,d,anal in albums]
        artists=self.cursor.execute("select * from artists").fetchall()
        return [{'artist':a,'path':p,'modified':m,'albums':__getAlbums(a)} for a,p,m in artists]
    def write(self,data):
        for d in data:
            self.cursor.execute('replace into artists values(?,?,?)',(d['artist'],d['path'],d['modified']))
            for a in d['albums']:
                self.cursor.execute('replace into albums values(?,?,?,?,?)',(
                    d['artist'],a['album'],a['year'],a['digital'],a['analog']))
        self.__connector.commit()

class Filesystem(object):
    def create(self,directory):
        mainDirectories=[f for f in os.listdir(directory)
                if os.path.isdir(os.path.join(directory,f))
                and f!="$RECYCLER" and f!="System Volume Information" and f!="Incoming"]
        return [{
            'artist':d,
            'path':os.path.join(directory,d),
            'modified':os.stat(os.path.join(directory,d)).st_mtime,
            'albums':self.__parseSubDirs(os.path.join(directory,d))
            } for d in mainDirectories]
    def update(self,directory,library):
        for l in library:
            if os.stat(l['path']).st_mtime!=l['modified']:
                print "LOL"
                l['albums']=self.__parseSubDirs(l['path'])
        mainDirectories=[f for f in os.listdir(directory)
                if os.path.isdir(os.path.join(directory,f))
                and f!="$RECYCLER" and f!="System Volume Information" and f!="Incoming"]
        def exists(d):
            state=False
            for l in library:
                if l['path']==d:
                    state=True
                    break
            return state
        library.extend([{
            'artist':d,
            'path':os.path.join(directory,d),
            'modified':os.stat(os.path.join(directory,d)).st_mtime,
            'albums':self.__parseSubDirs(os.path.join(directory,d))
            } for d in mainDirectories if not exists(os.path.join(directory,d))])
    def __parseSubDirs(self,d):
        subDirectories=[f.split(' - ') for f in os.listdir(d) if os.path.isdir(os.path.join(d,f))]
        return [{'album':d[1],'year':d[0],'digital':True,'analog':False} for d in subDirectories]

class Internet(object):
    def update(self,library):
        def exists(a,lib):
            state=False
            for l in lib:
                if l['album']==a:
                    state=True
                    break
            return state
        import urllib2
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
                print '.'
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

class FirstRun(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        from firstrun import Ui_firstRun
        self.ui=Ui_firstRun()
        self.ui.setupUi(self)
        self.ui.browse.clicked.connect(self.__browse)
        self.ui.cancel.clicked.connect(sys.exit)
        self.ui.ok.clicked.connect(self.close)
        self.setWindowTitle('Fetcher 0.1 - First Run Configuration')
    def __browse(self):
        dialog=QtGui.QFileDialog()
        self.ui.directory.setText(dialog.getExistingDirectory())

class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        if not os.path.exists(os.path.expanduser('~/.config/fetcher')):
            os.mkdir(os.path.expanduser('~/.config/fetcher'))
        self.fs=Filesystem()
        if not os.path.exists(os.path.expanduser('~/.config/fetcher/db.sqlite3')):
            dialog=FirstRun()
            dialog.exec_()
            self.db=Sqlite()
            mainDirectory=str(dialog.ui.directory.text())
            self.library=self.fs.create(mainDirectory)
            self.db.setMainPath(mainDirectory)
        else:
            self.db=Sqlite()
            self.library=self.db.read()
            self.fs.update(self.db.getMainPath(),self.library)
        self.inet=Internet()
        self.inet.update(self.library) # separate thread!
        from main import Ui_main
        self.ui=Ui_main()
        widget=QtGui.QWidget()
        self.ui.setupUi(widget)
        self.setCentralWidget(widget)
        self.ui.artists.setHorizontalHeaderLabels(QStringList(['Artist','Digital','Analog']))
        self.ui.artists.setRowCount(len(self.library))
        for i,a in enumerate(self.library):
            self.ui.artists.setItem(i,0,QtGui.QTableWidgetItem(a['artist']))
        self.ui.artists.sortItems(0)
        self.ui.artists.resizeColumnsToContents()
        self.ui.artists.itemSelectionChanged.connect(self.fillAlbums)
        self.ui.albums.setHorizontalHeaderLabels(QStringList(['Year','Album','Digital','Analog']))
        self.ui.close.clicked.connect(self.close)
        self.ui.save.clicked.connect(self.save)
        self.statusBar()
        self.setWindowTitle('Fetcher 0.1')
    def save(self):
        self.db.write(self.library)
        self.statusBar().showMessage('Saved')
    def fillAlbums(self):
        self.ui.albums.setRowCount(0)
        items=self.ui.artists.selectedItems()
        for l in self.library:
            for i in items:
                if i.text()==l['artist']:
                    for a in l['albums']:
                        rows=self.ui.albums.rowCount()
                        self.ui.albums.setRowCount(rows+1)
                        if a['year']:
                            self.ui.albums.setItem(rows,0,QtGui.QTableWidgetItem(a['year']))
                        else:
                            self.ui.albums.setItem(rows,0,QtGui.QTableWidgetItem('<None>'))
                        self.ui.albums.setItem(rows,1,QtGui.QTableWidgetItem(a['album']))
                        if a['digital']:
                            self.ui.albums.setItem(rows,2,QtGui.QTableWidgetItem('YES'))
                        else:
                            self.ui.albums.setItem(rows,2,QtGui.QTableWidgetItem('NO'))
                        if a['analog']:
                            self.ui.albums.setItem(rows,3,QtGui.QTableWidgetItem('YES'))
                        else:
                            self.ui.albums.setItem(rows,3,QtGui.QTableWidgetItem('NO'))
                        if a['digital'] and a['analog']:
                            for i in range(4):
                                self.ui.albums.item(rows,i).setBackground(Qt.green)
                        elif a['digital'] or a['analog']:
                            for i in range(4):
                                self.ui.albums.item(rows,i).setBackground(Qt.yellow)
                        else:
                            for i in range(4):
                                self.ui.albums.item(rows,i).setBackground(Qt.red)
        self.ui.albums.resizeColumnsToContents()

if __name__=='__main__':
    app=QtGui.QApplication(sys.argv)
    main=Main()
    main.show()
    sys.exit(app.exec_())
