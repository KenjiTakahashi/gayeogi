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

class BandBee(Thread):
    def __init__(self, tasks, lock):
        Thread.__init__(self)
        self.tasks = tasks
        self.lock = lock
        self.daemon = True
        self.start()
    def run(self):
        while True: # we need to catch ConnError here
            sense, url, results, releases = self.tasks.get()
            if(sense == False):
                break
            result = [sense(url, releases)]
            if result:
                self.lock.acquire()
                results.extend(result)
                self.lock.release()
            self.tasks.task_done()

class Bandsensor(object):
    def __init__(self, func, urls, albums, releases = None):
        self.sense = func
        self.urls = urls
        self.albums = albums
        self.releases = releases
        self.results = list()
    def run(self):
        tasks = Queue(5)
        lock = RLock()
        threads = list()
        for _ in range(5):
            threads.append(BandBee(tasks, lock))
        for url in self.urls:
            tasks.put((self.sense, url, self.results, self.releases))
        tasks.join()
        for _ in range(5):
            tasks.put((False, False, False, False))
        for thread in threads:
            thread.join()
        values = dict()
        for i, (url, single) in enumerate(self.results):
            for album, year in single:
                for eAlbum in self.albums.keys():
                    if album.lower() == eAlbum.lower() and \
                            year == self.albums[eAlbum][u'date']:
                        try:
                            values[url][0] += 1
                        except KeyError:
                            values[url] = list()
                            values[url].append(1)
                            values[url].append(i)
        if values.keys():
            best = values.keys()[0]
            for k, v in values.iteritems():
                if v[0] > values[best][0]:
                    best = k
            return (best, self.results[values[best][1]][1])
