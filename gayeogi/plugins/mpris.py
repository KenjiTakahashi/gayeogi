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

import dbus
import dbus.service
from dbus.mainloop.qt import DBusQtMainLoop
from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, Qt
from PyQt4.phonon import Phonon


class MPRIS1Main(dbus.service.Object):
    __path = '/'
    __busname = 'org.mpris.gayeogi'
    __interface = 'org.freedesktop.MediaPlayer'

    def __init__(self):
        bus = dbus.SessionBus()
        name = dbus.service.BusName(self.__busname, bus)
        super(type(self), self).__init__(name, self.__path)

    @dbus.service.method(dbus_interface=__interface, out_signature="s")
    def Identity(self):
        return "gayeogi"

    @dbus.service.method(dbus_interface=__interface)
    def Quit(self):
        pass

    @dbus.service.method(dbus_interface=__interface, out_signature="(qq)")
    def MprisVersion(self):
        return (1, 0)


class MPRIS1Tracklist(dbus.service.Object):
    __path = '/Tracklist'
    __busname = 'org.mpris.gayeogi'
    __interface = 'org.freedesktop.MediaPlayer'

    def __init__(self):
        bus = dbus.SessionBus()
        name = dbus.sevice.BusName(self.__busname, bus)
        super(type(self), self).__init__(name, self.__path)

    @dbus.service.method(dbus_interface=__interface,
        in_signature="i", out_signature="a{sv}")
    def GetMetadata(self, index):
        pass

    @dbus.service.method(dbus_interface=__interface, out_signature="i")
    def GetCurrentTrack(self):
        pass

    @dbus.service.method(dbus_interface=__interface, out_signature="i")
    def GetLength(self):
        pass

    @dbus.service.method(dbus_interface=__interface,
        in_signature="sb", out_signature="i")
    def AddTrack(self, uri, play):
        pass

    @dbus.service.method(dbus_interface=__interface, in_signature="i")
    def DelTrack(self, index):
        pass

    @dbus.service.method(dbus_interface=__interface, in_signature="b")
    def SetLoop(self, loop):
        pass

    @dbus.service.method(dbus_interface=__interface, in_signature="b")
    def SetRandom(self, random):
        pass

    @dbus.service.signal(dbus_interface=__interface, signature="i")
    def TrackListChange(self, i):
        pass


class MPRIS1Player(dbus.service.Object):
    __path = '/Player'
    __busname = 'org.mpris.gayeogi'
    __interface = 'org.freedesktop.MediaPlayer'

    def __init__(self):
        bus = dbus.SessionBus()
        name = dbus.service.BusName(self.__busname, bus)
        super(type(self), self).__init__(name, self.__path)

    @dbus.service.method(dbus_interface=__interface)
    def Next(self):
        pass

    @dbus.service.method(dbus_interface=__interface)
    def Prev(self):
        pass

    @dbus.service.method(dbus_interface=__interface)
    def Pause(self):
        pass

    @dbus.service.method(dbus_interface=__interface)
    def Stop(self):
        pass

    @dbus.service.method(dbus_interface=__interface)
    def Play(self):
        pass

    @dbus.service.method(dbus_interface=__interface, in_signature="b")
    def Repeat(self, repeat):
        pass

    @dbus.service.method(dbus_interface=__interface, out_signature="(iiii)")
    def GetStatus(self):
        return (0, 0, 0, 0)

    @dbus.service.method(dbus_interface=__interface, out_signature="a{sv}")
    def GetMetadata(self):
        metadata = dbus.Dictionary(signature="sv")
        metadata["artist"] = "Tst"
        metadata["title"] = "LOL"
        return metadata

    @dbus.service.method(dbus_interface=__interface, out_signature="i")
    def GetCaps(self):
        pass

    @dbus.service.method(dbus_interface=__interface, in_signature="i")
    def VolumeSet(self, volume):
        pass

    @dbus.service.method(dbus_interface=__interface, out_signature="i")
    def VolumeGet(self):
        pass

    @dbus.service.method(dbus_interface=__interface, in_signature="i")
    def PositionSet(self, position):
        pass

    @dbus.service.method(dbus_interface=__interface, out_signature="i")
    def PositionGet(self):
        pass

    @dbus.service.signal(__interface, signature="a{sv}")
    def TrackChange(self, metadata):
        pass

    @dbus.service.signal(__interface, signature="(iiii)")
    def StatusChange(self, iiii):
        return (0, 0, 0, 0)

    @dbus.service.signal(__interface, signature="i")
    def CapsChange(self, i):
        pass


