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
from beeexceptions import ConnError

class BandBee(Thread):
    def __init__(self, tasks, releases, rlock, elock):
        Thread.__init__(self)
        self.tasks = tasks
        self.releases = releases
        self.rlock = rlock
        self.elock = elock
        self.daemon = True
        self.start()
    def run(self):
        while True:
            sense, url, results, errors = self.tasks.get()
            if(sense == False):
                break
            try:
                result = [sense(url, self.releases)]
            except ConnError as e:
                self.elock.acquire()
                errors.append(e)
                self.elock.release()
            else:
                if result:
                    self.rlock.acquire()
                    results.extend(result)
                    self.rlock.release()
            finally:
                self.tasks.task_done()

class Bandsensor(object):
    def __init__(self, func, urls, albums, releases = None):
        self.sense = func
        self.urls = urls
        self.albums = albums
        self.releases = releases
        self.errors = list()
        self.results = list()
    def run(self):
        tasks = Queue(5)
        rlock = RLock()
        elock = RLock()
        threads = list()
        for _ in range(5):
            threads.append(BandBee(tasks, self.releases, rlock, elock))
        for url in self.urls:
            tasks.put((self.sense, url, self.results, self.errors))
        tasks.join()
        for _ in range(5):
            tasks.put((False, False, False, False))
        for thread in threads:
            thread.join()
        values = dict()
        for i, (url, single) in enumerate(self.results):
            for album, year in single:
                for eYear, data in self.albums.iteritems():
                    for eAlbum in data.keys():
                        if album.lower() == eAlbum.lower() and \
                                year == eYear[-4:]:
                            try:
                                values[url][0] += 1
                            except KeyError:
                                values[url] = list()
                                values.append(1)
                                values.append(i)
        if values.keys():
            best = values.keys()[0]
            for k, v in values.iteritems():
                if v[0] > values[best][0]:
                    best = k
            return (best, self.results[values[best][1]][1])
