# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2011 - 2012
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

from PyQt4 import QtGui, QtDBus
from PyQt4.QtCore import QSettings, QObject, QStringList
from PyQt4.QtCore import Q_CLASSINFO, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt4.phonon import Phonon


class MPRIS2Helper(object):
    def __init__(self):
        self.signal = QtDBus.QDBusMessage.createSignal(
            "/org/mpris/MediaPlayer2",
            "org.freedesktop.DBus.Properties",
            "PropertiesChanged"
        )

    def PropertiesChanged(self, interface, property, values):
        """Sends PropertiesChanged signal through sessionBus.

        Args:
            interface: interface name
            property: property name
            values: actual property value(s)

        """
        self.signal.setArguments(
            [interface, {property: values}, QStringList()]
        )
        QtDBus.QDBusConnection.sessionBus().send(self.signal)


class MPRIS2Main(QtDBus.QDBusAbstractAdaptor):
    Q_CLASSINFO("D-Bus Interface", "org.mpris.MediaPlayer2")

    def __init__(self, parent, player):
        super(MPRIS2Main, self).__init__(parent)
        self.setAutoRelaySignals(True)
        self.player = player

    @pyqtProperty(str)
    def Identity(self):
        """Returns identity of the player.

        Returns:
            str -- identity.

        """
        return "gayeogi"

    @pyqtProperty(bool)
    def CanQuit(self):
        """Returns whether player can quit or not.

        Returns:
            bool -- can quit or not.

        """
        return False

    @pyqtProperty(bool)
    def CanRaise(self):
        """Returns whether player can be raised* or not.

        *It means the client can bring him "on top".

        Returns:
            bool -- can raise or not.

        """
        return False

    @pyqtProperty(bool)
    def HasTrackList(self):
        """Returns whether player has tracklist support or not.

        Returns:
            bool -- has tracklist or not.

        """
        return True

    @pyqtProperty(str)
    def DesktopEntry(self):
        """Returns desktop entry* of the player.

        *Which is a human-readable identity.

        Returns:
            str -- desktop entry.

        """
        return "gayeogi"

    @pyqtProperty(QStringList)
    def SupportedUriSchemes(self):
        """Returns array of a supported Uri schemes (nothing here).

        Returns:
            QStringList -- supported Uri schemes.

        """
        return QStringList()

    @pyqtProperty(QStringList)
    def SupportedMimeTypes(self):
        """Returns supported Mime types (nothing here).

        Returns:
            QStringList -- supported Mime types.

        """
        return QStringList()


