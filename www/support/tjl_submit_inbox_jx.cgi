#!./python

# MGDquest

"""CGI script to process User Support Express Mail form.
MICETECH version (see tjl_inbox_jx.shtml)
This script generates a confirmation (or error) message, processes a form
and sends mail to TJL Support via Remedy.
schema: TJL-Inbox
form: tjl_inbox_jx.shtml
------------
version 1.0 9/98
version 1.2: 11/3/98: added email dest acv@jax.org to 
receive notice of all new micetech messages.
version 1.3: 5/20/1999: added code to switch view to jax
acknowledgement page.

"""

import sys
if '.' not in sys.path:
	sys.path.insert(0, '.')
import config

import wi_config 
import cgi
import os
import string
import mgi_utils
import errorlib

NL = '\n'
SP = ' '
HT = '\t'

REQUIRED_FIELDS = [ 'lastname',
	'firstname',
	'subject',
	'message',
	'emailaddr'
	]

#RECIPIENT = 'mgi-help@informatics.jax.org'
#RECIPIENT = 'mem@jax.org'
RECIPIENT = 'arsystem@jax.org'

# developer override for mailtarget 
dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
	RECIPIENT = dev_email

def main():

	form = cgi.FieldStorage()
	form_ok = 1
	for field in REQUIRED_FIELDS:
		if not form.has_key( field ):
			form_ok = 0
			break

	if not form_ok:
		print """<HTML>
           	 <HEAD>
		 <H1>TJL Support Express Mail Results</H1>
		 <TITLE></TITLE>
		 </HEAD>
		 <H2>Sorry...</H2>
		 Please fill in required fields: <BR><B>First Name, 
		 Last Name, E-mail address, Subject and Message. </B>
		 <BR>Then send the message.
		"""
	else:
		if form.has_key( 'title' ):
			title = form['title'].value
		else:
			title = ""
		firstname = form['firstname'].value
		lastname = form['lastname'].value
		if form.has_key( 'inst' ):
			inst = form['inst'].value
		else:
			inst = ""
		if form.has_key( 'positn' ):
			positn = form['positn'].value
		else:
			positn = ""
		emailaddr = form['emailaddr'].value
		if form.has_key( 'ph' ):
			ph = form['ph'].value
		else:
			ph = ""

		if form.has_key( 'fx' ):
			fax = form['fx'].value
		else:
			fax = ""
		subject = form['subject'].value
		message = form['message'].value
		attnto = form['attnto'].value
		domain = form['domain'].value

		msg = \
			'#' + NL \
			+ '#' + 2*SP + mgi_utils.date() + NL \
			+ '#' + NL \
			+ '#AR-Message-Begin' + 13*SP \
				+ 'Do Not Delete This Line' + NL \
			+ 'Schema: TJL-Inbox' + NL \
			+ 'Server: arserver.jax.org' + NL \
			+ 'Login: webmail' + NL \
			+ 'Password: webuser1' + NL \
			+ 'Action: Submit' + NL \
			+ '# Values: Submit, Query' + NL \
			+ 'Format: Short' + NL \
			+ '# Values: Short, Full' + NL \
			+ NL \
			+ string.rjust( 'title', 20 ) + ' !536870924!:' \
				+ title + NL \
			+ string.rjust( 'F_Name', 20 ) + ' !536870913!:' \
				+ firstname + NL \
			+ string.rjust( 'L_Name', 20 ) + ' !536870914!:' \
				+ lastname + NL \
			+ string.rjust( 'em', 20 ) \
				+ ' !536870915!:' + emailaddr + NL \
			+ string.rjust( 'in-ph', 20 ) \
				+ ' !536870920!:' + ph + NL \
			+ string.rjust( 'in-fax', 20 ) \
				+ ' !536870922!:' + fax + NL \
			+ string.rjust( 'inst', 20 ) \
				+ ' !536870921!:' + inst + NL \
			+ string.rjust( 'Position', 20 ) \
				+ ' !536870925!:' + positn + NL \
			+ string.rjust( 'Request Summary', 20 ) \
				+ ' !        8!:' + subject + NL \
			+ string.rjust( 'Request Details', 20 ) \
				+ ' !536870916!:' + message + NL \
			+ string.rjust( 'Submitter', 21 ) \
				+ '!        2!: webmail' + NL \
			+ string.rjust( 'Status', 21 ) + \
				'!        7!: New' + NL \
			+ string.rjust( 'ATTN', 20 ) \
				+ ' !536870923!:' + attnto + NL \
			+ string.rjust( 'jax_domain', 20) \
				+ ' !536870919!:' + domain + NL \
			+ NL \
			+ '#AR-Message-End' + 13*SP \
				+ 'Do Not Delete This Line' + NL

		print """
<HTML>
<HEAD>
<SCRIPT>
location.href = "http://jaxmice.jax.org/html/techsupport/tswebform_resp.shtml" 
</SCRIPT>
<NOSCRIPT>
<meta http-equiv="Refresh" content="1; URL="http://jaxmice.jax.org/html/techsupport/tswebform_resp.shtml" >
</NOSCRIPT>
<TITLE></TITLE>
</HEAD>
</HTML>
"""
#		print """
#<H1>Thank you.</H1>
#Your message has been forwarded to our
#<B>Technical Services</B> group.
#"""

		mail_header = 'Reply-to: micetech@jax.org' + NL \
			+ 'Subject: Express Mail' + NL
		fd = os.popen('%s -t %s' % (cfg['SENDMAIL'], RECIPIENT), 'w')
		fd.write( mail_header + msg + NL + '.' + NL )
		fd.close()
		
#	print '<HR>'

print 'Content-type: text/html'
print
try:
	main()
except:
	errorlib.handle_error()






#
# WARRANTY DISCLAIMER AND COPYRIGHT NOTICE 
#
#    THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE 
#    SUITABILITY OR ACCURACY OF THIS SOFTWARE OR DATA FOR ANY 
#    PURPOSE, AND MAKES NO WARRANTIES, EITHER EXPRESS OR IMPLIED, 
#    INCLUDING THE WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#    A PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA 
#    WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, 
#    TRADEMARKS OF OTHER RIGHTS. IT IS PROVIDED "AS IS." 
#
#    This software and data are provided as a service to the scientific 
#    community to be used only for research and educational purposes. Any
#    commercial reproduction is prohibited without the prior written 
#    permission of The Jackson Laboratory. 
#
#    Copyright © 1996 The Jackson Laboratory All Rights Reserved 
#
