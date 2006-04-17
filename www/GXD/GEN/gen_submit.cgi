#!/usr/local/bin/python

# Program: gen_submit.cgi
# Purpose: to process registration information submitted through the GEN download page.

import sys
#if '.' not in sys.path:
#	sys.path.insert (0, '.')
sys.path.insert (0, '/usr/local/mgi/lib/python')
import string
import types
import os
import db
import config
import table		# for unescape() function only
import homelib
import CGI
import errorlib
import geninclude

submit_addr = 'gen@informatics.jax.org'	# GEN submissions E-mail

# developer override for mailtarget
dev_email = config.lookup ('GEN_CGI_MAILTARGET')
if dev_email is not None:
	submit_addr = dev_email

# maps from actual fieldname to its label, for error reporting
required_fields = [ 'lastname', 'firstname', 'email' ]

# maps from actual fieldnames to the corresponding label:
labels = {
	'lastname'	: 'Last name',			# Contact Details
	'firstname'	: 'First name',
        'mi'            : 'Middle Initial',
	'email' 	: 'E-mail address',
	'organization'	: 'Institute/Organization',
	'computer'      : 'Computer',
	'os'		: 'Operating System',
   'excelVer' : 'Excel Version',
	 }
# order in which fields should be included in the e-mail.  This is a list of
# tuples, where each tuple is: (section name, [ fieldnames in order ])
field_order = [
	('Contact Details',
		[ 'lastname', 'firstname', 'email', 'organization'
		]),
	('Computer Information',
		['computer', 'os','excelVer'
		])
	       ]

# error message string for missing required fields
err_message = '''These required fields are missing: %s<BR>
	Please go back and try again.<P>'''

# header for generated e-mail
mailheader = '''From: %s
To: %s
Subject: %s

'''


class myCGI (CGI.CGI):
	def main(self):
		parms = self.get_parms()
		missing_fields = []
		for key in required_fields:
			if not parms.has_key (key):
				missing_fields.append (labels[key])
		if missing_fields:
			errorlib.show_error (
				err_message % \
					string.join (missing_fields, ', '),
				1, 'GEN registration Form',
				string.join (geninclude.banner(), '\n '),
				string.join (geninclude.footer(), '\n '))
			sys.exit (0)
		message = []
		for (heading, fieldlist) in field_order:
			section = [
				'-' * len(heading),
				heading,
				'-' * len(heading),
				]
			for field in fieldlist:
				if parms.has_key(field):
					section.append (labels[field])
					if type(parms[field]) == \
							types.ListType:
						for item in parms[field]:
							section.append ( \
								'\t%s' % item)
					else:
						section.append ('\t%s' % \
							parms[field])
			if len(section) > 3:
				message = message + section

		fd = os.popen('%s -t' % config.lookup('SENDMAIL'), 'w')
		fd.write(mailheader % (parms['email'], submit_addr,
			'GEN Registration'))
		fd.write(table.unescape(string.join (message, '\n')))
		fd.close()

		print '<HTML><HEAD><TITLE>Request Sent</TITLE></HEAD>'
		print '<BODY bgcolor=ffffff>'
		print string.join (geninclude.bannerok(), '\n')
		print '<H3>Thank you for registering!</H3>'
                print 'Please note: '
                print '<p>' 
                print '<ul>'
                print '<li>When downloading, if asked "What do you want to do with this file?", Choose <br>'
                print '<b>Save it to disk</b>. (When downloading on other platforms, GEN may be directly<br> saved to disk and may even open immediately.)'
                print '<li>You must <b>Enable Macros</b> to allow GEN to operate optimally. With some versions<br>of Excel this means you will need to reduce the Macro security level to Medium. '
                print '<li>To ensure your system is configured properly, review <a href="gen.shtml#sysreq">GEN system requirements</a>.'
		print '</ul>'
                print '<p>' 
                print '<li><a href="GEN.xls">Download the GEN</a></li>'
                print '<p>'
                print '</ul>'
		print '<PRE>\n%s\n</PRE>' % string.join (message, '\n')
		print string.join (geninclude.footer(), '\n')
		return

myCGI().go()
