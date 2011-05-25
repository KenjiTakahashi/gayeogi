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

class Bee(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    def run(self):
        while True:
            db, (artist, element), types, library = self.tasks.get()
            try:
                result = db.work(artist, element, types)
            except db.NoBandError as e:
                pass # emit signal here and then in Distributor redirect it to GUI?
            except db.ConnError as e:
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
        self.library = library[0]
        self.behaviour = behaviour
        self.start()
    def run(self):
        queues = list()
        for (name, threads, types) in self.bases:
            try:
                db = __import__(u'bees.' + name, globals(),
                        locals(), [u'work', u'NoBandError', u'ConnError'], -1)
            except:
                pass # signal sth to GUI
            else:
                tasks = Queue(threads)
                for _ in range(threads):
                    Bee(tasks)
                for entry in self.library.iteritems():
                    tasks.put((db, entry, types, self.library))
                if self.behaviour:
                    queues.append(tasks)
                else:
                    tasks.join() #need to change self.library here (probably we'll operate on copy)
        if self.behaviour:
            for q in queues:
                q.join()
