#!/usr/bin/env python

# Copyright (C) 2011  lech.twarog@gmail.com
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import getpass
import marshal

from optparse import OptionParser, OptionGroup

from finser import Finser
from importer import registry

def login():
    username = raw_input( "Username [%s]: " % getpass.getuser() )
    if not username:
        username = getpass.getuser()

    password = getpass.getpass()
    while not password:
        password = getpass.getpass()

    return username, password

parser = OptionParser( usage="usage: %prog [OPTIONS]" )

parser.add_option( "-g", "--get", dest="get", help="list last operations for given query" )
parser.add_option( "-i", "--insert", dest="insert", help="insert given operation" )

parser.add_option( "-r", "--remove", dest="remove", action="store_true", help="remove last operation" )
parser.add_option( "-l", "--last", dest="last", action="store_true", help="display last operations" )
parser.add_option( "-a", "--accounts", dest="accounts", action="store_true", help="display accounts info" )
parser.add_option( "-f", "--force-login", dest="force_login", action="store_true", help="force restore auth info" )

group = OptionGroup( parser, "Import Options" )
group.add_option( "--get-loaders", action="store_true", dest="get_loaders", help="list available loaders" )
group.add_option( "--import", dest="load", nargs=2, help="import file with specified loader" )

parser.add_option_group( group )

( options, args ) = parser.parse_args()

path = os.path.join( os.path.expanduser( "~" ), ".finser-py.cache" )
if os.path.exists( path ) and not options.force_login:
    f = open( path, 'r' )
    username, password = marshal.loads( f.read() )
    f.close()
else:
    username, password = login()
        
    f = open( path, 'w' )
    f.write( marshal.dumps( ( username, password ) ) )
    f.close()

finser = Finser( username, password )
logged = finser.login()
if not logged:
    print " \033[1m\033[92mFAILED TO LOGIN!\33[0m"
    sys.exit( 1 )
    
if options.insert:
    print " ------------------------------"
    print " \033[1mInserting new operation\033[0m"
    print " ------------------------------"
    
    print "\n %s\n" % options.insert

    if finser.insert( options.insert ):
        print " \033[1m\033[92mSUCCESFULLY ADDED!\033[0m"
    else: print " \033[1m\033[92mFAILED TO ADD!\33[0m"
    
    print " ------------------------------"

elif options.accounts:
    print " ------------------------------"
    print " \033[1mAccount information\033[0m"
    print " ------------------------------"

    ss = {}
    for account in finser.accounts():
        val = []
        for currency, summary in account.getCurrencySummary():
            val.append( "%s%10s %s\033[0m" % ( "\033[92m" if summary > 0 else "\033[91m", summary, currency ) )
            if not ss.has_key( currency ):
                ss[currency] = 0
            ss[currency] += summary
        print " \033[94m%-50s\033[0m %s" % ( account.name, ",".join( val ) )
    print " -----"
    for currency, summary in ss.items():
       print " \033[1m\033[94m%-50s\033[0m \033[1m%s%10s %s\033[0m" % ( "Summary", "\033[92m" if summary > 0 else "\033[91m", summary, currency )
    
    print " ------------------------------"

elif options.remove:
    print " ------------------------------"
    print " \033[1mRemoving last item\033[0m"
    print " ------------------------------"

    if finser.remove():
       print " \033[1m\033[92mSUCCESFULLY REMOVED!\033[0m"
    else: print " \033[1m\033[92mFAILED TO REMOVE!\33[0m"
    
    print " ------------------------------"

elif options.last or options.get:
    if options.get:
        query = options.get
    else: 
        query = "!last"

    print " ------------------------------"
    print " \033[1mLast operations %s \033[0m" % query
    print " ------------------------------"

    prev_day = None
    items = finser.get( query )
    if len( items ) == 0:
        print " Nothing to display"

    ss = {}
    for item in items:
        date = item.getDateTime()
        day = date.strftime( "%Y-%d-%m" )
        time = date.strftime( "%H:%I:%S" )

        if prev_day <> day:
            print "%s \033[1m\033[94m%s\033[0m" % ( "" if prev_day is None else "\n", day )
        
        description = item.getDescription()
        description = re.sub( r'#(?P<tag>\w+)', '\033[1m\033[95m#\g<tag>\033[0m', description )
        description = re.sub( r'\$(?P<account>\w+)', '\033[1m\033[96m$\g<account>\033[0m', description )

        value = item.getValue()
        currency = item.getCurrency()
        if not ss.has_key( currency ):
            ss[currency] = 0
        ss[currency] += value
        
        print "   \033[94m%s\033[0m %s%10s %s\033[0m %s" % ( time, "\033[92m" if value > 0 else "\033[91m", value, currency, description  )
        prev_day = day
    
    if len ( ss ):
        print "\n -----"
        for currency, summary in ss.items():
           print "     \033[1m\033[94m=\033[0m      \033[1m%s%10s %s\033[0m" % ( "\033[92m" if summary > 0 else "\033[91m", summary, currency )

    print " ------------------------------"

elif options.get_loaders:
    print " ------------------------------"
    print " \033[1m Available loaders \033[0m"
    print " ------------------------------"
    
    for key, value in registry.getLoaders():
        print " \033[1m%s\033[0m" % key

    print " ------------------------------"

elif options.load:
    loader, filename = options.load
    available_loaders = registry.getKeys()

    if not loader in available_loaders:
        print "loader %s not found, use on of this: %s" % ( loader, ', '.join( available_loaders ) )
        sys.exit( 1 )

    if not os.path.exists( filename ):
        print "file '%s' not exists use another" % filename
        sys.exit( 1 )

    print " ------------------------------"
    print " \033[1m Loading from %s \033[0m" % loader
    print " ------------------------------"
    
    cls = registry.get( loader )
    loader = cls( finser )
    loader.load( filename )

    print " ------------------------------"


finser.logout()
