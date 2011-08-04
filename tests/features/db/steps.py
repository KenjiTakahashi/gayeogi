from lettuce import step, world, after
from gayeogi.main import version
from gayeogi.db import local
from os import stat, path

@step('I have an empty database')
def have_an_empty_database(step):
    world.database = (version, {}, {}, {}, {}, [False])

@step('I have some files in "(.*)" directory')
def have_some_files(step, directory):
    world.directory = path.join(path.dirname(__file__), directory)
    world.ignores = list()

@step('ignore "(.*)" directory')
def ignore_directory(step, ignore):
    world.ignores.append((ignore, False))

@step('I scan the directory for files')
def scan_the_directory(step):
    db = local.Filesystem(world.directory, world.database, world.ignores)
    db.start()
    db.wait()

@step('they should get added to the database')
def should_get_added(step):
    clockwork_test = path.join(world.directory, u'clockwork_test.mp3')
    assert world.database == (version,
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
        {path.join(world.directory, u'clockwork_test.mp3'): {
                u'artist': u'Anthony Burgess',
                u'album': u'A Clockwork Orange',
                u'title': u'Sweet Hommie',
                u'date': u'1962',
                u'tracknumber': u'01',
                u'modified': stat(clockwork_test).st_mtime
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
