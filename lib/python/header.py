# header.py
# extracted from wi_utils.py in the wi product and altered for use in MGI Home

# Imports
#########
import sys
if '.' not in sys.path:
        sys.path.insert(0, '.')
import config 

import string

# Functions
###########

def bodyStart ():
	# Purpose: provides the opening for a WI page, including the toolbar
	#	and leaving the right-hand table cell open.  Most, if not all,
	#	CGI scripts should call header() instead.
	# Returns: string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	fp = open ('include/bodyStart.html', 'r')
	lines = fp.readlines()
	fp.close()
	return string.join (lines, '')

def bodyStop ():
	# Purpose: returns the string of HTML needed to properly close the
	#	tags left open by bodyStart().  Most, if not all, CGI scripts
	#	should call footer() instead.
	# Returns: string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	fp = open ('include/bodyStop.html', 'r')
	lines = fp.readlines()
	fp.close()
	return string.join (lines, '')

### --- BEGIN HEADER / FOOTER SECTION ------------------------------------ ###

black = "#000000"		# define colors for use in HTML
blueDark = "#D0E0F0"

# header string -- fill in Help section, Page Title, Your Input section
HEADER = string.join (
	[
	'<TABLE WIDTH="100%%" BORDER=0 CELLPADDING=2 CELLSPACING=1>',
	' <TR>',
	'  <TD WIDTH="100%%%%" BGCOLOR="%s">' % blueDark,
	'   <TABLE WIDTH="100%%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
	'    <TR>',
	'     <TD WIDTH="20%%" VALIGN="center" ALIGN="left">',
	'      %s',
	'     </TD>',
	'     <TD WIDTH="60%%" ALIGN="center" VALIGN="center">',
	'      <FONT COLOR="%s" SIZE=5 FACE="Arial,Helvetica">' % black,
	'       %s',
	'      </FONT>',
	'     </TD>',
	'     <TD WIDTH="20%%" VALIGN="center" ALIGN="center">',
	'      &nbsp;',
	'     </TD>',
	'    </TR>',
	'   </TABLE>'
	'  </TD>',
	' </TR>',
	'</TABLE>',
	],
	'\n')

# help section -- fill in Help Url
HELP = string.join (
	[
	'      <A HREF="%%s"><IMG SRC="%simages/shared/help_large.jpg" ',
	'	 BORDER=0 ',
	'        WIDTH=32 HEIGHT=30></A>',
	],
	'\n') % config.lookup('WI_URL')

def helpSection (
	helpUrl		# string; URL to the help page for this web page
	):
	# Purpose: private function - generates the Help graphic and link for
	#	a web page, according to the given 'helpUrl'
	# Returns: string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	if helpUrl == None:
		return '&nbsp;'
	return  HELP % helpUrl

def headerBar (
	dataset_id,		# string; brief ID for the data type
	format = None,		# string; identifies the format of the page
	additional = None,	# string; extra line of info about the page
	do_logo = None		# if non-None, use MGI logo not help link
	):
	# Purpose: returns the header bar at the top of the WI's right column.
	#	Most, if not all, CGI scripts should call header() instead.
	# Returns: string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	helpUrl = None
	pageTitle = dataset_id		# default - title is passed in
	pageFormat = ''
	moreInfo = ''

	if additional:
		moreInfo = '<BR><FONT SIZE=-1>%s</FONT>' % additional

	# if we need to use a logo, then put in the MGI logo, otherwise
	# give a link to a help doc if available.  Logo links to home page.

	if do_logo:
		left_column = ('<A HREF="%s" BORDER=0>' + \
			'<IMG SRC="%simages/shared/mgi_logo.jpg" ' + \
			'WIDTH=160 HEIGHT=80></A>') % \
			(config.lookup('WI_URL'), config.lookup('WI_URL'))
	else:
		left_column = helpSection (helpUrl)

	return HEADER % (left_column,
			pageTitle + pageFormat + moreInfo)

def header (
	dataset_id,		# string; brief ID for the data type
	format = None,		# string; identifies the format of the page
	additional = None,	# string; extra line of info about the page
	do_logo = None		# if non-None, use MGI logo not help link
	):
	# Purpose: provides the "header" inside the BODY section of a page,
	#	including both the toolbar and the header row.  must call
	#	footer() at the end to properly close the page.
	# Returns: string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	return bodyStart() + \
	    headerBar (dataset_id, format, additional, do_logo)

def footer ():
	# Purpose: returns the standard footer for the WI
	# Returns: empty string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing
	# Notes: closes the cell, row, and table that we opened in header()

	return bodyStop()

### --- END HEADER / FOOTER SECTION -------------------------------------- ###
