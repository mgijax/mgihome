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
import header
import CGI
import errorlib
import SimpleVocab
import formMailer

SimpleVocab.set_sqlFunction (homelib.sql)

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
	'firstname'	: 'First name &amp; middle initial(s)',
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

	'published' 	: 'Currently Published',	# References
	'publicize'	: 'Make Public',
	'citations'	: 'Citations',			
	'alleleURL'	: 'Allele URL',


	'description'	: 'Description',		# Phenotype
	'remarks'	: 'Other Remarks',

	'genesymbol'	: 'Gene Symbol',		# Nomenclature
	'allele'	: 'Allele Symbol',
	'allelename'	: 'Allele Name',
	'synonyms'	: 'Other Names/Synonyms',
	'nomenHelp'	: 'Nomenclature Help Requested',

							# Strain
	'strainMutation': 'Strain Background (where mutation arose)',
	'strainPhenotype': 'Strain Background (where phenotype analyzed)',
	'strainInfo'	: 'Other Strain Information',
	'strainHelp'	: 'Genetic Background Help Requested',

							# Mutation
	'method'	: 'Method of Allele Generation',
	'othermethod'	: '"Other" Specification',
	'promoter'	: 'Transgene Promoter',
	'celline'	: 'ES Cell Line',
	'mode'		: 'Mode of Inheritance',
	'othermode'	: '"Other" Mode of Inheritance',


	'chromosome'	: 'Chromosome Location',	# Mapping data
	'location'	: 'Other Genome Location Information',
	}

# order in which fields should be included in the e-mail.  This is a list of
# tuples, where each tuple is: (section name, [ fieldnames in order ])
field_order = [
	('Nomenclature',
		['genesymbol', 'allele', 'allelename','synonyms','nomenHelp']),
	('About this Mutation',
		['method', 'othermethod', 'promoter', 'celline',
		'mode', 'othermode','chromosome','location']),
	('Genetic Background',
		['strainMutation', 'strainPhenotype', 'strainInfo', 
		'strainHelp',]),
	('Phenotype',
		['description', 'remarks']),
	('References',
		[ 'published', 'publicize', 'citations', 'alleleURL' ]),
	('Contact Details',
		[ 'lastname', 'firstname', 'email', 'organization',
			'address1', 'address2', 'city', 'state', 'zip',
			'country', 'phone', 'fax' ]),
	]
# error message string for missing required fields
err_message = '''These required fields are missing: %s<BR>
	Please go back and try again.<P>'''

# header for generated e-mail
mailheader = '''From: %s
To: %s
Subject: %s

'''

def convertPhenoslim (dict):
	if not dict.has_key('phenoslim'):
		return

	ps = SimpleVocab.PhenoSlimVocab()
	terms = {}
	for term in ps.getTerms():
		terms[str(term.getKey())] = term.getTerm()

	if type(dict['phenoslim']) != types.ListType:
		dict['phenoslim'] = terms[dict['phenoslim']]
	else:
		list = []
		for key in dict['phenoslim']:
			list.append (terms[key])
		dict['phenoslim'] = list
	return

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
				'MGI Allele and Mutant Form',
				header.bodyStart(),
				header.bodyStop())
			sys.exit (0)
		message = []
		convertPhenoslim (parms)
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
		print header.bodyStart()
		print header.headerBar('New Allele and Mutant Submission Sent')
		print 'The following information was successfully submitted:'
		print '<PRE>\n%s\n</PRE>' % string.join (message, '\n')
		print '<HR>'
		print header.bodyStop()
		return

myCGI().go()
