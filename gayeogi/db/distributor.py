# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Woźniak © 2010 - 2012
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
from gayeogi.utils import ConnError
from gayeogi.db.bandsensor import Bandsensor
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

    def fetch(self, db, artist, url, albums, types):
        """@todo: Docstring for fetch

        :db: @todo
        :artist: @todo
        :url: @todo
        :albums: @todo
        :types: @todo
        :returns: @todo
        """
        if url:
            url, albums = db.sense(url, types)
            return (url, albums)
        try:
            urls = db.urls(artist)
        except ConnError as e:
            pass  # TODO: log connection error
        if not urls:
            return None
        sensor = Bandsensor(db.sense, urls, albums, types)
        data = sensor.run()
        if not data:
            return None
        for error in sensor.errors:
            pass  # TODO: log errors
        return (data[0], data[1])

    def run(self):
        """Starts worker thread, fetches releases for given artist
        and upserts them to the library.

        @note: Use Bee.start method to run in a separate thread.
        """
        while True:
            dbs, behaviour, (artist, urls, albums, upsert) = self.tasks.get()
            if dbs is None:
                break
            processed = False
            for db, types in dbs:
                url = urls  # TODO: get url
                if not behaviour:
                    if not processed[0]:
                        nurl, result = self.fetch(
                            db, artist, url, albums, types
                        )
                else:
                    nurl, result = self.fetch(db, artist, url, albums, types)
            if result is not None:
                for a1, y1 in result:
                    if self.case:
                        for a2, y2 in albums:
                            if y1 == y2 and a1.lower() == a2.lower():
                                a1 = a2
                    with self.rlock:
                        upsert((u'album', {
                            u'year': y1,
                            u'album': a1,
                            u'__r__': [True]
                        }))
                for a, y in list(set(albums) - set(result)):
                    with self.rlock:
                        upsert((u'album', {
                            u'year': y,
                            u'album': a,
                            u'__r__': [False]
                        }))


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
                    locals(), [u'sense', u'urls', u'name', u'init'], -1)
            except ImportError:  # it should not ever happen
                logger.error(
                    [name, self.trUtf8('No such module has been found!!!')]
                )
            else:
                try:
                    db.init()
                except AttributeError:
                    pass
                dbs.append((db, types))
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
        for _ in xrange(threadsnum):
            tasks.put(None, None, (None, None, None, None))
        for t in threads:
            t.wait()
        self.finished.emit()
