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
import getopt
import getpass
import marshal

from finser import Finser

USAGE = """   
 finser-client.py [OPTIONS] ...

 -l --last          display last operations
 -a --accounts        display accounts info
 -r --remove          remove last operation
 -i --insert TEXT    insert given operation
 -g --get QUERY    list last operations for
                                given query
    --clear-cache    clear cached auth info
    --no-cache         dont store auth info
    --help                  print this help

  Reports bugs to:    lech.twarog@gmail.com
"""

def usage():
   print USAGE

try:
    options, remainder = getopt.getopt( sys.argv[1:], 'i:g:arl', [ 'accounts', 'insert=', 'get=', 
                                                                 'remove', 'last', 'no-cache', 'clear-cache', 'help' ])
except getopt.GetoptError, e:
    usage()
    sys.exit( -1 )

action = ""
params = {}
noCache = False
clearCache = False

for opt, arg in options:
    
    if opt == '--help' :
        usage()
        sys.exit( 0 )

    elif opt in ( '-a', '--accounts' ):
        action = 'accounts'

    elif opt in ( '-i', '--insert' ):
        action = 'insert'
        params = { 'text': arg }

    elif opt in ( '-r', '--remove' ):
        action = 'remove'

    elif opt in ( '-l', '--last' ):
        action = 'last'

    elif opt in ( '-g', '--get' ):
        action = 'get'
        params = { 'query': arg }

    elif opt in ( '--no-cache' ):
        noCache = True
    
    elif opt in ( '--clear-cache' ):
        clearCache = True

def login():
    username = raw_input( "Username [%s]: " % getpass.getuser() )
    if not username:
        username = getpass.getuser()

    password = getpass.getpass()
    while not password:
        password = getpass.getpass()

    return username, password

if noCache:
    username, password = login()

else:
    path = os.path.join( os.path.expanduser( "~" ), ".finser-py.cache" )
    if os.path.exists( path ) and not clearCache:
        f = open( path, 'r' )
        username, password = marshal.loads( f.read() )
        f.close()
    else:
        username, password = login()
        
        f = open( path, 'w' )
        f.write( marshal.dumps( ( username, password ) ) )
        f.close()

if action:
    finser = Finser( username, password )
    logged = finser.login()
    if logged:

        if action == 'insert':
            print " ------------------------------"
            print " \033[1mInserting new operation\033[0m"
            print " ------------------------------"
            
            print " %s" % params['text']

            if finser.insert( params['text'] ):
                print " SUCCESFULLY !"
            else: print " ERROR: cannot insert ..."
            
            print " ------------------------------"

        elif action == "accounts":
            print " ------------------------------"
            print " \033[1mAccount information\033[0m"
            print " ------------------------------"

            ss = {}
            for account in finser.accounts():
                val = []
                for currency, summary in account.getCurrencySummary():
                    val.append( "%8s %s" % ( summary, currency ) )
                    if not ss.has_key( currency ):
                        ss[currency] = 0
                    ss[currency] += summary
                print " %-50s \033[1m%s\033[0m" % ( account.name, ",".join( val ) )
            print " -----"
            for currency, summary in ss.items():
               print " %-50s  \033[1m%s %s\033[0m" % ( "Summary", summary, currency )
            
            print " ------------------------------"

        elif action == "remove":
            print " ------------------------------"
            print " \033[1mRemoving last item\033[0m"
            print " ------------------------------"

            before = finser.summary()
            if finser.remove():
                print " SUCCESFULLY !"
            else: print " ERROR: cannot remove ..."
            
            print " ------------------------------"

        elif action in ( "last", "get" ):
            if action == "get":
                query = params['query']
            else: 
                query = "!last"

            print " ------------------------------"
            print " \033[1mLast operations %s \033[0m" % query
            print " ------------------------------"

            prev_day = None
            for item in finser.get( query ):
                date = item.getDateTime()
                day = date.strftime( "%Y-%d-%m" )
                time = date.strftime( "%H:%I:%S" )

                if prev_day <> day:
                    print "%s \033[1m\033[94m%s\033[0m" % ( "" if prev_day is None else "\n", day )
                
                description = item.getDescription()
                description = re.sub( r'#(?P<tag>\w+)', '\033[1m\033[95m#\g<tag>\033[0m', description )
                description = re.sub( r'\$(?P<account>\w+)', '\033[1m\033[96m#\g<account>\033[0m', description )

                value = item.getValue()
                
                print "   \033[94m%s\033[0m \033[1m%s%10s %s\033[0m %s" % ( time, "\033[92m" if value > 0 else "\033[91m", value, item.getCurrency(), description  )
                prev_day = day
            
            print " ------------------------------"

        finser.logout()

    else:
        print "ERROR: Bad username or password"
else:
    usage()
