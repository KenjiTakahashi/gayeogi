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

from threading import Thread
from Queue import Queue
from PyQt4.QtCore import QThread, QSettings
from bees.beeexceptions import ConnError, NoBandError

class Bee(Thread):
    def __init__(self, tasks, library, urls, avai):
        Thread.__init__(self)
        self.tasks = tasks
        self.library = library
        self.urls = urls
        self.avai = avai
        self.daemon = True
        self.start()
    def run(self):
        while True:
            work, (artist, element), types = self.tasks.get()
            try:
                result = work(artist, element, self.urls[artist], types)
            except NoBandError as e:
                pass # emit signal here and then in Distributor redirect it to GUI?
            except ConnError as e:
                pass # same as above?
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
        self.start()
    def run(self):
        queues = list()
        for (name, threads, types) in self.bases:
            try:
                db = __import__(u'bees.' + name, globals(),
                        locals(), [u'work'], -1)
            except:
                pass # signal sth to GUI
            else:
                tasks = Queue(threads)
                for _ in range(threads):
                    Bee(tasks, self.library, self.urls, self.avai)
                for entry in self.library.iteritems():
                    tasks.put((db.work, entry, types))
                if self.behaviour:
                    queues.append(tasks)
                else:
                    tasks.join() #need to change self.library here (probably we'll operate on copy)
        if self.behaviour:
            for q in queues:
                q.join()
