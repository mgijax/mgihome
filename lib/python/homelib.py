# Name:		mgihomelib.py
# Purpose:	provide general routines for use by MGI Home site scripts

import config

URL = config.lookup ('MGIHOME_URL')

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
