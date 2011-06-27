# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
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

from PyQt4.phonon import Phonon
from PyQt4 import QtGui
from PyQt4.QtCore import QSize, Qt, QModelIndex, QLocale, QTranslator
from PyQt4.QtCore import pyqtSignal, QSettings, QString, QPointF, QRect
from os.path import dirname, realpath

class PlayListItemDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        painter.save()
        rx = option.rect.x()
        ry = option.rect.y()
        wt = option.rect.width()
        ht = option.rect.height()
        size = option.font.pointSize()
        font = option.font
        if index.data(672).toBool():
            font.setBold(True)
            painter.setFont(font)
        if option.state & QtGui.QStyle.State_Selected:
            if option.state & QtGui.QStyle.State_HasFocus:
                painter.setPen(QtGui.QPen(option.palette.highlightedText(), 0))
            else:
                painter.setPen(QtGui.QPen(option.palette.brightText(), 0))
        painter.drawText(QRect(rx + 5, ry + 5, wt, ht), Qt.AlignLeft,
                index.data(666).toString() + u'. '
                + index.data(667).toString() + u'\n'
                + index.data(668).toString() + u' ('
                + index.data(669).toString() + u')')
        font.setPointSize(16)
        painter.setFont(font)
        data670 = index.data(670).toString()
        if data670 != u'':
            painter.drawText(QRect(rx, ry, wt - 5, ht),
                    Qt.AlignRight | Qt.AlignVCenter,
                    data670 + u'/' + index.data(671).toString())
        font.setPointSize(size)
        painter.restore()
    def sizeHint(self, option, index):
        return QSize(0, 12 + option.fontMetrics.height() * 2)

class Playlist(QtGui.QListWidget):
    dropped = pyqtSignal(QtGui.QTreeWidgetItem)
    previouslyActiveItem = None
    activeItem = -1
    activeRow = None
    def setActiveItem(self, item):
        self.previouslyActiveItem = self.activeItem
        self.activeItem = item
        if item:
            self.activeRow = self.row(item)
    def moveItems(self):
        self.previouslyActiveItem = self.activeItem
        self.activeItem = None
    def clearActive(self):
        self.activeItem = None
        self.activeRow = -1
        self.previouslyActiveItem = None
    def dropEvent(self, event):
        source = event.source()
        model = QtGui.QStandardItemModel()
        model.dropMimeData(event.mimeData(), Qt.CopyAction, 0, 0, QModelIndex())
        if isinstance(source, QtGui.QTreeWidget):
            for m in range(model.rowCount()):
                self.dropped.emit(source.topLevelItem(m))
        else:
            event.setDropAction(Qt.MoveAction)
            QtGui.QListWidget.dropEvent(self, event)

class PlayerPushButton(QtGui.QPushButton):
    def __init__(self, parent = None):
        QtGui.QPushButton.__init__(self, parent)
        self.path = QtGui.QPainterPath()
        self.path.setFillRule(Qt.WindingFill)
        self.setFixedWidth(30)
        self.setFixedHeight(30)
    def paintEvent(self, event):
        QtGui.QPushButton.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QPalette().mid())
        painter.drawPath(self.path)

class AddPushButton(PlayerPushButton):
    def __init__(self, parent = None):
        PlayerPushButton.__init__(self, parent)
        self.path.addRoundedRect(7, 12, 16, 6, 20, 60, Qt.RelativeSize)
        self.path.addRoundedRect(12, 7, 6, 16, 60, 20, Qt.RelativeSize)

class RemovePushButton(PlayerPushButton):
    def __init__(self, parent = None):
        PlayerPushButton.__init__(self, parent)
        self.path.addRoundedRect(7, 12, 16, 6, 20, 60, Qt.RelativeSize)

class PlayPausePushButton(PlayerPushButton):
    def __init__(self, parent = None):
        PlayerPushButton.__init__(self, parent)
        self.playPath = QtGui.QPainterPath()
        self.playPath.addPolygon(QtGui.QPolygonF(
            [QPointF(7, 7), QPointF(7, 23), QPointF(23, 15)]))
        self.pausePath = QtGui.QPainterPath()
        self.pausePath.addRoundedRect(7, 7, 6, 16, 60, 20, Qt.RelativeSize)
        self.pausePath.addRoundedRect(17, 7, 6, 16, 60, 20, Qt.RelativeSize)
        self.path = self.playPath
    def setPlaying(self, state):
        if state:
            self.path = self.pausePath
        else:
            self.path = self.playPath
        self.update()
    def isPlaying(self):
        return self.path != self.playPath