class MPRIS2Player(QtDBus.QDBusAbstractAdaptor):
    Q_CLASSINFO("D-Bus Interface", "org.mpris.MediaPlayer2.Player")

    def __init__(self, parent, player):
        super(MPRIS2Player, self).__init__(parent)
        self.setAutoRelaySignals(True)
        self.player = player
        self.helper = MPRIS2Helper()
        self.player.mediaobject.stateChanged.connect(self._SetPlaybackStatus)
        self.player.audiooutput.volumeChanged.connect(self._emitVolume)
        self.player.trackChanged.connect(self._emitMetadata)
        self.player.seeked.connect(self.__emitSeeked)

    @pyqtSlot()
    def Next(self):
        """Causes the player to skip to the next track."""
        self.player.next_()

    @pyqtSlot()
    def Previous(self):
        """Causes the player to skip to the previous track."""
        self.player.previous()

    @pyqtSlot()
    def Pause(self):
        """Pauses the player."""
        self.player.mediaobject.pause()

    @pyqtSlot()
    def Stop(self):
        """Stops the player."""
        self.player.stop()

    @pyqtSlot()
    def Play(self):
        """Starts playing."""
        self.player.mediaobject.play()

    @pyqtSlot(str, "qlonglong")
    def SetPosition(self, id, position):
        """Sets current playback to the specified position.

        Also converts timings and checks for possible problems.

        Args:
            id: id of the track (to check whether it's really playing now
            position: position to seek at

        """
        if(id == self.player.playlist.activeRow and
           position >= 0 and
           position <= self.player.mediaobject.totalTime()
        ):
            self.player.mediaobject.seek(position / 1000)

    def _emitMetadata(self, artist, title, album, tracknumber):
        """Emits new metadata on track changes.

        Args:
            artist: artist name
            title: track title
            album: album name
            tracknumber: track number

        """
        metadata = {
            'mpris:trackid': QtDBus.QDBusObjectPath(
                '/gayeogi/' + str(self.player.playlist.activeRow)
            ),
            'xesam:trackNumber': tracknumber,
            'xesam:title': unicode(title),
            'xesam:album': unicode(album),
            'xesam:artist': QStringList(unicode(artist))
        }
        self.helper.PropertiesChanged(
            "org.mpris.MediaPlayer2.Player", "Metadata", metadata
        )

    @pyqtProperty("QMap<QString, QVariant>")
    def Metadata(self):
        """Returns current track's metadata.

        See http://xmms2.org/wiki/MPRIS_Metadata#MPRIS_v2.0_metadata_guidelines
        for more information about returned object.
        """
        metadata = dict()
        try:
            activeItem = self.player.playlist.activeItem
        except AttributeError:
            activeItem = None
        if not activeItem:
            metadata["mpris:trackid"] = QtDBus.QDBusObjectPath(
                '/gayeogi/notrack'
            )
            return metadata
        metadata["mpris:trackid"] = QtDBus.QDBusObjectPath(
            '/gayeogi/' + str(self.player.playlist.activeRow)
        )
        metadata.update(self.player.playlist[self.player.playlist.activeRow])
        return metadata

    def _emitVolume(self, volume):
        """Emits new volume value when it gets changed

        Args:
            volume: a number from 0.0 (mute) to 1.0 (100%)

        """
        self.helper.PropertiesChanged(
            "org.mpris.MediaPlayer2.Player", "Volume", volume
        )

    @pyqtProperty(float)
    def Volume(self):
        """Gets current player's volume value.

        It is a number from 0.0 (mute) to 1.0 (100%).

        """
        return self.player.audiooutput.volume()

    @Volume.setter
    def Volume(self, volume):
        """Sets player volume to the specified value.

        Args:
            volume: a number from 0.0 (mute) to 1.0 (100%)

        """
        self.player.audiooutput.setVolume(volume)
        self._emitVolume(volume)

    @pyqtProperty("qlonglong")
    def Position(self):
        """Returns current position in the playing track.

        Returns:
            int -- current track's position in microseconds.

        """
        return self.player.mediaobject.currentTime() * 1000

    @pyqtSlot()
    def PlayPause(self):
        """Pauses the player if it's playing or starts playing if it's not."""
        self.player.playByButton()

    @pyqtSlot("qlonglong")
    def Seek(self, offset):
        """Seeks currently playing track to the specified position.

        Args:
            offset: position to which to seek

        """
        position = self.player.mediaobject.currentTime() * 1000 + offset
        self.SetPosition(self.player.playlist.activeRow, position)

    @pyqtSlot(str)
    def OpenUri(self, uri):
        """Opens specified Uri in the player.

        Does nothing, as there's no such support in the player right now.

        Args:
            uri: Uri pointing at a track to play

        """
        pass

    def __emitSeeked(self, position):
        """Emits new position when the current track was seeked.

        A proxy method to convert from miliseconds to microseconds.

        Args:
            position: new track's position (in miliseconds)

        """
        self.Seeked.emit(position * 1000)

    Seeked = pyqtSignal(int)
    """Emits new position when the current track was seeked.

    Args:
        position: new track's position

    """

    __playbackStates = {
        Phonon.LoadingState: "Playing",
        Phonon.StoppedState: "Stopped",
        Phonon.PlayingState: "Playing",
        Phonon.BufferingState: "Playing",
        Phonon.PausedState: "Paused",
        Phonon.ErrorState: "Stopped"
    }
    __playbackStatus = "Stopped"

    def _SetPlaybackStatus(self, state):
        """Changes current playback status according to changes in the player.

        Args:
            state (int): One of possible Phonon playback states

        """
        self.__playbackStatus = self.__playbackStates[state]
        self.helper.PropertiesChanged(
            "org.mpris.MediaPlayer2.Player",
            "PlaybackStatus", self.__playbackStatus
        )

    @pyqtProperty(str)
    def PlaybackStatus(self):
        """Returns current playback status.

        Should be 'Playing', 'Paused' or 'Stopped'.
        Set internally with _SetPlaybackStatus method.

        Note: It might not be accurate as Phonon supports more states than
        MPRIS standard.

        """
        return self.__playbackStatus

    @pyqtProperty(str)
    def LoopStatus(self):
        """Returns current loop status.

        Should be 'None', 'Track' or 'Playlist', but returns 'None'
        for now, because there's no loop support in the player.

        """
        return "None"  # that's temporary

    @LoopStatus.setter
    def LoopStatus(self, loops):
        """Sets looping type.

        Does nothing for now as there's no loop support in the player.

        """
        pass

    @pyqtProperty(float)
    def Rate(self):
        """Returns current playback rate.

        Always returns 1.0 as our player has no ability to change it.

        """
        return 1.0

    @Rate.setter
    def Rate(self, rate):
        """Sets playback rate.

        Does nothing, because rate cannot be changed in the player.

        """
        pass

    @pyqtProperty(bool)
    def Shuffle(self):
        """Returns if player is currently shuffling or not.

        Returns False for now as there's no shuffle support in the player.

        """
        return False

    @Shuffle.setter
    def Shuffle(self, shuffle):
        """Enables/disables shuffle.

        Does nothing for now as there's not shuffle support in the player.

        """
        pass

    @pyqtProperty(float)
    def MinimumRate(self):
        """Returns the lowest possible playback rate.

        It's always 1.0 (see Rate).

        """
        return 1.0

    @pyqtProperty(float)
    def MaximumRate(self):
        """Returns the highest possible playback rate.

        It's always 1.0 (see Rate).

        """
        return 1.0

    @pyqtProperty(bool)
    def CanGoNext(self):
        """Returns whether player can skip to the next track or not.

        Returns:
            bool -- can skip or not.

        """
        return True

    @pyqtProperty(bool)
    def CanGoPrevious(self):
        """Returns whether player can skip to the previous track or not.

        Returns:
            bool -- can skip or not.

        """
        return True

    @pyqtProperty(bool)
    def CanPlay(self):
        """Returns whether player can start playing or not.

        Returns:
            bool -- can start or not.

        """
        return True

    @pyqtProperty(bool)
    def CanPause(self):
        """Returns whether player can be paused or not.

        Returns:
            bool -- can pause or not.

        """
        return True

    @pyqtProperty(bool)
    def CanSeek(self):
        """Returns whether currently playing track can be seeked or not.

        Returns:
            bool - can seek or not.

        """
        return True

    @pyqtProperty(bool)
    def CanControl(self):
        """Returns whether player can be controlled by MPRIS or not.

        Returns:
            bool -- can be controlled or not.

        """
        return True


