#!/usr/bin/env python
#-*- coding: utf-8 -*-

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

import re
import sys
import time, calendar
import xml.dom.minidom
from datetime import datetime
from base import FileLoader

class IPKOLoader( FileLoader ):
    
    TAGS_MAP = {
        "Wypłata gotówkowa w kasie": "$bank>$portfel",
        "Wypłata gotówkowa z kasy": "$bank>$portfel",
        "Wypłata z bankomatu": "$bank>$portfel",
        "Opłata za użytkowanie karty": "#opłata_bankowa",
        "Opłata": "#opłata_bankowa",
        "Naliczenie odsetek": "#opłata_bankowa #odsetki",
        "Prowizja": "#opłata_bankowa #prowizja",
    }

    DESCRIPTION_RE = {
        r'.*Lokalizacja: Kraj: (?P<country>.*)Miasto: (?P<city>.*) Adres: (?P<address>.*) Data i czas operacji:.*': 'Wypłata z bankomatu, \g<country> \g<city> \g<address>',
        r'Nr rach\..* Dane adr. rach. przeciwst\.:(?P<name>.*) Tytuł:(?P<title>.*)': '\g<name>, \g<title>',
        r'Dane adr\. rach\. przeciwst\.:(?P<title>.*)': '\g<title>',
        r'Tytuł:(?P<title>.*)': '\g<title>',
    }

    def __init__( self, finser ):
        self.finser = finser

    def load( self, filename ):
        dom = xml.dom.minidom.parseString( open( filename, 'r' ).read().encode( 'utf-8') )
        operations = dom.getElementsByTagName( 'operation' )
        for o in operations:
            value = o.getElementsByTagName( 'amount' )[0].childNodes[0].toxml()
            date = o.getElementsByTagName( 'exec-date' )[0].childNodes[0].toxml()
            type = o.getElementsByTagName( 'type' )[0].childNodes[0].toxml()
            description = ' '.join( o.getElementsByTagName( 'description' )[0].childNodes[0].toxml().split( '\n' ) )

            value = value.replace( '.', ',' )
            
            description = description.encode( 'iso-8859-2' ).encode( 'utf8' )
            date = time.mktime( time.localtime( calendar.timegm( datetime.strptime( date, "%Y-%m-%d" ).timetuple() ) ) )
            type = type.encode( 'iso-8859-2' ).encode( 'utf8' )

            desc_tmp = []
            if self.TAGS_MAP.has_key( type ):
                desc_tmp.append( self.TAGS_MAP[type] )

            if not '$bank' in ' '.join( desc_tmp ):
                desc_tmp.append( '$bank' )
        
            for key, val in self.DESCRIPTION_RE.items():
                if re.compile( key ).match( description ):
                    description = re.sub( key, val, description )
                    break;

            desc_tmp.append( description )
            desc_tmp.append( value )
            
            description = ' '.join( desc_tmp )
            print description

            self.addOperation( description, date )
            time.sleep( self.INSERT_SLEEP )
