#!/usr/bin/env python

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
