#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# pytrash, the command line tool for the GNOME Trash
# License: GPLv2, see README and COPYING for more details.
# 

import os
import sys
import shutil
import re
from urllib import quote,unquote
from datetime import datetime,timedelta
from optparse import OptionParser
from ConfigParser import ConfigParser

VERSION = '0.3.3'
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

def trash():
    parser = OptionParser(usage='%prog [options] [files]',version='%prog: '+VERSION)
    parser.add_option('-d','--dry',action='store_true',dest='dry',default=False,help='only shows what items will be trashed')
    parser.add_option('-f','--force',action='store_true',dest='force',default=False,help='remove locked items')
    parser.add_option('-r','--recursive',action='store_true',dest='recursive',default=False,help='remove directories recursively')
    parser.add_option('-e','--regexp',action='store',dest='regexp',default=None,
            help='regular expression to select trashes (use with -D)')
    parser.add_option('-H','--hours',action='store',dest='hours',type=int,default=None,
            help='select trashes till this hours (use with -D)')
    parser.add_option('-D','--delete',action='store_true',dest='delete',default=False,help='delete trashes')
    parser.add_option('-U','--undelete',action='store_true',dest='undelete',default=False,help='undelete specified trashes')
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',default=False,help='explain what is being done')

    (opts, args) = parser.parse_args()

    trashcan = TrashCan(PATH, opts.dry, opts.verbose)

    if opts.undelete:
        trashes = trashcan.all()

        if trashes == []:
            sys.stderr.write('No trashes are in the trashcan.\n')
            sys.exit(1)

        if args == []:
            '''if no args specified, select the last one.'''
            args = [len(trashes)-1]

        args = sorted(map(int,args))
        for arg in args:
            if arg in xrange(len(trashes)):
                trashcan.undelete(trashes[arg])
            else:
                sys.stderr.write('Invalid number was specified.: %d\n' % arg)

    if opts.regexp:
        for trash in trashcan.all():
            if re.search(opts.regexp, unquote(trash.origpath)):
                if opts.delete:
                    trashcan.delete(trash)
                    if opts.verbose:
                        print 'remove "%s"' % trash
                else:
                    print trash

    if opts.hours:
        hourdelta = timedelta(0,opts.hours*60*60)
        threshold = datetime.today() - hourdelta

        for trash in trashcan.all():
            if trash.date < threshold.strftime('%Y-%m-%dT%H:%M:%S'):
                if opts.delete:
                    trashcan.delete(trash)
                    if opts.verbose:
                        print 'remove "%s"' % trash
                else:
                    print trash

    if opts.undelete or opts.delete or opts.regexp or opts.hours:
        sys.exit(0)

    if args == []:
        '''show a list of trashes.'''
        trashes = trashcan.all()
        for order,trash in zip(xrange(len(trashes)), trashes):
            print order,trash
        sys.exit(0)

    for target in args:
        target = target.rstrip('/')

        if not os.path.exists(target):
            print '%s: No such file or directory.\n' % target
        elif not os.access(target, os.W_OK) and not opts.force:
            print '%s: is write-protected. Use -f option.\n' % target
        elif os.path.isdir(target) and not opts.recursive:
            print '%s: Cannot remove directory. Use -r option.\n' % target
        else:
            trashcan.add(target) 

    if opts.verbose:
        print '%d files and directories are trashed.' % len(trashcan)
