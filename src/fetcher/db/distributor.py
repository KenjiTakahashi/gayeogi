# This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
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
# -*- coding: utf-8 -*-

from threading import RLock
from Queue import Queue
from PyQt4.QtCore import QThread, QSettings, pyqtSignal
from bees.beeexceptions import ConnError, NoBandError

class Bee(QThread):
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    def __init__(self, tasks, library, urls, avai, name, rlock):
        QThread.__init__(self)
        self.tasks = tasks
        self.library = library
        self.urls = urls
        self.avai = avai
        self.name = name
        self.rlock = rlock
        self.start()
    def run(self):
        while True:
            work, (artist, element), types = self.tasks.get()
            if not work:
                break
            try:
                try:
                    val = self.urls[artist]
                except KeyError:
                    result = work(artist, element, {}, types)
                else:
                    result = work(artist, element, val, types)
            except NoBandError as e:
                self.errors.emit(self.name, u'errors', artist, e)
            except ConnError as e:
                self.errors.emit(self.name, u'errors', artist, e)
            else:
                for error in result[u'errors']:
                    self.errors.emit(self.name, u'errors', artist, error)
                for (album, year) in result[u'result']:
                    self.rlock.acquire()
                    partial = self.library[artist]
                    try:
                        partial = partial[year]
                    except KeyError:
                        partial[year] = {album: {}}
                    else:
                        try:
                            partial = partial[album]
                        except KeyError:
                            partial[album] = {}
                    try:
                        partial = self.avai[artist + year + album]
                    except KeyError:
                        self.avai[artist + year + album] = {
                                u'digital': False,
                                u'analog': False,
                                u'remote': True
                                }
                    else:
                        partial[u'remote'] = True
                    try:
                        partial = self.urls[artist]
                    except KeyError:
                        self.urls[artist] = {self.name: result[u'choice']}
                    else:
                        try:
                            partial[self.name]
                        except KeyError:
                            partial[self.name] = result[u'choice']
                    self.rlock.release()
            finally:
                self.tasks.task_done()

class Distributor(QThread):
    __settings = QSettings(u'fetcher', u'Databases')
    updated = pyqtSignal()
    stepped = pyqtSignal(unicode)
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    def __init__(self, library):
        QThread.__init__(self)
        self.library = library[1]
        self.urls = library[3]
        self.avai = library[4]
    def run(self):
        bases = [(unicode(self.__settings.value(x + u'/module').toString()),
                    self.__settings.value(x + u'/size').toInt()[0],
                    [unicode(t) for t, e in
                        self.__settings.value(x +
                            u'/types').toPyObject().iteritems() if e])
                for x in self.__settings.value(u'order').toPyObject()
                if self.__settings.value(x + u'/Enabled').toBool()]
        behaviour = self.__settings.value(u'behaviour').toInt()[0]
        for (name, threads, types) in bases:
            try:
                db = __import__(u'bees.' + name, globals(),
                        locals(), [u'work'], -1)
            except ImportError:
                pass # signal sth to GUI
            else:
                tasks = Queue(threads)
                threa = list()
                rlock = RLock()
                for _ in range(threads):
                    t = Bee(tasks, self.library,
                        self.urls, self.avai, name, rlock)
                    t.errors.connect(self.errors)
                    threa.append(t)
                for entry in self.library.iteritems():
                    if not behaviour:
                        try:
                            val = self.urls[entry[0]].keys()
                        except KeyError:
                            tasks.put((db.work, entry, types))
                        else:
                            if name in val:
                                tasks.put((db.work, entry, types))
                    self.stepped.emit(entry[0])
                tasks.join()
                for _ in range(threads):
                    tasks.put((False, (False, False), False))
                for t in threa:
                    t.wait()
            self.updated.emit()
