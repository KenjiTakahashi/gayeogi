Fetcher is aimed to be fully-featured music management suite, including library collecting, new and missing releases checking, playing, scrobbling, tagging, converting and so on,
but keep in mind that it's still in beta stage, so some features may be still missing or not fully working.

At the moment, these features are considered "working":

- Library
- Internet DB checking

  - metal-archives
  - discogs (see usage notes)

- Playback

  - last.fm/libre.fm scrobbling

INSTALLATION
============
REQUIRES
--------
MAIN
****
    python >= 2.6

    PyQt >= 4.6

    BeautifulSoup >= 3.0

    mutagen >= 1.20

    distribute >= 0.6.14 (setup only)
PLAYER
******
    phonon >= 4.4
LAST.FM/LIBRE.FM
****************
    pylast >= 0.5.6
NOTES
*****
- Windows installer provides all that dependencies to you, don't bother getting them separately (unless you want to build from source, of course).
- Versions specified here are "known to work", but it may be possible that and older one will fit too.
LINUX
-----
ARCHLINUX
*********
::

    yaourt -S fetcher (or any other AUR wrapper)

GENERAL
*******
In package main directory::

    python2 setup.py install

WINDOWS
-------
You should have no problems with provided installer (just few clicks ;). If you want to build it on your own then... you're on your own.

USAGE
=====
NOTES
-----
- Keep in mind that first time refresh could take quite some time, but then it should be much faster :).
- Discogs is a mess, use at your own risk (Note: It seems they're writing new API, maybe i'll re-visit it in some time).
