from lettuce import step, world
from gayeogi.main import version
from gayeogi.db.distributor import Distributor, Bee
from gayeogi.db.bees.beeexceptions import NoBandError
from PyQt4.QtCore import QSettings
from os import path
from sys import modules
from threading import RLock
from Queue import Queue
from copy import deepcopy
import logging

class Handler(logging.Handler):
    def __init__(self, logs, level = logging.DEBUG):
        logging.Handler.__init__(self, level)
        self.logs = logs
    def emit(self, record):
        self.logs.append(record.msg)

@step('I have an existing database with some entries')
def have_an_existing_database_with_some_entries(step):
    world.database = (version,
        {
            u'Metallica': {
                u'1984': {
                    u'Ride the Lightning': {
                        u'01': {
                            u'Fight Fire with Fire': {
                                u'path': u'fire.mp3'
                            }
                        }
                    }
                }
            },
            u'Iron Maiden': {
                u'1992': {
                    u'Fear of the Dark': {
                        u'01': {
                            u'Be Quick or Be Dead': {
                                u'path': u'quick.mp3'
                            }
                        }
                    }
                }
            },
            u'Pink Floyd': {
                u'1977': {
                    u'Animals': {
                        u'02': {
                            u'Dogs': {
                                u'path': u'dogs.mp3'
                            }
                        }
                    }
                }
            }
        },
        {}, # It doesn't matter in these tests
        {},
        {
            u'Metallica1984Ride the Lightning': {
                u'remote': set(),
                u'analog': False,
                u'digital': True
            },
            u'Iron Maiden1992Fear of the Dark': {
                u'remote': set(),
                u'analog': False,
                u'digital': True
            },
            u'Pink Floyd1977Animals': {
                u'remote': set(),
                u'analog': False,
                u'digital': True
            }
        },
        [False]
    )
    world.expected = deepcopy(world.database)
    world.logs = list()
    world.expected_logs = list()
    logger = logging.getLogger('gayeogi.remote')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(Handler(world.logs))

@step('I start an internet update for "(.*)" (or|and) "(.*)"')
def start_an_internet_update(step, firstdb, tribe, seconddb):
    if tribe == 'or':
        Distributor._Distributor__settings = QSettings(
                path.join(path.dirname(__file__), u'data', u'db1.conf'),
                QSettings.NativeFormat)
    elif tribe == 'and':
        Distributor._Distributor__settings = QSettings(
                path.join(path.dirname(__file__), u'data', u'db2.conf'),
                QSettings.NativeFormat)
    print "It is fetching things from internet and can take quite some time"
    dr = Distributor(world.database)
    dr.start()
    dr.wait()

@step('I should get releases from (either|both) of them')
def should_get_releases(step, option):
    ride = world.database[4][u'Metallica1984Ride the Lightning'][u'remote']
    fear = world.database[4][u'Iron Maiden1992Fear of the Dark'][u'remote']
    pink = world.database[4][u'Pink Floyd1977Animals'][u'remote']
    if option == 'either':
        assert (u'metal-archives.com' in ride or u'musicbrainz.org' in ride)\
                and (u'metal-archives.com' in fear or\
                u'musicbrainz.org' in fear) and\
                (u'metal-archives.com' in pink or u'musicbrainz.org' in pink)
    elif option == 'both':
        assert u'metal-archives.com' in ride and u'musicbrainz.org' in ride and\
               u'metal-archives.com' in fear and u'musicbrainz.org' in fear and\
               u'musicbrainz.org' in pink

def __realalbum(artist):
    if artist == u'Iron Maiden':
        return ('Fear of the Dark', '1992')
    elif artist == u'Metallica':
        return ('Ride the Lightning', '1984')
    elif artist == u'Pink Floyd':
        return ('Animals', '1977')
def __remoteaddexp(album2, remote):
    world.expected[4][u'Iron Maiden1992Fear of the Dark']\
        [u'remote'].add(remote)
    world.expected[4].setdefault(u'Iron Maiden2010' + album2, {
        u'remote': set([remote]),
        u'digital': False,
        u'analog': False
    })[u'remote'].add(remote)
    world.expected[4][u'Metallica1984Ride the Lightning']\
        [u'remote'].add(remote)
    world.expected[4].setdefault(u'Metallica2010' + album2, {
        u'remote': set([remote]),
        u'digital': False,
        u'analog': False
    })[u'remote'].add(remote)
    world.expected[4][u'Pink Floyd1977Animals']\
        [u'remote'].add(remote)
    world.expected[4].setdefault(u'Pink Floyd2010' + album2, {
        u'remote': set([remote]),
        u'digital': False,
        u'analog': False
    })[u'remote'].add(remote)
    world.expected[5][0] = True
def remote1add(artist, element, urls, types):
    return {
        u'errors': set(),
        u'result': [
            __realalbum(artist),
            ('Album1', '1990'),
            ('Album2', '2010')
        ],
        u'choice': u'r1a'
    }
def remote1addexp():
    world.expected[4][u'Iron Maiden1990Album1'] = {
        u'remote': set([u'remote1']),
        u'digital': False,
        u'analog': False
    }
    world.expected[4][u'Metallica1990Album1'] = {
        u'remote': set([u'remote1']),
        u'digital': False,
        u'analog': False
    }
    world.expected[4][u'Pink Floyd1990Album1'] = {
        u'remote': set([u'remote1']),
        u'digital': False,
        u'analog': False
    }
    __remoteaddexp(u'Album2', u'remote1')
    world.expected[1][u'Iron Maiden'].update({
        '1990': {
            'Album1': {}
        },
        '2010': {
            'Album2': {}
        }
    })
    world.expected[1][u'Metallica'].update({
        '1990': {
            'Album1': {}
        },
        '2010': {
            'Album2': {}
        }
    })
    world.expected[1][u'Pink Floyd'].update({
        '1990': {
            'Album1': {}
        },
        '2010': {
            'Album2': {}
        }
    })
    world.expected[3][u'Iron Maiden'] = {u'remote1': u'r1a'}
    world.expected[3][u'Metallica'] = {u'remote1': u'r1a'}
    world.expected[3][u'Pink Floyd'] = {u'remote1': u'r1a'}
    world.expected_logs.extend([
        [u'Pink Floyd', u'Something has been added.'],
        [u'Iron Maiden', u'Something has been added.'],
        [u'Metallica', u'Something has been added.']
    ])
