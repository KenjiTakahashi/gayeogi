from lettuce import step, world, after, before
from gayeogi.main import version
from gayeogi.db import local
import os
import shutil

@before.all
def init():
    world.basedir = os.path.dirname(__file__)
    world.renames = list()

@after.all
def deinit(total):
    os.remove(os.path.join(world.basedir, u'data/second_test.flac'))
    for (old, new) in world.renames:
        os.rename(old, new)

#@after.each_step
#def each(step):
#    try:
#        print "db1"
#        for key1, value1 in world.database[1].iteritems():
#            print key1
#            for key2, value2 in value1.iteritems():
#                print key2
#                for key3, value3 in value2.iteritems():
#                    print key3, value3
#        print "db2"
#        for key1, value1 in world.database[2].iteritems():
#            print key1
#            for key2, value2 in value1.iteritems():
#                print key2, value2
#        print "db4"
#        for key1, value1 in world.database[4].iteritems():
#            print key1
#            for key2, value2 in value1.iteritems():
#                print key2, value2
#    except AttributeError:
#        pass
#    try:
#        print "expected"
#        print "db1"
#        for key1, value1 in world.expected[1].iteritems():
#            print key1
#            for key2, value2 in value1.iteritems():
#                print key2
#                for key3, value3 in value2.iteritems():
#                    print key3, value3
#        print "db2"
#        for key1, value1 in world.expected[2].iteritems():
#            print key1
#            for key2, value2 in value1.iteritems():
#                print key2, value2
#        print "db4"
#        for key1, value1 in world.expected[4].iteritems():
#            print key1
#            for key2, value2 in value1.iteritems():
#                print key2, value2
#    except AttributeError:
#        pass

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
    shutil.copy(os.path.join(world.basedir, u'temp/second_test.flac'),
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
