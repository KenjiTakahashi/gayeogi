# This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
# Karol "Kenji Takahashi" Wozniak (C) 2010 - 2011
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
from PyQt4 import QtGui
from PyQt4.QtCore import QStringList, Qt, QSettings, QLocale, QTranslator
from copy import deepcopy
from fetcher.db.local import Filesystem
from fetcher.db.distributor import Distributor
from fetcher.interfaces.settings import Settings
import fetcher.plugins

version = u'0.6'
if sys.platform == 'win32':
    from PyQt4.QtGui import QDesktopServices
    service = QDesktopServices()
    dbPath = os.path.join(unicode(service.storageLocation(9)), u'fetcher')
else: # Most POSIX systems, there may be more elifs in future.
    dbPath=os.path.expanduser(u'~/.config/fetcher')

class NumericTreeWidgetItem(QtGui.QTreeWidgetItem):
    def __lt__(self, qtreewidgetitem):
        column = self.treeWidget().sortColumn()
        if not column:
            track1 = self.text(0).split(u'/')[0].toInt()[0]
            track2 = qtreewidgetitem.text(0).split(u'/')[0].toInt()[0]
            album1 = self.album
            album2 = qtreewidgetitem.album
            if album1 == album2:
                return track1 < track2
            else:
                return False
        else:
            return self.text(column) < qtreewidgetitem.text(column)

class DB(object):
    def __init__(self):
        self.dbPath = os.path.join(dbPath, u'db.pkl')
    def write(self, data):
        handler = open(self.dbPath, u'wb')
        cPickle.dump(data, handler, -1)
        handler.close()
        saved = False
        while(not saved):
            try:
                handler = open(self.dbPath, u'rb')
                cPickle.load(handler)
            except:
                handler = open(self.dbPath, u'wb')
                cPickle.dump(data, handler, -1)
            else:
                saved = True
            finally:
                handler.close()
    def read(self):
        handler = open(self.dbPath, u'rb')
        result = cPickle.load(handler)
        handler.close()
        if isinstance(result[0], list):
            result = (self.convert(result[0]), result[1])
        try:
            result[2]
        except IndexError:
            return self.convert2(result[0])
        else:
            return result
    def convert(self, data):
        def checkRemote(digital, analog):
            if not digital and not analog:
                return True
            return False
        results = {}
        for artists in data:
            results[artists[u'artist']] = {
                    u'url': artists[u'url'],
                    u'albums': {}
                    }
            for albums in artists[u'albums']:
                results[artists[u'artist']][u'albums'][albums[u'album']] = {
                        u'date': albums[u'date'],
                        u'digital': albums[u'digital'],
                        u'analog': albums[u'analog'],
                        u'remote': checkRemote(albums[u'digital'], albums[u'analog']),
                        u'tracks': {}
                        }
                for tracks in albums[u'tracks']:
                    results[artists[u'artist']][u'albums'][albums[u'album']] \
                            [u'tracks'][tracks[u'title']] = {
                            u'tracknumber': tracks[u'tracknumber'],
                            u'path': tracks[u'path'],
                            u'modified': tracks[u'modified']
                            }
        return results
    def convert2(self, data):
        main = dict()
        path = dict()
        urls = dict()
        avai = dict()
        for artist, albums in data.iteritems():
            main[artist] = dict()
            avai[artist] = dict()
            for album, tracks in albums[u'albums'].iteritems():
                try:
                    main[artist][tracks[u'date']]
                except KeyError:
                    main[artist][tracks[u'date']] = dict()
                avai[artist + tracks[u'date'] + album] = {
                        u'digital': tracks[u'digital'],
                        u'analog': tracks[u'analog'],
                        u'remote': tracks[u'remote']
                        }
                main[artist][tracks[u'date']][album] = dict()
                for track, deepest in tracks[u'tracks'].iteritems():
                    main[artist][tracks[u'date']][album] \
                            [deepest[u'tracknumber']] = {
                                    track: {
                                        u'path': deepest[u'path']
                                        }
                                    }
                    path[deepest[u'path']] = {
                        u'artist': artist,
                        u'date': tracks[u'date'],
                        u'album': album,
                        u'tracknumber': deepest[u'tracknumber'],
                        u'title': track,
                        u'modified': deepest[u'modified']
                    }
        return (version, main, path, urls, avai)

