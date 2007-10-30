#!./python

# MGDquest

"""CGI script to process User Support Express Mail form.

This script generates a confirmation (or error) message, processes a form
and sends mail to User Support via Remedy.
schema: TJL-Inbox
forms: tjl_inbox.shtml, tjl_inbox_jx.shtml

version 1.0 9/98
revised 1/14/1999

"""

import sys
if '.' not in sys.path:
	sys.path.insert(0, '.')

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import cgi
import os
import string
import mgi_utils
import errorlib
import template

reply_message = template.Template(config['TEMPLATE_PATH'])

NL = '\n'
SP = ' '
HT = '\t'

REQUIRED_FIELDS = [ 'lastname',
	'firstname',
	'subject',
	'message',
	'emailaddr'
	]

RECIPIENT = 'mgi-help@informatics.jax.org'
# developer override for mailtarget 
if config.has_key('CGI_MAILTARGET'):
	RECIPIENT = config['CGI_MAILTARGET']

def hd():
	reply_message.setTitle('User Support Express Mail Results')
	reply_message.setHeaderBarMainText('User Support <I>Express</I> Mail Results')
	return

def main():
	hd()

	form = cgi.FieldStorage()
	form_ok = 1
	for field in REQUIRED_FIELDS:
		if not form.has_key( field ):
			form_ok = 0
			break

	if not form_ok:
		error_message = """<H1>Sorry...</H1>Please fill in required fields: 
			First Name, Last Name, E-mail address, Subject and Message. Then 
			send the message.  Please fill in required fields: First Name, 
			Last Name, E-mail address, Subject and Message. Then send the 
			message."""
		
		reply_message.appendBody(error_message)
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
		
		body = """
			<H1>Thank you.</H1>
			Your message has been received and is being forwarded to our
			<A HREF="support.shtml">User Support Group</A>."""
			
		reply_message.appendBody(body)

		mail_header = 'Reply-to: ps@informatics.jax.org' + NL \
			+ 'Subject: Express Mail' + NL
		fd = os.popen('%s -t %s' % (config['SENDMAIL'], \
			RECIPIENT), 'w')
		fd.write( mail_header + msg + NL + '.' + NL )
		fd.close()
		
		print reply_message.getFullDocument()
		
	return

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
#    Copyright (c) 1996 The Jackson Laboratory All Rights Reserved 
#
