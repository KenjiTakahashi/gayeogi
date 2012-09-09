# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2010 - 2012
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
import logging

logger = logging.getLogger('gayeogi.remote')


class Bee(QThread):
    """Worker thread used by Distributor."""

    def __init__(self, tasks, rlock, case):
        """Constructs new worker instance.

        @note: :rlock: object should be the same for all Bee instances!

        :tasks: Initial tasks queue (Bee will get tasks from here).
        :rlock: RLock object used to provide thread-safety.
        :case: Case sensitivity.
        """
        super(Bee, self).__init__()
        self.tasks = tasks
        self.rlock = rlock
        self.case = case
        self.start()

    def fetch(self, work, artist, url, albums, types):
        """@todo: Docstring for fetch

        :work: @todo
        :artist: @todo
        :url: @todo
        :albums: @todo
        :types: @todo
        :returns: @todo

        """
        try:
            result = work(artist, albums, url, types)
        except NoBandError as e:
            pass  # TODO: remove url (no such artist in that db)
        except ConnError as e:
            pass  # TODO: log connection error
        else:
            for error in result[u'errors']:
                pass  # TODO: log errors
            return result[u'result']

    def run(self):
        """Starts worker thread, fetches given artist releases
        and appends them to the library.

        @note: Use Bee.start method to run in a separate thread.
        """
        while True:
            dbs, behaviour, (artist, urls, albums, upsert) = self.tasks.get()
            processed = False
            for db, types in dbs:
                url = ""  # TODO: get url
                if not behaviour:
                    if not processed[0]:
                        result = self.fetch(db, artist, url, albums, types)
                else:
                    result = self.fetch(db, artist, url, albums, types)
            if result is not None:
                for a1, y1 in result[u'result']:
                    if self.case:
                        for a2, y2 in albums:
                            if y1 == y2 and a1.lower() == a2.lower():
                                a1 = a2
                    with self.rlock:
                        pass  # TODO: upsert
            added = False
            albums = dict()
            try:
                pass
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
                logger.warning([artist, e.message])
            else:
                for (album, year) in result[u'result']:
                    if self.case and year in self.library[artist]:
                        for alb in self.library[artist][year].iterkeys():
                            key = artist + year + alb
                            if(
                                alb.lower() == album.lower()
                                and self.avai[key][u'digital']
                            ):
                                album = alb
                                break
                    albums.setdefault(year, set([album])).add(album)
                    self.rlock.acquire()
                    partial = self.library[artist].setdefault(year, {})
                    partial.setdefault(album, {})
                    key = artist + year + album
                    partial = self.avai.setdefault(key, {})
                    if not partial:
                        partial[u'analog'] = False
                        partial[u'digital'] = False
                        partial[u'remote'] = set([self.name])
                        added = True
                    elif self.name not in partial[u'remote']:
                        partial[u'remote'].add(self.name)
                        added = True
                    self.urls.setdefault(artist,
                        {self.name: result[u'choice']}
                    )[self.name] = result[u'choice']
                    self.processed[artist] = True
                    self.rlock.release()
            finally:
                self.rlock.acquire()

                def __internal(artist, year, album):
                    key = artist + year + album
                    if (
                        not self.avai[key][u'digital'] and
                        not self.avai[key][u'analog'] and
                        self.avai[key][u'remote'] == set([self.name])
                    ):
                        __internal.torem.add((artist, year, album))
                    else:
                        try:
                            self.avai[key][u'remote'].remove(self.name)
                        except KeyError:
                            pass
                        else:
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
                    logger.info(
                        [artist, self.trUtf8('Something has been added.')]
                    )
                    self.modified[0] = True
                if __internal.torem or __internal.norem:
                    logger.info(
                        [artist, self.trUtf8('Something has been removed.')]
                    )
                    self.modified[0] = True
                elif not added:
                    logger.info(
                        [artist, self.trUtf8('Nothing has been changed.')]
                    )
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
    """Main db object to fetch all releases and append them to the library.

    @signals:
    updated -- emitted at the end (should be 'finished', but comp. reasons)
    stepped -- emitted after every release:
        unicode -- release name
    """

    __settings = QSettings(u'gayeogi', u'Databases')
    finished = pyqtSignal()
    stepped = pyqtSignal(unicode)

    def __init__(self, library):
        """Constructs new Distributor instance.

        :library: Iterator over all artists in library.
        """
        super(Distributor, self).__init__()
        self.library = library

    def run(self):
        """Starts Distributor and fetches releases for enabled dbs.

        @note: Also reads appropriate settings from Databases.conf file.
        @note: Use Distributor.start method to run in separate thread.
        """
        bases = [(unicode(self.__settings.value(x + u'/module').toString()),
                    [unicode(t) for t, e in self.__settings.value(
                        x + u'/types'
                    ).toPyObject().iteritems() if e]
                ) for x in self.__settings.value(u'order').toPyObject()
                if self.__settings.value(x + u'/Enabled').toBool()]
        dbs = list()
        for name, types in bases:
            try:
                db = __import__(u'gayeogi.db.bees.' + name, globals(),
                    locals(), [u'work', u'name', u'init'], -1)
            except ImportError:  # it should not ever happen
                logger.error(
                    [name, self.trUtf8('No such module has been found!!!')]
                )
            else:
                try:
                    db.init()
                except AttributeError:
                    pass
                dbs.append((db.work, types))
        threadsnum = self.__settings.value(u'threads', 1).toInt()[0]
        behaviour = self.__settings.value(u'behaviour').toBool()
        tasks = Queue(threadsnum)
        threads = [Bee(
            tasks, RLock(), self.__settings.value(u'case').toBool()
        ) for i in xrange(threadsnum)]
        for artist in self.library:
            self.stepped.emit(artist)
            tasks.put((dbs, behaviour, artist))
        tasks.join()
        # FIXME: It was here, but do we need it?
        for t in threads:
            t.wait()
        self.finished.emit()
