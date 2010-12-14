# This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
# Karol "Kenji Takahashi" Wozniak (C) 2010
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

import sys
import os
import cPickle
import re
from threading import Thread
from PyQt4 import QtGui
from PyQt4.QtCore import QStringList, Qt, QSettings
from copy import deepcopy
from db.local import Filesystem
from interfaces.settings import Settings
from db.metalArchives import MetalArchives
from db.discogs import Discogs
import plugins

version = '0.4.1'
if sys.platform=='win32':
    from PyQt4.QtGui import QDesktopServices
    service = QDesktopServices()
    dbPath = os.path.join(unicode(service.storageLocation(9)), u'fetcher')
else: # Most POSIX systems, there may be more elifs in future.
    dbPath=os.path.expanduser(u'~/.config/fetcher')

class NumericTreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent = None):
        QtGui.QTreeWidgetItem.__init__(self, parent)
    def __lt__(self, qtreewidgetitem):
        return self.text(0).toInt()[0] < qtreewidgetitem.text(0).toInt()[0]

class DB(object):
    def __init__(self):
        self.dbPath = os.path.join(dbPath, u'db.pkl')
    def write(self, data):
        handler = open(self.dbPath, u'wb')
        cPickle.dump(data, handler, -1)
        handler.close()
    def read(self):
        handler = open(self.dbPath, u'rb')
        result = cPickle.load(handler)
        handler.close()
        return result

