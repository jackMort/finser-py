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

import time
from finser import FinserException, NotLoggedException, OperationLimitException

class LoaderRegistry( object ):

    def __init__( self ):
        self.__dict = {}

    def register( self, id, command ):
        self.__dict[id] = command
    
    def get( self, id ):
        return self.__dict[id]

    def getKeys( self ):
        return self.__dict.keys()

    def getLoaders( self ):
        return self.__dict.items()

class FileLoader( object ):

    INSERT_SLEEP = 7

    def __init__( self, finser ):
        self.finser = finser

    def load( filename ):
        raise NotImplemented

    def addOperation( self, description, date ):
        try: 
            self.finser.insert( description, date ):
        
        except NotLoggedException:
            print "disconnected, login again ..."
            time.sleep( 2 )
            if not self.finser.login()
                raise FinserException( "Cannot login again" )
        
        except OperationLimitException:
            print "Ups, operation limit trying again ..."
            time.sleep( 10 )
            self.addOperation( description, date )