class MPRIS2Tracklist(QtDBus.QDBusAbstractAdaptor):
    Q_CLASSINFO("D-Bus Interface", "org.mpris.MediaPlayer2.TrackList")

    def __init__(self, parent, player):
        super(MPRIS2Tracklist, self).__init__(parent)
        self.setAutoRelaySignals(True)
        self.player = player

    #@pyqtSlot(QStringList, result="QList<QVariantMap>")
    # it doesn't want do work with the definition above :(
    #def GetTracksMetadata(self, ids):
        #"""Returns a list of metadata for all specified ids in order.

        #Args:
            #ids: an array of track ids (in a form of '/gayeogi/<number>')

        #Returns:
            #list -- a list of metadata dictionaries.

        #"""
        #pass

    @pyqtSlot(str, QtDBus.QDBusObjectPath, bool)
    def AddTrack(self, uri, aftertrack, setascurrent):
        """Adds specified track to the playlist after the given position
        and optionally sets it as current track.

        Does nothing now, as we do not support adding tracks by Uri.
        """
        pass

    def __getId(self, id):
        """Converts mpris-compliant id to number in the playlist.

        Args:
            id: mpris-compliant item id (looks like '/gayeogi/<number>')

        Returns:
            int -- number in the playlist corresponding the supplied id.
        """
        try:
            return int(id[9:])
        except ValueError:
            return None

    @pyqtSlot(QtDBus.QDBusObjectPath)
    def RemoveTrack(self, id):
        """Removes track with specified id from the playlist.

        Args:
            id: An id unique in the context (which is the playlist,
            looks like '/gayeogi/<number>')

        """
        self.player.playlist.remove(self.__getId(id))

    @pyqtSlot(QtDBus.QDBusObjectPath)
    def GoTo(self, id):
        """Skips to the track with specified id.

        Args:
            id: An id unique in the context (which is the playlist,
            looks liks '/gayeogi/<number>')

        """
        self.player.goTo(self.__getId(id))

    TrackListReplaced = pyqtSignal(QStringList, QtDBus.QDBusObjectPath)
    """Emits new contents of the playlist.

    Used only to indicate the change of the WHOLE playlist.
    So: never here now.

    Args:
        tracks: array of new tracks in the playlist
        current: new current track id

    """

    TrackAdded = pyqtSignal("QMap<QString, QVariant>", QtDBus.QDBusObjectPath)
    """Emits newly added track metadata and position.

    NotImplemented

    Args:
        metadata: new track metadata
        after: after which track the new one got added

    """

    TrackRemoved = pyqtSignal(QtDBus.QDBusObjectPath)
    """Emits id of the track when it gets removed.

    NotImplemented

    Args:
        id: id of the removed track

    """

    TrackMetadataChanged = pyqtSignal(QtDBus.QDBusObjectPath, "QVariantMap")
    """Emits new metadata for the track when it gets changed.

    NotImplemented

    Args:
        id: id of the changed track
        metadata: new metadata

    """

    @pyqtProperty(QStringList)
    def Tracks(self):
        """Returns list of identifiers for all items in the playlist in order.

        Returns:
            list -- list of unique identifiers in form of '/gayeogi/<number>'.

        """
        return ['/gayeogi/' + str(i) for i in self.player.playlist.count()]

    @pyqtProperty(bool)
    def CanEditTracks(self):
        """Returns whether tracks in the playlist can be edited.

        Note: It doesn't mean that all editing methods are always available.

        """
        return True


