#!./python

# lists.shtml 

"""CGI script to process a list service  subscription.

This script generates a confirmation (or error) message, processes a 
subscribe request and sends mail to th listserver.

"""

import sys
if '.' not in sys.path:
	sys.path.insert(0, '.')
import config
import homelib

import wi_config
import cgi
import os
import string
import wi_utils
import mgi_utils
import errorlib

NL = '\n'
SP = ' '
HT = '\t'

REQUIRED_FIELDS = [ 
	'emailaddr',
	'username',
	'listname'
	]

RECIPIENT = 'listmgr@informatics.jax.org'

# developer override for mailtarget 
dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
	RECIPIENT = dev_email

def hd():
	print """<HTML>
	<HEAD>
	<TITLE>List Subscription</TITLE>
	</HEAD>
	<BODY BGCOLOR="#FFFFFF">"""

	for line in homelib.banner():
		print line

	print """
	<H2>
	List Subscription Mail Results
	</H2>
	<HR>
	"""

def main():
	hd()

	form = cgi.FieldStorage()
	form_ok = 1
	for field in REQUIRED_FIELDS:
		if not form.has_key( field ):
			form_ok = 0
			break

	if not form_ok:
		print "<H1>Sorry...</H1>"
		print "Please enter your name, E-mail address, \
		and select the lists you want to join before submitting."
	else:
		username = form['username'].value
		emailaddr = form['emailaddr'].value
		listname = form['listname'].value

		if form['listname'].value=='both':
			sublists = ['mgi-list','rat-list']
		elif form['listname'].value=='mgi-list':
			sublists = ['mgi-list']
		elif form['listname'].value=='rat-list':
			sublists = ['rat-list']
		
		msg = ''
		listname1 = 'mgi-list'
		if listname1 in sublists:		
			msg = 'add' + SP + listname1 + SP + emailaddr+ SP + \
				username + NL 
		listname2 = 'rat-list'
		if listname2 in sublists:
			msg = msg + NL + 'add' + SP + listname2 + SP + \
				emailaddr + SP + username + NL 

		print """
	<H1>Thank you.</H1>
	Your subscribe request has been received and is being forwarded to our
	list_manager. You will receive an acknowlegement and instructions via
	E-mail.
	"""

		mail_header = 'From: webmaster' + NL \
			+ 'Subject: List Subscription' + NL
		fd = os.popen('%s -t %s' % (config.lookup ('SENDMAIL'), \
			RECIPIENT), 'w')
		fd.write( mail_header + msg + NL + '.' + NL )
		fd.close()
		
	print '<HR>'
	for line in homelib.footer():
		print line
	print '</BODY></HTML>'

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
