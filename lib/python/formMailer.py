# Name: formMailer.py
# Purpose: provide classes to facilitate accepting the submission of an HTML
#	form, performing any necessary validations, providing user feedback,
#	and mailing the submission contents to a specified e-mail address.

import types		# standard Python modules
import string

import CGI		# MGI-written Python modules
import mgi_utils

###--- Global Variables/Constants ---###

# messages produced when incorrect or insufficient data is submitted and
# detected:

MISSING_FIELDS = '''These required fields are missing: %s<BR>
	Please go back and try again.<P>'''

FAILED_CHECKS = '''The following field(s) contained errant values:<BR>
	<DL>
	%s
	</DL>
	Please go back and try again.<P>'''

# responses produced by a valid submission, depending on whether the e-mail
# could be sent or not:

MESSAGE_SENT = '''<HTML><HEAD><TITLE>Request Sent</TITLE></HEAD>
	<BODY bgcolor=ffffff>
	%s
	<H3>%s Submission Sent</H3>
	The following information was successfully submitted.
	<PRE>\n%s\n</PRE>
	<HR>
	%s
	</BODY></HTML>'''

MESSAGE_FAILED = '''<HTML><HEAD><TITLE>Request Not Sent</TITLE></HEAD>
	<BODY bgcolor=ffffff>
	%s
	<H3>%s Submission Not Sent</H3>
	An error occurred, so your submission could not be sent.  Please
	try again later.<P>
	<HR>
	%s
	</BODY></HTML>'''

###--- Functions ---###

def handleError (
	message,	# string; message describing the error
	title,		# string; name of the form being submitted
	banner,		# string; page header
	footer		# string; page footer
	):
	# Purpose: send to the user an HTML page describing an error which
	#	was detected
	# Returns: nothing
	# Assumes: nothing
	# Effects: writes to stdout
	# Throws: nothing

	print '''<HTML><HEAD><TITLE>%s Submission Error</TITLE></HEAD>
		<BODY bgcolor="#FFFFFF">%s
		<H2>%s Submission Error</H2>
		%s<HR>
		%s
		</BODY></HTML>''' % (title, banner, title, message, footer)
	return

###--- Classes ---###

