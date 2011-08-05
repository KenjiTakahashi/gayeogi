from lettuce import step, world, after, before
from gayeogi.main import version
from gayeogi.db import local
import os
import shutil
from copy import deepcopy

@before.all
def init():
    world.basedir = os.path.dirname(__file__)
    world.renames = list()
    world.exchanges = set()

@after.all
def deinit(total):
    for (old, new) in world.renames:
        os.rename(old, new)
    for ex in world.exchanges:
        os.remove(ex)
    os.remove(os.path.join(world.basedir, u'data/second_test.flac'))

def __add_to_expected(newone):
    world.expected[1].update(newone[0])
    world.expected[2].update(newone[1])
    world.expected[4].update(newone[2])

@step('I have some files in "(.*)" directory')
def have_some_files(step, directory):
    world.directory = os.path.join(world.basedir, directory)
    world.ignores = list()
    clockwork_test = os.path.join(world.directory, u'clockwork_test.mp3')
    world.expected = (version,
        {u'Anthony Burgess': {
            u'1962': {
                u'A Clockwork Orange': {
                    u'01': {
                        u'Sweet Hommie': {
                            u'path': clockwork_test
                            }
                        }
                    }
                }
            }
        },
        {os.path.join(world.directory, u'clockwork_test.mp3'): {
                u'artist': u'Anthony Burgess',
                u'album': u'A Clockwork Orange',
                u'title': u'Sweet Hommie',
                u'date': u'1962',
                u'tracknumber': u'01',
                u'modified': os.stat(clockwork_test).st_mtime
            },
        },
        {},
        {u'Anthony Burgess1962A Clockwork Orange': {
                u'remote': set([]),
                u'digital': True,
                u'analog': False
            },
        },
        [True])

@step('ignore "(.*)" directory')
def ignore_directory(step, ignore):
    world.ignores.append((ignore, False))

@step('I have an empty database')
def have_an_empty_database(step):
    world.database = (version, {}, {}, {}, {}, [False])
    world.db = local.Filesystem(world.directory, world.database, world.ignores)

@step('I scan the directory for files')
def scan_the_directory(step):
    world.db.start()
    world.db.wait()

@step('they should get added to the database')
@step('they should be updated in the database')
def should_get_added(step):
    assert world.database == world.expected

@step('I add some more files to the directory')
def add_some_more_files(step):
    shutil.copy2(os.path.join(world.basedir, u'temp/second_test.flac'),
            os.path.join(world.basedir, u'data'))
    second_test = os.path.join(world.directory, u'second_test.flac')
    __add_to_expected((
        {u'Second': {
            u'0000': {
                u'Test': {
                    u'666': {
                        u'ST': {
                            u'path': second_test
                            }
                        }
                    }
                }
            }
        },
        {os.path.join(world.directory, u'second_test.flac'): {
                u'artist': u'Second',
                u'album': u'Test',
                u'title': u'ST',
                u'date': u'0000',
                u'tracknumber': u'666',
                u'modified': os.stat(second_test).st_mtime
            },
        },
        {u'Second0000Test': {
                u'remote': set([]),
                u'digital': True,
                u'analog': False
            },
        }))

@step('I rename file "(.*)" to "(.*)"')
def rename_file(step, oldname, newname):
    oldpath = os.path.join(world.directory, oldname)
    newpath = os.path.join(world.directory, newname)
    os.rename(oldpath, newpath)
    world.renames.append((newpath, oldpath))
    world.expected[2][newpath] = world.expected[2][oldpath]
    world.expected[2][newpath][u'modified'] = os.stat(newpath).st_mtime
    del world.expected[2][oldpath]
    world.expected[1][u'Anthony Burgess'][u'1962'][u'A Clockwork Orange']\
            [u'01'][u'Sweet Hommie'][u'path'] = newpath

@step('I change (.*) tag for file "(.*)"')
def change_tags_for_file(step, tag, filename):
    oldpath = os.path.join(world.directory, filename)
    if tag == 'artist':
        world.expected[1][u'Changed'] = world.expected[1][u'Second']
        del world.expected[1][u'Second']
        world.expected[2][oldpath][u'artist'] = u'Changed'
        world.expected[4][u'Changed0000Test'] =\
                world.expected[4][u'Second0000Test']
        del world.expected[4][u'Second0000Test']
    elif tag == 'date':
        world.expected[1][u'Changed'][u'1111'] =\
                world.expected[1][u'Changed'][u'0000']
        del world.expected[1][u'Changed'][u'0000']
        world.expected[2][oldpath][u'date'] = u'1111'
        world.expected[4][u'Changed1111Test'] =\
                world.expected[4][u'Changed0000Test']
        del world.expected[4][u'Changed0000Test']
    elif tag == 'album':
        world.expected[1][u'Changed'][u'1111'][u'Changed'] =\
                world.expected[1][u'Changed'][u'1111'][u'Test']
        del world.expected[1][u'Changed'][u'1111'][u'Test']
        world.expected[2][oldpath][u'album'] = u'Changed'
        world.expected[4][u'Changed1111Changed'] =\
                world.expected[4][u'Changed1111Test']
        del world.expected[4][u'Changed1111Test']
    elif tag == 'tracknumber':
        world.expected[1][u'Changed'][u'1111'][u'Changed'][u'777'] =\
                world.expected[1][u'Changed'][u'1111'][u'Changed'][u'666']
        del world.expected[1][u'Changed'][u'1111'][u'Changed'][u'666']
        world.expected[2][oldpath][u'tracknumber'] = u'777'
    elif tag == 'title':
        world.expected[1][u'Changed'][u'1111'][u'Changed'][u'777'][u'Ch'] =\
                world.expected[1][u'Changed']\
                [u'1111'][u'Changed'][u'777'][u'ST']
        del world.expected[1][u'Changed'][u'1111'][u'Changed'][u'777'][u'ST']
        world.expected[2][oldpath][u'title'] = u'Ch'
    else:
        assert False
    newpath = os.path.join(world.basedir,
            u'temp', tag + u'_change_test_.flac')
    oldnewpath = os.path.join(world.basedir,
            u'temp', tag + u'_change_test.flac')
    shutil.copy2(oldpath, newpath)
    shutil.copy2(oldnewpath, oldpath)
    world.exchanges.add(newpath)
    world.expected[2][oldpath][u'modified'] = os.stat(oldpath).st_mtime
