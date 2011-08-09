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

from threading import RLock
from Queue import Queue
from PyQt4.QtCore import QThread, QSettings, pyqtSignal
from gayeogi.db.bees.beeexceptions import ConnError, NoBandError

class Bee(QThread):
    u"""Worker thread used by Distributor.

    Signals:
    errors -- emitted when an error occurs:
        unicode -- database name
        unicode -- error type
        unicode -- release name
        unicode -- error message
    """
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    def __init__(self, tasks, library, urls, avai,
            modified, name, rlock, processed):
        u"""Worker thread constructor.

        Arguments:
        tasks -- initial tasks queue (it will get tasks from here)
        library -- main library part (library[1])
        urls -- urls library part (library[3])
        avai -- available library part (library[4])
        name -- used database name
        rlock -- RLock object used to provide thread-safety (should be the same
        for all instances of Bee!)
        processed -- processed artists storage (used in ~behaviour mode)
        """
        QThread.__init__(self)
        self.tasks = tasks
        self.library = library
        self.urls = urls
        self.avai = avai
        self.modified = modified
        self.name = name
        self.rlock = rlock
        self.processed = processed
        self.start()
    def run(self):
        u"""Start worker thread, fetch given artist releases and append them
        to the library.

        Note: Use start() method to run it in a separate thread.
        """
        while True:
            work, (artist, element), types = self.tasks.get()
            if not work:
                break
            added = False
            albums = dict()
            try:
                try:
                    result = work(artist, element, self.urls[artist], types)
                except KeyError:
                    result = work(artist, element, {}, types)
            except NoBandError as e:
                self.rlock.acquire()
                try:
                    del self.urls[artist][self.name]
                except KeyError:
                    pass
                else:
                    self.modified[0] = True
                try:
                    del self.processed[artist]
                except KeyError:
                    pass
                self.rlock.release()
                self.errors.emit(self.name, u'errors', artist, e.message)
            except ConnError as e:
                self.errors.emit(self.name, u'errors', artist, e.message)
            else:
                for error in result[u'errors']:
                    self.errors.emit(self.name, u'errors', artist, error)
                for (album, year) in result[u'result']:
                    albums.setdefault(year, set([album])).add(album)
                    self.rlock.acquire()
                    partial = self.library[artist]
                    try:
                        partial = partial[year]
                    except KeyError:
                        partial[year] = {album: {}}
                        added = True
                    else:
                        try:
                            partial = partial[album]
                        except KeyError:
                            partial[album] = {}
                            added = True
                    self.avai.setdefault(artist + year + album,
                            {u'digital': False, u'analog': False,
                                u'remote': set([self.name])}
                            )[u'remote'].add(self.name)
                    self.urls.setdefault(artist,
                            {self.name: result[u'choice']}
                            )[self.name] = result[u'choice']
                    self.processed[artist] = True
                    self.rlock.release()
            finally:
                self.rlock.acquire()
                def __internal(artist, year, album):
                    key = artist + year + album
                    if not self.avai[key][u'digital'] and \
                            not self.avai[key][u'analog'] and \
                            self.avai[key][u'remote'] == set([self.name]):
                        __internal.torem.add((artist, year, album))
                    else:
                        self.avai[key][u'remote'].discard(self.name)
                        __internal.norem = True
                __internal.torem = set()
                __internal.norem = False
                for year, a in self.library[artist].iteritems():
                    try:
                        for album in set(a) ^ albums[year]:
                            __internal(artist, year, album)
                    except KeyError:
                        for album in a:
                            __internal(artist, year, album)
                if added:
                    self.errors.emit(self.name, u'info', artist,
                            self.trUtf8('Something has been added.'))
                    self.modified[0] = True
                if __internal.torem or __internal.norem:
                    self.errors.emit(self.name, u'info', artist,
                            self.trUtf8('Something has been removed.'))
                    self.modified[0] = True
                elif not added:
                    self.errors.emit(self.name, u'info', artist,
                            self.trUtf8('Nothing has been changed.'))
                while __internal.torem:
                    (artist, year, album) = __internal.torem.pop()
                    del self.library[artist][year][album]
                    del self.avai[artist + year + album]
                    if not self.library[artist][year]:
                        del self.library[artist][year]
                    if not self.library[artist]:
                        del self.library[artist]
                        del self.urls[artist]
                        try:
                            self.processed[artist]
                        except KeyError:
                            pass
                        else:
                            del self.processed[artist]
                self.rlock.release()
                self.tasks.task_done()

class Distributor(QThread):
    u"""Main db object to fetch all releases and append them to the library.

    Signals:
    updated -- emitted at the end (should be 'finished', but comp. reasons)
    stepped -- emitted after every release:
        unicode -- release name
    errors -- emitted when an error occurs:
        unicode -- database name
        unicode -- error type
        unicode -- release name
        unicode -- error message
    """
    __settings = QSettings(u'gayeogi', u'Databases')
    updated = pyqtSignal()
    stepped = pyqtSignal(unicode)
    errors = pyqtSignal(unicode, unicode, unicode, unicode)
    def __init__(self, library):
        u"""Distributor constructor.

        Arguments:
        library -- reference to the library structure
        """
        QThread.__init__(self)
        self.library = library[1]
        self.urls = library[3]
        self.avai = library[4]
        self.modified = library[5]
    def run(self):
        u"""Start Distributor and fetch releases for enabled dbs.
        It also reads appropriate settings from Databases.conf file.

        Note: Use start() method to run in separate thread.
        """
        bases = [(unicode(self.__settings.value(x + u'/module').toString()),
                    self.__settings.value(x + u'/size').toInt()[0],
                    [unicode(t) for t, e in
                        self.__settings.value(x +
                            u'/types').toPyObject().iteritems() if e])
                for x in self.__settings.value(u'order').toPyObject()
                if self.__settings.value(x + u'/Enabled').toBool()]
        behaviour = self.__settings.value(u'behaviour').toBool()
        processed = dict()
        for (name, threads, types) in bases:
            try:
                db = __import__(u'gayeogi.db.bees.' + name, globals(),
                        locals(), [u'work', u'name'], -1)
            except ImportError: # it should not ever happen
                self.errors.emit(db.name, u'errors', u'gayeogi.db.bees.' + name,
                        u'No such module has been found!!!')
            else:
                tasks = Queue(threads)
                threa = list()
                rlock = RLock()
                for _ in range(threads):
                    t = Bee(tasks, self.library, self.urls,
                            self.avai, self.modified, db.name, rlock, processed)
                    t.errors.connect(self.errors)
                    threa.append(t)
                for entry in self.library.iteritems():
                    if not behaviour:
                        try:
                            processed[entry[0]]
                        except KeyError:
                            tasks.put((db.work, entry, types))
                    else:
                        tasks.put((db.work, entry, types))
                    self.stepped.emit(entry[0])
                tasks.join()
                for _ in range(threads):
                    tasks.put((False, (False, False), False))
                for t in threa:
                    t.wait()
        self.updated.emit()
