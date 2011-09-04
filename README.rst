gayeogi is aimed to be fully-featured music management suite, including library collecting, new and missing releases checking, playing, scrobbling, tagging, and so on,
but keep in mind that it's still in beta stage, so some features may be still missing or not fully working.

At the moment, these features are considered "working":

- Library
- Internet DB checking

    - metal-archives.com
    - musicbrainz.org
    - progarchives.com

- Playback

    - last.fm/libre.fm scrobbling

INSTALLATION
============
REQUIRES
--------
    python >= 2.6

    PyQt >= 4.6

    mutagen >= 1.20

    distribute >= 0.6.14 (setup)

    lettuce >= 0.1.31 (test suite)

    phonon >= 4.4 (player)

    pylast >= 0.5.6 (last.fm, libre.fm scrobbling)

    lxml >= 2.3 (metal-archives.com, musicbrainz.org, progarchives.com)

NOTES
*****
- Windows installer provides all that dependencies to you, don't bother getting them separately (unless you want to build from source, of course).
- Versions specified here are "known to work", but it may be possible that and older one will fit too.
- Due to the name change during update to 0.6 you'll have to execute following commands if you want to keep your db and settings: ::

    mkdir ~/.config/gayeogi
    cp ~/.config/fetcher/* ~/.config/gayeogi/
    mv ~/.config/gayeogi/Fetcher.conf ~/.config/gayeogi/gayeogi.conf

LINUX
-----
ARCHLINUX
*********
::

    yaourt -S gayeogi (or any other AUR wrapper)

.DEB/.RPM
*********

There are binary packages (along with custom repositories) for some popular distributions available through `Novell's Open Build Service`_.

.. _Novell's Open Build Service: https://build.opensuse.org/package/show?package=gayeogi&project=home%3AKenjiTakahashi

GENERAL
*******
In package main directory::

    python2 setup.py install

also available in PyPI_::

    pip install gayeogi
    #or
    easy_install gayeogi

.. _PyPI: http://pypi.python.org/pypi/gayeogi/

WINDOWS
-------
You should have no problems with provided installer (just few clicks ;). If you want to build it on your own then... you're on your own.

USAGE
=====
NOTES
-----
- Keep in mind that first time refresh could take quite some time, but then it should be much faster :).

