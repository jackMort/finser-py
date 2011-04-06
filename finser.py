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

import json
import urllib
import urllib2

class Account:

    def __init__( self, name ):
        self.name = name
        self.currencyMap = {}

    def addCurrencySummary( self, currency, plus, minus ):
        self.currencyMap[currency] = { 'p': plus, 'm': minus, 's': plus - minus }

    def getCurrencySummary( self ):
        return [ ( c, dt['s'] ) for c, dt in self.currencyMap.items() ]

class AbstractOperation( object ):
    ADDED      = 'a'
    MOVED      = 'm'
    NOTE       = 'n'
    TRANSFERED = 't'

    def __init__( self, type, time, text ):
        self.type = type
        self.time = time
        self.text = text

    def getValue( self ):
        pass

    def getCurrency( self ):
        pass

    def getDescription( self ):
        return self.text

class AccountOperation( AbstractOperation ):

    def __init__( self, type, time, text, account ):
        super( AccountOperation, self ).__init__( type, time, text )
        
        self.account = account

class AccountValueOperation( AccountOperation ):

    def __init__( self, type, time, text, account, value  ):
        super( AccountValueOperation, self ).__init__( type, time, text, account )
        
        self.value = value
        self.__value, self.__currency = value.split()

    def getValue( self ):
        return self.__value

    def getCurrency( self ):
        return self.__currency

class MoveOperation( AbstractOperation ):

    def __init__( self, type, time, text, value, account_from, account_to  ):
        super( MoveOperation, self ).__init__( type, time, text )
        
        self.value = value
        self.__value, self.__currency = value.split()
        self.account_from = account_from
        self.account_to = account_to

    def getValue( self ):
        return self.__value

    def getCurrency( self ):
        return self.__currency

    def getDescription( self ):
        description = super( MoveOperation, self ).getDescription()
        return "%s > %s %s" % ( self.account_from, self.account_to, description )

class TransferOperation( AccountOperation ):

    def __init__( self, type, time, text, account, value_from, value_to ):
        super( TransferOperation, self ).__init__( type, time, text, account )
        
        self.value_from = value_from
        self.value_to = value_to

operationDict = {
    AbstractOperation.ADDED     : AccountValueOperation,
    AbstractOperation.MOVED     : MoveOperation,
    AbstractOperation.NOTE      : AccountOperation,
    AbstractOperation.TRANSFERED: TransferOperation
}

def getOperationByType( id, **kwargs ):
    if not operationDict.has_key( id ):
        raise AttributeError
    return operationDict[id]( **kwargs )


class Finser:

    SUCCESS_CODE = 200

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

        return self.__isSuccess( code )

    def remove( self ):
        data, code = self.__openUrl( self.URL_PATTERN % "remove" )

        return self.__isSuccess( code )

    def insert( self, text, time=None ):
        params = { 'text': text }
        if time is not None:
            time = time

        data, code = self.__openUrl( self.URL_PATTERN % "insert", params )
        
        return self.__isSuccess( code )

    def accounts( self ):
        data, code = self.__openUrl( self.URL_PATTERN % "accounts" )

        if self.__isSuccess( code ):
            raw = json.loads( data )
            result = []
            for id, dt in raw.items():
                account = Account( dt['name'] )
                for c, s in dt['summary'].items():
                    account.addCurrencySummary( c, float( s['plus'] ), float( s['minus'] ) )
                result.append( account )
            return result
        else:
            return {}

    def get( self, query="!last" ):
        data, code = self.__openUrl( self.URL_PATTERN % "get", { "query": query } )

        if self.__isSuccess( code ):
            raw = json.loads( data )
            result = []
            for id, dt in raw['operations'].items():
                result.append( getOperationByType( dt['type'], **dt ) )
            return result
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

    def __isSuccess( self, code ):
        return code == self.SUCCESS_CODE
