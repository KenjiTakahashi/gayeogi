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

class Main(object):
    name = u'Last.FM'
    loaded = False
    depends = [u'player']
    __key = u'a3f47739f0f87e24f499a7683cc0d1fd'
    __sec = u'1e4a65fba65e59cfb76adcc5af2fc3e3'
    #__settings = QSettings(u'fetcher', u'Lastfm')
    def __init__(self, parent, library, _, __):
        pass
    def load(self):
        Main.loaded = True
    def unload(self):
        Main.loaded = False
    def QConfiguration():
        __settings = QSettings(u'fetcher', u'Lastfm')
        username = QtGui.QLineEdit(
                __settings.value(u'username', u'').toString())
        password = QtGui.QLineEdit(
                __settings.value(u'password', u'').toString())
        formLayout = QtGui.QFormLayout()
        formLayout.addRow(u'Username:', username)
        formLayout.addRow(u'Password:', password)
        def store():
            __settings.setValue(u'username', unicode(username.text()))
            __settings.setValue(u'password',
                    pylast.md5(unicode(password.text())))
        apply_ = QtGui.QPushButton(u'Apply')
        apply_.clicked.connect(store)
        msg = QtGui.QLabel(u'Not tested yet')
        msg.setAutoFillBackground(True)
        msg.setFrameShape(QtGui.QFrame.Box)
        palette = msg.palette()
        palette.setColor(msg.backgroundRole(), Qt.yellow)
        msg.setPalette(palette)
        testLayout = QtGui.QHBoxLayout()
        testLayout.addWidget(apply_)
        testLayout.addWidget(msg)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addLayout(testLayout)
        widget = QtGui.QWidget()
        widget.setLayout(layout)
        widget.enabled = __settings.value(u'enabled', 0).toInt()[0]
        widget.setSetting = lambda x, y : __settings.setValue(x, y)
        return widget
    QConfiguration = staticmethod(QConfiguration)
