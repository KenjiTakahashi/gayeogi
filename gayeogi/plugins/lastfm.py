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

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, Qt
import pylast
from threading import Thread
from time import time, sleep

class Main(object):
    """Last.FM/Libre.FM plugin."""
    name = u'Last.FM'
    loaded = False
    depends = [u'player']
    __key = u'a3f47739f0f87e24f499a7683cc0d1fd'
    __sec = u'1e4a65fba65e59cfb76adcc5af2fc3e3'
    __net = None
    __opt = {u'Last.FM': u'LastFMNetwork', u'Libre.FM': u'LibreFMNetwork'}
    __settings = QSettings(u'gayeogi', u'Last.FM')
    __sem = True
    def __init__(self, parent, ___, _, __):
        """Creates new Main instance.

        Args:
            parent: parent widget
            ___: whatever
            _: whatever
            __: whatever

        """
        username = unicode(Main.__settings.value(u'username', u'').toString())
        password = unicode(
            Main.__settings.value(u'password_hash', u'').toString()
        )
        kind = unicode(Main.__settings.value(u'kind', u'Last.FM').toString())
        proxyhost = unicode(Main.__settings.value(u'phost', u'').toString())
        proxyport = unicode(Main.__settings.value(u'pport', u'').toString())
        if username != u'' and password != u'':
            self.parent = parent
            def __connect():
                def __connect_():
                    try:
                        Main.__net = getattr(pylast, Main.__opt[kind])(
                            api_key = self.__key,
                            api_secret = self.__sec,
                            username = username,
                            password_hash = password
                        )
                        if proxyhost and proxyport:
                            Main.__net.enable_proxy(proxyhost, proxyport)
                        Main.__sem = False
                    except:
                        sleep(5)
                while Main.__sem:
                    t = Thread(target = __connect_)
                    t.start()
                    t.join()
            Thread(target = __connect).start()
            parent.plugins[u'player'].trackChanged.connect(self.scrobble)
    def load(self):
        """Loads the plugin in."""
        Main.__sem = True
        Main.loaded = True
    def unload(self):
        """Unloads the plugin."""
        Main.__sem = False
        try:
            self.parent.plugins[u'player'].trackChanged.disconnect()
        except AttributeError:
            pass
        Main.loaded = False
    @staticmethod
    def QConfiguration():
        """Creates configuration widget.

        Returns:
            QWidget -- config widget used in settings dialog.

        """
        kind = QtGui.QComboBox()
        kind.addItem(u'Last.FM')
        kind.addItem(u'Libre.FM')
        username = QtGui.QLineEdit(
            Main.__settings.value(u'username', u'').toString()
        )
        password = QtGui.QLineEdit()
        password.setEchoMode(password.Password)
        password.setText(
            Main.__settings.value(u'password', u'').toInt()[0] * u'*'
        )
        proxyhost = QtGui.QLineEdit(
            Main.__settings.value(u'phost', u'').toString()
        )
        proxyport = QtGui.QLineEdit(
            Main.__settings.value(u'pport', u'').toString()
        )
        formLayout = QtGui.QFormLayout()
        formLayout.addRow(QtGui.QApplication.translate(
            'Last.FM', 'Database:'), kind)
        formLayout.addRow(QtGui.QApplication.translate(
            'Last.FM', 'Username:'), username)
        formLayout.addRow(QtGui.QApplication.translate(
            'Last.FM', 'Password:'), password)
        formLayout.addRow(QtGui.QApplication.translate(
            'Last.FM', 'Proxy host:'), proxyhost)
        formLayout.addRow(QtGui.QApplication.translate(
            'Last.FM', 'Proxy port:'), proxyport)
        msg = QtGui.QLabel(QtGui.QApplication.translate(
            'Last.FM', 'Not tested yet'))
        msg.setAutoFillBackground(True)
        msg.setFrameShape(QtGui.QFrame.Box)
        palette = msg.palette()
        palette.setColor(msg.backgroundRole(), Qt.yellow)
        msg.setPalette(palette)
        def test():
            kind_ = unicode(kind.currentText())
            username_ = unicode(username.text())
            password_ = unicode(password.text())
            pass_hash = pylast.md5(password_)
            proxyhost_ = unicode(proxyhost.text())
            proxyport_ = unicode(proxyport.text())
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
                        if proxyhost_ and proxyport_:
                            Main.__net.enable_proxy(proxyhost_, proxyport_)
                        update(QtGui.QApplication.translate(
                            'Last.FM', 'Successful'), Qt.green)
                    except (pylast.NetworkError, pylast.WSError) as msg_:
                        update(unicode(msg_).split(u'.')[0], Qt.red)
                Thread(target = __connect).start()
            else:
                update(QtGui.QApplication.translate(
                    'Last.FM', 'Username and/or password is empty'), Qt.yellow)
        apply_ = QtGui.QPushButton(
            QtGui.QApplication.translate('Last.FM', 'Test')
        )
        apply_.clicked.connect(test)
        testLayout = QtGui.QHBoxLayout()
        testLayout.addWidget(apply_)
        testLayout.addWidget(msg)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addLayout(testLayout)
        layout.addStretch()
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        widget.enabled = Main.__settings.value(u'enabled', 0).toInt()[0]
        def save(x, y):
            Main.__settings.setValue(x, y)
            Main.__settings.setValue(u'kind', unicode(kind.currentText()))
            Main.__settings.setValue(u'username',unicode(username.text()))
            password_ = unicode(password.text())
            Main.__settings.setValue(u'password', len(password_))
            Main.__settings.setValue(u'password_hash', pylast.md5(password_)) 
            Main.__settings.setValue(u'phost', unicode(proxyhost.text()))
            Main.__settings.setValue(u'pport', unicode(proxyport.text()))
        widget.setSetting = lambda x, y : save(x, y)
        return widget
    def scrobble(self, artist, title, album, track_number):
        """Send specified track to selected scrobbling service.

        It also reads and sends tracks from queue, if any.

        Args:
            artist (unicode): artist name
            title (unicode): track title
            album (unicode): album name
            track_number (int): track number

        """
        def __scrobble(artist, title, album, track_number, timestamp = None):
            try:
                Main.__net.scrobble(
                    artist = unicode(artist),
                    title = unicode(title),
                    timestamp = timestamp or unicode(int(time())),
                    album = unicode(album),
                    track_number = unicode(track_number)
                )
            except:
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
