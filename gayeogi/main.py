# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/Fetcher/
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

import sys
import os
import cPickle
import re
from PyQt4 import QtGui
from PyQt4.QtCore import QStringList, Qt, QSettings, QLocale, QTranslator, QSize
from PyQt4.QtCore import pyqtSignal, QModelIndex
from copy import deepcopy
from gayeogi.db.local import Filesystem
from gayeogi.db.distributor import Distributor
from gayeogi.interfaces.settings import Settings
import gayeogi.plugins

version = u'0.6'
if sys.platform == 'win32':
    from PyQt4.QtGui import QDesktopServices
    service = QDesktopServices()
    dbPath = os.path.join(unicode(service.storageLocation(9)), u'gayeogi')
else: # Most POSIX systems, there may be more elifs in future.
    dbPath = os.path.expanduser(u'~/.config/gayeogi')

class ADRItemDelegate(QtGui.QStyledItemDelegate):
    buttonClicked = pyqtSignal(QModelIndex)
    def __init__(self, parent = None):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.palette = QtGui.QPalette()
        self.buttoned = False
        self.mx = 0
        self.my = 0
        self.ry = 0
        self.rry = -1
        self.rx = 0
        self.ht = 0
    def paint(self, painter, option, index):
        QtGui.QStyledItemDelegate.paint(self, painter, option, QModelIndex())
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.palette.mid())
        ry = option.rect.y()
        rx = option.rect.x()
        self.ht = option.rect.height()
        self.ry = ry
        self.rx = rx
        painter.drawRoundedRect(rx + 1, ry + 2, 36,
                self.ht - 5, 20, 60, Qt.RelativeSize)
        painter.setPen(QtGui.QPen())
        metrics = option.fontMetrics
        x = rx + 8 + metrics.width(u'a')
        if index.data(234).toBool():
            painter.drawText(x, ry + self.ht - 6, u'd')
        x += metrics.width(u'd')
        if index.data(345).toBool():
            painter.drawText(x, ry + self.ht - 6, u'r')
        mouseOver = option.state & QtGui.QStyle.State_MouseOver
        if self.buttonOver(mouseOver, rx):
            if self.buttoned:
                if self.my >= ry + 1 and self.my <= ry + self.ht - 6:
                    self.rry = ry
                    self.buttonClicked.emit(index)
                    self.buttoned = False
            elif ry != self.rry:
                painter.setPen(QtGui.QPen(self.palette.brightText(), 0))
                self.rry = -1
                painter.drawText(rx + 8, ry + self.ht - 6, u'a')
            elif index.data(123).toBool():
                painter.drawText(rx + 8, ry + self.ht - 6, u'a')
        elif index.data(123).toBool():
            painter.drawText(rx + 8, ry + self.ht - 6, u'a')
        painter.restore()
        pSize = self.ht / 2 + option.font.pointSize() / 2
        if pSize % 2 == 0:
            pSize += 1
        pSize -= 1
        painter.save()
        if option.state & QtGui.QStyle.State_Selected:
            if option.state & QtGui.QStyle.State_HasFocus:
                painter.setPen(QtGui.QPen(self.palette.highlightedText(), 0))
            else:
                painter.setPen(QtGui.QPen(self.palette.brightText(), 0))
        painter.drawText(rx + 39, ry + pSize, index.data(987).toString())
        painter.restore()
    def buttonOver(self, mo, x):
        return self.mx >= x + 1 and self.mx <= x + 36 and mo
    def sizeHint(self, option, index):
        return QSize(39 + option.fontMetrics.width(
            index.data(987).toString()), option.fontMetrics.height() + 2)

