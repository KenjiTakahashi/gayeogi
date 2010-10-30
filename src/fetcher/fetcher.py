# -*- coding: utf-8 -*-

import sys
import os
import sqlite3
from PyQt4 import QtGui
from PyQt4.QtCore import QStringList,Qt

version='0.3.1'
if sys.platform=='win32':
    import ctypes
    dll=ctypes.windll.shell32
    buf=ctypes.create_string_buffer(300)
    dll.SHGetSpecialFolderPathA(None,buf,0x0005,False)
    dbPath=buf.value+'\\fetcher'
else: # Most POSIX systems, there may be more elifs in future.
    dbPath=os.path.expanduser(u'~/.config/fetcher')

class Sqlite(object):
    def __init__(self):
        self.__connector=sqlite3.connect(os.path.join(dbPath,u'db.sqlite3'))
        self.cursor=self.__connector.cursor()
        self.cursor.execute(u"create table if not exists settings(main_path text,metal_archives boolean,discogs boolean)")
        self.cursor.execute(u"""create table if not exists artists(
                artist text,
                path text,
                modified float,
                url text,primary key(artist,url))""")
        self.cursor.execute(u"""create table if not exists albums(
                artist text,
                album text,
                year text,
                digital boolean,
                analog boolean,primary key(artist,album,year))""")
    def setSettings(self,settings):
        self.cursor.execute(u'insert into settings values(?,?,?)',settings)
        self.__connector.commit()
    def getSettings(self):
        return self.cursor.execute(u'select * from settings').fetchone()
    def getStatistics(self):
        (red,yellow,green)=(0,0,0)
        colors=[]
        for artist in self.cursor.execute(u'select artist from artists').fetchall():
            if self.cursor.execute(u'select count(*) from albums where artist=? and digital=0 and analog=0',artist).fetchone()[0]!=0:
                red+=1
                colors.append((0,0))
            elif self.cursor.execute(u'select count(*) from albums where artist=? and (digital=1 or analog=1)',artist).fetchone()[0]!=0:
                yellow+=1
                if self.cursor.execute(u'select digital from albums where artist=?',artist).fetchone()[0]==1:
                    colors.append((1,0))
                else:
                    colors.append((0,1))
            else:
                green+=1
                colors.append((1,1))
        return {
                u'artists':(str(green),str(yellow),str(red)),
                u'albums':(
                    str(self.cursor.execute(u'select count(*) from albums where digital=1 and analog=1').fetchone()[0]),
                    str(self.cursor.execute(u'select count(*) from albums where digital=1 or analog=1').fetchone()[0]),
                    str(self.cursor.execute(u'select count(*) from albums where digital=0 and analog=0').fetchone()[0])
                    ),
                u'detailed':colors
                }
    def read(self):
        def __getAlbums(artist):
            albums=self.cursor.execute(u'select album,year,digital,analog from albums where artist=?',(artist,))
            return [{
                u'album':a,
                u'year':y,
                u'digital':d,
                u'analog':anal
                } for a,y,d,anal in albums]
        artists=self.cursor.execute(u'select * from artists').fetchall()
        return [{
            u'artist':a,
            u'path':p,
            u'modified':m,
            u'albums':__getAlbums(a),
            u'url':h
            } for a,p,m,h in artists]
    def write(self,data):
        for d in data:
            if (u'',) in self.cursor.execute(u'select url from artists where artist=?',(d[u'artist'],)).fetchall():
                self.cursor.execute(u'delete from artists where artist=? and url=?',(d[u'artist'],''))
            self.cursor.execute(u'replace into artists values(?,?,?,?)',(d['artist'],d[u'path'],d[u'modified'],d[u'url']))
            for a in d[u'albums']:
                self.cursor.execute('replace into albums values(?,?,?,?,?)',
                        (d[u'artist'],a[u'album'],a[u'year'],a[u'digital'],a[u'analog']))
        def exists1(a):
            state=False
            for d in data:
                if d[u'artist']==a:
                    state=True
                    break
            return state
        def exists2(a):
            state=False
            for d in data:
                for alb in d[u'albums']:
                    if a==alb[u'album']:
                        state=True
                        break
            return state
        for artist, in self.cursor.execute(u'select artist from artists').fetchall():
            if not exists1(artist):
                self.cursor.execute(u'delete from artists where artist=?',(artist,))
                self.cursor.execute(u'delete from albums where artist=?',(artist,))
            else:
                for album, in self.cursor.execute(u'select album from albums where artist=?',(artist,)):
                    if not exists2(album):
                        self.cursor.execute(u'delete from albums where artist=? and album=?',(artist,album))
    def commit(self):
        self.__connector.commit()
    def updatePre04(self):
        self.cursor.execute(u"""create temporary table albums_backup(
                artist text,
                album text,
                year text,
                digital boolean,
                analog boolean,
                primary key(artist,album,year))""")
        self.cursor.execute(u'insert into albums_backup select * from albums')
        self.cursor.execute(u'drop table albums')
        self.cursor.execute(u"""create table albums(
                artist text,
                album text,
                year text,
                digital boolean,
                analog boolean,
                primary key(artist,album,year))""")
        self.cursor.execute(u'insert into albums select * from albums_backup')
        self.cursor.execute(u'drop table albums_backup')
        self.__connector.commit()
        print "Pre-0.4 db updated to current scheme."

