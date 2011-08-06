from lettuce import step, world
from gayeogi.main import version
from gayeogi.db.distributor import Distributor
from PyQt4.QtCore import QSettings
from os import path

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
            [False])

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
                (u'metal-archives.com' in pink or u'musicbrainz.org' in pink), world.database[4][u'Pink Floyd1977Animals']
    elif option == 'both':
        assert u'metal-archives.com' in ride and u'musicbrainz.org' in ride and\
               u'metal-archives.com' in fear and u'musicbrainz.org' in fear and\
               u'musicbrainz.org' in pink
