#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# pytrash, the command line tool for the GNOME Trash
# License: GPLv2, see README and COPYING for more details.
# 

import os,sys,shutil
from urllib import quote,unquote
from datetime import datetime,timedelta

VERSION = '0.2'
PATH = '.local/share/Trash'

class TrashCan:
    '''A class of trash can.'''
    def __init__(self, PATH, is_dry):
        '''configuring trash directories.'''
        self.FILES = os.path.join(os.environ['HOME'],PATH,'files')
        self.INFO = os.path.join(os.environ['HOME'],PATH,'info')
        self.__all = sorted([Trash(os.path.join(self.INFO,name)) for name in os.listdir(self.INFO)])
        self.__count = 0
        self.dry = is_dry

    def all(self):
        '''return all trash files.'''
        return self.__all

    def add(self,target):
        '''target is a new trash file.'''
        sub = 2
        name = os.path.basename(target)
        while os.path.exists(os.path.join(self.FILES, name)):
            name = os.path.basename(target) + '.' + str(sub)
            sub += 1

        if self.dry:
            print target, name
        else:
            shutil.move(target, os.path.join(self.FILES, name))
            out = open(os.path.join(self.INFO, name)+'.trashinfo', 'w')
            out.write('[Trash Info]\nPath=%s\nDeletionDate=%s' % (
                 quote(os.path.abspath(target)),
                 datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
                 ))
            out.close()
        self.__count += 1

    def remove(self,trash):
        name = os.path.basename(trash.path)
        if os.path.exists(name):
            print 'cannot overwrite "%s"' % name
        else:
            if not self.dry:
                shutil.move(os.path.join(self.FILES, trash.file), unquote(name))
                os.remove(os.path.join(self.INFO, trash.infofile))

    def delete(self, trash):
        if os.path.isfile(os.path.join(self.FILES, trash.file)) and not self.dry:
          os.remove(os.path.join(self.FILES, trash.file))
          os.remove(os.path.join(self.INFO, trash.infofile))
        elif os.path.isdir(os.path.join(self.FILES, trash.file)) and not self.dry:
          shutil.rmtree(os.path.join(self.FILES, trash.file))
          os.remove(os.path.join(self.INFO, trash.infofile))

    def __len__(self):
        return self.__count

class Trash:
    '''A class of trash file.'''
    def __init__(self,infofile):
        '''load a trash information file.'''
        from ConfigParser import ConfigParser
        c = ConfigParser()
        c.read(infofile)
        self.path = c.get('Trash Info', 'Path')
        self.date = c.get('Trash Info', 'DeletionDate')
        self.infofile = os.path.basename(infofile)
        self.file = self.infofile[0:-10]

    def __cmp__(self,other):
        return cmp(self.date, other.date)

    def __str__(self):
        return '%s\t%s' % (self.date, unquote(self.path))