class Filesystem(object):
    def __init__(self):
        self.ignores=[u'$RECYCLE.BIN',u'System Volume Information',u'Incoming',u'msdownld.tmp']
        self.syntax=[((u'',u''),(u'---',u' - ',u''),(u'year',u'album'))]
        self.errors=[]
    def __clean(self,string,lgi,rgi):
        for s in self.syntax:
            string=string.lstrip(s[lgi[0]][lgi[1]]).rstrip(s[rgi[0]][rgi[1]])
        return string
    def create(self,directory):
        mainDirectories=[f for f in os.listdir(directory)
                if os.path.isdir(os.path.join(directory,f)) and f not in self.ignores]
        results=[{
            u'artist':self.__clean(d,(0,0),(0,1)),
            u'path':os.path.join(directory,d),
            u'modified':os.stat(os.path.join(directory,d)).st_mtime,
            u'albums':self.__parseSubDirs(os.path.join(directory,d),[]),
            u'url':u''
            } for d in mainDirectories]
        if self.errors:
            from interfaces.errordialog import ErrorDialog
            dialog=ErrorDialog(self.errors)
            dialog.exec_()
        return results
    def update(self,directory,library):
        def exists(d,t,l):
            for e in l:
                if e[t]==d:
                    return True
            return False
        mainDirectories=[f for f in os.listdir(directory)
                if os.path.isdir(os.path.join(directory,f)) and f not in self.ignores]
        parsedDirectories=[self.__clean(f,(0,0),(0,1)) for f in mainDirectories]
        for l in library:
            if l[u'artist'] not in parsedDirectories:
                del library[library.index(l)]
            elif os.stat(l[u'path']).st_mtime!=l[u'modified']:
                subs=self.__parseSubDirs(l[u'path'],l[u'albums'])
                for ll in l[u'albums']:
                    if ll[u'digital']==1 and not exists(ll[u'album'],u'album',subs):
                        del l[u'albums'][l[u'albums'].index(ll)]
                subs.extend([f for f in l[u'albums'] if not exists(f[u'album'],u'album',subs)])
                l[u'albums']=subs
                l[u'modified']=os.stat(l[u'path']).st_mtime
        library.extend([{
            u'artist':self.__clean(d,(0,0),(0,1)),
            u'path':os.path.join(directory,d),
            u'modified':os.stat(os.path.join(directory,d)).st_mtime,
            u'albums':self.__parseSubDirs(os.path.join(directory,d),[]),
            u'url':u''
            } for d in mainDirectories if not exists(os.path.join(directory,d),u'path',library)])
        if self.errors:
            from interfaces.errordialog import ErrorDialog
            dialog=ErrorDialog(self.errors)
            dialog.exec_()
    def __parseSubDirs(self,d,albums):
        def getAnalog(album):
            for a in albums:
                if album==a[u'album'] and a[u'analog']:
                    return True
            return False
        subDirectories=[f for f in os.listdir(d) if os.path.isdir(os.path.join(d,f))]
        results=[]
        self.errors=[]
        for sd in subDirectories:
            sdy=self.__clean(sd,(1,0),(1,2))
            for syn in self.syntax:
                splitted=sdy.split(syn[1][1])
                year=splitted[0]
                del splitted[0]
                album=syn[1][1].join(splitted)
                if album:
                    results.append({
                        u'year':year,
                        u'album':album,
                        u'digital':True,
                        u'analog':getAnalog(album)
                        })
                else:
                    path=os.path.join(d,sd)
                    self.errors.append(path)
        return results

