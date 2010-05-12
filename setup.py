#!/usr/bin/env python
# coding:utf-8
#

from distutils.core import setup

setup(
        name='pytrash',
        version='0.3.2',
        url='http://code.google.com/p/pytrash/',
        author='Kei Taneishi',
        author_email='ktaneishi@gmail.com',
        description='The command line tool for the GNOME Trash',
        packages=['pytrash'],
        scripts=['scripts/trash', 'scripts/undel',],
        license='GNU Public License Version 2',
        )
