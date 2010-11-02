# -*- coding: utf-8 -*-

from distutils.core import setup
from sys import platform
if platform=='win32':
    import py2exe

setup(name='Fetcher',
        version='0.4',
        description='',
        author='Karol Woźniak',
        author_email='wozniakk@gmail.com',
        url='http://fetcher.sourceforge.net',
        packages=['fetcher','fetcher/interfaces'],
        package_dir={'fetcher':'src/fetcher','fetcher/interfaces':'src/fetcher/interfaces'},
        scripts=['fetcher'],
        requires=['BeautifulSoup(>=2.0)','threadpool','PyQt4'],
        windows=['fetcher'],
        options={'py2exe':{'includes':['sip']}}
        )
        