class formMailer (CGI.CGI):
	# IS: a CGI script which catches input from a form, composes a reply
	#	for the remote user, and includes it in an e-mail to a
	#	designated mail account`
	# HAS: name of the web form sent, e-mail address to which to send the
	#	e-mail, output page header & footer, a dictionary of
	#	internal fieldnames and corresponding labels, a list of
	#	fieldnames for required fields, and a list of tuples which
	#	specify various sections for the e-mail sent
	# DOES: see IS section

	def __init__ (self,
		form_name,		# string; name of the form submitted
		address,		# string; where to send the e-mail

		# all of the remaining parameters are optional:

		header = [],		# string or list of strings; header
					# 	to go at the top of the output
					#	page's BODY section
		footer = [],		# string or list of strings; footer
					# 	to go at the bottom of the
					#	output page's BODY section
		labels = {},		# dictionary mapping internal field-
					#	names to the labels shown to
					#	the user
		required_fields = [],	# list of strings; internal fieldnames
					#	of fields required to have a
					#	value submitted by the user
		sections = []		# list of tuples; each tuple describes
					#	a "section" for the e-mail and
					#	has two values: a string title
					#	for the section, and a list of
					#	string fieldnames to include
					#	in the section
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: gets parameters from the form submission;
		#	constructs a set of labels if one is not given
		# Throws: nothing

		CGI.CGI.__init__ (self)		# parent class's constructor

		self.parms = self.get_parms()

		# initialize the basic attributes, based on parameters

		self.form_name = form_name
		self.address = address
		self.labels = labels
		self.required_fields = required_fields
		self.sections = sections

		# if the user gave a list of strings for header and/or footer,
		# join them to form a single string for each

		if type(header) == types.StringType:
			self.header = header
		else:
			self.header = string.join (header, '\n')

		if type(footer) == types.StringType:
			self.footer = footer
		else:
			self.footer = string.join (footer, '\n')

		# if the user didn't give us a set of labels, then we use the
		# fieldnames submitted to compose a set

		if not self.labels:
			fields = self.parms.keys()
			for field in fields:
				self.labels[field] = field
		return

	###--- Private Methods ---###

	def doValidations(self):
		# Purpose: perform any necessary validations of the parameters
		#	as submitted by the user
		# Returns: list of tuples describing the errors.  each tuple
		#	contains (fieldname, error string)
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: By default, we perform no validations.  This method
		#	should be overridden in subclasses as needed.

		return []

	def doPreValidationProcessing(self):
		# Purpose: perform any necessary pre-processing of parameters
		#	before they may be validated
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: By default, we perform no pre-processing.  This
		#	method should be overridden in subclasses as needed.

		return

	def doPostValidationProcessing(self):
		# Purpose: perform any necessary post-processing of parameters
		#	after they have been validated
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: By default, we perform no post-processing.  This
		#	method should be overridden in subclasses as needed.

		return

	def getFrom (self):
		# Purpose: return the e-mail address which should be used as
		#	the 'From' address for the message we'll send
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: Subclasses may override this method to provide access
		#	to any e-mail address submitted by the user, if
		#	needed.

		return 'unknown'

	def main(self):
		# Purpose: main processing loop.  check the parameters for
		#	validity and completeness.  send an e-mail if 
		#	able.  send an HTML reponse to the user.
		# Returns: nothing
		# Assumes: nothing
		# Effects: writes an HTML page to stdout; sends an e-mail
		#	if possible
		# Throws: propagates any exceptions (none caught here)

		# look for any missing fields:  (bail out if any found)

		missing_fields = []
		for field in self.required_fields:
			if not self.parms.has_key (field):
				missing_fields.append (self.labels[field])
		if missing_fields:
			handleError (MISSING_FIELDS % \
				string.join (missing_fields, ', '),
				self.form_name,
				self.header,
				self.footer
				)
			return

		# do any pre-validation processing

		self.doPreValidationProcessing()

		# validate the input parameters as needed

		failed_checks = self.doValidations()
		if failed_checks:
			list = []
			for (field, error) in failed_checks:
				list.append ('<DT>%s<DD>%s' % \
					(self.labels[field], error))
			handleError (FAILED_CHECKS % string.join (list, '\n'),
				self.form_name,
				self.header,
				self.footer
				)
			return

		# do any post-validation processing

		self.doPostValidationProcessing()

		# Compose the message to be sent, breaking it into sections
		# if we were given any section definitions at instantiation-
		# time.  Note that field values will appear indented on the
		# line below the field label.  For fields with multiple
		# values, each will appear on a separate line indented under
		# the label.

		message = []	# list of strings; e-mail message to send

		if self.sections:
		    # do grouping into sections with headings

		    for (heading, fieldlist) in self.sections:
			section = [
			    '-' * len(heading),
			    heading,
			    '-' * len(heading),
			    ]
			for field in fieldlist:
			    if self.parms.has_key(field):
				section.append(self.labels[field])
				if type(self.parms[field]) == types.ListType:
				    for item in self.parms[field]:
				    	section.append('\t%s' % item)
				else:
				    section.append('\t%s' % self.parms[field])

			# if the section had fields submitted, add it to the
			# e-mail message

			if len(section) > 3:
			    message = message + section
		else:
		    # no sections - just alphabetize the fields by label

		    fields = self.parms.keys()
		    list = []
		    for field in fields:
			list.append ((self.labels[field], field))
		    list.sort()

		    for (label, field) in list:
		    	message.append (self.labels[field])
			if type(self.parms[field]) == types.ListType:
			    for item in self.parms[field]:
			        message.append('\t%s' % item)
			else:
			    message.append ('\t%s' % self.parms[field])

		# compile the list of strings into a single string to e-mail

		message = string.join (message, '\n')

		# send the message and give the user an appropriate page of
		# feedback

		sentCode = mgi_utils.send_Mail (
			self.getFrom(),
			self.address,
			'%s Submission' % self.form_name,
			message
			)

		if sentCode == 0:		# successful
		    print MESSAGE_SENT % (
		    	self.header,
			self.form_name,
			message,
			self.footer)
		else:				# unsuccessful
		    print MESSAGE_FAILED % (
		    	self.header,
			self.form_name,
			self.footer)

		return

###--- Example Usage ---###

#	myCGI = formMailer.formMailer ('Address Submission',
#			'test@informatics.jax.org',
#			{ 'first' : 'First Name',
#			  'mid'   : 'Middle Initial',
#			  'last'  : 'Last Name',
#			  'street': 'Street',
#			  'city'  : 'City',
#			  'state' : 'State/Province',
#			  'zip'   : 'ZIP/Postal Code'
#			},
#			[ 'first', 'last', 'city', 'state', 'zip' ],
#			[ ('Individual',
#				[ 'last', 'first', 'mid' ]),
#			  ('Address',
#				[ 'street', 'city', 'state', 'zip' ])
#			])
#	myCGI.go()
