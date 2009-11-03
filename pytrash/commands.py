#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# pytrash, the command line tool for the GNOME Trash
# License: GPLv2, see README and COPYING for more details.
# 

import os
import sys
from datetime import datetime,timedelta
from optparse import OptionParser
from pytrash import PATH, VERSION, TrashCan, Trash

def trash():
    parser = OptionParser(usage='%prog [files]')
    parser.add_option('-d','--dry',action='store_true',dest='dry',default=False,help='only shows what items will be trashed')
    parser.add_option('-f','--force',action='store_true',dest='force',default=False,help='remove locked items')
    parser.add_option('-r','--recursive',action='store_true',dest='recursive',default=False,help='remove directories recursively')
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',default=False,help='explain what is being done')
    parser.add_option('-V','--version',action='store_true',dest='version',default=False,help='show version')

    (opts, args) = parser.parse_args()

    if opts.version:
        print 'Trash script; Version %s' % VERSION
        sys.exit(1)

    trashcan = TrashCan(PATH, opts.dry)

    if args == []:
        for i,trash in zip(range(len(trashcan.all())), trashcan.all()):
            print i, trash
        print '\nTo empty these trashes, use "emptytrash"'
        sys.exit(1)

    for target in args:
        target = target.rstrip('/')

        if not os.path.exists(target):
            print '%s: No such file or directory.' % target
        elif not os.access(target, os.W_OK) and not opts.force:
            print '%s: is write-protected. Use -f option.\n' % target
        elif os.path.isdir(target) and not opts.recursive:
            print '%s: Cannot remove directory. Use -r option.\n' % target
        else:
            trashcan.add(target) 

    if opts.verbose:
        print '%d files and directories' % len(trashcan),
        print 'are trashed'
        
def undel():
    parser = OptionParser(usage='%prog [num]')
    parser.add_option('-d','--dry',action='store_true',dest='dry',default=False,help='only shows what items will be trashed')
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',default=False,help='explain what is being done')
    parser.add_option('-V','--version',action='store_true',dest='version',default=False,help='show version')

    (opts, args) = parser.parse_args()

    if opts.version:
        print 'Trash script; Version %s' % VERSION
        sys.exit(1)

    trashcan = TrashCan(PATH, opts.dry)
    trashes = trashcan.all()

    if trashes == []:
        print 'No dust is in the trash.'
        sys.exit(1)

    if args == []:
        args = [len(trashes)-1]
    for arg in args:
        arg = int(arg)
        if arg in range(len(trashes)):
            trashcan.remove(trashes[arg])
            if opts.verbose:
                print 'undelete "%s".' % trashes[arg]
        else:
            print 'Invalid number of trash.: %d' % arg

def empty():
    parser = OptionParser(usage='%prog [72]')
    parser.add_option('-d','--dry',action='store_true',dest='dry',default=False,help='only shows what items will be trashed')
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',default=False,help='explain what is being done')
    parser.add_option('-V','--version',action='store_true',dest='version',default=False,help='show version')

    (opts, args) = parser.parse_args()

    if opts.version:
        print 'Trash script; Version %s' % VERSION
        sys.exit(1)

    if args == []:
        HOUR = 24*3
    else:
        HOUR = int(args[0])

    hourdelta = timedelta(0,HOUR*60*60)
    threshold = datetime.today() - hourdelta

    trashcan = TrashCan(PATH, opts.dry)
    trashes = trashcan.all()

    # compare the time
    trashes = [trash for trash in trashes if trash.date < threshold.strftime('%Y-%m-%dT%H:%M:%S')]

    for trash in trashes:
        trashcan.delete(trash)
        if opts.verbose:
            print 'remove "%s"' % trash
