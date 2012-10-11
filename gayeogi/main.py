# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak © 2010 - 2012
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
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QSettings, QLocale, QTranslator
from PyQt4.QtCore import pyqtSignal, QModelIndex
from gayeogi.db.local import DB
from gayeogi.db.distributor import Distributor
from gayeogi.interfaces.settings import Settings
from gayeogi.utils import Filter
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
        super(ADRItemDelegate, self).__init__(parent)
        self.palette = QtGui.QPalette()
        self.buttoned = False
        self.mx = 0
        self.my = 0
        self.ry = 0
        self.rry = -1
        self.rx = 0
        self.ht = 0

    def paint(self, painter, option, index):
        super(ADRItemDelegate, self).paint(painter, option, QModelIndex())
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.palette.mid())
        ry = option.rect.y()
        rx = option.rect.x()
        width = option.rect.width()
        self.ht = option.rect.height()
        self.ry = ry
        self.rx = rx
        painter.drawRoundedRect(
            rx + 1, ry + 2, 36, self.ht - 5, 20, 60, Qt.RelativeSize
        )
        painter.setPen(QtGui.QPen())
        metrics = option.fontMetrics
        x = rx + 8 + metrics.width(u'a')
        if index.data(234).toBool():
            painter.drawText(x, ry + self.ht - 6, u'd')
        x += metrics.width(u'd')
        if index.data(345).toBool():
            painter.drawText(x, ry + self.ht - 6, u'r')
        if self.buttonOver(rx, ry):
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
        painter.drawText(
            rx + 39, ry + pSize, index.data(Qt.DisplayRole).toString()
        )
        painter.restore()
        pixmap = index.data(666).toPyObject()
        if pixmap:
            painter.drawPixmap(rx + width - 80, ry, pixmap)

    def buttonOver(self, x, y):
        return (
            self.mx >= x + 1 and self.mx <= x + 36 and
            self.my >= y + 1 and self.my <= y + self.ht
        )


class TableView(QtGui.QTableView):
    """Docstring for TableView """

    def __init__(self, state, parent=None):
        """@todo: to be defined

        :parent: @todo
        """
        super(TableView, self).__init__(parent)
        self.setSelectionMode(self.ExtendedSelection)
        self.setSelectionBehavior(self.SelectRows)
        self.setEditTriggers(self.NoEditTriggers)
        self.setShowGrid(False)
        self.setCornerButtonEnabled(False)
        self.setWordWrap(False)
        vheader = self.verticalHeader()
        vheader.setHidden(True)
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        hheader.setDefaultAlignment(Qt.AlignLeft)
        hheader.setHighlightSections(False)
        hheader.setMovable(True)
        hheader.setContextMenuPolicy(Qt.CustomContextMenu)
        hheader.customContextMenuRequested.connect(self.showHeaderContextMenu)
        # This restores state over and over for every column added.
        # FIXME: Restore state once (somehow).
        #hheader.sectionCountChanged.connect(
            #lambda: self.horizontalHeader().restoreState(state)
        #)

    def showHeaderContextMenu(self):
        """@todo: Docstring for showHeaderContextMenu """
        menu = QtGui.QMenu()
        model = self.model()
        for i in xrange(model.columnCount()):
            action = menu.addAction(
                model.headerData(i, Qt.Horizontal, Qt.DisplayRole).toString()
            )
            action.setProperty(u'column', i)
            action.setCheckable(True)
            if not self.isColumnHidden(i):
                action.setChecked(True)
        menu.triggered.connect(self.showHideColumn)
        menu.exec_(QtGui.QCursor.pos())

    def showHideColumn(self, action):
        """@todo: Docstring for showHideColumn

        :action: @todo
        :returns: @todo

        """
        column = action.property(u'column').toInt()[0]
        self.setColumnHidden(column, not self.isColumnHidden(column))