class Main(QtGui.QMainWindow):
    __settings = QSettings(u'fetcher', u'Fetcher')
    runningThreads = 0
    oldLib = None
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.statistics = None
        if not os.path.exists(dbPath):
            os.mkdir(dbPath)
        self.metalArchives = None
        self.discogs = None
        self.fs = Filesystem()
        self.fs.stepped.connect(self.statusBar().showMessage)
        self.fs.created.connect(self.create)
        self.fs.updated.connect(self.update)
        self.fs.errors.connect(self.logs)
        self.db = DB()
        from interfaces.main import Ui_main
        self.ui=Ui_main()
        widget=QtGui.QWidget()
        self.ui.setupUi(widget)
        self.setCentralWidget(widget)
        firstStart = not os.path.exists(os.path.join(dbPath, u'db.pkl'))
        if firstStart:
            dialog = Settings()
            dialog.exec_()
        self.fs.setDirectory(unicode(self.__settings.value(u'directory').toPyObject()))
        self.ignores = self.__settings.value(u'ignores').toPyObject()
        if not self.ignores:
            self.ignores = []
        if firstStart:
            self.fs.setArgs([], [], self.ignores, False)
        else:
            (self.library, self.paths) = self.db.read()
            self.oldLib = deepcopy(self.library)
            self.fs.setArgs(self.library, self.paths, self.ignores, True)
            self.update()
        self.ui.artists.setHeaderLabels(QStringList([u'Artist', u'Digital', u'Analog']))
        self.ui.albums.setHeaderLabels(QStringList([u'Year', u'Album', u'Digital', u'Analog']))
        self.ui.tracks.setHeaderLabels(QStringList([u'#', u'Title']))
        self.ui.logs.setHeaderLabels(QStringList([u'Database', u'Type', u'File/Entry', u'Message']))
        self.ui.albums.itemActivated.connect(self.setAnalog)
        self.ui.local.clicked.connect(self.fs.start)
        self.ui.remote.clicked.connect(self.refresh)
        self.ui.close.clicked.connect(self.close)
        self.ui.save.clicked.connect(self.save)
        self.ui.settings.clicked.connect(self.showSettings)
        self.ui.clearLogs.clicked.connect(self.ui.logs.clear)
        self.ui.saveLogs.clicked.connect(self.saveLogs)
        self.ui.artistFilter.textEdited.connect(self.filter_)
        self.ui.albumFilter.textEdited.connect(self.filter_)
        self.ui.trackFilter.textEdited.connect(self.filter_)
        self.statusBar()
        self.setWindowTitle(u'Fetcher '+version)
        self.loadPlugins()
    def loadPlugins(self):
        reload(plugins)
        for plugin in plugins.__all__:
            class_ = getattr(getattr(plugins, plugin), u'Main')(self.ui)
            if self.__settings.value(u'plugins/' + plugin, 0).toInt()[0]:
                class_.load()
            else:
                class_.unload()
    def filter_(self, text):
        columns = []
        arguments = []
        for a in (unicode(text)).split(u'|'):
            temp = a.split(u':')
            if len(temp) != 2 or temp[1] == u'':
                break
            columns.append(temp[0].lower())
            arguments.append(temp[1].lower())
        if len(columns) != 0 and len(columns) == len(arguments):
            tree = self.sender().parent().children()[2]
            header = tree.header().model()
            num_columns = [i for i in range(tree.columnCount())
                    if (unicode(header.headerData(i, Qt.Horizontal).toString())).lower()
                    in columns]
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                hidden = []
                for j, c in enumerate(num_columns):
                    try:
                        if item not in hidden:
                            if not re.search(arguments[j], (unicode(item.text(c)).lower())):
                                item.setHidden(True)
                                hidden.append(item)
                            else:
                                item.setHidden(False)
                    except:
                        pass
        else:
            tree = self.sender().parent().children()[2]
            for i in range(tree.topLevelItemCount()):
                tree.topLevelItem(i).setHidden(False)
    def confirm(self, event):
        if self.oldLib != self.library:
            def save():
                self.save()
            def reject():
                event.ignore()
            from interfaces.confirmation import ConfirmationDialog
            dialog = ConfirmationDialog()
            dialog.buttons.accepted.connect(save)
            dialog.buttons.rejected.connect(reject)
            dialog.exec_()
    def saveLogs(self):
        dialog = QtGui.QFileDialog()
        filename = dialog.getSaveFileName()
        if filename:
            fh = open(filename, u'w')
            fh.write(u'Database:Type:File/Entry:Message')
            for i in range(self.ui.logs.topLevelItemCount()):
                item = self.ui.logs.topLevelItem(i)
                for c in range(4):
                    fh.write(item.text(c))
                    if c != 3:
                        fh.write(u':')
                fh.write(u'\n')
            fh.close()
            self.statusBar().showMessage(u'Saved logs')
    def create(self, (library, paths)):
        self.library = library
        self.oldLib = deepcopy(self.library)
        self.paths = paths
        self.computeStats()
        self.update()
        self.fs.setArgs(self.library, self.paths, self.ignores, True)
    def showSettings(self):
        dialog=Settings()
        dialog.exec_()
        directory = unicode(self.__settings.value(u'directory', u'').toString())
        if self.fs.directory != directory:
            self.fs.setDirectory(directory)
            self.ignores = self.__settings.value(u'ignores', []).toPyObject()
            self.fs.setArgs([], [], self.ignores, False)
        self.loadPlugins()
    def logs(self, db, kind, filename, message):
        if self.__settings.value(u'logs/' + kind).toInt()[0]:
            item = QtGui.QTreeWidgetItem(QStringList([
                db,
                kind,
                filename,
                message
                ]))
            self.ui.logs.addTopLevelItem(item)
            self.ui.logs.scrollToItem(item)
        for i in range(4):
            self.ui.logs.resizeColumnToContents(i)
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
                            a[u'analog'] = True
                        else:
                            a[u'analog'] = False
                        break
                break
        self.computeStats()
        self.ui.artistsGreen.setText(self.statistics[u'artists'][0])
        self.ui.artistsYellow.setText(self.statistics[u'artists'][1])
        self.ui.artistsRed.setText(self.statistics[u'artists'][2])
        self.ui.albumsGreen.setText(self.statistics[u'albums'][0])
        self.ui.albumsYellow.setText(self.statistics[u'albums'][1])
        self.ui.albumsRed.setText(self.statistics[u'albums'][2])
        if digital == u'YES' and analog == u'YES':
            for i in range(4):
                item.setBackground(i, Qt.green)
        elif digital==u'YES':
            for i in range(4):
                item.setBackground(i, Qt.yellow)
        elif analog == u'YES':
            for i in range(4):
                item.setBackground(i, Qt.yellow)
        else:
            for i in range(4):
                item.setBackground(i, Qt.red)
        artists={}
        for i in range(self.ui.albums.topLevelItemCount()):
            item = self.ui.albums.topLevelItem(i)
            artist = item.artist
            state = unicode(item.background(0).color().name())
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
        def __refresh():
            behaviour = self.__settings.value(u'behaviour', 0).toInt()[0]
            for o in self.__settings.value(u'order').toPyObject():
                if self.__settings.value(o, 0).toInt()[0]:
                    releases = [unicode(k) for k, v
                            in self.__settings.value(u'options/' + o, {}).toPyObject().iteritems()
                            if v == 2]
                    if unicode(o) == u'metal-archives.com':
                        thread = self.metalArchives = MetalArchives(self.library, releases, behaviour)
                    elif unicode(o) == u'discogs.com':
                        thread = self.discogs = Discogs(self.library, releases, behaviour)
                    thread.finished.connect(self.decrement)
                    thread.stepped.connect(self.statusBar().showMessage)
                    thread.errors.connect(self.logs)
                    self.runningThreads += 1
                    thread.start()
                    if not behaviour:
                        thread.wait()
        Thread(target = __refresh).start()
    def decrement(self):
        self.runningThreads -= 1
        if not self.runningThreads:
            self.update()
    def update(self):
        self.computeStats()
        self.statusBar().showMessage(u'Done')
        self.ui.artists.clear()
        self.ui.artists.setSortingEnabled(False)
        for i,l in enumerate(self.library):
            item = QtGui.QTreeWidgetItem(QStringList([
                l[u'artist'],
                self.statistics[u'detailed'][i][0] and u'YES' or u'NO',
                self.statistics[u'detailed'][i][1] and u'YES' or u'NO'
                ]))
            if self.statistics[u'detailed'][i][0] and self.statistics[u'detailed'][i][1]:
                for j in range(3):
                    item.setBackground(j, Qt.green)
                    item.setForeground(j, Qt.black)
            elif self.statistics[u'detailed'][i][0] or self.statistics[u'detailed'][i][1]:
                for j in range(3):
                    item.setBackground(j, Qt.yellow)
                    item.setForeground(j, Qt.black)
            else:
                for j in range(3):
                    item.setBackground(j, Qt.red)
                    item.setForeground(j, Qt.black)
            self.ui.artists.insertTopLevelItem(i, item)
        self.ui.artists.setSortingEnabled(True)
        self.ui.artists.sortItems(0, 0)
        self.ui.artists.resizeColumnToContents(0)
        self.ui.artists.resizeColumnToContents(2)
        self.ui.artists.itemSelectionChanged.connect(self.fillAlbums)
        self.ui.artistsGreen.setText(self.statistics[u'artists'][0])
        self.ui.artistsYellow.setText(self.statistics[u'artists'][1])
        self.ui.artistsRed.setText(self.statistics[u'artists'][2])
        self.ui.albumsGreen.setText(self.statistics[u'albums'][0])
        self.ui.albumsYellow.setText(self.statistics[u'albums'][1])
        self.ui.albumsRed.setText(self.statistics[u'albums'][2])
    def save(self):
        try:
            self.db.write((self.library, self.paths))
        except AttributeError:
            self.statusBar().showMessage(u'Nothing to save...')
        else:
            self.statusBar().showMessage(u'Saved')
            self.oldLib = deepcopy(self.library)
    def fillAlbums(self):
        self.ui.albums.clear()
        items=self.ui.artists.selectedItems()
        self.ui.albums.setSortingEnabled(False)
        for l in self.library:
            for i in items:
                if i.text(0)==l[u'artist']:
                    for k, a in enumerate(l[u'albums']):
                        item = QtGui.QTreeWidgetItem(QStringList([
                            a[u'date'],
                            a[u'album'],
                            a[u'digital'] and u'YES' or u'NO',
                            a[u'analog'] and u'YES' or u'NO'
                            ]))
                        item.artist = l[u'artist']
                        if a[u'digital'] and a[u'analog']:
                            for i in range(4):
                                item.setBackground(i, Qt.green)
                                item.setForeground(i, Qt.black)
                        elif a[u'digital'] or a[u'analog']:
                            for i in range(4):
                                item.setBackground(i, Qt.yellow)
                                item.setForeground(i, Qt.black)
                        else:
                            for i in range(4):
                                item.setBackground(i, Qt.red)
                                item.setForeground(i, Qt.black)
                        self.ui.albums.insertTopLevelItem(k, item)
        self.ui.albums.setSortingEnabled(True)
        self.ui.albums.sortItems(0, 0)
        for i in range(4):
            self.ui.albums.resizeColumnToContents(i)
        self.ui.albums.itemSelectionChanged.connect(self.fillTracks)
    def fillTracks(self):
        self.ui.tracks.clear()
        artists = self.ui.artists.selectedItems()
        albums = self.ui.albums.selectedItems()
        self.ui.tracks.setSortingEnabled(False)
        for l in self.library:
            for artist in artists:
                if artist.text(0) == l[u'artist']:
                    for ll in l[u'albums']:
                        for album in albums:
                            if album.text(1) == ll[u'album']:
                                for k, a in enumerate(ll[u'tracks']):
                                    item = NumericTreeWidgetItem(QStringList([
                                        a[u'tracknumber'],
                                        a[u'title']
                                        ]))
                                    self.ui.tracks.insertTopLevelItem(k, item)
        self.ui.tracks.setSortingEnabled(True)
        self.ui.tracks.sortItems(0, 0)
        self.ui.tracks.resizeColumnToContents(0)
        self.ui.tracks.resizeColumnToContents(1)
    def computeStats(self):
        artists = [0, 0, 0]
        albums = [0, 0, 0]
        detailed = []
        for l in self.library:
            artist = 0
            for a in l[u'albums']:
                if not a[u'digital'] and not a[u'analog']:
                    albums[2] += 1
                    artist = 1
                elif a[u'digital'] and a[u'analog']:
                    albums[0] += 1
                    if not artist:
                        artist = 4
                else:
                    albums[1] += 1
                    if not artist or artist == 4:
                        if a[u'digital']:
                            artist = 2
                        else:
                            artist = 3
            if artist == 4:
                artists[0] += 1
                detailed.append((1, 1))
            elif artist == 1:
                artists[2] += 1
                detailed.append((0, 0))
            else:
                artists[1] += 1
                if artist == 2:
                    detailed.append((1, 0))
                else:
                    detailed.append((0, 1))
        self.statistics = {
                u'artists': (unicode(artists[0]), unicode(artists[1]), unicode(artists[2])),
                u'albums': (unicode(albums[0]), unicode(albums[1]), unicode(albums[2])),
                u'detailed': detailed
                }
    def closeEvent(self, event):
        self.confirm(event)

def run():
    app=QtGui.QApplication(sys.argv)
    main=Main()
    main.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    run()
