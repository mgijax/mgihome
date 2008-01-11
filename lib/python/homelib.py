# Name:		mgihomelib.py
# Purpose:	provide general routines for use by MGI Home site scripts

import os

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import string
import db
import webshare_lib

# for key in config.keys():
	# print key + " "  + config[key]

URL = config['MGIHOME_URL']
WI_URL = config['WI_URL']
db.set_sqlLogin (config['DB_USER'], config['DB_PASSWORD'],
	config['DB_SERVER'], config['DB_DATABASE'])

def sql (queries, parsers = 'auto'):
	# Purpose: wrapper over the db.sql routine
	# Returns: list of dictionaries, or list of lists of dictionaries,
	#	depending on whether 'queries' is a string or a list or
	#	strings.
	# Assumes: nothing
	# Effects: runs 'queries' against the database specified in the
	#	Configuration file
	# Throws: propagates any exceptions raised by db.sql()

	return db.sql (queries, parsers)

def makepath (
	*items		# strings
	):
	# Purpose: join one or more directory levels to create a single
	#	path
	# Returns: string pathname
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	s = ''
	for item in items:
		s = os.path.join (s, item)
	return s

def valOrNone (
	key,		# variable type; key to look for in 'dict'
	dict		# dictionary; where to look up a value for 'key'
	):
	# Purpose: return the value in 'dict' which corresponds to 'key', or
	#	None if 'key' is not in 'dict'
	# Returns: see Purpose
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	if dict.has_key(key):
		return dict[key]
	return None

def wrapLines (
	s,		# the string to wrap.  can contain multiple lines, with
			# line breaks delimited by LF (defined below)
        maxlen		# integer; desired maximum line length
	):
	# Purpose: wrap lines of text in "s" so that each has length less than
	#	or equal to "maxlen", where possible
	# Returns: string containing the wrapped lines.  Individual lines are
	#	delimited by LF
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing
	# Notes: We do not guarantee that all the output lines are <= "maxlen"
	#	characters.  This is because wrapLines() does intelligent
	#	wrapping -- it wraps at word boundaries (defined by a space).
	#	If a line has no spaces before length "maxlen", we do not
	#	attempt to wrap it.
	# Example:
	#	s = "Here is a simple\nexample of a wrapped line.\n"
	#	wrapLines (s, 10) returns:
	#	    "Here is a \nsimple\nexample \nof a \nwrapped \nline.\n"
	# This code was freely pilfered from WTS's wtslib.py file.

	LF = '\n'
	TRUE = 1
	line_list = []				# list of generated lines
	lines = string.split (s, LF)		# list of input lines

	for line in lines:
		done = (len (line) <= maxlen)	# done splitting this line?
		while not done:
			# get "p", the position after the final space in the
			# first maxlen characters of "line".

			p = 1 + string.rfind (line [:maxlen], ' ')
			if p == 0:
				done = TRUE	# no spaces in line
			else:
				line_list.append (line [:p])
				line = line [p:]
				done = (len (line) <= maxlen)
		line_list.append (line)
	return string.join (line_list, LF)
