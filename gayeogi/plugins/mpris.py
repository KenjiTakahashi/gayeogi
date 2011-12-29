# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2011
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

    @dbus.service.method(__root, out_signature="b")
    def CanQuit(self):
        return False

    @dbus.service.method(__root, out_signature="b")
    def CanRaise(self):
        return False

    @dbus.service.method(__root, out_signature="b")
    def HasTrackList(self):
        return True

    @dbus.service.method(__root, out_signature="s")
    def Identity(self):
        return "gayeogi"

    @dbus.service.method(__root, out_signature="s")
    def DesktopEntry(self):
        return "gayeogi"

    @dbus.service.method(__root, out_signature="as")
    def SupportedUriSchemes(self):
        return dbus.Array(signature="s")

    @dbus.service.method(__root, out_signature="as")
    def SupportedMimeTypes(self):
        return dbus.Array(signature="s")

    @dbus.service.method(__player)
    def Next(self):
        self.player.next_()

    @dbus.service.method(__player)
    def Previous(self):
        self.player.previous()

    @dbus.service.method(__player)
    def Pause(self):
        self.player.mediaobject.pause()

    @dbus.service.method(__player)
    def PlayPause(self):
        self.player.playByButton()

    @dbus.service.method(__player)
    def Stop(self):
        self.player.stop()

    @dbus.service.method(__player)
    def Play(self):
        self.player.mediaobject.play()

    @dbus.service.method(__player, in_signature="x")
    def Seek(self, offset):
        position = self.player.mediaobject.currentTime() * 1000 + offset
        self.SetPosition(self.player.playlist.activeRow, position)

    @dbus.service.method(__player, in_signature="ox")
    def SetPosition(self, id, position):
        if(id == self.player.playlist.activeRow and
           position >= 0 and
           position <= self.player.mediaobject.totalTime()
        ):
            self.player.mediaobject.seek(position / 1000)

    @dbus.service.method(__player, in_signature="s")
    def OpenUri(self, uri):
        pass

    @dbus.service.signal(__player, signature="x")
    def Seeked(self, position):
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
        """Changes current playback status as it changes in the player.

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

        Should be 'None', 'Track' or 'Playlist', but returns 'NotSupported'
        for now, because we have no loop support in the player.

        """
        return "NotSupported"  # that's temporary

    @dbus.service.method(__player, in_signature="s")
    def SetLoopStatus(self, loops):
        pass

    @dbus.service.method(__player, out_signature="d")
    def Rate(self):
        """Returns current playback rate.

        Always returns 1.0 as our player has no ability to change it.

        """
        return 1.0

    @dbus.service.method(__player, in_signature="d")
    def SetRate(self, rate):
        pass

    @dbus.service.method(__player, out_signature="b")
    def Shuffle(self):
        """Returns if player is currently shuffling or not.

        Returns False for now as we don't have shuffling support in the player.

        """
        return False

    @dbus.service.method(__player, in_signature="b")
    def SetShuffle(self, shuffle):
        pass

    @dbus.service.method(__player, out_signature="a{sv}")
    def Metadata(self):
        metadata = dbus.Dictionary(signature="sv")
        metadata["artist"] = "Test"
        metadata["title"] = "Lol"
        return metadata

    def __emitVolume(self, volume):
        self.PropertiesChanged(self.__player, {"Volume": volume}, [])

    @dbus.service.method(__player, out_signature="d")
    def Volume(self):
        return self.player.audiooutput.volume()

    @dbus.service.method(__player, in_signature="d")
    def SetVolume(self, volume):
        self.player.audiooutput.setVolume(volume)
        self.__emitVolume(volume)

    @dbus.service.method(__player, out_signature="x")
    def Position(self):
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
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanGoPrevious(self):
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanPlay(self):
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanPause(self):
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanSeek(self):
        return True

    @dbus.service.method(__player, out_signature="b")
    def CanControl(self):
        return True

    @dbus.service.method(__tracklist, in_signature="ao",
        out_signature="aa{sv}")
    def GetTracksMetadata(self, ids):
        pass

    @dbus.service.method(__tracklist, in_signature="sob")
    def AddTrack(self, uri, aftertrack, setascurrent):
        pass

    @dbus.service.method(__tracklist, in_signature="o")
    def RemoveTrack(self, id):
        pass

    @dbus.service.method(__tracklist, in_signature="o")
    def GoTo(self, id):
        pass

    @dbus.service.signal(__tracklist, signature="aoo")
    def TrackListReplaced(self, arg1, arg2):  # change names!
        pass

    @dbus.service.signal(__tracklist, signature="a{sv}o")
    def TrackAdded(self, arg1, arg2):
        pass

    @dbus.service.signal(__tracklist, signature="o")
    def TrackRemoved(self, arg1):
        pass

    @dbus.service.signal(__tracklist, signature="oa{sv}")
    def TrackMetadataChanged(self, arg1, arg2):
        pass

    @dbus.service.method(__tracklist, out_signature="ao")
    def Tracks(self, arg1):
        pass

    @dbus.service.method(__tracklist, out_signature="b")
    def CanEditTracks(self, arg1):
        pass

    @dbus.service.method(__propint, in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        return getattr(self, prop)()

    @dbus.service.method(__propint, in_signature="ssv")
    def Set(self, interface, prop, value):
        getattr(self, "Set" + prop)(value)

    @dbus.service.method(__propint, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        return {key: getattr(self, key)() for key in self.__mapping[interface]}

    @dbus.service.signal(__propint, signature="sa{sv}as")
    def PropertiesChanged(self, interface, chprops, invprops):
        pass


#from PyQt4 import QtGui
#import sys
#app = QtGui.QApplication(sys.argv)
#DBusQtMainLoop(set_as_default=True)
##s = MPRIS1Main()
##ss = MPRIS1Tracklist()
##sss = MPRIS1Player()
#s = MPRIS2Main()
#sys.exit(app.exec_())


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