class MPRIS2(QObject):
    def __init__(self, player):
        super(MPRIS2, self).__init__()
        MPRIS2Main(self, player)
        MPRIS2Player(self, player)
        MPRIS2Tracklist(self, player)
        self.conn = QtDBus.QDBusConnection.sessionBus()
        self.conn.registerObject("/org/mpris/MediaPlayer2", self)
        self.conn.registerService("org.mpris.MediaPlayer2.gayeogi")

    def destroy(self):
        self.conn.unregisterObject("/org/mpris/MediaPlayer2")
        self.conn.unregisterService("org.mpris.MediaPlayer2.gayeogi")


class Main(object):
    name = u'MPRIS'
    loaded = False
    depends = [u'player']
    __settings = QSettings(u'gayeogi', u'MPRIS')

    def __init__(self, parent, ___, _, __):
        """Constructs new Main instance.

        Args:
            parent: parent widget
            ___: whatever
            _: whatever
            __: whatever

        """
        self.player = parent.plugins[u'player']

    def load(self):
        """Loads the plugin in."""
        self.__21 = MPRIS2(self.player)
        Main.loaded = True

    def unload(self):
        """Unloads the plugin."""
        self.__21.destroy()
        Main.loaded = False

    @staticmethod
    def QConfiguration():
        """Creates configuration widget.

        Returns:
            QWidget -- config widget used in settings dialog.

        """
        widget = QtGui.QWidget()
        widget.enabled = Main.__settings.value(u'enabled', 0).toInt()[0]
        widget.setSetting = lambda x, y: Main.__settings.setValue(x, y)
        return widget
