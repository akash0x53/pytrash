#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# pytrash, the command line tool for the GNOME Trash
# License: GPLv2, see README and COPYING for more details.
# 

import os
import sys
import shutil
from urllib import quote,unquote
from datetime import datetime,timedelta
from ConfigParser import ConfigParser

VERSION = '0.3.2'
PATH = '.local/share/Trash'
HOME = os.environ['HOME']
TRASH = os.path.join(HOME,PATH)
POSTFIX = '.trashinfo'

class TrashCan:
    '''Class of trash can.'''
    def __init__(self, PATH, dry, verbose):
        '''initial settings.'''
        self.FILE = os.path.join(TRASH,'files')
        self.INFO = os.path.join(TRASH,'info')
        self.count = 0 # a number of trashed targets.
        self.dry = dry
        self.verbose = verbose
        self.__all__ = sorted([Trash(name) for name in os.listdir(self.INFO)])

    def __len__(self):
        return self.count

    def all(self):
        '''return all trash files.'''
        return self.__all__

    def add(self,target):
        '''move a target file into TrashCan.'''
        sub = 0 # subscription number
        name = os.path.basename(target)
        while os.path.exists(os.path.join(self.FILE, name)):
            name = '%s.%d' % (os.path.basename(target),sub)
            sub += 1

        if self.dry:
            print target,name
        else:
            shutil.move(target, os.path.join(self.FILE, name))
            out = open(os.path.join(self.INFO, name)+POSTFIX, 'w')
            out.write('[Trash Info]\nPath=%s\nDeletionDate=%s' % (
                 quote(os.path.abspath(target)),
                 datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
                 ))
            out.close()
        self.count += 1

    def undelete(self,trash):
        '''undelete trash from TrashCan.'''
        name = unquote(os.path.basename(trash.origpath))
        if os.path.exists(name):
            '''if the same name file exists.'''
            sys.stderr.write('cannot overwrite "%s"\n' % name)
        else:
            if not self.dry:
                shutil.move(trash.filepath, name)
                os.remove(trash.infopath)
            if self.verbose:
                sys.stderr.write('"%s" undeleted.\n' % trash)

    def delete(self,trash):
        '''delete trashes.'''
        if os.path.isfile(trash.filepath) or os.path.islink(trash.filepath):
            if not self.dry:
                os.remove(trash.filepath)
                os.remove(trash.infopath)
            if self.verbose:
                sys.stderr.write('"%s" removed.\n' % trash)
        elif os.path.isdir(trash.filepath):
            if not self.dry:
                shutil.rmtree(trash.filepath)
                os.remove(trash.infopath)
            if self.verbose:
                sys.stderr.write('"%s" removed.\n' % trash)

class Trash:
    '''Class of trash file.'''
    def __init__(self,info):
        '''load a trash information file.'''
        self.INFO = os.path.join(HOME,PATH,'info')
        self.FILE = os.path.join(HOME,PATH,'files')
        c = ConfigParser()
        c.read(os.path.join(self.INFO,info))
        self.origpath = c.get('Trash Info', 'Path') # original path
        self.date = c.get('Trash Info', 'DeletionDate')
        self.file = info[0:-len(POSTFIX)] # filename
        self.info = info # info filename
        self.filepath = os.path.join(self.FILE, self.file)
        self.infopath = os.path.join(self.INFO, self.info)

    def __cmp__(self,other):
        return cmp(self.date, other.date)

    def __str__(self):
        return '%s\t%s' % (self.date, unquote(self.origpath))

