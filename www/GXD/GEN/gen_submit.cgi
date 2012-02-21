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

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import table		# for unescape() function only
import homelib
import CGI
import template

reply_message = template.Template(config['TEMPLATE_PATH'])
reply_message.setContentType('')

submit_addr = 'gen@jax.org'	# GEN submissions E-mail

# developer override for mailtarget
if config.has_key('GEN_CGI_MAILTARGET'):
	submit_addr = config['GEN_CGI_MAILTARGET']

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
	
# Purposefully vague captcha error message
captcha_err_message = '''You did not fill out all of the required fields.<BR>
	Please go back and try again.<P>'''	

# header for generated e-mail
mailheader = '''From: %s
To: %s
Subject: %s

'''

gen_footer = ['<SMALL>',
		'Send questions and comments to <a href="mailto:gen@jax.org">gen@jax.org</a><BR>',
		'The Gene Expression Database (GXD) Project is supported by <a href="http://www.nih.gov/">NIH</a> grant <a href="http://crisp.cit.nih.gov/crisp/CRISP_LIB.getdoc?textkey=6363398&p_grant_num=5R01HD033745-05&p_query=&ticket=430962&p_audit_session_id=3171719&p_keywords=">HD062499</a><BR>',
		'</SMALL>']


class myCGI (CGI.CGI):
	def main(self):
	
		captchaFound = False
		captcha_element = ''
		if config.has_key('CAPTCHA_ELEMENT'):
			captcha_element = config['CAPTCHA_ELEMENT']
		captcha_timeout = ''
		if config.has_key('CAPTCHA_TIMEOUT'):
			captcha_timeout = config['CAPTCHA_TIMEOUT']
		captche_hide = ''
		if config.has_key('CAPTCHA_HIDE'):
			captcha_hide = config['CAPTCHA_HIDE']
	
		parms = self.get_parms()
		missing_fields = []
		for key in required_fields:
			if not parms.has_key (key):
				missing_fields.append (labels[key])
				
		if parms.has_key(captcha_element):
			if int(parms[captcha_element]) < int(captcha_timeout):
				captchaFound = True
		if parms.has_key(captcha_hide):
			if parms[captcha_hide] != '':
				captchaFound = True
				
		if captchaFound == True:
			reply_message.setTitle('GEN registration Form')
			reply_message.setHeaderBarMainText('GEN-Registration Error')
			reply_message.setBody(captcha_err_message)
			reply_message.appendBody(string.join (gen_footer, '\n '))
			print reply_message.getFullDocument()
			sys.exit (0)
				
		if missing_fields:
			reply_message.setTitle('GEN registration Form')
			reply_message.setHeaderBarMainText('GEN-Registration Error')
			reply_message.setBody(err_message % string.join (missing_fields, ', '))
			reply_message.appendBody(string.join (gen_footer, '\n '))
			print reply_message.getFullDocument()
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

		fd = os.popen('%s -t' % config['SENDMAIL'], 'w')
		fd.write(mailheader % (parms['email'], submit_addr,
			'GEN Registration'))
		fd.write(table.unescape(string.join (message, '\n')))
		fd.close()
		
		reply_message.setTitle('Request Sent')
		reply_message.setHeaderBarMainText('GEN-Registration Confirmation')
		
		body =  ['<H3>Thank you for registering!</H3>',
                'Please note: ',
                '<p>', 
                '<ul>',
                '<li>When downloading, if asked "What do you want to do with this file?", Choose <br>',
                '<b>Save it to disk</b>. (When downloading on other platforms, GEN may be directly<br> saved to disk and may even open immediately.)',
                '<li>You must <b>Enable Macros</b> to allow GEN to operate optimally. With some versions<br>of Excel this means you will need to reduce the Macro security level to Medium. ',
                '<li>To ensure your system is configured properly, review <a href="gen.shtml#sysreq">GEN system requirements</a>.',
                '</ul>',
                '<p>', 
                '<li><a href="GEN.xls">Download the GEN</a></li>',
                '<p>',
                '</ul>',
                '<BLOCKQUOTE><PRE>\n%s\n</PRE></BLOCKQUOTE>' % string.join (message, '\n')
        ]
		
		reply_message.setBody(string.join (body, '\n'))
		reply_message.appendBody(string.join (gen_footer, '\n'))
		
		print reply_message.getFullDocument()
		
		return

myCGI().go()
