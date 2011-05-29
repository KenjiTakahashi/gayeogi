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

from threading import Thread, RLock
from Queue import Queue
from PyQt4.QtCore import QThread, QSettings
from bees.beeexceptions import ConnError, NoBandError

class Bee(Thread):
    def __init__(self, tasks, library, urls, avai, elock):
        Thread.__init__(self)
        self.tasks = tasks
        self.library = library
        self.urls = urls
        self.avai = avai
        self.elock = elock
        self.daemon = True
        self.start()
    def run(self):
        while True:
            work, (artist, element), types, errors = self.tasks.get()
            if not work:
                break
            try:
                result = work(artist, element, self.urls[artist], types)
            except NoBandError as e:
                self.elock.acquire()
                errors.append(e)
                self.elock.release()
            except ConnError as e:
                self.elock.acquire()
                errors.append(e)
                self.elock.release()
            else:
                pass
            finally:
                self.tasks.task_done()

class Distributor(QThread):
    __settings = QSettings(u'fetcher', u'Databases')
    def __init__(self, library, behaviour):
        QThread.__init__(self)
        self.bases = [
                (unicode(self.__settings.value(x + u'/module').toString()),
                    self.__settings.value(x + u'/size').toInt()[0],
                    [unicode(t) for t, e in
                        self.__settings.value(x +
                            u'/types').toPyObject().iteritems() if e])
                for x in self.__settings.value(u'order').toPyObject()
                if self.__settings.value(x + u'/Enabled').toBool()]
        self.library = library[1]
        self.urls = library[3]
        self.avai = library[4]
        self.behaviour = behaviour
        self.errors = list()
        self.start()
    def run(self):
        for (name, threads, types) in self.bases:
            try:
                db = __import__(u'bees.' + name, globals(),
                        locals(), [u'work'], -1)
            except ImportError:
                pass # signal sth to GUI
            else:
                tasks = Queue(threads)
                threa = list()
                elock = RLock()
                for _ in range(threads):
                    threa.append(Bee(tasks, self.library,
                        self.urls, self.avai, elock))
                for entry in self.library.iteritems():
                    if not self.behaviour and not name in self.avai[entry[0]]:
                        tasks.put((db.work, entry, types, self.errors))
                tasks.join()
                for _ in range(threads):
                    tasks.put((False, False, False, False))
                for t in threa:
                    t.join()
