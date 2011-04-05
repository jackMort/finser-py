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
import sys
import getopt
import marshal

from finser import Finser

options, remainder = getopt.getopt( sys.argv[1:], 'u:p:i:arl', [ 'username=',
                                                                   'password=',
                                                                   'accounts', 'insert=', 
                                                                   'remove', 'last'])
username = ""
password = ""
action = ""
params = {}

for opt, arg in options:
    if opt in ( '-u', '--username' ):
        username = arg

    elif opt in ( '-p', '--password' ):
        password = arg

    elif opt in ( '-a', '--accounts' ):
        action = 'accounts'

    elif opt in ( '-i', '--insert' ):
        action = 'insert'
        params = { 'text': arg }

    elif opt in ( '-r', '--remove' ):
        action = 'remove'

    elif opt in ( '-l', '--last' ):
        action = 'last'

path = os.path.join( os.path.expanduser( "~" ), ".finser-py.cache" )
if username == "" or password == "":
    if os.path.exists( path ):
        f = open( path, 'r' )
        username, password = marshal.loads( f.read() )
        f.close()
else:
    f = open( path, 'w' )
    f.write( marshal.dumps( ( username, password ) ) )
    f.close()

if username and password and action:
    finser = Finser( username, password )
    logged = finser.login()
    if logged:

        if action == 'insert':
            if not finser.insert( params['text'] ):
                print "ERROR: cannot insert text %s" % params['text']

        elif action == "accounts":
            ss = {}
            for account in finser.accounts():
                val = []
                for currency, summary in account.getCurrencySummary():
                    val.append( "%8s %s" % ( summary, currency ) )
                    if not ss.has_key( currency ):
                        ss[currency] = 0
                    ss[currency] += summary
                print "%-50s %s" % ( account.name, ",".join( val ) )
            print "-----"
            for currency, summary in ss.items():
               print "%-50s %s %s" % ( "Summary", summary, currency )

        elif action == "remove":
            before = finser.summary()
            if not finser.remove():
                print "ERROR: cannot remove last item ..."

        elif action == "last":
            for item in finser.get():
                print "%-50s %8s %s" % ( item.text, item.getValue(), item.getCurrency() )

        finser.logout()

    else:
        print "ERROR: Bad username or password"
else:
    print "Username, password and action are required"
