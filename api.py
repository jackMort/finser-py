#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib, urllib2, socket, json

class Finser:

    URL_PATTERN = "http://api.finser.pl/%s/"

    DEFAULT_HEADERS = [
        ( 'User-Agent', 'finser-py' ),
        ( 'Accept', 'application/json, text/javascript, */*' ),
        ( 'X-Finser-API', '0.5' )
    ]

    def __init__( self, username, password ):
        self.username = username
        self.password = password

        self.opener = None

    def login( self ):
        data, code = self.__openUrl( self.URL_PATTERN % "login", { "username": self.username, 
                                                     "password": self.password })
        return code == 200

    def logout( self ):
        data, code = self.__openUrl( self.URL_PATTERN % "logout" )

        return code == 200

    def remove( self ):
        data, code = self.__openUrl( self.URL_PATTERN % "remove" )

        return code == 200

    def insert( self, text, time=None ):
        params = { 'text': text }
        if time is not None:
            time = time

        data, code = self.__openUrl( self.URL_PATTERN % "insert", params )
        
        return code == 200

    def accounts( self ):
        data, code = self.__openUrl( self.URL_PATTERN % "accounts" )

        if code == 200:
            return json.loads( data )
        else:
            return {}

    def get( self, query="!last" ):
        data, code = self.__openUrl( self.URL_PATTERN % "get", { "query": query } )

        if code == 200:
            return json.loads( data )
        else:
            return {}

    def summary( self ):
        data = self.accounts()
        summary = 0
        for k, v in data.items():
            for t, s in v["summary"].items():
                summary += float( s['plus'] ) - float( s['minus'] )
        return summary

    def __openUrl( self, url, params=None ):
        data = urllib.urlencode( params ) if params else None

        if not self.opener:
            self.opener = urllib2.build_opener( urllib2.HTTPCookieProcessor() )
            self.opener.addheaders = self.DEFAULT_HEADERS
            urllib2.install_opener( self.opener )

        try:
            response = self.opener.open( url, data )
            return ( response.read(), response.code )
        except urllib2.URLError, e:
            return ( e.read(), e.code )


if __name__ == "__main__":
    
    import getopt, sys, marshal, os

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
                if params.has_key( 'text' ):
                    before = finser.summary()
                    if finser.insert( params['text'] ):
                        print "Bilance before: %s, after insert: %s" % ( before, finser.summary() )
                    else:
                        print "ERROR: cannot insert text %s" % params['text']
                else:
                    print "nothing to insert !"

            elif action == "accounts":
                data = finser.accounts()
                ss = 0
                for k, v in data.items():
                    val = []
                    for t, s in v["summary"].items():
                        bill = float( s['plus'] ) - float( s['minus'] )
                        val.append( "%8s %s" % ( bill, t ) )
                        ss += bill
                    
                    print "%-50s %s" % ( v['name'], ",".join( val ) )
                print "-----"
                print "%-50s %s PLN" % ( "Summary", ss )

            elif action == "remove":
                before = finser.summary()
                if finser.remove():
                    print "Bilance before: %s, after insert: %s" % ( before, finser.summary() )
                else:
                    print "ERROR: cannot remove last item ..."

            elif action == "last":
                data = finser.get()
                for k, o in data['operations'].items():
                    v, vv = o['value'].split()
                    print "%-50s %8s %s" % ( o['text'], v, vv )

            finser.logout()
        else:
            print "Ups not logged ..."
    else:
        print "username, password and action are required", username, password, action
