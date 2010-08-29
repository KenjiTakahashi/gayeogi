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
        self.cursor.execute("create table if not exists settings(main_path text,metal_archives boolean,discogs boolean)")
        self.cursor.execute("""create table if not exists artists(
                artist text,
                path text,
                modified float,
                url text,primary key(artist,url))""")
        self.cursor.execute("""create table if not exists albums(
                artist text,
                album text,
                year text,
                digital boolean,
                analog boolean,primary key(album,year))""")
    def setSettings(self,settings):
        self.cursor.execute("insert into settings values(?,?,?)",settings)
        self.__connector.commit()
    def getSettings(self):
        return self.cursor.execute("select * from settings").fetchone()
    def read(self):
        def __getAlbums(artist):
            albums=self.cursor.execute("select album,year,digital,analog from albums where artist=?",(artist,))
            return [{'album':a,'year':y,'digital':d,'analog':anal} for a,y,d,anal in albums]
        artists=self.cursor.execute("select * from artists").fetchall()
        return [{'artist':a,'path':p,'modified':m,'albums':__getAlbums(a),'url':h} for a,p,m,h in artists]
    def write(self,data):
        for d in data:
            self.cursor.execute('replace into artists values(?,?,?,?)',(d['artist'],d['path'],d['modified'],d['url']))
            for a in d['albums']:
                self.cursor.execute('replace into albums values(?,?,?,?,?)',(
                    d['artist'],a['album'],a['year'],a['digital'],a['analog']))
        self.__connector.commit()
        self.cursor.close()

class Filesystem(object):
    def create(self,directory):
        mainDirectories=[f for f in os.listdir(directory)
                if os.path.isdir(os.path.join(directory,f))
                and f!="$RECYCLE.BIN" and f!="System Volume Information" and f!="Incoming"]
        return [{
            'artist':d,
            'path':os.path.join(directory,d),
            'modified':os.stat(os.path.join(directory,d)).st_mtime,
            'albums':self.__parseSubDirs(os.path.join(directory,d)),
            'url':''
            } for d in mainDirectories]
    def update(self,directory,library):
        mainDirectories=[f for f in os.listdir(directory)
                if os.path.isdir(os.path.join(directory,f))
                and f!='$RECYCLE.BIN' and f!='System Volume Information' and f!='Incoming']
        for l in library:
            if l['artist'] not in mainDirectories:
                del library[library.index(l)]
            elif os.stat(l['path']).st_mtime!=l['modified']:
                l['albums']=self.__parseSubDirs(l['path'])
        def exists(d,t):
            state=False
            for l in library:
                if l[t]==d:
                    state=True
                    break
            return state
        library.extend([{
            'artist':d,
            'path':os.path.join(directory,d),
            'modified':os.stat(os.path.join(directory,d)).st_mtime,
            'albums':self.__parseSubDirs(os.path.join(directory,d)),
            'url':''
            } for d in mainDirectories if not exists(os.path.join(directory,d),'path')])
    def __parseSubDirs(self,d):
        subDirectories=[f.split(' - ') for f in os.listdir(d) if os.path.isdir(os.path.join(d,f))]
        return [{'album':len(d)>2 and d[1]+' - '+d[2] or d[1],'year':d[0],'digital':True,'analog':False} for d in subDirectories]

class FirstRun(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        from interfaces.firstrun import Ui_firstRun
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
    log=[]
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        if not os.path.exists(os.path.expanduser('~/.config/fetcher')):
            os.mkdir(os.path.expanduser('~/.config/fetcher'))
        self.fs=Filesystem()
        if not os.path.exists(os.path.expanduser('~/.config/fetcher/db.sqlite3')):
            dialog=FirstRun()
            dialog.exec_()
            self.db=Sqlite()
            settings=(str(dialog.ui.directory.text()),dialog.ui.metalArchives.isChecked(),dialog.ui.discogs.isChecked())
            self.library=self.fs.create(settings[0])
            self.db.setSettings(settings)
        else:
            self.db=Sqlite()
            self.library=self.db.read()
            settings=self.db.getSettings()
            self.fs.update(settings[0],self.library)
        from interfaces.main import Ui_main
        self.ui=Ui_main()
        widget=QtGui.QWidget()
        self.ui.setupUi(widget)
        if settings[1]:
            self.ui.log.setEnabled(False)
            from internet import MetalArchives
            self.metalThread=MetalArchives(self.library)
            self.metalThread.disambiguation.connect(self.chooser)
            self.metalThread.finished.connect(self.update)
            self.metalThread.nextBand.connect(self.ui.label.setText)
            self.metalThread.message.connect(self.addLogEntry)
            self.metalThread.start()
        #if settings[2]: #discogs here
        self.setCentralWidget(widget)
        self.ui.artists.setHorizontalHeaderLabels(QStringList(['Artist','Digital','Analog']))
        if not settings[1] and not settings[2]:
            self.update()
        self.ui.albums.setHorizontalHeaderLabels(QStringList(['Year','Album','Digital','Analog']))
        self.ui.close.clicked.connect(self.close)
        self.ui.save.clicked.connect(self.save)
        self.ui.log.clicked.connect(self.showLogs)
        self.statusBar()
        self.setWindowTitle('Fetcher 0.1')
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
        self.ui.label.setText('')
        self.ui.artists.setRowCount(len(self.library))
        for i,a in enumerate(self.library):
            self.ui.artists.setItem(i,0,QtGui.QTableWidgetItem(a['artist']))
        self.ui.artists.sortItems(0)
        self.ui.artists.resizeColumnsToContents()
        self.ui.artists.itemSelectionChanged.connect(self.fillAlbums)
        self.ui.log.setEnabled(True)
    def save(self):
        self.db.write(self.library)
        self.statusBar().showMessage('Saved')
    def fillAlbums(self):
        self.ui.albums.setRowCount(0)
        items=self.ui.artists.selectedItems()
        self.ui.albums.setSortingEnabled(False)
        for l in self.library:
            for i in items:
                if i.text()==l['artist']:
                    for a in l['albums']:
                        rows=self.ui.albums.rowCount()
                        self.ui.albums.setRowCount(rows+1)
                        self.ui.albums.setItem(rows,0,QtGui.QTableWidgetItem(a['year'] or '<None>'))
                        self.ui.albums.setItem(rows,1,QtGui.QTableWidgetItem(a['album']))
                        self.ui.albums.setItem(rows,2,QtGui.QTableWidgetItem(a['digital'] and 'YES' or 'NO'))
                        self.ui.albums.setItem(rows,3,QtGui.QTableWidgetItem(a['analog'] and 'YES' or 'NO'))
                        if a['digital'] and a['analog']:
                            for i in range(4):
                                self.ui.albums.item(rows,i).setBackground(Qt.green)
                        elif a['digital'] or a['analog']:
                            for i in range(4):
                                self.ui.albums.item(rows,i).setBackground(Qt.yellow)
                        else:
                            for i in range(4):
                                self.ui.albums.item(rows,i).setBackground(Qt.red)
        self.ui.albums.setSortingEnabled(True)
        self.ui.albums.sortItems(0)
        self.ui.albums.resizeColumnsToContents()

if __name__=='__main__':
    app=QtGui.QApplication(sys.argv)
    main=Main()
    main.show()
    sys.exit(app.exec_())
