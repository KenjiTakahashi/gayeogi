# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak (C) 2010 - 2012
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
import re
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QSettings, QLocale, QTranslator, QSize
from PyQt4.QtCore import pyqtSignal, QModelIndex
from gayeogi.db.local import DB
from gayeogi.db.distributor import Distributor
from gayeogi.interfaces.settings import Settings
from gayeogi.utils.filter import Filter
import gayeogi.plugins

__version__ = '0.6.3'
locale = QLocale.system().name()
if sys.platform == 'win32':
    from PyQt4.QtGui import QDesktopServices
    service = QDesktopServices()
    dbPath = os.path.join(
        unicode(service.storageLocation(9)), u'gayeogi', u'db'
    )
    lnPath = u''
else:  # Most POSIX systems, there may be more elifs in future.
    dbPath = os.path.expanduser(u'~/.config/gayeogi/db')
    lnPath = os.path.dirname(__file__)


class ADRItemDelegate(QtGui.QStyledItemDelegate):
    buttonClicked = pyqtSignal(QModelIndex)

    def __init__(self, parent=None):
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


class ADRTreeView(QtGui.QTreeView):
    buttonClicked = pyqtSignal(QtGui.QTreeWidgetItem)

    def __init__(self, parent=None):
        super(ADRTreeView, self).__init__(parent)
        self.setIndentation(0)
        self.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self.setMouseTracking(True)
        self.delegate = ADRItemDelegate()
        self.delegate.buttonClicked.connect(self.callback)
        self.setItemDelegateForColumn(1, self.delegate)
        self.setSortingEnabled(True)

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


class View(QtGui.QWidget):
    def __init__(self, model, parent=None):
        """@todo: Docstring for __init__

        :model: @todo
        :parent: @todo
        :returns: @todo

        """
        super(View, self).__init__(parent)
        self.model = Filter(model)
        self.filter = QtGui.QLineEdit()
        self.filter.textEdited.connect(self.model.setFilter)
        self.filter.setStatusTip(self.trUtf8((
            u"Pattern: <pair>|<pair>, "
            u"where <pair> is <column_name>:<searching_phrase> or (not) "
            u"(a or d or r). Case insensitive, regexp allowed."
        )))
        self.view = QtGui.QTreeView()
        self.view.setModel(self.model)
        self.view.setSelectionMode(QtGui.QTreeView.ExtendedSelection)
        self.view.setEditTriggers(QtGui.QTreeView.NoEditTriggers)
        self.view.setIndentation(0)
        self.view.setItemsExpandable(False)
        self.view.setSortingEnabled(True)
        self.view.selectionModel().selectionChanged.connect(
            self.model.setSelection
        )
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.filter)
        layout.addWidget(self.view)
        self.setLayout(layout)


