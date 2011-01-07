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

from PyQt4.phonon import Phonon
from PyQt4 import QtGui
from PyQt4.QtCore import QSize, Qt
from copy import deepcopy

class PlayListItemDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        start = deepcopy(option.rect)
        size = option.font.pointSize()
        painter.save()
        font = option.font
        if index.data(672).toBool():
            font.setBold(True)
            painter.setFont(font)
        start.setLeft(start.left() + 5)
        start.setTop(start.top() + 20)
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        painter.drawText(start, Qt.AlignLeft, index.data(668).toString() + u' (' +
                index.data(669).toString() + u')')
        start.setY(start.y() - (size + 6))
        painter.drawText(start, Qt.AlignLeft, index.data(666).toString() + u'. ' +
                index.data(667).toString())
        start = deepcopy(option.rect)
        start.setRight(start.right() - 5)
        font.setPointSize(16)
        painter.setFont(font)
        data670 = index.data(670).toString()
        if data670 != u'':
            painter.drawText(start, Qt.AlignRight | Qt.AlignVCenter,
                    index.data(670).toString() + u'/' + index.data(671).toString())
        font.setPointSize(10)
        font.setBold(False)
        painter.restore()
    def sizeHint(self, option, index):
        return QSize(0, 18 + option.font.pointSize() * 2)

class Main(QtGui.QWidget):
    loaded = False
    __current = None
    def __init__(self, parent, library):
        QtGui.QWidget.__init__(self, None)
        self.parent = parent
        self.library = library
    def load(self):
        add = QtGui.QPushButton(u'Add')
        add.clicked.connect(self.addByButton)
        remove = QtGui.QPushButton(u'Remove')
        remove.clicked.connect(self.removeByButton)
        pIcon = self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward)
        previous = QtGui.QPushButton(pIcon, u'')
        previous.clicked.connect(self.previous)
        playIcon = self.style().standardIcon(QtGui.QStyle.SP_MediaPlay)
        self.playButton = QtGui.QPushButton(playIcon, u'')
        self.playButton.clicked.connect(self.playByButton)
        self.playButton.playing = False
        stopIcon = self.style().standardIcon(QtGui.QStyle.SP_MediaStop)
        stop = QtGui.QPushButton(stopIcon, u'')
        stop.clicked.connect(self.stop)
        nextIcon = self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward)
        next_ = QtGui.QPushButton(nextIcon, u'')
        next_.clicked.connect(self.next_)
        volume = Phonon.VolumeSlider()
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
        buttons.setLayout(buttonsLayout)
        delegate = PlayListItemDelegate()
        self.playlist = QtGui.QListWidget()
        self.playlist.setItemDelegate(delegate)
        self.playlist.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self.playlist.itemActivated.connect(self.play)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(progress)
        layout.addWidget(self.playlist)
        self.setLayout(layout)
        self.parent.artists.itemActivated.connect(self.addItem)
        self.parent.albums.itemActivated.connect(self.addItem)
        self.parent.tracks.itemActivated.connect(self.addItem)
        self.parent.horizontalLayout_2.addWidget(self)
        self.mediaobject = Phonon.MediaObject()
        self.mediaobject.setTickInterval(500)
        self.mediaobject.tick.connect(self.tick)
        self.mediaobject.totalTimeChanged.connect(self.setTime)
        self.mediaobject.finished.connect(self.nextTrack)
        self.audiooutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        Phonon.createPath(self.mediaobject, self.audiooutput)
        progress.setMediaObject(self.mediaobject)
        volume.setAudioOutput(self.audiooutput)
        Main.loaded = True
    def unload(self):
        children = self.parent.horizontalLayout_2.parentWidget().children()
        for i, child in enumerate(children):
            if isinstance(child, Main):
                item = self.parent.horizontalLayout_2.takeAt(i - 1)
                item.widget().deleteLater()
        Main.loaded = False
    def QConfiguration():
        pass
    QConfiguration = staticmethod(QConfiguration)
    def play(self, item):
        self.__resetCurrent()
        self.mediaobject.setCurrentSource(Phonon.MediaSource(item.path))
        self.mediaobject.play()
        self.__current = item
        self.__current.setData(672, True)
        icon = self.style().standardIcon(QtGui.QStyle.SP_MediaPause)
        self.playButton.setIcon(icon)
        self.playButton.playing = True
    def stop(self):
        self.__resetCurrent()
        self.__current = None
        self.mediaobject.stop()
    def previous(self):
        index = self.playlist.row(self.__current)
        if self.__current and index:
            self.play(self.playlist.item(index - 1))
    def next_(self):
        index = self.playlist.row(self.__current) + 1
        if self.__current and index < self.playlist.count():
            self.play(self.playlist.item(index))
    def tick(self, interval):
        if interval:
            self.__current.setData(670, self.__timeConvert(interval))
    def nextTrack(self):
        index = self.playlist.row(self.__current)
        self.playlist.itemActivated.emit(self.playlist.item(index + 1))
    def setTime(self, time):
        if self.__current:
            self.__current.setData(671, self.__timeConvert(time))
    def playByButton(self):
        button = self.sender()
        if not button.playing:
            if not self.__current:
                self.play(self.playlist.item(0))
            else:
                icon = self.style().standardIcon(QtGui.QStyle.SP_MediaPause)
                button.setIcon(icon)
                button.playing = True
                self.mediaobject.play()
        else:
            icon = self.style().standardIcon(QtGui.QStyle.SP_MediaPlay)
            button.setIcon(icon)
            button.playing = False
            self.mediaobject.pause()
    def addByButton(self):
        def addItems(items):
            if items:
                for item in items:
                    self.addItem(item, -1)
                return True
            return False
        if not addItems(self.parent.tracks.selectedItems()):
            if not addItems(self.parent.albums.selectedItems()):
                addItems(self.parent.artists.selectedItems())
    def removeByButton(self):
        for item in self.playlist.selectedItems():
            self.playlist.takeItem(self.playlist.row(item))
    def addItem(self, item, column):
        if column != 3:
            if column != -1:
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
                        album = unicode(item_.text(1))
                        items_ = [self.__createItem((vv[u'tracknumber'], title,
                            album, item.text(0), vv[u'path'])) for title, vv
                            in self.library[item_.artist][u'albums']\
                                    [album][u'tracks'].iteritems()]
                        items_.sort(self.__compare)
                        items.extend(items_)
                    for i in items:
                        self.playlist.addItem(i)
                else:
                    for i in range(self.parent.tracks.topLevelItemCount()):
                        item_ = self.parent.tracks.topLevelItem(i)
                        path = self.library[item_.artist][u'albums'][item_.album]\
                                [u'tracks'][unicode(item_.text(1))][u'path']
                        self.playlist.addItem(self.__createItem((item_.text(0),
                            item_.text(1), item_.album, item_.artist, path)))
            else:
                path = self.library[item.artist][u'albums'][item.album]\
                        [u'tracks'][unicode(item.text(1))][u'path']
                self.playlist.addItem(self.__createItem(
                    (item.text(0), item.text(1), item.album, item.artist, path)))
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
        if self.__current:
            self.__current.setData(670, None)
            self.__current.setData(671, None)
            self.__current.setData(672, False)
            self.mediaobject.clear()