class StopPushButton(PlayerPushButton):
    def __init__(self, parent = None):
        PlayerPushButton.__init__(self, parent)
        self.path.addRoundedRect(7, 7, 16, 16, 60, 60, Qt.RelativeSize)

class PreviousPushButton(PlayerPushButton):
    def __init__(self, parent = None):
        PlayerPushButton.__init__(self, parent)
        self.path.addRoundedRect(7, 7, 6, 16, 60, 20, Qt.RelativeSize)
        self.path.addPolygon(QtGui.QPolygonF(
            [QPointF(13, 15), QPointF(18, 7), QPointF(18, 23)]))
        self.path.addPolygon(QtGui.QPolygonF(
            [QPointF(18, 15), QPointF(23, 7), QPointF(23, 23)]))

class NextPushButton(PlayerPushButton):
    def __init__(self, parent = None):
        PlayerPushButton.__init__(self, parent)
        self.path.addPolygon(QtGui.QPolygonF(
            [QPointF(7, 7), QPointF(7, 23), QPointF(12, 15)]))
        self.path.addPolygon(QtGui.QPolygonF(
            [QPointF(12, 7), QPointF(12, 23), QPointF(17, 15)]))
        self.path.addRoundedRect(17, 7, 6, 16, 60, 20, Qt.RelativeSize)