class FirstRun(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        from interfaces.firstrun import Ui_firstRun
        self.ui=Ui_firstRun()
        self.ui.setupUi(self)
        self.ui.browse.clicked.connect(self.__browse)
        self.ui.cancel.clicked.connect(sys.exit)
        self.ui.ok.clicked.connect(self.close)
        self.setWindowTitle(u'Fetcher '+version+' - First Run Configuration')
    def __browse(self):
        dialog=QtGui.QFileDialog()
        self.ui.directory.setText(dialog.getExistingDirectory())

class Main(QtGui.QMainWindow):
    log=[]
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.metalThread=None
        self.discogsThread=None
        if not os.path.exists(dbPath):
            os.mkdir(dbPath)
        self.fs=Filesystem()
        if not os.path.exists(os.path.join(dbPath,u'db.sqlite3')):
            dialog=FirstRun()
            dialog.exec_()
            self.db=Sqlite()
            self.settings=(str(dialog.ui.directory.text()).decode(u'utf-8'),dialog.ui.metalArchives.isChecked(),dialog.ui.discogs.isChecked())
            self.library=self.fs.create(self.settings[0])
            self.db.setSettings(self.settings)
        else:
            self.db=Sqlite()
            self.library=self.db.read()
            self.settings=self.db.getSettings()
            self.fs.update(self.settings[0],self.library)
        from interfaces.main import Ui_main
        self.ui=Ui_main()
        widget=QtGui.QWidget()
        self.ui.setupUi(widget)
        self.setCentralWidget(widget)
        self.ui.artists.setHeaderLabels(QStringList([u'Artist', u'Digital', u'Analog']))
        self.update()
        self.ui.albums.setHeaderLabels(QStringList([u'Year', u'Album', u'Digital', u'Analog']))
        self.ui.albums.itemActivated.connect(self.setAnalog)
        self.ui.remote.clicked.connect(self.refresh)
        self.ui.close.clicked.connect(self.close)
        self.ui.save.clicked.connect(self.save)
        self.ui.log.clicked.connect(self.showLogs)
        self.ui.settings.clicked.connect(self.showSettings)
        self.statusBar()
        self.setWindowTitle(u'Fetcher '+version)
    def showSettings(self):
        from interfaces.settings import Settings
        dialog=Settings()
        dialog.exec_()
    def setAnalog(self,item):
        digital = item.text(2)
        analog = item.text(3)
        if analog == u'NO':
            item.setText(3, u'YES')
            analog = u'YES'
        else:
            item.setText(3, u'NO')
            analog = u'NO'
        album = item.text(1)
        for l in self.library:
            if l[u'artist'] == item.artist:
                for a in l[u'albums']:
                    if a[u'album']==album:
                        if analog == u'YES':
                            a[u'analog']=1
                        else:
                            a[u'analog']=0
                        break
                break
        if digital == u'YES' and analog == u'YES':
            for i in range(4):
                item.setBackground(i, Qt.green)
            self.ui.albumsYellow.setText(str(int(self.ui.albumsYellow.text())-1))
            self.ui.albumsGreen.setText(str(int(self.ui.albumsGreen.text())+1))
        elif digital=='YES':
            for i in range(4):
                item.setBackground(i, Qt.yellow)
            self.ui.albumsGreen.setText(str(int(self.ui.albumsGreen.text())-1))
            self.ui.albumsYellow.setText(str(int(self.ui.albumsYellow.text())+1))
        elif analog == u'YES':
            for i in range(4):
                item.setBackground(i, Qt.yellow)
            self.ui.albumsRed.setText(str(int(self.ui.albumsRed.text())-1))
            self.ui.albumsYellow.setText(str(int(self.ui.albumsYellow.text())+1))
        else:
            for i in range(4):
                item.setBackground(i, Qt.red)
            self.ui.albumsYellow.setText(str(int(self.ui.albumsYellow.text())-1))
            self.ui.albumsRed.setText(str(int(self.ui.albumsRed.text())+1))
        artists={}
        item = self.ui.albums.topLevelItem(0)
        while item:
            artist = item.artist
            state = str(item.background(0).color().name())
            if artist in artists:
                if state in artists[artist]:
                    artists[artist][state] += 1
                else:
                    artists[artist][state] = 1
                if artists[artist][u'analog'] != u'NO' and item.text(3) == u'NO':
                    artists[artist][u'analog'] = u'NO'
            else:
                artists[artist] = {state: 1}
                if item.text(3) == u'YES':
                    artists[artist][u'analog'] = u'YES'
                else:
                    artists[artist][u'analog'] = u'NO'
            item = self.ui.albums.itemBelow(item)
        def setColor(artist,qcolor,analogState):
            for item in self.ui.artists.selectedItems():
                if item.text(0) == artist:
                    for i in range(3):
                        item.setBackground(i, qcolor)
                    item.setText(2, analogState)
                    break
        for artist,states in artists.items():
            if u'#ff0000' in states:
                setColor(artist,Qt.red,states[u'analog'])
            elif u'#ffff00' in states:
                setColor(artist,Qt.yellow,states[u'analog'])
            else:
                setColor(artist,Qt.green,states[u'analog'])
    def refresh(self):
        if self.settings[1]:
            self.ui.log.setEnabled(False)
            from db.metalArchives import MetalArchives
            self.metalThread=MetalArchives(self.library)
            self.metalThread.disambiguation.connect(self.chooser)
            self.metalThread.finished.connect(self.update)
            self.metalThread.nextBand.connect(self.statusBar().showMessage)
            self.metalThread.message.connect(self.addLogEntry)
            self.metalThread.start()
        if self.settings[2]:
            self.ui.log.setEnabled(False)
            from db.discogs import Discogs
            self.discogsThread=Discogs(self.library)
            self.discogsThread.disambiguation.connect(self.chooser)
            self.discogsThread.finished.connect(self.update)
            self.discogsThread.nextBand.connect(self.statusBar().showMessage)
            self.discogsThread.message.connect(self.addLogEntry)
            self.discogsThread.start()
    def showLogs(self):
        from interfaces.logsview import LogsView
        dialog=LogsView(self.log)
        dialog.exec_()
    def addLogEntry(self,artist,message):
        self.log.append((artist,message))
    def chooser(self,artist,partial):
        from interfaces import chooser
        dialog=chooser.Chooser()
        dialog.setArtist(artist)
        for p in partial:
            dialog.addButton(p)
        dialog.exec_()
        self.metalThread.disambigue(dialog.getChoice())
        self.metalThread.setPaused(False)
    def update(self):
        self.db.write(self.library)
        self.statusBar().showMessage(u'')
        self.ui.artists.clear()
        statistics=self.db.getStatistics()
        self.ui.artists.setSortingEnabled(False)
        for i,l in enumerate(self.library):
            item = QtGui.QTreeWidgetItem(QStringList([
                l[u'artist'],
                statistics[u'detailed'][i][0] and u'YES' or u'NO',
                statistics[u'detailed'][i][1] and u'YES' or u'NO'
                ]))
            if statistics[u'detailed'][i][0] and statistics[u'detailed'][i][1]:
                for j in range(3):
                    item.setBackground(j, Qt.green)
            elif statistics[u'detailed'][i][0] or statistics[u'detailed'][i][1]:
                for j in range(3):
                    item.setBackground(j, Qt.yellow)
            else:
                for j in range(3):
                    item.setBackground(j, Qt.red)
            self.ui.artists.insertTopLevelItem(i, item)
        self.ui.artists.setSortingEnabled(True)
        self.ui.artists.sortItems(0, 0)
        self.ui.artists.resizeColumnToContents(0)
        self.ui.artists.itemSelectionChanged.connect(self.fillAlbums)
        statistics=self.db.getStatistics()
        self.ui.artistsGreen.setText(statistics[u'artists'][0])
        self.ui.artistsYellow.setText(statistics[u'artists'][1])
        self.ui.artistsRed.setText(statistics[u'artists'][2])
        self.ui.albumsGreen.setText(statistics[u'albums'][0])
        self.ui.albumsYellow.setText(statistics[u'albums'][1])
        self.ui.albumsRed.setText(statistics[u'albums'][2])
        self.ui.log.setEnabled(True)
    def save(self):
        self.db.write(self.library)
        self.db.commit()
        self.statusBar().showMessage(u'Saved')
    def fillAlbums(self):
        self.ui.albums.clear()
        items=self.ui.artists.selectedItems()
        self.ui.albums.setSortingEnabled(False)
        for l in self.library:
            for i in items:
                if i.text(0)==l[u'artist']:
                    for k, a in enumerate(l[u'albums']):
                        item = QtGui.QTreeWidgetItem(QStringList([
                            a[u'year'],
                            a[u'album'],
                            a[u'digital'] and u'YES' or u'NO',
                            a[u'analog'] and u'YES' or u'NO'
                            ]))
                        item.artist = l[u'artist']
                        if a[u'digital'] and a[u'analog']:
                            for i in range(4):
                                item.setBackground(i, Qt.green)
                        elif a[u'digital'] or a[u'analog']:
                            for i in range(4):
                                item.setBackground(i, Qt.yellow)
                        else:
                            for i in range(4):
                                item.setBackground(i, Qt.red)
                        self.ui.albums.insertTopLevelItem(k, item)
        self.ui.albums.setSortingEnabled(True)
        self.ui.albums.sortItems(0, 0)
        self.ui.albums.resizeColumnToContents(0)
        self.ui.albums.resizeColumnToContents(1)

def run():
    app=QtGui.QApplication(sys.argv)
    main=Main()
    main.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    run()
