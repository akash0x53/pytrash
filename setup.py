#!/usr/bin/env python
# coding:utf-8
from distutils.core import setup

setup(
        name='pytrash',
        version='0.3.3',
        url='http://code.google.com/p/pytrash/',
        author='Kei Taneishi',
        author_email='ktaneishi@gmail.com',
        description='The command line interface for the gnome trash can',
        #packages=['pytrash'],
        py_modules=['pytrash',],
        scripts=['scripts/trash',],
        license='GNU Public License Version 3',
        )
