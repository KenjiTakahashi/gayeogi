# -*- coding: utf-8 -*-

from distutils.core import setup
from sys import platform
if platform=='win32':
    import py2exe

setup(name='Fetcher',
        version='0.4',
        description='',
        author='Karol "Kenji Takahashi" Woźniak',
        author_email='wozniakk@gmail.com',
        url='http://github.com/KenjiTakahashi/fetcher',
        packages=['fetcher', 'fetcher/interfaces', 'fetcher/db'],
        package_dir={
            'fetcher': 'src/fetcher',
            'fetcher/interfaces': 'src/fetcher/interfaces',
            'fetcher/db': 'src/fetcher/db'
            },
        scripts=['fetcher'],
        requires=['BeautifulSoup(>=3.0)', 'threadpool', 'PyQt4', 'mutagen'],
        windows=['fetcher'],
        options={'py2exe':{'includes':['sip']}}
        )
        
