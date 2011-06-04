# This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
# Karol "Kenji Takahashi" Wozniak (C) 2010
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

from setuptools import setup

setup(
        name = u'Fetcher',
        version = u'0.6',
        description = u'A fully-featured music management suite.',
        author = u'Karol "Kenji Takahashi" Wozniak',
        author_email = u'wozniakk@gmail.com',
        license = u'GPL3',
        url = u'http://github.com/KenjiTakahashi/fetcher',
        packages = [
            u'fetcher',
            u'fetcher.interfaces',
            u'fetcher.db',
            u'fetcher.plugins'
            ],
        scripts = [u'scripts/fetcher'],
        install_requires = [
            u'mutagen'
            ],
        extras_require = {
            u'Last.FM': [u'pylast'],
            u'metal-archives.com': [u'lxml']
            },
        classifiers = [f.strip() for f in u"""
        Development Status :: 4 - Beta
        Environment :: Win32 (MS Windows)
        Environment :: X11 Applications :: Qt
        Intended Audience :: End Users/Desktop
        License :: OSI Approved :: GNU General Public License (GPL)
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python :: 2
        Topic :: Multimedia :: Sound/Audio :: Players
        """.splitlines() if f.strip()]
        )
