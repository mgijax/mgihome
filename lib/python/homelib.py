# Name:		mgihomelib.py
# Purpose:	provide general routines for use by MGI Home site scripts

import os
import config
import db

URL = config.lookup ('MGIHOME_URL')
db.set_sqlLogin (config.lookup ('DBUSER'), config.lookup ('DBPASSWORD'),
	config.lookup ('DBSERVER'), config.lookup ('DATABASE'))

def footer ():
	# Purpose: provide a standard footer for MGI Home-based web pages
	# Returns: list of strings
	# Assumes: nothing
	# Effects: nothing
	# Throws: None

	return [ '<A HREF="http://www.jax.org/" target="_top">',
		  '''<IMG SRC="%simages/jax_logo.gif" ALIGN=right
			ALT="The Jackson Laboratory"></A>''' % URL,
		  '<SMALL>',
		  '''<A HREF="%sother/citation.shtml" target="_top">
		        Citing These Resources</A>''' % URL, '<BR>',
		  '''<A HREF="%sother/mgi_funding.shtml" target="_top">
		        Funding Information</A>''' % URL, '<BR>',
		  '''<A HREF="%sother/copyright.shtml" target="_top">
		        Warranty Disclaimer &amp; Copyright Notice</A>.''' \
			% URL,
		        '<BR>',
		  '''Send questions and comments to
			<A HREF="%ssupport/tjl_inbox.shtml"
			target="_top">User Support</A>.''' % URL,
		  '</SMALL>' ]

def banner ():
	# Purpose: provide a standard banner for MGI Home-based web pages
	# Returns: list of strings
	# Assumes: nothing
	# Effects: nothing
	# Throws: None

	return [ '<CENTER>',
		 '<IMG SRC="%simages/mgi_small_banner.gif"' % URL,
	    	 'WIDTH=501   HEIGHT=40   ALT="Mouse Genome Informatics">',
		 '</CENTER>' ]

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