class ADRTreeWidget(QtGui.QTreeWidget):
    buttonClicked = pyqtSignal(QtGui.QTreeWidgetItem)
    def __init__(self, parent = None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setIndentation(0)
        self.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self.setMouseTracking(True)
        self.delegate = ADRItemDelegate()
        self.delegate.buttonClicked.connect(self.callback)
        self.setItemDelegateForColumn(1, self.delegate)
    def buttoned(self, mx, rx):
        return mx >= rx + 1 and mx <= rx + 36
    def callback(self, index):
        self.buttonClicked.emit(self.itemFromIndex(index))
    def mouseMoveEvent(self, event):
        if event.y() == 0 or self.delegate.rry + self.delegate.ht < event.y():
            self.delegate.rry = -1
        self.delegate.mx = event.x()
        self.delegate.my = event.y()
        self.viewport().update()
    def mouseReleaseEvent(self, event):
        if not self.buttoned(event.x(), self.delegate.rx):
            QtGui.QTreeWidget.mouseReleaseEvent(self, event)
        else:
            self.delegate.buttoned = True
            self.delegate.my = event.y()
            self.viewport().update()
    def mousePressEvent(self, event):
        if not self.buttoned(event.x(), self.delegate.rx):
            QtGui.QTreeWidget.mousePressEvent(self, event)
    def mouseDoubleClickEvent(self, event):
        if not self.buttoned(event.x(), self.delegate.rx):
            QtGui.QTreeWidget.mouseDoubleClickEvent(self, event)

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
    __settings = QSettings(u'gayeogi', u'gayeogi')
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
        self.ui.artists.setHeaderLabels(QStringList([u'Artist']))
        self.ui.artists.itemSelectionChanged.connect(self.fillAlbums)
        delegate = ADRItemDelegate()
        self.ui.artists.setItemDelegateForColumn(0, delegate)
        self.ui.albums = ADRTreeWidget()
        self.ui.albums.setHeaderLabels(QStringList([u'Year', u'Album']))
        self.ui.albums.buttonClicked.connect(self.setAnalog)
        self.ui.albums.itemSelectionChanged.connect(self.fillTracks)
        self.ui.verticalLayout_4.addWidget(self.ui.albums)
        self.ui.tracks.setHeaderLabels(QStringList(['#', u'Title']))
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
        self.ui.logs.setHeaderLabels(QStringList([
            self.trUtf8('Module'),
            self.trUtf8('Type'),
            self.trUtf8('File/Entry'),
            self.trUtf8('Message')]))
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
        self.setWindowTitle(u'gayeogi ' + version)
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
        reload(gayeogi.plugins)
        app = QtGui.QApplication.instance()
        for plugin in gayeogi.plugins.__all__:
            class_ = getattr(gayeogi.plugins, plugin).Main
            translator = class_.translator()
            if translator:
                self.translators.append(translator)
                app.installTranslator(translator)
    def removePluginsTranslators(self):
        app = QtGui.QApplication.instance()
        for translator in self.translators:
            app.removeTranslator(translator)
    def loadPlugins(self):
        reload(gayeogi.plugins)
        def depends(plugin):
            for p in gayeogi.plugins.__all__:
                class_ = getattr(gayeogi.plugins, p).Main
                if plugin in class_.depends and class_.loaded:
                    return True
            return False
        for plugin in gayeogi.plugins.__all__:
            class_ = getattr(gayeogi.plugins, plugin).Main
            __settings_ = QSettings(u'gayeogi', class_.name)
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
        adr = [u'a', u'd', u'r', u'not a', u'not d', u'not r']
        num_adr = dict()
        __num_adr = {
                u'a': 123,
                u'd': 234,
                u'r': 345
                }
        for a in (unicode(text)).split(u'|'):
            temp = a.split(u':')
            if len(temp) == 1 and temp[0] in adr:
                temp2 = temp[0].split(u' ')
                if len(temp2) == 2:
                    num_adr[temp2[1]] = False
                else:
                    num_adr[temp2[0]] = True
                continue
            if len(temp) != 2 or temp[1] == u'':
                break
            columns.append(temp[0].lower())
            arguments.append(temp[1].lower())
        if (len(columns) != 0 and len(columns) == len(arguments)) or num_adr:
            tree = self.sender().parent().children()[2]
            header = tree.header().model()
            num_columns = [i for i in range(tree.columnCount())
                    if (unicode(header.headerData(i,
                        Qt.Horizontal).toString())).lower() in columns]
            adr_column = -1
            if num_adr:
                item = tree.topLevelItem(0)
                for i in range(item.columnCount()):
                    if item.data(i, 987).toString():
                        adr_column = i
                        break
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                hidden = list()
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
                if adr_column != -1 and item not in hidden:
                    for adr, v in num_adr.iteritems():
                        if item.data(adr_column, __num_adr[adr]).toBool() == v:
                            item.setHidden(False)
                        else:
                            item.setHidden(True)
                            hidden.append(item)
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
    def save(self):
        u"""Save database to file."""
        try:
            self.db.write(self.library)
        except AttributeError:
            self.statusBar().showMessage(self.trUtf8('Nothing to save...'))
        else:
            self.statusBar().showMessage(self.trUtf8('Saved'))
            self.oldLib = deepcopy(self.library)
    def setAnalog(self, item):
        data = not item.data(1, 123).toBool()
        item.setData(1, 123, data)
        self.library[4][item.artist + unicode(item.text(0))
                + unicode(item.data(1, 987).toString())][u'analog'] = data
        if data:
            self.statistics[u'albums'][0] += 1
            switch = True
            for y, d in self.library[1][item.artist].iteritems():
                for a in d.keys():
                    if not self.library[4][item.artist + y + a][u'analog']:
                        switch = False
                        break
                if not switch:
                    break
            if switch:
                self.statistics[u'artists'][0] += 1
                self.ui.artistsGreen.setText(
                        unicode(self.statistics[u'artists'][0]))
                self.statistics[u'detailed'][item.artist][u'a'] = True
                self.ui.artists.topLevelItem(item.aIndex).setData(0, 123, True)
        else:
            self.statistics[u'albums'][0] -= 1
            if self.ui.artists.topLevelItem(item.aIndex).data(0, 123).toBool():
                self.statistics[u'artists'][0] -= 1
                self.ui.artistsGreen.setText(
                        unicode(self.statistics[u'artists'][0]))
                self.statistics[u'detailed'][item.artist][u'a'] = False
                self.ui.artists.topLevelItem(item.aIndex).setData(0, 123, False)
        self.ui.albumsGreen.setText(unicode(self.statistics[u'albums'][0]))
    def update(self):
        self.computeStats()
        self.statusBar().showMessage(self.trUtf8('Done'))
        self.ui.local.setEnabled(True)
        self.ui.remote.setEnabled(True)
        self.ui.save.setEnabled(True)
        self.ui.settings.setEnabled(True)
        sArtists = [i.text(0) for i in self.ui.artists.selectedItems()]
        sAlbums = [i.text(1) for i in self.ui.albums.selectedItems()]
        sTracks = [i.text(0) for i in self.ui.tracks.selectedItems()]
        self.ui.artists.clear()
        self.ui.artists.setSortingEnabled(False)
        for i, l in enumerate(self.library[1].keys()):
            item = QtGui.QTreeWidgetItem(QStringList([l]))
            item.setData(0, 123, self.statistics[u'detailed'][l][u'a'])
            item.setData(0, 234, self.statistics[u'detailed'][l][u'd'])
            item.setData(0, 345, self.statistics[u'detailed'][l][u'r'])
            item.setData(0, 987, l)
            self.ui.artists.insertTopLevelItem(i, item)
        self.ui.artists.setSortingEnabled(True)
        self.ui.artists.sortItems(0, 0)
        for i in range(3):
            self.ui.artists.resizeColumnToContents(i)
        for a in sArtists:
            i = self.ui.artists.findItems(a, Qt.MatchExactly)
            if i:
                i[0].setSelected(True)
        for a in sAlbums:
            i = self.ui.albums.findItems(a, Qt.MatchExactly)
            if i:
                i[0].setSelected(True)
        for a in sTracks:
            i = self.ui.tracks.findItems(a, Qt.MatchExactly)
            if i:
                i[0].setSelected(True)
        self.ui.artistsGreen.setText(unicode(self.statistics[u'artists'][0]))
        self.ui.artistsYellow.setText(unicode(self.statistics[u'artists'][1]))
        self.ui.artistsRed.setText(unicode(self.statistics[u'artists'][2]))
        self.ui.albumsGreen.setText(unicode(self.statistics[u'albums'][0]))
        self.ui.albumsYellow.setText(unicode(self.statistics[u'albums'][1]))
        self.ui.albumsRed.setText(unicode(self.statistics[u'albums'][2]))
    def fillAlbums(self):
        items = self.ui.artists.selectedItems()
        self.ui.albums.clear()
        self.ui.albums.setSortingEnabled(False)
        for item in items:
            artist = unicode(item.data(0, 987).toString())
            for date, albums in self.library[1][artist].iteritems():
                for album, data in albums.iteritems():
                    key = self.library[4][artist + date + album]
                    item_ = QtGui.QTreeWidgetItem(QStringList([date, album]))
                    item_.artist = artist
                    item_.aIndex = self.ui.artists.indexOfTopLevelItem(item)
                    item_.setData(1, 123, key[u'analog'])
                    item_.setData(1, 234, key[u'digital'])
                    item_.setData(1, 345, key[u'remote'])
                    item_.setData(1, 987, album)
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
            album = unicode(item.data(1, 987).toString())
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
        detailed = dict()
        for a, d in self.library[1].iteritems():
            detailed[a] = dict()
            aa = 1
            ad = 1
            ar = 1
            for y, t in d.iteritems():
                for al in t.keys():
                    key = self.library[4][a + y + al]
                    if key[u'analog']:
                        albums[0] += 1
                    elif key[u'digital']:
                        albums[1] += 1
                    elif key[u'remote']:
                        albums[2] += 1
                    if not key[u'analog']:
                        aa = 0
                    if not key[u'digital']:
                        ad = 0
                    if not key[u'remote']:
                        ar = 0
            if aa:
                artists[0] += 1
            elif ad:
                artists[1] += 1
            elif ar:
                artists[2] += 1
            if aa:
                detailed[a][u'a'] = True
            else:
                detailed[a][u'a'] = False
            if ad:
                detailed[a][u'd'] = True
            else:
                detailed[a][u'd'] = False
            if ar:
                detailed[a][u'r'] = True
            else:
                detailed[a][u'r'] = False
        self.statistics = {
                u'artists': artists,
                u'albums': albums,
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
    app.setApplicationName(u'gayeogi')
    locale = QLocale.system().name()
    path = os.path.dirname(os.path.realpath(__file__)) + u'/langs/'
    translator = QTranslator()
    if translator.load(u'main_' + locale, path):
        app.installTranslator(translator)
    main = Main()
    main.show()
    sys.exit(app.exec_())
