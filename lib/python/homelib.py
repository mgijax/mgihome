# Name:         mgihomelib.py
# Purpose:      provide general routines for use by MGI Home site scripts

import os

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import time
import re
import webshare_lib
import urllib.request, urllib.parse, urllib.error

URL = config['MGIHOME_URL']
WI_URL = config['WI_URL']

def makepath (
        *items          # strings
        ):
        # Purpose: join one or more directory levels to create a single
        #       path
        # Returns: string pathname
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing

        s = ''
        for item in items:
                s = os.path.join (s, item)
        return s

def valOrNone (
        key,            # variable type; key to look for in 'dict'
        dict            # dictionary; where to look up a value for 'key'
        ):
        # Purpose: return the value in 'dict' which corresponds to 'key', or
        #       None if 'key' is not in 'dict'
        # Returns: see Purpose
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing

        if key in dict:
                return dict[key]
        return None

def wrapLines (
        s,              # the string to wrap.  can contain multiple lines, with
                        # line breaks delimited by LF (defined below)
        maxlen          # integer; desired maximum line length
        ):
        # Purpose: wrap lines of text in "s" so that each has length less than
        #       or equal to "maxlen", where possible
        # Returns: string containing the wrapped lines.  Individual lines are
        #       delimited by LF
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing
        # Notes: We do not guarantee that all the output lines are <= "maxlen"
        #       characters.  This is because wrapLines() does intelligent
        #       wrapping -- it wraps at word boundaries (defined by a space).
        #       If a line has no spaces before length "maxlen", we do not
        #       attempt to wrap it.
        # Example:
        #       s = "Here is a simple\nexample of a wrapped line.\n"
        #       wrapLines (s, 10) returns:
        #           "Here is a \nsimple\nexample \nof a \nwrapped \nline.\n"
        # This code was freely pilfered from WTS's wtslib.py file.

        LF = '\n'
        TRUE = 1
        line_list = []                          # list of generated lines
        lines = s.split (LF)            # list of input lines

        for line in lines:
                done = (len (line) <= maxlen)   # done splitting this line?
                while not done:
                        # get "p", the position after the final space in the
                        # first maxlen characters of "line".

                        p = 1 + line[:maxlen].rfind(' ')
                        if p == 0:
                                done = TRUE     # no spaces in line
                        else:
                                line_list.append (line [:p])
                                line = line [p:]
                                done = (len (line) <= maxlen)
                line_list.append (line)
        return LF.join (line_list)

def getJsonResults(fewiPath, field, value):
        # Get a string of JSON back from the fewi, searching in 'field' for
        #       the given 'value'.
        # params:
        #       fewiPath is the portion of the URL after the fewi's base URL
        #       field is the name of the field to search
        #       value is the value to search for

        url = '%s%s?%s=%s' % (config['FEWI_URL'], fewiPath, field, urllib.parse.quote(value))
        f = urllib.request.urlopen(url)
        s = f.read()
        f.close()

        try:
                x = eval(s.replace('null', 'None'))
        except:
                return { 'summaryRows' : [] }
        return x

def _parseMarkerSymbol(symbol):
        if symbol:
                # need to pull symbol out of middle of link
                regex = re.compile(">([^<]+)<")
                match = regex.search(symbol)
                if match:
                        return match.group(1)
        return None

def getMarkers(searchString):
        # return [ list of matching markers ] for the given 'searchString'.
        # Each marker is:  (symbol, feature type).

        byID = getJsonResults('marker/json', 'markerID', searchString)
        bySymbol = getJsonResults('marker/json', 'nomen', searchString)
        rows = []
        for marker in byID['summaryRows'] + bySymbol['summaryRows']:
                rows.append ( (_parseMarkerSymbol(marker['symbol']),
                        marker['featureType']) )

        return rows

def _parseAlleleSymbol(symbol):
        # need to pull symbol out of middle of link and convert
        # superscript HTML tags to angle brackets
        if symbol:
                t = symbol.replace('<sup>', '###').replace('</sup>', '#-#')
                regex = re.compile(">([^<]+)<")
                match = regex.search(t)
                if match:
                        return match.group(1).replace("#-#", ">").replace("###", "<")
        return None

def getAlleles(searchString):
        # return [ list of symbols for matching alleles ] for the given
        # 'searchString'.
        byID = getJsonResults('allele/summary/json', 'allIds', searchString)
        bySymbol = getJsonResults('allele/summary/json', 'nomen', searchString)
        rows = []
        for allele in byID['summaryRows'] + bySymbol['summaryRows']:
                rows.append ( _parseAlleleSymbol(allele['nomen']) )

        return rows

def getObjectTypes(searchString):
        # return [ list of MGI Types matching the given 'searchString' ]
        byID = getJsonResults('accession/json', 'id', searchString)
        rows = []
        for row in byID['summaryRows']:
                rows.append(row['objectType'])
        return rows

def getObjects(searchString):
        # return [ list of objects matching the given 'searchString' ]
        byID = getJsonResults('accession/json', 'id', searchString)
        return byID['summaryRows']

def sanitizeID(accID):
        # return a sanitized version of 'accID' that only contains certain
        # allowed characters (letters, numbers, colons, underscores, hyphens,
        # and periods).  Helps prevent reflected cross-site scripting attacks.
        
        if not accID:
                return accID
        
        return re.sub('[^A-Za-z0-9_:\\.\\-]', '', accID)

def sanitizeDate(mmddyyyy):
        # return a sanitized version of the date in 'mmddyyyy' that only contains
        # allowed characters (numbers plus two slashes, as mm/dd/yyyy).  If there
        # is any issue identifying the date, return today's date instead.
        
        dateRE = re.compile('([0-9]{2}/[0-9]{2}/[0-9]{4})')
        match = dateRE.match(mmddyyyy)
        if match:
                return match.group(1)
        return time.strftime('%m/%d/%Y', time.localtime())
