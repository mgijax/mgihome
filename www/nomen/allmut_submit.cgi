#!/usr/local/bin/python

# Program: allele_submit.cgi
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
import CGI
import errorlib

submit_addr = 'mutants@informatics.jax.org'	# MGD Allele and Mutant E-mail

# developer override for mailtarget
dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
	submit_addr = dev_email

# maps from actual fieldname to its label, for error reporting
required_fields = [ 'lastname', 'firstname', 'email' ]

# maps from actual fieldnames to the corresponding label:
labels = {
	'lastname'	: 'Last name',			# Contact Details
	'firstname'	: 'First name &amp; middle name(s)',
	'email' 	: 'E-mail address',
	'organization'	: 'Institute/Organization',
	'address1'	: 'Address',
	'address2'	: 'Address',
	'city'		: 'City',
	'state'		: 'State/Province',
	'zip'		: 'Postal Code',
	'country'	: 'Country',
	'phone'		: 'Telephone Number',
	'fax'		: 'Fax Number',

	'citations'	: 'Citations',			# References
	'alleleURL'	: 'Allele URL',

	'status'	: 'Status Requested',		# Status

	'phenotype'	: 'Phenotypic Categories',	# Phenotype
	'othercategory'	: 'Other Classification',
	'description'	: 'Description',
	'remarks'	: 'Other Remarks',

	'genesymbol'	: 'Gene Symbol',		# Allele or Mutant
	'allele'	: 'Allele Designation',
	'allelename'	: 'Allele Name',
	'newgenesymbol'	: 'Proposed Gene Symbol',
	'newgenename'	: 'Proposed Gene Name',
	'synonyms'	: 'Other Names/Synonyms',
	'strainMutation': 'Strain Background (where mutation arose)',
	'strainPhenotype': 'Strain Background (where phenotype analyzed)',
	'strainInfo'	: 'Other Strain Information',
	'method'	: 'Method of Allele Generation',
	'othermethod'	: '"Other" Specification',
	'promoter'	: 'Transgene Promoter',
	'celline'	: 'ES Cell Line',
	'mode'		: 'Mode of Inheritance',
	'chromosome'	: 'Chromosome Location',
	'location'	: 'Other Genome Location Information',
	}

# order in which fields should be included in the e-mail.  This is a list of
# tuples, where each tuple is: (section name, [ fieldnames in order ])
field_order = [
	('Contact Details',
		[ 'lastname', 'firstname', 'email', 'organization',
			'address1', 'address2', 'city', 'state', 'zip',
			'country', 'phone', 'fax' ]),
	('Allele or Mutant',
		['genesymbol', 'allele', 'allelename',
		'newgenesymbol', 'newgenename', 'synonyms',
		'strainMutation', 'strainPhenotype', 'strainInfo',
		'method', 'othermethod', 'promoter', 'celline',
		'mode', 'chromosome', 'location']),
	('Phenotype',
		['phenotype', 'othercategory', 'description', 'remarks']),
	('Status',
		['status']),
	('References',
		[ 'citations', 'alleleURL' ]),
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
				1, 'MGI Allele and Mutant Form',
				string.join (homelib.banner(), '\n '),
				string.join (homelib.footer(), '\n '))
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
			'Allele and Mutant Submission'))
		fd.write(table.unescape(string.join (message, '\n')))
		fd.close()

		print '<HTML><HEAD><TITLE>Request Sent</TITLE></HEAD>'
		print '<BODY bgcolor=ffffff>'
		print string.join (homelib.banner(), '\n')
		print '<H3>New Allele and Mutant Submission Sent</H3>'
		print 'The following information was successfully submitted:'
		print '<PRE>\n%s\n</PRE>' % string.join (message, '\n')
		print '<HR>'
		print string.join (homelib.footer(), '\n')
		return

myCGI().go()
