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

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, Qt
import pylast
from socket import gaierror, error
from threading import Thread
from time import time, sleep

class Main(object):
    name = u'Last.FM'
    loaded = False
    depends = [u'player']
    __key = u'a3f47739f0f87e24f499a7683cc0d1fd'
    __sec = u'1e4a65fba65e59cfb76adcc5af2fc3e3'
    __net = None
    __opt = {u'Last.FM': u'LastFMNetwork', u'Libre.FM': u'LibreFMNetwork'}
    __settings = QSettings(u'fetcher', u'Last.FM')
    __sem = True
    def __init__(self, parent, ___, _, __):
        username = unicode(Main.__settings.value(u'username', u'').toString())
        password = unicode(
                Main.__settings.value(u'password_hash', u'').toString())
        kind = unicode(Main.__settings.value(u'kind', u'Last.FM').toString())
        if username != u'' and password != u'':
            self.parent = parent
            def __connect():
                def __connect_():
                    try:
                        print "trying trying"
                        Main.__net = getattr(pylast, Main.__opt[kind])(
                                api_key = self.__key,
                                api_secret = self.__sec,
                                username = username,
                                password_hash = password
                                )
                        Main.__sem = False
                    except (pylast.WSError, gaierror, error):
                        sleep(5)
                while Main.__sem:
                    t = Thread(target = __connect_)
                    t.start()
                    t.join()
            Thread(target = __connect).start()
            parent.plugins[u'player'].trackChanged.connect(self.scrobble)
    def load(self):
        Main.__sem = True
        Main.loaded = True
    def unload(self):
        Main.__sem = False
        self.parent.plugins[u'player'].trackChanged.disconnect()
        Main.loaded = False
    def QConfiguration():
        kind = QtGui.QComboBox()
        kind.addItem(u'Last.FM')
        kind.addItem(u'Libre.FM')
        username = QtGui.QLineEdit(
                Main.__settings.value(u'username', u'').toString())
        password = QtGui.QLineEdit()
        password.setEchoMode(password.Password)
        password__ = Main.__settings.value(u'password', u'').toInt()[0] * u'*'
        password.setText(password__)
        formLayout = QtGui.QFormLayout()
        formLayout.addRow(u'Database:', kind)
        formLayout.addRow(u'Username:', username)
        formLayout.addRow(u'Password:', password)
        msg = QtGui.QLabel(u'Not tested yet')
        msg.setAutoFillBackground(True)
        msg.setFrameShape(QtGui.QFrame.Box)
        palette = msg.palette()
        palette.setColor(msg.backgroundRole(), Qt.yellow)
        msg.setPalette(palette)
        def store():
            kind_ = unicode(kind.currentText())
            username_ = unicode(username.text())
            if password.text() == password__:
                pass_hash = unicode(
                        Main.__settings.value(u'password_hash', u'').toString())
                password_ = Main.__settings.value(u'password',
                        0).toInt()[0] * u'*'
            else:
                password_ = unicode(password.text())
                pass_hash = pylast.md5(password_)
            def update(msg_, color):
                msg.setText(msg_)
                palette.setColor(msg.backgroundRole(), color)
                msg.setPalette(palette)
            if username_ != u'' and password_ != u'':
                def __connect():
                    try:
                        Main.__net = getattr(pylast, Main.__opt[kind_])(
                                api_key = Main.__key,
                                api_secret = Main.__sec,
                                username = username_,
                                password_hash = pass_hash
                                )
                        update(u'Successful', Qt.green)
                        Main.__settings.setValue(u'kind', kind_)
                        Main.__settings.setValue(u'username', username_) 
                        Main.__settings.setValue(u'password', len(password_))
                        Main.__settings.setValue(u'password_hash', pass_hash) 
                    except pylast.WSError as msg_:
                        update(unicode(msg_).split(u'.')[0], Qt.red)
                Thread(target = __connect).start()
            else:
                update(u'Username and/or password is empty', Qt.yellow)
        apply_ = QtGui.QPushButton(u'Apply')
        apply_.clicked.connect(store)
        testLayout = QtGui.QHBoxLayout()
        testLayout.addWidget(apply_)
        testLayout.addWidget(msg)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addLayout(testLayout)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        widget.enabled = Main.__settings.value(u'enabled', 0).toInt()[0]
        widget.setSetting = lambda x, y : Main.__settings.setValue(x, y)
        return widget
    QConfiguration = staticmethod(QConfiguration)
    def scrobble(self, artist, title, album, track_number):
        def __scrobble(artist, title, album, track_number, timestamp = None):
            try:
                Main.__net.scrobble(
                        artist = unicode(artist),
                        title = unicode(title),
                        timestamp = timestamp or unicode(int(time())),
                        album = unicode(album),
                        track_number = unicode(track_number)
                        )
            except (gaierror, error, AttributeError):
                i = Main.__settings.value(u'queue/size', 0).toInt()[0]
                Main.__settings.setValue(u'queue/' + unicode(i) + u'/elem',
                        (artist, title, album, track_number,
                            timestamp or unicode(int(time()))))
                Main.__settings.setValue(u'queue/size', i + 1)
        queue = []
        for i in range(Main.__settings.value(u'queue/size', 0).toInt()[0]):
            queue.append(Main.__settings.value(
                    u'queue/' + unicode(i) + u'/elem').toPyObject())
            Main.__settings.remove(u'queue/' + unicode(i) + u'/elem')
        Main.__settings.setValue(u'queue/size', 0)
        for q in queue:
            Thread(target = __scrobble, args = q).start()
        Thread(target = __scrobble, args = (
            artist, title, album, track_number)).start()
