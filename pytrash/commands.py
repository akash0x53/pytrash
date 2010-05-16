#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# pytrash, the command line tool for the GNOME Trash
# License: GPLv2, see README and COPYING for more details.
 

import os
import sys
import re
from datetime import datetime,timedelta
from optparse import OptionParser
from pytrash import PATH,VERSION,TrashCan,Trash
from urllib import quote,unquote

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
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',default=False,help='explain what is being done')

    (opts, args) = parser.parse_args()

    trashcan = TrashCan(PATH, opts.dry, opts.verbose)

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

    if opts.delete or opts.regexp or opts.hours:
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
        
def undel():
    parser = OptionParser(usage='%prog [num]',version='%prog: '+VERSION)
    parser.add_option('-d','--dry',action='store_true',dest='dry',default=False,
            help='only shows what items will be trashed')
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',default=False,
            help='explain what is being done')

    (opts, args) = parser.parse_args()

    trashcan = TrashCan(PATH, opts.dry, opts.verbose)
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

