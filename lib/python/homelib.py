# Name:		mgihomelib.py
# Purpose:	provide general routines for use by MGI Home site scripts

def footer ():
	# Purpose: provide a standard footer for MGI Home-based web pages
	# Returns: list of strings
	# Assumes: nothing
	# Effects: nothing
	# Throws: None

	return [ '<A HREF="http://www.jax.org/" target="_top">',
		  '''<IMG SRC="/mgihome/images/jax_logo.gif"
			ALT="The Jackson Laboratory" ALIGN=right></A>''',
		  '<SMALL>',
		  '''<A HREF="/mgihome/other/citation.shtml" target="_top">
		        Citing These Resources</A>''', '<BR>',
		  '''<A HREF="/mgihome/other/mgi_funding.shtml" target="_top">
		        Funding Information</A>''', '<BR>',
		  '''<A HREF="/mgihome/other/copyright.shtml" target="_top">
		        Warranty Disclaimer &amp; Copyright Notice</A>.''',
		        '<BR>',
		  '''Send questions and comments to
			<A HREF="/mgihome/support/tjl_inbox.shtml"
			target="_top">User Support</A>.''',
		  '</SMALL>' ]

def banner ():
	# Purpose: provide a standard banner for MGI Home-based web pages
	# Returns: list of strings
	# Assumes: nothing
	# Effects: nothing
	# Throws: None

	return [ '<CENTER>',
		 '<IMG SRC="/mgihome/images/mgi_small_banner.gif"',
	    	 'WIDTH=501   HEIGHT=40   ALT="Mouse Genome Informatics">',
		 '</CENTER>' ]