class Main(QtGui.QMainWindow):
    __settings = QSettings(u'fetcher', u'Fetcher')
    oldLib = None
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.statistics = None
        if not os.path.exists(dbPath):
            os.mkdir(dbPath)
        self.db = DB()
        from interfaces.main import Ui_main
        self.ui = Ui_main()
        widget = QtGui.QWidget()
        self.ui.setupUi(widget)
        self.ui.plugins = {}
        self.ui.splitter.restoreState(
                self.__settings.value(u'splitters').toByteArray())
        self.setCentralWidget(widget)
        self.library = (version, {}, {}, {}, {})
        self.ignores = self.__settings.value(u'ignores').toPyObject()
        if not self.ignores:
            self.ignores = []
        if not os.path.exists(os.path.join(dbPath, u'db.pkl')):
            dialog = Settings()
            dialog.exec_()
        else:
            self.library = self.db.read()
            self.oldLib = deepcopy(self.library)
            self.update()
        directory = unicode(self.__settings.value(u'directory').toPyObject())
        self.fs = Filesystem(directory, self.library, self.ignores)
        self.fs.stepped.connect(self.statusBar().showMessage)
        self.fs.updated.connect(self.update)
        self.fs.errors.connect(self.logs)
        self.rt = Distributor(self.library)
        self.rt.stepped.connect(self.statusBar().showMessage)
        self.rt.updated.connect(self.update)
        self.rt.errors.connect(self.logs)
        self.ui.artists.setHeaderLabels(QStringList([
            u'Artist', u'Digital', u'Analog']))
        self.ui.artists.itemSelectionChanged.connect(self.fillAlbums)
        self.ui.albums.setHeaderLabels(QStringList([
            u'Year', u'Album', u'Digital', u'Analog']))
        self.ui.albums.itemSelectionChanged.connect(self.fillTracks)
        self.ui.tracks.setHeaderLabels(QStringList(['#', u'Title']))
        self.ui.logs.setHeaderLabels(QStringList([
            self.trUtf8('Module'),
            self.trUtf8('Type'),
            self.trUtf8('File/Entry'),
            self.trUtf8('Message')]))
        self.ui.albums.itemActivated.connect(self.setAnalog)
        self.ui.local.clicked.connect(self.local)
        self.ui.remote.clicked.connect(self.remote)
        self.ui.close.clicked.connect(self.close)
        self.ui.save.clicked.connect(self.save)
        self.ui.settings.clicked.connect(self.showSettings)
        self.ui.clearLogs.clicked.connect(self.ui.logs.clear)
        self.ui.saveLogs.clicked.connect(self.saveLogs)
        self.ui.artistFilter.textEdited.connect(self.filter_)
        self.ui.albumFilter.textEdited.connect(self.filter_)
        self.ui.trackFilter.textEdited.connect(self.filter_)
        self.statusBar()
        self.setWindowTitle(u'Fetcher ' + version)
        self.translators = list()
        self.loadPluginsTranslators()
        self.loadPlugins()
    def disableButtons(self):
        u"""Disable some buttons one mustn't use during the update.

        Note: They are then re-enabled in the update() method.
        """
        self.ui.local.setDisabled(True)
        self.ui.remote.setDisabled(True)
        self.ui.save.setDisabled(True)
        self.ui.settings.setDisabled(True)
    def local(self):
        u"""Start local database update."""
        self.disableButtons()
        self.fs.start()
    def remote(self):
        u"""Start remote databases update."""
        self.disableButtons()
        self.rt.start()
    def loadPluginsTranslators(self):
        reload(fetcher.plugins)
        app = QtGui.QApplication.instance()
        for plugin in fetcher.plugins.__all__:
            class_ = getattr(fetcher.plugins, plugin).Main
            translator = class_.translator()
            if translator:
                self.translators.append(translator)
                app.installTranslator(translator)
    def removePluginsTranslators(self):
        app = QtGui.QApplication.instance()
        for translator in self.translators:
            app.removeTranslator(translator)
    def loadPlugins(self):
        reload(fetcher.plugins)
        def depends(plugin):
            for p in fetcher.plugins.__all__:
                class_ = getattr(fetcher.plugins, p).Main
                if plugin in class_.depends and class_.loaded:
                    return True
            return False
        for plugin in fetcher.plugins.__all__:
            class_ = getattr(fetcher.plugins, plugin).Main
            __settings_ = QSettings(u'fetcher', class_.name)
            option = __settings_.value(u'enabled', 0).toInt()[0]
            if option and not class_.loaded:
                class__ = class_(self.ui, self.library, self.appendPlugin,
                        self.removePlugin)
                class__.load()
                if hasattr(class__, 'errors'):
                    class__.errors.connect(self.logs)
                self.ui.plugins[plugin] = class__
            elif not option and class_.loaded:
                self.ui.plugins[plugin].unload()
                for d in self.ui.plugins[plugin].depends:
                    if not self.ui.plugins[d].loaded \
                            and d in self.ui.plugins.keys():
                        del self.ui.plugins[d]
                if not depends(plugin):
                    del self.ui.plugins[plugin]
    def appendPlugin(self, parent, child, position):
        parent = getattr(self.ui, parent)
        if isinstance(parent, QtGui.QLayout):
            widget = parent.itemAt(position)
            if not widget:
                parent.insertWidget(position, child)
            else:
                if isinstance(widget, QtGui.QTabWidget):
                    widget.addTab(child, child.name)
                else:
                    widget = parent.takeAt(position).widget()
                    tab = QtGui.QTabWidget()
                    tab.setTabPosition(tab.South)
                    tab.addTab(widget, widget.name)
                    tab.addTab(child, child.name)
                    parent.insertWidget(position, tab)
    def removePlugin(self, parent, child, position):
        parent = getattr(self.ui, parent)
        if isinstance(parent, QtGui.QLayout):
            widget = parent.itemAt(position).widget()
            try:
                if widget.name == child.name:
                    parent.takeAt(position).widget().deleteLater()
            except AttributeError:
                for i in range(widget.count()):
                    if widget.widget(i).name == child.name:
                        widget.removeTab(i)
                if widget.count() == 1:
                    tmp = widget.widget(0)
                    parent.takeAt(position).widget().deleteLater()
                    parent.insertWidget(position, tmp)
                    parent.itemAt(position).widget().show()
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
                    if (unicode(header.headerData(i,
                        Qt.Horizontal).toString())).lower() in columns]
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                hidden = []
                for j, c in enumerate(num_columns):
                    try:
                        if item not in hidden:
                            if not re.search(arguments[j],
                                    (unicode(item.text(c)).lower())):
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
    def saveLogs(self):
        dialog = QtGui.QFileDialog()
        filename = dialog.getSaveFileName()
        if filename:
            fh = open(filename, u'w')
            fh.write(self.trUtf8('Database:Type:File/Entry:Message'))
            for i in range(self.ui.logs.topLevelItemCount()):
                item = self.ui.logs.topLevelItem(i)
                for c in range(4):
                    fh.write(item.text(c))
                    if c != 3:
                        fh.write(u':')
                fh.write(u'\n')
            fh.close()
            self.statusBar().showMessage(self.trUtf8('Logs saved'))
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
    def showSettings(self):
        u"""Show settings dialog and then update accordingly."""
        def __save():
            directory = unicode(
                    self.__settings.value(u'directory', u'').toString())
            self.ignores = self.__settings.value(u'ignores', []).toPyObject()
            self.fs.actualize(directory, self.ignores)
            self.removePluginsTranslators()
            self.loadPluginsTranslators()
            self.loadPlugins()
        dialog = Settings()
        dialog.ok.clicked.connect(__save)
        dialog.exec_()
    def setAnalog(self, item, column):
        if column == 3:
            digital = item.text(2)
            analog = item.text(3)
            if analog == u'NO':
                item.setText(3, u'YES')
                analog = u'YES'
            else:
                item.setText(3, u'NO')
                analog = u'NO'
            album = unicode(item.text(1))
            if analog == u'YES':
                self.library[item.artist][u'albums'][album][u'analog'] = True
            else:
                self.library[item.artist][u'albums'][album][u'analog'] = False
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
    def update(self):
        self.computeStats()
        self.statusBar().showMessage(self.trUtf8('Done'))
        self.ui.local.setEnabled(True)
        self.ui.remote.setEnabled(True)
        self.ui.save.setEnabled(True)
        self.ui.settings.setEnabled(True)
        sArtists = [i.text(0) for i in self.ui.artists.selectedItems()]
        sAlbums = [i.text(0) for i in self.ui.albums.selectedItems()]
        sTracks = [i.text(0) for i in self.ui.tracks.selectedItems()]
        self.ui.artists.clear()
        self.ui.artists.setSortingEnabled(False)
        for i, l in enumerate(self.library[1].keys()):
            item = QtGui.QTreeWidgetItem(QStringList([l,
                self.statistics[u'detailed'][i][0] and u'YES' or u'NO',
                self.statistics[u'detailed'][i][1] and u'YES' or u'NO'
                ]))
            if self.statistics[u'detailed'][i][0] and \
                    self.statistics[u'detailed'][i][1]:
                for j in range(3):
                    item.setBackground(j, Qt.green)
                    item.setForeground(j, Qt.black)
            elif self.statistics[u'detailed'][i][0] or \
                    self.statistics[u'detailed'][i][1]:
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
        for i in range(3):
            self.ui.artists.resizeColumnToContents(i)
        for a in sArtists:
            i = self.ui.artists.findItems(a, Qt.MatchExactly)
            i[0].setSelected(True)
        for a in sAlbums:
            i = self.ui.albums.findItems(a, Qt.MatchExactly)
            i[0].setSelected(True)
        for a in sTracks:
            i = self.ui.tracks.findItems(a, Qt.MatchExactly)
            i[0].setSelected(True)
        self.ui.artistsGreen.setText(self.statistics[u'artists'][0])
        self.ui.artistsYellow.setText(self.statistics[u'artists'][1])
        self.ui.artistsRed.setText(self.statistics[u'artists'][2])
        self.ui.albumsGreen.setText(self.statistics[u'albums'][0])
        self.ui.albumsYellow.setText(self.statistics[u'albums'][1])
        self.ui.albumsRed.setText(self.statistics[u'albums'][2])
    def save(self):
        u"""Save database to file."""
        try:
            self.db.write(self.library)
        except AttributeError:
            self.statusBar().showMessage(self.trUtf8('Nothing to save...'))
        else:
            self.statusBar().showMessage(self.trUtf8('Saved'))
            self.oldLib = deepcopy(self.library)
    def fillAlbums(self):
        items = self.ui.artists.selectedItems()
        self.ui.albums.clear()
        self.ui.albums.setSortingEnabled(False)
        for item in items:
            artist = unicode(item.text(0))
            for date, albums in self.library[1][artist].iteritems():
                for album, data in albums.iteritems():
                    key = self.library[4][artist + date + album]
                    item_ = QtGui.QTreeWidgetItem(QStringList([
                        date, album,
                        key[u'digital'] and u'YES' or u'NO',
                        key[u'analog'] and u'YES' or u'NO'
                        ]))
                    item_.artist = artist
                    if key[u'digital'] and key[u'analog']:
                        for i in range(4):
                            item_.setBackground(i, Qt.green)
                            item_.setForeground(i, Qt.black)
                    elif key[u'digital'] or key[u'analog']:
                        for i in range(4):
                            item_.setBackground(i, Qt.yellow)
                            item_.setForeground(i, Qt.black)
                    else:
                        for i in range(4):
                            item_.setBackground(i, Qt.red)
                            item_.setForeground(i, Qt.black)
                    self.ui.albums.addTopLevelItem(item_)
        self.ui.albums.setSortingEnabled(True)
        self.ui.albums.sortItems(0, 0)
        for i in range(4):
            self.ui.albums.resizeColumnToContents(i)
    def fillTracks(self):
        items = self.ui.albums.selectedItems()
        self.ui.tracks.clear()
        self.ui.tracks.setSortingEnabled(False)
        for item in items:
            date = unicode(item.text(0))
            album = unicode(item.text(1))
            for num, titles in self.library[1][item.artist] \
                    [date][album].iteritems():
                for title in titles.keys():
                    item_ = NumericTreeWidgetItem(QStringList([
                        num, title]))
                    item_.album = album
                    item_.year = date
                    item_.artist = item.artist
                    self.ui.tracks.addTopLevelItem(item_)
        self.ui.tracks.setSortingEnabled(True)
        self.ui.tracks.sortItems(0, 0)
        self.ui.tracks.resizeColumnToContents(0)
        self.ui.tracks.resizeColumnToContents(1)
    def computeStats(self):
        artists = [0, 0, 0]
        albums = [0, 0, 0]
        detailed = []
        for a, d in self.library[1].iteritems():
            artist = 0
            for y, t in d.iteritems():
                for aa in t.keys():
                    key = self.library[4][a + y + aa]
                    if not key[u'digital'] and not key[u'analog']:
                        albums[2] += 1
                        artist = 1
                    elif key[u'digital'] and key[u'analog']:
                        albums[0] += 1
                        if not artist:
                            artist = 4
                    else:
                        albums[1] += 1
                        if not artist or artist == 4:
                            if key[u'digital']:
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
                u'artists': (unicode(artists[0]),
                    unicode(artists[1]), unicode(artists[2])),
                u'albums': (unicode(albums[0]),
                    unicode(albums[1]), unicode(albums[2])),
                u'detailed': detailed
                }
    def closeEvent(self, event):
        def unload():
            for plugin in self.ui.plugins.values():
                plugin.unload()
            self.__settings.setValue(u'splitters', self.ui.splitter.saveState())
        if self.oldLib != self.library:
            def save():
                self.save()
            def reject():
                event.ignore()
            from interfaces.confirmation import ConfirmationDialog
            dialog = ConfirmationDialog()
            dialog.buttons.accepted.connect(save)
            dialog.buttons.accepted.connect(unload)
            dialog.buttons.rejected.connect(reject)
            dialog.buttons.helpRequested.connect(unload)
            dialog.exec_()
        else:
            unload()

def run():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(u'Fetcher')
    locale = QLocale.system().name()
    path = os.path.dirname(os.path.realpath(__file__)) + u'/langs/'
    translator = QTranslator()
    if translator.load(u'main_' + locale, path):
        app.installTranslator(translator)
    main = Main()
    main.show()
    sys.exit(app.exec_())
