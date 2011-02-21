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

from distutils.core import setup
from sys import platform
if platform=='win32':
    import py2exe

setup(
        name='Fetcher',
        version='0.5',
        description='',
        author='Karol "Kenji Takahashi" Wozniak',
        author_email='wozniakk@gmail.com',
        url='http://github.com/KenjiTakahashi/fetcher',
        packages = [
            'fetcher',
            'fetcher/interfaces',
            'fetcher/db',
            'fetcher/plugins'
            ],
        package_dir={
            'fetcher': 'src/fetcher',
            'fetcher/interfaces': 'src/fetcher/interfaces',
            'fetcher/db': 'src/fetcher/db',
            'fetcher/plugins': 'src/fetcher/plugins'
            },
        scripts=['fetcher'],
        requires = ['BeautifulSoup(>=3.0)', 'PyQt4', 'mutagen'],
        windows=['fetcher'],
        options={'py2exe':{'includes':['sip']}}
        )
        