class Main(QtGui.QMainWindow):
    __settings = QSettings(u'gayeogi', u'gayeogi')

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.statistics = None
        if not os.path.exists(dbPath):
            os.mkdir(dbPath)
            if os.path.exists(os.path.join(dbPath[:-3], u'db.pkl')):
                pass  # TODO: convert old db to new
            else:
                dialog = Settings()
                dialog.exec_()
        self.db = DB(dbPath)
        from interfaces.main import Ui_main
        self.ui = Ui_main()
        widget = QtGui.QWidget()
        self.ui.setupUi(widget)
        self.ui.artists = View(self.db.artists, self.ui.splitter)
        delegate = ADRItemDelegate()
        #self.ui.artists.setItemDelegateForColumn(0, delegate)
        self.ui.albums = ADRTreeView(self.ui.splitter)
        self.ui.albums.setModel(self.db.albums)
        #self.ui.albums = View(self.db.albums, self.ui.splitter)
        self.ui.albums.selectionModel().selectionChanged.connect(
            self.db.tracks.setSelection
        )
        self.ui.albums.buttonClicked.connect(self.setAnalog)
        self.ui.tracks = View(self.db.tracks, self.ui.splitter)
        self.ui.plugins = {}
        self.ui.splitter.restoreState(
            self.__settings.value(u'splitters').toByteArray()
        )
        self.setCentralWidget(widget)
        ###
        self.library = (__version__, {}, {}, {}, {}, [False])
        self.ignores = self.__settings.value(u'ignores', []).toPyObject()
        if self.ignores == None:
            self.ignores = []
        directory = self.__settings.value(u'directory', []).toPyObject()
        if type(directory) != list:
            directory = [(unicode(directory), 2)]
        self.rt = Distributor(self.library)
        self.rt.stepped.connect(self.statusBar().showMessage)
        self.rt.updated.connect(self.update)
        self.ui.local.clicked.connect(self.disableButtons)
        self.ui.local.clicked.connect(self.db.run)  # FIXME: threadify
        self.ui.remote.clicked.connect(self.disableButtons)
        self.ui.remote.clicked.connect(self.rt.start)
        self.ui.close.clicked.connect(self.close)
        self.ui.save.clicked.connect(self.save)
        self.ui.settings.clicked.connect(self.showSettings)
        self.statusBar()
        self.setWindowTitle(u'gayeogi ' + __version__)
        self.translators = list()
        #self.loadPluginsTranslators()
        #self.loadPlugins()

    def disableButtons(self):
        """Disable some buttons one mustn't use during the update.

        @note: They are then re-enabled in the update() method.
        """
        self.ui.local.setDisabled(True)
        self.ui.remote.setDisabled(True)
        self.ui.save.setDisabled(True)
        self.ui.settings.setDisabled(True)

    def loadPluginsTranslators(self):
        reload(gayeogi.plugins)
        app = QtGui.QApplication.instance()
        for plugin in gayeogi.plugins.__all__:
            translator = QTranslator()
            if translator.load(plugin + u'_' + locale,
                    os.path.join(lnPath, u'plugins', u'langs')):
                self.translators.append(translator)
                app.installTranslator(translator)

    def removePluginsTranslators(self):
        app = QtGui.QApplication.instance()
        for translator in self.translators:
            app.removeTranslator(translator)

    def loadPlugins(self):
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
        if position == 'start':
            position = 0
        elif position == 'end':
            position = len(parent.parent().children()) - 7
        if isinstance(parent, QtGui.QLayout):
            widget = parent.itemAt(position)
            if not widget:
                parent.insertWidget(position, child)
            else:
                if isinstance(widget, QtGui.QTabWidget):
                    widget.addTab(child, child.name)
                else:
                    try:
                        widget.name
                    except AttributeError:
                        parent.insertWidget(position, child)
                    else:
                        widget = parent.takeAt(position).widget()
                        tab = QtGui.QTabWidget()
                        tab.setTabPosition(tab.South)
                        tab.addTab(widget, widget.name)
                        tab.addTab(child, child.name)
                        parent.insertWidget(position, tab)

    def removePlugin(self, parent, child, position):
        parent = getattr(self.ui, parent)
        if position == 'start':
            position = 0
        elif position == 'end':
            position = len(parent.parent().children()) - 8
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

    def showSettings(self):
        u"""Show settings dialog and then update accordingly."""
        def __save():
            directory = self.__settings.value(u'directory', []).toPyObject()
            if type(directory) != list:
                directory = [(unicode(directory), 2)]
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
            self.library[5][0] = False
            self.db.write(self.library)
        except AttributeError:
            self.statusBar().showMessage(self.trUtf8('Nothing to save...'))
        else:
            self.statusBar().showMessage(self.trUtf8('Saved'))
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
            item = QtGui.QTreeWidgetItem([l])
            item.setData(0, 123, self.statistics[u'detailed'][l][u'a'])
            item.setData(0, 234, self.statistics[u'detailed'][l][u'd'])
            item.setData(0, 345, self.statistics[u'detailed'][l][u'r'])
            item.setData(0, 987, l)
            self.ui.artists.insertTopLevelItem(i, item)
        self.ui.artists.setSortingEnabled(True)
        self.ui.artists.sortItems(0, 0)
        for i in range(3):
            self.ui.artists.resizeColumnToContents(i)
        self.ui.artistFilter.textEdited.emit(self.ui.artistFilter.text())
        for a in sArtists:
            i = self.ui.artists.findItems(a, Qt.MatchExactly)
            if i:
                i[0].setSelected(True)
        for a in sAlbums:
            i = self.ui.albums.findItems(a, Qt.MatchExactly, 1)
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
                    analog = int(key[u'analog'])
                    digital = int(key[u'digital'])
                    remote = int(bool(key[u'remote']))
                    albums[0] += analog
                    albums[1] += digital
                    albums[2] += remote
                    if not analog:
                        aa = 0
                    if not digital:
                        ad = 0
                    if not remote:
                        ar = 0
            detailed[a][u'a'] = bool(aa)
            detailed[a][u'd'] = bool(ad)
            detailed[a][u'r'] = bool(ar)
            artists[0] += aa
            artists[1] += ad
            artists[2] += ar
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
        if self.library[5][0]:
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
    translator = QTranslator()
    if translator.load(u'main_' + locale, os.path.join(lnPath, u'langs')):
        app.installTranslator(translator)
    main = Main()
    main.show()
    sys.exit(app.exec_())
