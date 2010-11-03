# -*- coding: utf-8 -*-

import sys
import os
import cPickle
from PyQt4 import QtGui
from PyQt4.QtCore import QStringList, Qt, QSettings
from db.local import Filesystem

version='0.4'
if sys.platform=='win32':
    from PyQt4.QtGui import QDesktopServices
    service = QDesktopServices()
    dbPath = service.storageLocation(9) + '\\fetcher'
#    import ctypes
#    dll=ctypes.windll.shell32
#    buf=ctypes.create_string_buffer(300)
#    dll.SHGetSpecialFolderPathA(None,buf,0x0005,False)
#    dbPath=buf.value+'\\fetcher'
else: # Most POSIX systems, there may be more elifs in future.
    dbPath=os.path.expanduser(u'~/.config/fetcher')

class DB(object):
    def __init__(self):
        self.dbPath = os.path.join(dbPath, u'db.pkl')
        self.stPath = os.path.join(dbPath, u'st.pkl')
    def write(self, data):
        handler = open(self.dbPath, u'wb')
        cPickle.dump(data, handler, -1)
        handler.close()
    def read(self):
        handler = open(self.dbPath, u'rb')
        result = cPickle.load(handler)
        handler.close()
        return result
    def setStatistics(self, statistics):
        artists = albums = (0, 0, 0)
        detailed = []
        for s in statistics:
            for a in s[u'albums']:
                if a[u'digital'] == 0 and a[u'analog'] == 0:
                    artists[0] += 1
                    albums[0] += 1
                    detailed.append((0, 0))
                elif a[u'digital'] == 1 or a[u'analog'] == 1:
                    artists[1] += 1
                    albums[1] += 1
                    if a[u'digital'] == 1:
                        detailed.append((1, 0))
                    else:
                        detailed.append((0, 1))
                else:
                    artists[2] += 1
                    albums[2] += 1
        data = {
                u'artists': (str(artists[0]), str(artists[1]), str(artists[2])),
                u'albums': (str(albums[0]), str(albums[1]), str(albums[2])),
                u'detailed': detailed
                }
        handler = open(self.stPath, u'wb')
        cPickle.dump(data, handler, -1)
        handler.close()
    def getStatistics(self):
        handler = open(self.stPath, u'rb')
        result = cPickle.load(handler)
        handler.close()
        return result

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
    __settings = QSettings(u'fetcher', u'Fetcher')
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.metalThread=None
        self.discogsThread=None
        if not os.path.exists(dbPath):
            os.mkdir(dbPath)
        self.fs = Filesystem()
        self.db = DB()
        if not os.path.exists(os.path.join(dbPath,u'db.pkl')):
            dialog=FirstRun()
            dialog.exec_()
            directory = str(dialog.ui.directory.text()).decode(u'utf-8')
            self.__settings.setValue(u'directory', directory)
            self.__settings.setValue(u'metalArchives', dialog.ui.metalArchives.isChecked())
            self.__settings.setValue(u'discogs', dialog.ui.discogs.isChecked())
            self.fs.setDirectory(directory)
        else:
            (self.library, self.paths)=self.db.read()
            self.fs.setDirectory(str(self.__settings.value(u'directory').toString()).decode(u'utf-8'))
            self.fs.setArgs(self.library, self.paths, True)
        from interfaces.main import Ui_main
        self.ui=Ui_main()
        widget=QtGui.QWidget()
        self.ui.setupUi(widget)
        self.setCentralWidget(widget)
        self.ui.artists.setHeaderLabels(QStringList([u'Artist', u'Digital', u'Analog']))
        self.update()
        self.ui.albums.setHeaderLabels(QStringList([u'Year', u'Album', u'Digital', u'Analog']))
        self.ui.tracks.setHeaderLabels(QStringList([u'#', u'Title']))
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