def remote1remove(artist, element, urls, types):
    return {
        u'errors': set(),
        u'result': [
            ('Album1', '1990')
        ],
        u'choice': u'r1a'
    }
def __remoteremoveexp(remote):
    world.expected[4][u'Iron Maiden1992Fear of the Dark']\
        [u'remote'].discard(remote)
    world.expected[4][u'Metallica1984Ride the Lightning']\
        [u'remote'].discard(remote)
    world.expected[4][u'Pink Floyd1977Animals'][u'remote'].discard(remote)
    world.expected_logs.extend([
        [u'Pink Floyd', u'Something has been removed.'],
        [u'Iron Maiden', u'Something has been removed.'],
        [u'Metallica', u'Something has been removed.']
    ])
def remote1removeexp():
    __remoteremoveexp(u'remote1')
    world.expected[4][u'Iron Maiden2010Album2'][u'remote'].discard(u'remote1')
    world.expected[4][u'Metallica2010Album2'][u'remote'].discard(u'remote1')
    world.expected[4][u'Pink Floyd2010Album2'][u'remote'].discard(u'remote1')
def remote2add(artist, element, urls, types):
    return {
        u'errors': set(),
        u'result': [
            __realalbum(artist),
            ('Album2', '2010'),
            ('Album3', '2110')
        ],
        u'choice': u'r2a'
    }
def remote2addexp():
    __remoteaddexp(u'Album2', u'remote2')
    world.expected[4][u'Iron Maiden2110Album3'] = {
        u'remote': set([u'remote2']),
        u'digital': False,
        u'analog': False
    }
    world.expected[4][u'Metallica2110Album3'] = {
        u'remote': set([u'remote2']),
        u'digital': False,
        u'analog': False
    }
    world.expected[4][u'Pink Floyd2110Album3'] = {
        u'remote': set([u'remote2']),
        u'digital': False,
        u'analog': False
    }
    world.expected[1][u'Iron Maiden']['2110'] = {'Album3': {}}
    world.expected[1][u'Metallica']['2110'] = { 'Album3': {}}
    world.expected[1][u'Pink Floyd']['2110'] = { 'Album3': {}}
    world.expected[3][u'Iron Maiden'][u'remote2'] = u'r2a'
    world.expected[3][u'Metallica'][u'remote2'] = u'r2a'
    world.expected[3][u'Pink Floyd'][u'remote2'] = u'r2a'
    world.expected_logs.extend([
        [u'Pink Floyd', u'Something has been added.'],
        [u'Iron Maiden', u'Something has been added.'],
        [u'Metallica', u'Something has been added.']
    ])
def remote2remove(artist, element, urls, types):
    return {
        u'errors': set(),
        u'result': [
            ('Album3', '2110')
        ],
        u'choice': u'r2a'
    }
def remote2removeexp():
    __remoteremoveexp(u'remote2')
    del world.expected[4][u'Iron Maiden2010Album2']
    del world.expected[4][u'Metallica2010Album2']
    del world.expected[4][u'Pink Floyd2010Album2']
    del world.expected[1][u'Iron Maiden'][u'2010']
    del world.expected[1][u'Metallica'][u'2010']
    del world.expected[1][u'Pink Floyd'][u'2010']
def remote2removecomp(artist, element, urls, types):
    raise NoBandError()
def remote2removecompexp():
    del world.expected[4][u'Iron Maiden2110Album3']
    del world.expected[4][u'Metallica2110Album3']
    del world.expected[4][u'Pink Floyd2110Album3']
    del world.expected[3][u'Iron Maiden'][u'remote2']
    del world.expected[3][u'Metallica'][u'remote2']
    del world.expected[3][u'Pink Floyd'][u'remote2']
    del world.expected[1][u'Iron Maiden'][u'2110']
    del world.expected[1][u'Metallica'][u'2110']
    del world.expected[1][u'Pink Floyd'][u'2110']
    world.expected_logs.extend([
        [u'Pink Floyd', u'No such band has been found.'],
        [u'Pink Floyd', u'Something has been removed.'],
        [u'Iron Maiden', u'No such band has been found.'],
        [u'Iron Maiden', u'Something has been removed.'],
        [u'Metallica', u'No such band has been found.'],
        [u'Metallica', u'Something has been removed.']
    ])

@step('I (add|remove) (some|all) remote informations from "(.*)"')
def some_remote_informations(step, option, option2, base):
    if option2 == 'some':
        real_base = getattr(modules[__name__], base + option)
        getattr(modules[__name__], base + option + "exp")()
    elif option2 == 'all':
        real_base = remote2removecomp
        remote2removecompexp()
    tasks = Queue(1)
    bee = Bee(tasks, world.database[1], world.database[3],
        world.database[4], world.database[5], base, RLock(), dict())
    for entry in world.database[1].iteritems():
        tasks.put((real_base, entry, []))
    tasks.put((False, (False, False), False))
    bee.wait()

@step('The local database should get updated appropriately')
def local_database_should_get_updated(step):
    assert world.database == world.expected
