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
from PyQt4.QtCore import QSettings

class MPRIS1Main(dbus.service.Object):
    __path = '/'
    __busname = 'org.mpris.gayeogi'
    __interface = 'org.freedesktop.MediaPlayer'
    def __init__(self):
        bus = dbus.SessionBus()
        name = dbus.service.BusName(self.__busname, bus)
        super(MPRIS1Main, self).__init__(name, self.__path)
    @dbus.service.method(dbus_interface = __interface, out_signature = "s")
    def Identity(self):
        return "gayeogi"
    @dbus.service.method(dbus_interface = __interface)
    def Quit(self):
        pass
    @dbus.service.method(dbus_interface = __interface, out_signature = "(qq)")
    def MprisVersion(self):
        return (1, 0)

class MPRIS1Tracklist(dbus.service.Object):
    __path = '/Tracklist'
    __busname = 'org.mpris.gayeogi'
    __interface = 'org.freedesktop.MediaPlayer'
    def __init__(self):
        bus = dbus.SessionBus()
        name = dbus.sevice.BusName(self.__busname, bus)
        super(MPRIS1Tracklist, self).__init__(name, self.__path)
    @dbus.service.method(dbus_interface = __interface,
        in_signature = "i", out_signature = "a{sv}")
    def GetMetadata(self, index):
        pass
    @dbus.service.method(dbus_interface = __interface, out_signature = "i")
    def GetCurrentTrack(self):
        pass
    @dbus.service.method(dbus_interface = __interface, out_signature = "i")
    def GetLength(self):
        pass
    @dbus.service.method(dbus_interface = __interface,
        in_signature = "sb", out_signature = "i")
    def AddTrack(self, uri, play):
        pass
    @dbus.service.method(dbus_interface = __interface, in_signature = "i")
    def DelTrack(self, index):
        pass
    @dbus.service.method(dbus_interface = __interface, in_signature = "b")
    def SetLoop(self, loop):
        pass
    @dbus.service.method(dbus_interface = __interface, in_signature = "b")
    def SetRandom(self, random):
        pass
    @dbus.service.signal(dbus_interface = __interface, signature = "i")
    def TrackListChange(self, i):
        pass

class MPRIS1Player(dbus.service.Object):
    __path = '/Player'
    __busname = 'org.mpris.gayeogi'
    __interface = 'org.freedesktop.MediaPlayer'
    def __init__(self):
        bus = dbus.SessionBus()
        name = dbus.service.BusName(self.__busname, bus)
        super(MPRIS1Player, self).__init__(name, self.__path)
    @dbus.service.method(dbus_interface = __interface)
    def Next(self):
        pass
    @dbus.service.method(dbus_interface = __interface)
    def Prev(self):
        pass
    @dbus.service.method(dbus_interface = __interface)
    def Pause(self):
        pass
    @dbus.service.method(dbus_interface = __interface)
    def Stop(self):
        pass
    @dbus.service.method(dbus_interface = __interface)
    def Play(self):
        pass
    @dbus.service.method(dbus_interface = __interface, in_signature = "b")
    def Repeat(self, repeat):
        pass
    @dbus.service.method(dbus_interface = __interface, out_signature = "(iiii)")
    def GetStatus(self):
        return (0, 0, 0, 0)
    @dbus.service.method(dbus_interface = __interface, out_signature = "a{sv}")
    def GetMetadata(self):
        metadata = dbus.Dictionary(signature="sv")
        metadata["artist"] = "Tst"
        metadata["title"] = "LOL"
        return metadata
    @dbus.service.method(dbus_interface = __interface, out_signature = "i")
    def GetCaps(self):
        pass
    @dbus.service.method(dbus_interface = __interface, in_signature = "i")
    def VolumeSet(self, volume):
        pass
    @dbus.service.method(dbus_interface = __interface, out_signature = "i")
    def VolumeGet(self):
        pass
    @dbus.service.method(dbus_interface = __interface, in_signature = "i")
    def PositionSet(self, position):
        pass
    @dbus.service.method(dbus_interface = __interface, out_signature = "i")
    def PositionGet(self):
        pass
    @dbus.service.signal(__interface, signature = "a{sv}")
    def TrackChange(self, metadata):
        pass
    @dbus.service.signal(__interface, signature = "(iiii)")
    def StatusChange(self, iiii):
        return (0, 0, 0, 0)
    @dbus.service.signal(__interface, signature = "i")
    def CapsChange(self, i):
        pass

from PyQt4 import QtGui
import sys
app=QtGui.QApplication(sys.argv)
DBusQtMainLoop(set_as_default=True)
s=MPRIS1Main()
ss=MPRIS1Player()
sys.exit(app.exec_())

#DBusGMainLoop(set_as_default=True)
#s=MPRIS1Main()
#ss=MPRIS1Player()
#import gtk
#gtk.main()

class Main(object):
    name = u'MPRIS'
    loaded = False
    depends = [u'player'] # don't know if it will stay here
    __settings = QSettings(u'gayeogi', u'Mpris')
    def __init__(self, parent, ___, _, __):
        pass
