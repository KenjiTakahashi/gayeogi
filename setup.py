# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
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

from setuptools import setup

setup(
    name = 'gayeogi',
    version = '0.6.3',
    description = 'A fully-featured music management suite.',
    long_description = open('README.rst').read(),
    author = 'Karol "Kenji Takahashi" Woźniak',
    author_email = 'wozniakk@gmail.com',
    license = 'GPL3',
    url = 'http://github.com/KenjiTakahashi/gayeogi',
    packages = [
        'gayeogi',
        'gayeogi.interfaces',
        'gayeogi.db',
        'gayeogi.db.bees',
        'gayeogi.plugins'
    ],
    package_data = {
        '': ['langs/*.qm', '*/*.rst']
    },
    scripts = ['scripts/gayeogi'],
    install_requires = [
        'mutagen'
    ],
    extras_require = {
        'Last.FM': ['pylast'],
        'metal-archives.com': ['lxml'],
        'musicbrainz.org': ['lxml'],
        'progarchives.com': ['lxml']
    },
    classifiers = [f.strip() for f in """
    Development Status :: 4 - Beta
    Environment :: Win32 (MS Windows)
    Environment :: X11 Applications :: Qt
    Intended Audience :: End Users/Desktop
    License :: OSI Approved :: GNU General Public License (GPL)
    Natural Language :: English
    Natural Language :: Polish
    Operating System :: OS Independent
    Programming Language :: Python :: 2
    Topic :: Multimedia :: Sound/Audio :: Players
    """.splitlines() if f.strip()]
)
