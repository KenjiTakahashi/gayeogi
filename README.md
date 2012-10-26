**gayeogi** is aimed to be fully-featured music management suite, including library collecting, new and missing releases checking, playing, scrobbling, tagging, and so on,
but keep in mind that it's still in beta stage, so some features may be still missing or not fully working.

At the moment, these features are considered *working*:

- Library
- Internet DB checking

    - metal-archives.com
    - musicbrainz.org
    - progarchives.com

- Playback

    - last.fm/libre.fm scrobbling
    - MPRIS (2.1 with partial TrackList support, not available on Windows)

# INSTALLATION
## REQUIRES
```
python >= 2.6
PyQt >= 4.6
mutagen >= 1.20
distribute >= 0.6.14 (setup)
python-nose >= 1.2.1 (test suite)
phonon >= 4.4 (player)
pylast >= 0.5.6 (last.fm, libre.fm scrobbling)
lxml >= 2.3 (metal-archives.com, musicbrainz.org, progarchives.com)
```

## NOTES
- Windows installer provides all that dependencies to you, don't bother getting them separately (unless you want to build from source, of course).
- Versions specified here are "known to work", but it may be possible that and older one will fit too.
- Due to the name change during update to 0.6 you'll have to execute following commands if you want to keep your db and settings:
```sh
mkdir ~/.config/gayeogi
cp ~/.config/fetcher/* ~/.config/gayeogi/
mv ~/.config/gayeogi/Fetcher.conf ~/.config/gayeogi/gayeogi.conf
```

## LINUX
### ARCHLINUX

There is a PKGBUILD available in [AUR][aur].

[aur]: https://aur.archlinux.org/packages.php?ID=50500

### .DEB/.RPM

There are binary packages (along with custom repositories) for some popular distributions available through [Novell's Open Build Service][novell].

[novell]: https://build.opensuse.org/package/show?package=gayeogi&project=home%3AKenjiTakahashi

### GENTOO

There is an ebuild available in [overlays][overlays] thanks to <someone> (if you're the one, feel free to send me a message).

[overlays]: http://gpo.zugaina.org/media-sound/gayeogi

### GENERAL

Through [PyPI][pypi]
```sh
$ pip install gayeogi
```
or directly from source
```sh
$ python2 setup.py install
```

[pypi]: http://pypi.python.org/pypi/gayeogi/

### WINDOWS
There is a binary installer provided in the [downloads][downloads] section.

[downloads]: https://github.com/KenjiTakahashi/gayeogi/downloads
