#!./python

# Program: strain_submit.cgi
# Purpose: accept submission from strain_form.shtml, do input validation,
#	send an e-mail to strain curators, and provide feedback to the user.

import sys				# standard Python libraries
if '.' not in sys.path:
	sys.path.insert (0, '.')
import os
import string

import config				# MGI-written Python libraries
import homelib
import formMailer

###--- Global Variables ---###

# mapping from internal fieldname to label for the user:

labels = {
	'method'	: 'Strain Name New or Revised',
	'strain_name'	: 'Strain Name',
	'gene_symbols'	: 'Gene Symbols',
	'JR_num'	: 'JR',
	'status'	: 'Strain Public or Private',
	'category'	: 'Categories',
	'synonyms'	: 'Synonyms',
	'references'	: 'References',
	'notes'		: 'Notes',
	'name'		: 'User Name',
	'email'		: 'E-Mail Address',
	}

# list of internal fieldnames for required fields:

required_fields = [ 'name', 'method', 'status' ]

# sections for e-mail:
# each tuple contains (section heading string, list of internal fieldnames
#	to include in that section)

sections = [
	('Strain Info',
		[ 'method', 'JR_num', 'strain_name', 'gene_symbols',
		  'status', 'category' ]),
	('Additional Info',
		[ 'synonyms', 'references', 'notes' ]),
	('Contact Info',
		[ 'name', 'email' ]),
	]

###--- Classes ---###

class strainMailer (formMailer.formMailer):
	# IS: a formMailer that deals specifically with the strain_form.shtml
	#	strain submission form
	# HAS: see formMailer
	# DOES: see formMailer

	def doPostValidationProcessing(self):
		# Purpose: convert any submitted multi-line field to be a list
		#	of strings (with each string being a single line)
		# Returns: nothing
		# Assumes: nothing
		# Effects: alters self.parms
		# Throws: nothing
		# Notes: The four possible multi-line fields are defined in
		#	the 'fields' variable below.  Even if one of these
		#	fields contains only a single line, we will convert
		#	it to a list for consistency.

		fields = [ 'notes', 'references', 'synonyms', 'gene_symbols' ]
		for field in fields:
			if self.parms.has_key (field):
				self.parms[field] = string.split (
					self.parms[field], '\n')
		return

	def doValidations(self):
		# Purpose: perform validation of submitted data
		# Returns: list of tuples; each tuple is (fieldname, error
		#	string).  An empty list means no errors were found.
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: For now, we do two validations - check that the
		#	e-mail address contains an '@' sign, and check that
		#	the username in the e-mail address matches that of
		#	the person logged in using the htaccess mechanism.

		errors = []

		# check that the e-mail address contains a '@'

		if self.parms.has_key ('email'):
			atPos = string.find (self.parms['email'], '@')
			if atPos == -1:
				errors.append ( ('email',
					'Invalid e-mail address') )
		return errors

	def getFrom (self):
		# Purpose: return the e-mail address which should appear in
		#	the 'From' line for the generated e-mail
		# Returns: string
		# Assumes: an 'email' field was submitted, though this would
		#	have already been confirmed when we check for
		#	required fields
		# Effects: nothing
		# Throws: nothing
		# Notes: We return the e-mail address submitted by the user,
		#	so the e-mail appears that it comes from him/her.

		if self.parms.has_key ('email'):
			return self.parms['email']
		return self.parms['name']

###--- Main Program ---###

# set up the 'To' address for the submission, and allow it to be over-ridden
# in the configuration file for testing.

submit_addr = 'strains@informatics.jax.org'

dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
	submit_addr = dev_email

# construct the strainMailer object, and let it run...

myCGI = strainMailer ('Strain',
	submit_addr,
	homelib.banner(),
	homelib.footer(),
	labels,
	required_fields,
	sections
	)
myCGI.go()

