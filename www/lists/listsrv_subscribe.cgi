#!./python

# lists.shtml 

"""CGI script to process a list service  subscription.

This script generates a confirmation (or error) message, processes a 
subscribe request and sends mail to th listserver.

"""

import sys
if '.' not in sys.path:
	sys.path.insert(0, '.')
import types

import Configuration

config = Configuration.get_Configuration ('Configuration', 1)

import homelib

import cgi
import os
import string
import errorlib
import template

page_template = template.Template(config['TEMPLATE_PATH'])

NL = '\n'
SP = ' '
HT = '\t'

REQUIRED_FIELDS = [ 
	'emailaddr',
	'username',
	'listname'
	]

RECIPIENT = 'mgi-help@jax.org'

# developer override for mailtarget 
if config.has_key('CGI_MAILTARGET'):
	RECIPIENT = config['CGI_MAILTARGET']

def hd():
	page_template.setTitle('List Subscription')
	page_template.setHeaderBarMainText('List Subscription Mail Results')

	print page_template.getNavigationAndHeader()
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
		print "<H1>Sorry...</H1>"
		print "Please enter your name, E-mail address, \
		and select the lists you want to join before submitting."
	else:
		username = form['username'].value
		emailaddr = form['emailaddr'].value

		if type(form['listname']) == types.ListType:
			sublists = []
			for item in form['listname']:
				sublists.append (item.value)
		else:
			sublists = [ form['listname'].value ]

		subscribe = 'add %s %s %s\n'
		cmds = []
		for item in sublists:
			cmds.append (subscribe % (item, emailaddr, username))
		msg = string.join (cmds, '\n')

		print """
	<H1>Thank you.</H1>
	Your subscribe request has been received and is being forwarded to our
	list_manager. You will receive an acknowlegement and instructions via
	E-mail.
	"""

		mail_header = 'From: webmaster' + NL \
			+ 'Subject: List Subscription' + NL
		fd = os.popen('%s -t %s' % (config['SENDMAIL'], \
			RECIPIENT), 'w')
		fd.write( mail_header + msg + NL + '.' + NL )
		fd.close()
		
	print page_template.getTemplateBodyStop()
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
#    Copyright � 1996 The Jackson Laboratory All Rights Reserved 
#
