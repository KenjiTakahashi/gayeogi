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

class BandBee(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    def run(self):
        while True:
            sense, url, results, releases = self.tasks.get()
            try:
                result = [sense(url, releases)]
            except:
                raise # do sth with it!
            else:
                if result:
                    results.extend(result) # use a mutex probably
            finally:
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
        for _ in range(5):
            BandBee(tasks)
        for url in self.urls:
            tasks.put((self.sense, url, self.results, self.releases))
        tasks.join()
        values = dict()
        for i, (url, single) in enumerate(self.results):
            for album, year in single:
                for eAlbum in self.albums.keys():
                    if album.lower() == eAlbum.lower():
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