class Main(QtGui.QWidget):
    name = u'Player'
    loaded = False
    depends = []
    trackChanged = pyqtSignal(QString, QString, QString, int)
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    __settings = QSettings('gayeogi', 'Player')
    def __init__(self, parent, library, addWidget, removeWidget):
        QtGui.QWidget.__init__(self, None)
        self.parent = parent
        self.library = library
        self.addWidget = addWidget
        self.removeWidget = removeWidget
    def translator():
        locale = QLocale().system().name()
        path = dirname(realpath(__file__)) + u'/langs/'
        translator = QTranslator()
        if translator.load(u'player_' + locale, path):
            return translator
    translator = staticmethod(translator)
    def load(self):
        add = AddPushButton()
        add.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Add selected item(s) to the playlist.'))
        add.clicked.connect(self.addByButton)
        addShortcut = QtGui.QShortcut(
                QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_A), add)
        addShortcut.activated.connect(self.addByButton)
        remove = RemovePushButton()
        remove.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Remove selected item(s) from the playlist.'))
        remove.clicked.connect(self.removeByButton)
        removeShortcut = QtGui.QShortcut(
                QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_R), remove)
        removeShortcut.activated.connect(self.removeByButton)
        previous = PreviousPushButton()
        previous.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Jump to previous track.'))
        previous.clicked.connect(self.previous)
        previousShortcut = QtGui.QShortcut(
                QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_B), previous)
        previousShortcut.activated.connect(self.previous)
        self.playButton = PlayPausePushButton()
        self.playButton.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Begin/Pause/Resume playback.'))
        self.playButton.clicked.connect(self.playByButton)
        playShortcut = QtGui.QShortcut(QtGui.QKeySequence(
            Qt.CTRL + Qt.SHIFT + Qt.Key_P), self.playButton)
        playShortcut.activated.connect(self.playButton.click)
        stop = StopPushButton()
        stop.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Stop playback.'))
        stop.clicked.connect(self.stop)
        stopShortcut = QtGui.QShortcut(
                QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S), stop)
        stopShortcut.activated.connect(self.stop)
        next_ = NextPushButton()
        next_.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Jump to next track.'))
        next_.clicked.connect(self.next_)
        next_Shortcut = QtGui.QShortcut(
                QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_N), next_)
        next_Shortcut.activated.connect(self.next_)
        volume = Phonon.VolumeSlider()
        volume.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Change volume.'))
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.setContentsMargins(0, 0, 0, 0)
        buttonsLayout.addWidget(add)
        buttonsLayout.addWidget(remove)
        buttonsLayout.addWidget(previous)
        buttonsLayout.addWidget(self.playButton)
        buttonsLayout.addWidget(stop)
        buttonsLayout.addWidget(next_)
        buttonsLayout.addWidget(volume)
        buttons = QtGui.QWidget()
        progress = Phonon.SeekSlider()
        progress.setStatusTip(QtGui.QApplication.translate(
            'Player', 'Seek the track.'))
        buttons.setLayout(buttonsLayout)
        delegate = PlayListItemDelegate()
        self.playlist = Playlist()
        self.playlist.setItemDelegate(delegate)
        self.playlist.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self.__settings.beginGroup('playlist')
        for i in range(self.__settings.value('size').toInt()[0]):
            item = QtGui.QListWidgetItem()
            item.setData(666, self.__settings.value(unicode(i) + '666'))
            item.setData(667, self.__settings.value(unicode(i) + '667'))
            item.setData(668, self.__settings.value(unicode(i) + '668'))
            item.setData(669, self.__settings.value(unicode(i) + '669'))
            item.path = self.__settings.value(unicode(i) + 'path').toString()
            self.playlist.addItem(item)
        self.__settings.endGroup()
        #self.playlist.setDragDropMode(self.playlist.DragDrop)
        self.playlist.itemActivated.connect(self.play)
        #self.playlist.dropped.connect(self.addItem)
        playlistShortcut = QtGui.QShortcut(
                QtGui.QKeySequence(Qt.Key_Delete), self.playlist)
        playlistShortcut.activated.connect(self.removeByButton)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(progress)
        layout.addWidget(self.playlist)
        self.setLayout(layout)
        self.parent.artists.itemActivated.connect(self.addItem)
        self.parent.albums.itemActivated.connect(self.addItem)
        self.parent.tracks.itemActivated.connect(self.addItem)
        self.addWidget(u'horizontalLayout_2', self, 2)
        self.mediaobject = Phonon.MediaObject()
        self.mediaobject.setTickInterval(200)
        self.mediaobject.tick.connect(self.tick)
        self.mediaobject.aboutToFinish.connect(self.nextTrack)
        self.mediaobject.totalTimeChanged.connect(self.updateView)
        self.mediaobject.finished.connect(self.stop)
        self.mediaobject.stateChanged.connect(self.state)
        self.audiooutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.audiooutput.setVolume(
                self.__settings.value('volume', 1).toReal()[0])
        Phonon.createPath(self.mediaobject, self.audiooutput)
        progress.setMediaObject(self.mediaobject)
        volume.setAudioOutput(self.audiooutput)
        Main.loaded = True
    def unload(self):
        self.__settings.setValue('volume', self.audiooutput.volume())
        self.__settings.beginGroup('playlist')
        self.__settings.remove('')
        self.__settings.setValue('size', self.playlist.count())
        for i in range(self.playlist.count()):
            item = self.playlist.item(i)
            self.__settings.setValue(unicode(i) + '666', item.data(666))
            self.__settings.setValue(unicode(i) + '667', item.data(667))
            self.__settings.setValue(unicode(i) + '668', item.data(668))
            self.__settings.setValue(unicode(i) + '669', item.data(669))
            self.__settings.setValue(unicode(i) + 'path', item.path)
        self.__settings.endGroup()
        self.removeWidget(u'horizontalLayout_2', self, 2)
        Main.loaded = False
    def QConfiguration():
        __settings = QSettings(u'gayeogi', u'Player')
        widget = QtGui.QWidget()
        widget.enabled = __settings.value(u'enabled', 0).toInt()[0]
        widget.setSetting = lambda x, y : __settings.setValue(x, y)
        return widget
    QConfiguration = staticmethod(QConfiguration)
    def updateView(self, time):
        self.__resetCurrent()
        item = self.playlist.activeItem
        if item:
            item.setData(670, self.__timeConvert(0))
            item.setData(671, self.__timeConvert(time))
            item.setData(672, True)
            self.playlist.scrollToItem(item)
            self.trackChanged.emit(
                    item.data(669).toString(),
                    item.data(667).toString(),
                    item.data(668).toString(),
                    item.data(666).toInt()[0]
                    )
    def play(self, item):
        self.mediaobject.stop()
        self.mediaobject.clear()
        self.playlist.setActiveItem(item)
        self.mediaobject.enqueue(Phonon.MediaSource(item.path))
        self.mediaobject.play()
        self.playButton.setPlaying(True)
    def stop(self):
        self.playlist.moveItems()
        self.__resetCurrent()
        self.playButton.setPlaying(False)
        self.mediaobject.stop()
    def previous(self):
        index = self.playlist.activeRow - 1
        if index > -1:
            self.play(self.playlist.item(index))
    def next_(self):
        index = self.playlist.activeRow + 1
        if index < self.playlist.count():
            self.play(self.playlist.item(index))
    def tick(self, interval):
        if interval and self.playlist.activeItem:
            self.playlist.activeItem.setData(670, self.__timeConvert(interval))
    def nextTrack(self):
        index = self.playlist.activeRow
        item = self.playlist.item(index + 1)
        if item:
            self.playlist.setActiveItem(item)
            self.mediaobject.enqueue(Phonon.MediaSource(item.path))
    def playByButton(self):
        if not self.playlist.activeItem:
            self.play(self.playlist.item(0))
        else:
            button = self.sender()
            if not button.isPlaying():
                button.setPlaying(True)
                self.mediaobject.play()
            else:
                button.setPlaying(False)
                self.mediaobject.pause()
    def addByButton(self):
        def addItems(items):
            if items:
                for item in items:
                    self.addItem(item)
                return True
            return False
        if not addItems(self.parent.tracks.selectedItems()):
            if not addItems(self.parent.albums.selectedItems()):
                addItems(self.parent.artists.selectedItems())
    def removeByButton(self):
        for item in self.playlist.selectedItems():
            if item == self.playlist.activeItem:
                self.stop()
            self.playlist.takeItem(self.playlist.row(item))
    def addItem(self, item, column = -1):
        if column != -1:
            self.stop()
            self.playlist.clearActive()
            self.playlist.clear()
        try:
            item.album
        except AttributeError:
            try:
                item.artist
            except AttributeError:
                items = []
                for i in range(self.parent.albums.topLevelItemCount()):
                    item_ = self.parent.albums.topLevelItem(i)
                    year = unicode(item_.text(0))
                    album = unicode(item_.data(1, 987).toString())
                    items_ = [self.__createItem((tracknumber, title, album,
                        item.data(0, 987).toString(), d[u'path']))
                        for tracknumber, tracks
                        in self.library[1][item_.artist][year]\
                                [album].iteritems() for title, d in 
                                tracks.iteritems()]
                    items_.sort(self.__compare)
                    items.extend(items_)
                for i in items:
                    self.playlist.addItem(i)
            else:
                for i in range(self.parent.tracks.topLevelItemCount()):
                    item_ = self.parent.tracks.topLevelItem(i)
                    path = self.library[1][item_.artist][item_.year]\
                            [item_.album][unicode(item_.text(0))]\
                            [unicode(item_.text(1))][u'path']
                    self.playlist.addItem(self.__createItem((item_.text(0),
                        item_.text(1), item_.album, item_.artist, path)))
        else:
            path = self.library[1][item.artist][item.year][item.album]\
                    [unicode(item.text(0))][unicode(item.text(1))][u'path']
            self.playlist.addItem(self.__createItem((item.text(0),
                item.text(1), item.album, item.artist, path)))
        if column != -1 and self.playlist.count():
            self.playByButton()
    def state(self, state):
        if state == Phonon.ErrorState:
            def getErrorMessage():
                error = self.mediaobject.errorType()
                if error == Phonon.NormalError:
                    return u'An non-critical error has occurred.'
                elif error == Phonon.FatalError:
                    return u'An fatal error has occurred.'
                else:
                    return u'Completely unknown error.'
            self.errors.emit(
                    u'Player',
                    u'errors',
                    self.playlist.activeItem.path,
                    getErrorMessage())
    def __createItem(self, source):
        item = QtGui.QListWidgetItem()
        item.setData(666, source[0])
        item.setData(667, source[1])
        item.setData(668, source[2])
        item.setData(669, source[3])
        item.path = source[4]
        return item
    def __compare(self, i1, i2):
        tracknumber1 = i1.data(666).toString().split(u'/')[0].toInt()[0]
        tracknumber2 = i2.data(666).toString().split(u'/')[0].toInt()[0]
        if tracknumber1 > tracknumber2:
            return 1
        elif tracknumber1 == tracknumber2:
            return 0
        else:
            return -1
    def __timeConvert(self, time):
        addZero = lambda x : x < 10 and u"0" + unicode(x) or unicode(x)
        time /= 1000
        return addZero(time / 3600 % 60) + u":" + addZero(time / 60 % 60)\
                + u":" + addZero(time % 60)
    def __resetCurrent(self):
        item = self.playlist.previouslyActiveItem
        if item and item != -1:
            item.setData(670, None)
            item.setData(671, None)
            item.setData(672, False)
