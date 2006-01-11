#!./python

# Program: survey.cgi
# Purpose: to process data submitted on the "New Allele and Mutant Submission
#	Form" within the MGI Home product.  Basically, we check to see that
#	some mandatory fields are present.  If not, we give an error message.
#	If they are, we build all the fields and values into an e-mail message
#	to send to a mail alias specified below.

import sys
if '.' not in sys.path:
	sys.path.insert (0, '.')
import string
import types
import os

import config
import table		# for unescape() function only
import homelib
import header
import CGI
import errorlib
import SimpleVocab
import formMailer

SimpleVocab.set_sqlFunction (homelib.sql)

submit_addr = 'survey@informatics.jax.org'	# Survey E-mail

# developer override for mailtarget
dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
	submit_addr = dev_email

# maps from actual fieldname to its label, for error reporting
required_fields = []

# maps from actual fieldnames to the corresponding label:
labels = {
	'use':'Frequency of use',
	'useComments':'Usage comments',
	'look':'The new look is',
	'lookComments':'Look and Feel comments',
	'info':'Information Searched for',
	'infoComments':'Information comments',
	'access':'Access information',
	'accessComments':'Access comments',
	'query':'Query forms and Resources used',
	'queryComments':'Query form comments',
	'othersites':'Other sites visited',
	'othersitesComments':'Comments about other sites',
	'awareSeq' : 'I was aware of the addition of sequences',
	'usedSeq' : 'I have used the new sequence information',
	'awareIMSR' : 'I was aware of the IMSR release',
	'usedIMSR' : 'I have used the new IMSR release',	
	'improvedComments':'Potential improvements',
	'newComments':'New functionality requested',
	'research':'Research area',
	'orgo':'Research organisms',
	'orgoComments':'Other organisms',
	'datasub':'Data submission improvements',
	'os':'Operating System',
	'osOther':'Other operating system',
	'browser':'Web browser',
	'altBrowse':'Other browser',
	'comments':'Other comments',
	'name':'Name',
	'email':'email address',
	}

# order in which fields should be included in the e-mail.  This is a list of
# tuples, where each tuple is: (section name, [ fieldnames in order ])
field_order = [
	('Answers',
		['use',
		 'useComments',
		 'look',
		 'lookComments',
		 'info',
		 'infoComments',
		 'access',
		 'accessComments',
		 'query',
		 'queryComments',
		 'othersites',
		 'othersitesComments',
		 'awareSeq',
		 'usedSeq',
		 'awareIMSR',
		 'usedIMSR',		 
		 'improvedComments',
		 'newComments',
		 'research',
		 'orgo',
		 'orgoComments',
		 'datasub',
		 'os',
		 'osOther',
		 'browser',
		 'altBrowse',
		 'comments',
		 'name',
		 'email',]),
	]
# error message string for missing required fields
err_message = '''These required fields are missing: %s<BR>
	Please go back and try again.<P>'''

# header for generated e-mail
mailheader = '''From: Web Survey
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
			formMailer.handleError (
				err_message % \
					string.join (missing_fields, ', '),
				'Survey Form',
				header.bodyStart(),
				header.bodyStop())
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

		print '<HTML><HEAD><TITLE>Survey Results Sent!</TITLE></HEAD>'
		print '<BODY bgcolor=ffffff>'
		print header.bodyStart()
		print header.headerBar('Survey Results Sent!')
		print 'The following information was successfully submitted:'
		print '<PRE>\n%s\n</PRE>' % string.join (message, '\n')
		print '<HR>'
		print header.bodyStop()

		ip = []
		ip.append('IP addr\n'+os.environ['REMOTE_ADDR'])
		message = message + ip
		fd = os.popen('%s -t' % config.lookup('SENDMAIL'), 'w')
		fd.write(mailheader % (submit_addr,
			'Survey Submission'))
		fd.write(table.unescape(string.join (message, '\n')))
		fd.close()

		return

myCGI().go()
