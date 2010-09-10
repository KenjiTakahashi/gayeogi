# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='Fetcher',
        version='0.3',
        description='',
        author='Karol Woźniak',
        author_email='wozniakk@gmail.com',
        url='http://fetcher.sourceforge.net',
        packages=['fetcher','fetcher/interfaces'],
        package_dir={'fetcher':'src/fetcher','fetcher/interfaces':'src/fetcher/interfaces'},
        scripts=['fetcher'],
        requires=['BeautifulSoup(>=2.0)','threadpool','PyQt4']
        )
        