class ADRTableView(TableView):
    def __init__(self, state, parent=None):
        super(ADRTableView, self).__init__(state, parent)
        self.setMouseTracking(True)
        self.delegate = ADRItemDelegate()
        self.delegate.buttonClicked.connect(self.callback)
        self.setItemDelegateForColumn(1, self.delegate)

    def buttoned(self, mx, rx):
        return mx >= rx + 1 and mx <= rx + 36

    def callback(self, index):
        self.model().setData(index, not index.data(123).toBool(), 123)

    def mouseMoveEvent(self, event):
        if event.y() == 0 or self.delegate.rry + self.delegate.ht < event.y():
            self.delegate.rry = -1
        self.delegate.mx = event.x()
        self.delegate.my = event.y()
        self.viewport().update()

    def mouseReleaseEvent(self, event):
        if not self.buttoned(event.x(), self.delegate.rx):
            super(ADRTableView, self).mouseReleaseEvent(event)
        else:
            self.delegate.buttoned = True
            self.delegate.my = event.y()
            self.viewport().update()

    def mousePressEvent(self, event):
        if not self.buttoned(event.x(), self.delegate.rx):
            super(ADRTableView, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if not self.buttoned(event.x(), self.delegate.rx):
            super(ADRTableView, self).mouseDoubleClickEvent(event)


class View(QtGui.QWidget):
    def __init__(self, model, view, pixmap, parent=None):
        """@todo: Docstring for __init__

        :model: @todo
        :view: @todo
        :pixmap: @todo
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
        self.view = view
        self.view.setModel(self.model)
        vheader = self.view.verticalHeader()
        if pixmap is not None:
            vheader.setDefaultSectionSize(80)
        else:
            vheader.setDefaultSectionSize(
                self.view.fontMetrics().lineSpacing()
            )
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.filter)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.view.setSortingEnabled(True)


class Main(QtGui.QMainWindow):
    __settings = QSettings(u'gayeogi', u'gayeogi')
    __dbsettings = QSettings(u'gayeogi', u'Databases')

    def __init__(self):
        super(Main, self).__init__()
        if not os.path.exists(dbPath):
            os.mkdir(dbPath)
            if os.path.exists(os.path.join(dbPath[:-3], u'db.pkl')):
                pass  # TODO: convert old db to new
            else:
                dialog = Settings()
                dialog.exec_()
        self.db = DB(dbPath)
        self.db.finished.connect(self.enableButtons)
        self.db.artistsStatisticsChanged.connect(self.updateArtistsStatistics)
        self.db.albumsStatisticsChanged.connect(self.updateAlbumsStatistics)
        from interfaces.main import Ui_main
        self.ui = Ui_main()
        widget = QtGui.QWidget()
        self.ui.setupUi(widget)
        self.ui.artists = View(self.db.artists, TableView(
            self.__settings.value(u'artistsView').toByteArray()
        ), Main.__dbsettings.value(
            u'image/artist/enabled', 2
        ).toBool(), self.ui.splitter)
        delegate = ADRItemDelegate()
        self.ui.artists.view.setItemDelegateForColumn(0, delegate)
        self.ui.albums = View(self.db.albums, ADRTableView(
            self.__settings.value(u'albumsView').toByteArray()
        ), Main.__dbsettings.value(
            u'image/album/enabled', 2
        ).toBool(), self.ui.splitter)
        self.ui.tracks = View(self.db.tracks, TableView(
            self.__settings.value(u'tracksView').toByteArray()
        ), None, self.ui.splitter)
        self.ui.tracks.view.setAlternatingRowColors(True)
        self.ui.artists.view.selectionModel().selectionChanged.connect(
            self.ui.albums.model.setSelection
        )
        self.ui.albums.view.selectionModel().selectionChanged.connect(
            self.ui.tracks.model.setSelection
        )
        self.ui.plugins = {}
        self.ui.splitter.restoreState(
            self.__settings.value(u'splitters').toByteArray()
        )
        self.setCentralWidget(widget)
        self.rt = Distributor(self.db.iterator())
        self.rt.stepped.connect(self.statusBar().showMessage)
        self.rt.finished.connect(self.enableButtons)
        self.ui.local.clicked.connect(self.disableButtons)
        self.ui.local.clicked.connect(self.db.start)
        self.ui.remote.clicked.connect(self.disableButtons)
        self.ui.remote.clicked.connect(self.rt.start)
        self.ui.close.clicked.connect(self.close)
        self.ui.save.clicked.connect(self.save)
        self.ui.settings.clicked.connect(self.showSettings)
        self.statusBar()
        self.setWindowTitle(u'gayeogi ' + __version__)
        self.translators = list()
        self.loadPluginsTranslators()
        self.loadPlugins()

    def disableButtons(self):
        """Disable some buttons one mustn't use during the update."""
        self.ui.local.setDisabled(True)
        self.ui.remote.setDisabled(True)
        self.ui.save.setDisabled(True)
        self.ui.settings.setDisabled(True)

    def enableButtons(self):
        """Enable buttons disabled by Main.disableButtons.
        Also shows the "Done" message.
        """
        self.ui.local.setEnabled(True)
        self.ui.remote.setEnabled(True)
        self.ui.save.setEnabled(True)
        self.ui.settings.setEnabled(True)
        self.statusBar().showMessage(self.trUtf8('Done'))

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
                class__ = class_(self.ui, self.db.artists, self.appendPlugin,
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
            self.removePluginsTranslators()
            self.loadPluginsTranslators()
            self.loadPlugins()
        dialog = Settings()
        dialog.ok.clicked.connect(__save)
        dialog.exec_()

    def save(self):
        u"""Save database to file."""
        self.db.save()
        self.statusBar().showMessage(self.trUtf8('Saved'))

    def updateArtistsStatistics(self, a, d, r):
        """Updates global artists' statistics.

        :a: A statistics.
        :d: D statistics.
        :r: R statistics.
        """
        self.ui.artistsGreen.setText(unicode(a))
        self.ui.artistsYellow.setText(unicode(d))
        self.ui.artistsRed.setText(unicode(r))

    def updateAlbumsStatistics(self, a, d, r):
        """Updated global albums' statistics.

        @note: Attributes as in Main.updateArtistsStatistics.
        """
        self.ui.albumsGreen.setText(unicode(a))
        self.ui.albumsYellow.setText(unicode(d))
        self.ui.albumsRed.setText(unicode(r))

    def closeEvent(self, event):
        def unload():
            for plugin in self.ui.plugins.values():
                plugin.unload()
            self.__settings.setValue(
                u'splitters', self.ui.splitter.saveState()
            )
            self.__settings.setValue(u'artistsView',
                self.ui.artists.view.horizontalHeader().saveState()
            )
            self.__settings.setValue(u'albumsView',
                self.ui.albums.view.horizontalHeader().saveState()
            )
            self.__settings.setValue(u'tracksView',
                self.ui.tracks.view.horizontalHeader().saveState()
            )
        if self.db.modified:
            from interfaces.confirmation import ConfirmationDialog
            dialog = ConfirmationDialog()
            dialog.buttons.accepted.connect(self.save)
            dialog.buttons.accepted.connect(unload)
            dialog.buttons.rejected.connect(event.ignore)
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