class MPRIS2Main(dbus.service.Object):
    __path = '/org/mpris/MediaPlayer2'
    __busname = 'org.mpris.MediaPlayer2.gayeogi'
    __propint = 'org.freedesktop.DBus.Properties'
    __root = 'org.mpris.MediaPlayer2'
    __player = 'org.mpris.MediaPlayer2.Player'
    __tracklist = 'org.mpris.MediaPlayer2.TrackList'

    def __init__(self, player):
        """Constructs new MPRIS2Main instance.

        Initializes all needed fields and mappings and a D-Bus session bus.

        Args:
            player: reference to the player instance

        """
        bus = dbus.SessionBus()
        name = dbus.service.BusName(self.__busname, bus)
        self.__mapping = {
            self.__root: [
                "CanQuit",
                "CanRaise",
                "HasTrackList",
                "Identity",
                "DesktopEntry",
                "SupportedUriSchemes",
                "SupportedMimeTypes"
            ],
            self.__player: [
                "PlaybackStatus",
                "LoopStatus",
                "Rate",
                "Shuffle",
                "Metadata",
                "Volume",
                "Position",
                "MinimumRate",
                "MaximumRate",
                "CanGoNext",
                "CanGoPrevious",
                "CanPlay",
                "CanPause",
                "CanSeek",
                "CanControl"
            ],
            self.__tracklist: [
                "Tracks",
                "CanEditTracks"
            ]
        }
        self.player = player
        super(type(self), self).__init__(name, self.__path)
        self.player.mediaobject.stateChanged.connect(self.__SetPlaybackStatus)
        self.player.audiooutput.volumeChanged.connect(self.__emitVolume)
        self.player.trackChanged.connect(self.__emitMetadata)
        self.player.seeked.connect(self.__emitSeeked)

    @dbus.service.method(__root, out_signature="b")
    def CanQuit(self):
        """Returns whether player can quit or not.

        Returns:
            bool -- can quit or not.

        """
        return False

    @dbus.service.method(__root, out_signature="b")
    def CanRaise(self):
        """Returns whether player can be raised* or not.

        *It means the client can bring him "on top".

        Returns:
            bool -- can raise or not.

        """
        return False

    @dbus.service.method(__root, out_signature="b")
    def HasTrackList(self):
        """Returns whether player has tracklist support or not.

        Returns:
            bool -- has tracklist or not.

        """
        return True

    @dbus.service.method(__root, out_signature="s")
    def Identity(self):
        """Returns identity of the player.

        Returns:
            str -- identity.

        """
        return "gayeogi"

    @dbus.service.method(__root, out_signature="s")
    def DesktopEntry(self):
        """Returns desktop entry* of the player.

        *Which is a human-readable identity.

        Returns:
            str -- desktop entry.

        """
        return "gayeogi"

    @dbus.service.method(__root, out_signature="as")
    def SupportedUriSchemes(self):
        """Returns array of a supported Uri schemes (nothing here).

        Returns:
            dbus.Array -- supported Uri schemes.

        """
        return dbus.Array(signature="s")

    @dbus.service.method(__root, out_signature="as")
    def SupportedMimeTypes(self):
        """Returns supported Mime types (nothing here).

        Returns:
            dbus.Array -- supported Mime types.

        """
        return dbus.Array(signature="s")

    @dbus.service.method(__player)
    def Next(self):
        """Causes the player to skip to the next track."""
        self.player.next_()

    @dbus.service.method(__player)
    def Previous(self):
        """Causes the player to skip to the previous track."""
        self.player.previous()

    @dbus.service.method(__player)
    def Pause(self):
        """Pauses the player."""
        self.player.mediaobject.pause()

    @dbus.service.method(__player)
    def PlayPause(self):
        """Pauses the player if it's playing or starts playing when it's not."""
        self.player.playByButton()

    @dbus.service.method(__player)
    def Stop(self):
        """Stops the player."""
        self.player.stop()

    @dbus.service.method(__player)
    def Play(self):
        """Starts playing."""
        self.player.mediaobject.play()

    @dbus.service.method(__player, in_signature="x")
    def Seek(self, offset):
        """Seeks currently playing track to the specified position.

        Args:
            offset: position to which to seek

        """
        position = self.player.mediaobject.currentTime() * 1000 + offset
        self.SetPosition(self.player.playlist.activeRow, position)

    @dbus.service.method(__player, in_signature="ox")
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

    @dbus.service.method(__player, in_signature="s")
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
        self.Seeked(position * 1000)

    @dbus.service.signal(__player, signature="x")
    def Seeked(self, position):
        """Emits new position when the current track was seeked.

        Args:
            position: new track's position

        """
        pass

    __playbackStates = {
        Phonon.LoadingState: "Playing",
        Phonon.StoppedState: "Stopped",
        Phonon.PlayingState: "Playing",
        Phonon.BufferingState: "Playing",
        Phonon.PausedState: "Paused",
        Phonon.ErrorState: "Stopped"
    }
    __playbackStatus = "Stopped"

    def __SetPlaybackStatus(self, state):
        """Changes current playback status according to changes in the player.

        Args:
            state (int): One of possible Phonon playback states

        """
        self.__playbackStatus = self.__playbackStates[state]
        self.PropertiesChanged(
            self.__player,
            {"PlaybackStatus": self.__playbackStatus},
            []
        )

    @dbus.service.method(__player, out_signature="s")
    def PlaybackStatus(self):
        """Returns current playback status.

        Should be 'Playing', 'Paused' or 'Stopped'.
        Set internally with __SetPlaybackStatus method.

        Note: It might not be accurate as Phonon supports more states than
        MPRIS standard.

        """
        return self.__playbackStatus

    @dbus.service.method(__player, out_signature="s")
    def LoopStatus(self):
        """Returns current loop status.

        Should be 'None', 'Track' or 'Playlist', but returns 'None'
        for now, because there's no loop support in the player.

        """
        return "None"  # that's temporary

    @dbus.service.method(__player, in_signature="s")
    def SetLoopStatus(self, loops):
        """Sets looping type.

        Does nothing for now as there's no loop support in the player.

        """
        pass

    @dbus.service.method(__player, out_signature="d")
    def Rate(self):
        """Returns current playback rate.

        Always returns 1.0 as our player has no ability to change it.

        """
        return 1.0

    @dbus.service.method(__player, in_signature="d")
    def SetRate(self, rate):
        """Sets playback rate.

        Does nothing, because rate cannot be changed in the player.

        """
        pass

    @dbus.service.method(__player, out_signature="b")
    def Shuffle(self):
        """Returns if player is currently shuffling or not.

        Returns False for now as there's no shuffle support in the player.

        """
        return False

    @dbus.service.method(__player, in_signature="b")
    def SetShuffle(self, shuffle):
        """Enables/disables shuffle.

        Does nothing for now as there's not shuffle support in the player.

        """
        pass

    def __emitMetadata(self, artist, title, album, tracknumber):
        """Emits new metadata on track changes.

        Args:
            artist: artist name
            title: track title
            album: album name
            tracknumber: track number

        """
        metadata = dbus.Dictionary(signature="sv")
        metadata.update({
            'mpris:trackid': dbus.ObjectPath(
                '/gayeogi/' + str(self.player.playlist.activeRow)
            ),
            'xesam:trackNumber': tracknumber,
            'xesam:title': unicode(title),
            'xesam:album': unicode(album),
            'xesam:artist': [unicode(artist)]
        })
        self.PropertiesChanged(self.__player, {"Metadata": metadata}, [])

    @dbus.service.method(__player, out_signature="a{sv}")
    def Metadata(self):
        """Returns current track's metadata.

        See http://xmms2.org/wiki/MPRIS_Metadata#MPRIS_v2.0_metadata_guidelines
        for more information about returned object.
        """
        metadata = dbus.Dictionary(signature="sv")
        try:
            activeItem = self.player.playlist.activeItem
        except AttributeError:
            activeItem = None
        if not activeItem:
            metadata["mpris:trackid"] = dbus.ObjectPath(self.__path)
            return metadata
        metadata["mpris:trackid"] = dbus.ObjectPath(
            '/gayeogi/' + str(self.player.playlist.activeRow)
        )
        metadata.update(self.player.playlist[self.player.playlist.activeRow])
        return metadata

    def __emitVolume(self, volume):
        """Emits new volume value when it gets changed

        Args:
            volume: a number from 0.0 (mute) to 1.0 (100%)

        """
        self.PropertiesChanged(self.__player, {"Volume": volume}, [])

    @dbus.service.method(__player, out_signature="d")
    def Volume(self):
        """Gets current player's volume value.

        It is a number from 0.0 (mute) to 1.0 (100%).

        """
        return self.player.audiooutput.volume()

    @dbus.service.method(__player, in_signature="d")
    def SetVolume(self, volume):
        """Sets player volume to the specified value.

        Args:
            volume: a number from 0.0 (mute) to 1.0 (100%)

        """
        self.player.audiooutput.setVolume(volume)
        self.__emitVolume(volume)

    @dbus.service.method(__player, out_signature="x")
    def Position(self):
        """Returns current position in the playing track.

        Returns:
            int -- current track's position in microseconds.

        """
        return self.player.mediaobject.currentTime() * 1000

    @dbus.service.method(__player, out_signature="d")
    def MinimumRate(self):
        """Returns the lowest possible playback rate.

        It's always 1.0 (see Rate).

        """
        return 1.0

    @dbus.service.method(__player, out_signature="d")
    def MaximumRate(self):
        """Returns the highest possible playback rate.

        It's always 1.0 (see Rate).

        """
        return 1.0

    @dbus.service.method(__player, out_signature="b")
    def CanGoNext(self):
        """Returns whether player can skip to the next track or not.

        Returns:
            bool -- can skip or not.

        """
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanGoPrevious(self):
        """Returns whether player can skip to the previous track or not.

        Returns:
            bool -- can skip or not.

        """
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanPlay(self):
        """Returns whether player can start playing or not.

        Returns:
            bool -- can start or not.

        """
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanPause(self):
        """Returns whether player can be paused or not.

        Returns:
            bool -- can pause or not.

        """
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanSeek(self):
        """Returns whether currently playing track can be seeked or not.

        Returns:
            bool - can seek or not.

        """
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanControl(self):
        """Returns whether player can be controlled by MPRIS or not.

        Returns:
            bool -- can be controlled or not.

        """
        return True

    @dbus.service.method(__tracklist, in_signature="ao",
        out_signature="aa{sv}")
    def GetTracksMetadata(self, ids):
        """Returns a list of metadata for all specified ids in order.

        Args:
            ids: an array of track ids (in a form of '/gayeogi/<number>')

        Returns:
            list -- a list of metadata dictionaries.

        """
        return [
            m for i, m in enumerate(self.player.playlist)
            if '/gayeogi/' + str(i) in ids
        ]

    @dbus.service.method(__tracklist, in_signature="sob")
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

    @dbus.service.method(__tracklist, in_signature="o")
    def RemoveTrack(self, id):
        """Removes track with specified id from the playlist.

        Args:
            id: An id unique in the context (which is the playlist,
            looks like '/gayeogi/<number>')

        """
        self.player.playlist.remove(self.__getId(id))

    @dbus.service.method(__tracklist, in_signature="o")
    def GoTo(self, id):
        """Skips to the track with specified id.

        Args:
            id: An id unique in the context (which is the playlist,
            looks liks '/gayeogi/<number>')

        """
        self.player.goTo(self.__getId(id))

    @dbus.service.signal(__tracklist, signature="aoo")
    def TrackListReplaced(self, tracks, current):
        """Emits new contents of the playlist.

        Used only to indicate the change of the WHOLE playlist.
        So: never here now.

        Args:
            tracks: array of new tracks in the playlist
            current: new current track id

        """
        pass

    @dbus.service.signal(__tracklist, signature="a{sv}o")
    def TrackAdded(self, metadata, after):
        """Emits newly added track metadata and position.

        Args:
            metadata: new track metadata
            after: after which track the new one got added

        """
        pass

    @dbus.service.signal(__tracklist, signature="o")
    def TrackRemoved(self, id):
        """Emits id of the track when it gets removed.

        Args:
            id: id of the removed track

        """
        pass

    @dbus.service.signal(__tracklist, signature="oa{sv}")
    def TrackMetadataChanged(self, id, metadata):
        """Emits new metadata for the track when it gets changed.

        Args:
            id: id of the changed track
            metadata: new metadata

        """
        pass

    @dbus.service.method(__tracklist, out_signature="ao")
    def Tracks(self):
        """Returns a list of identifiers for all items in the playlist in order.

        Returns:
            list -- list of unique identifiers in a form of '/gayeogi/<number>'.

        """
        return ['/gayeogi/' + str(i) for i in self.player.playlist.count()]

    @dbus.service.method(__tracklist, out_signature="b")
    def CanEditTracks(self):
        """Returns whether tracks in the playlist can be edited.

        Note that it doesn't mean that all editing methods are always
        available.

        """
        return True

    @dbus.service.method(__propint, in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        """Gets value of the specified property from the specified interface.

        Args:
            interface: name of the interface to get property from
            prop: name of the property to get value of

        Returns:
            variant -- value of the given property.

        """
        return getattr(self, prop)()

    @dbus.service.method(__propint, in_signature="ssv")
    def Set(self, interface, prop, value):
        """Sets value of the specified property from the specified interface.

        Args:
            interface: name of the interface fo set property in
            prop: name of the property to set
            value: new value for the property

        """
        getattr(self, "Set" + prop)(value)

    @dbus.service.method(__propint, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        """Gets values of all possible porperties in the specified interface.

        Args:
            interface: name of the interface to get properties from

        """
        return {key: getattr(self, key)() for key in self.__mapping[interface]}

    @dbus.service.signal(__propint, signature="sa{sv}as")
    def PropertiesChanged(self, interface, chprops, invprops):
        """Emits changes in the properties.

        Args:
            interface: name of the interface in which there were changes
            chprops: dictionary of names:values of the changed properties
            invprops: old values (usually empty)

        """
        pass


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
        DBusQtMainLoop(set_as_default=True)
        if self.__settings.value(u'2.1').toBool():
            self.__21 = MPRIS2Main(self.player)
        if self.__settings.value(u'1.0').toBool():
            self.__10Main = MPRIS1Main()
            self.__10Player = MPRIS1Player()
            self.__10Tracklist = MPRIS1Tracklist()
        Main.loaded = True

    def unload(self):  # should we do sth more here?
        """Unloads the plugin."""
        Main.loaded = False

    @staticmethod
    def QConfiguration():
        """Creates configuration widget.

        Returns:
            QWidget -- config widget used in settings dialog.

        """
        types = QtGui.QListWidget()
        for type in [u'1.0', u'2.1']:
            item = QtGui.QListWidgetItem(type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Main.__settings.value(type, 0).toInt()[0])
            types.addItem(item)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(types)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        widget.enabled = Main.__settings.value('enabled', 0).toInt()[0]

        def save(x, y):
            Main.__settings.setValue(x, y)
            for i in range(types.count()):
                item = types.item(i)
                type = unicode(item.text())
                state = item.checkState()
                Main.__settings.setValue(type, state)
        widget.setSetting = lambda x, y: save(x, y)
        return widget
