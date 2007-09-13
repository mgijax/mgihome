# Name: feedbacklib.py
# Purpose: to provide needed classes and functions for the "Your Input"
#	forms

import sys			# standard Python libraries
if '.' not in sys.path:
	sys.path.insert (0, '.')
import os
import string
import cgi

# import config			# MGI-written libraries

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import homelib
import header
import mgi_utils

###--- Global Constants ---###

OPTIONAL = 0			# values to indicate whether a Field is
REQUIRED = 1			# required or optional

MARKER_TYPE = 2			# list all needed MGI Type keys here
ASSAY_TYPE = 8
ALLELE_TYPE = 11

# Email changed (circumventing rememdy) in 3.54 - see TR8365
RECIPIENT = 'mgi-help@informatics.jax.org' 

MAIL_HEADER = '''From: %s
To: %s
Subject: %s

'''

REMEDY_MESSAGE = '''#
#  %s
#
#AR-Message-Begin             Do Not Delete This Line
Schema: TJL-Inbox
Server: arserver.jax.org
Login: webmail
Password: webuser1
Action: Submit
# Values: Submit, Query
Format: Short
# Values: Short, Full

%s

#AR-Message-End             Do Not Delete This Line
''' % (mgi_utils.date(), '%s')

ALLOWED_TYPES = [2,  # markers
		 8,  # assays
		 11  # alleles
		]

###--- Remedy-Template Functions ---###

# These two functions are modeled after the formatting embedded in the
# www/support/tjl_submit_inbox.cgi script.

def style20 (
	fieldname,	# string; name of the input field
	fieldID,	# string; id number corresponding to that field
	value		# string; value entered for that field (may be '')
	):
	# Purpose: format the parameters into a line of e-mail for Remedy,
	#	formatted with twenty columns for the fieldname
	# Returns: string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	template = '%s !%s!:%s'
	return template % (string.rjust (fieldname, 20),
			string.rjust (fieldID, 9), value)

def style21 (
	fieldname,	# string; name of the input field
	fieldID,	# string; id number corresponding to that field
	value		# string; value entered for that field (may be '')
	):
	# Purpose: format the parameters into a line of e-mail for Remedy,
	#	formatted with twenty-one columns for the fieldname
	# Returns: string
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	template = '%s!%s!: %s'
	return template % (string.rjust (fieldname, 21),
			string.rjust (fieldID, 9), value)

###--- Class-Checking Functions ---###

def isSubclassOf (
	a,		# class; prospective child class
	b		# class; prospective parent class
	):
	# Purpose: determine if 'a' is a subclass of 'b'
	# Returns: boolean (0/1)
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing
	# Notes: A class 'x' is defined to be a subclass of itself.  (That
	#	is, 'a' is a subclass of 'b' even if 'a' and 'b' are the same
	#	class.)

	if a == b:
		return 1
	for parent_a in a.__bases__:		# go through multiple parents
		if isSubclassOf (parent_a, b):
			return 1
	return 0

def isInstanceOf (
	inst,		# instance; an instance of some class
	clas		# class; prospective parent class
	):
	# Purpose: determine if 'inst' is an instance of 'clas' (or a subclass
	#	of 'clas')
	# Returns: boolean (0/1)
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing

	if str(type(inst)) != "<type 'instance'>":
		return 0
	return isSubclassOf (inst.__class__, clas)

###--- Classes ---###

# Our class hierarchy is:
#	Field
#	|------	HiddenField
#	|------	OneLineTextField
#	|	|------	AlleleSubjectField
#	|	|------	MarkerSubjectField
#	|------	MultiLineTextField
#
#	UserInput
#	|------	SimpleTextUserInput
#	|	|------	AlleleUserInput
#	|	|------	MarkerUserInput

class Field:
	# Concept:
	#	IS: a data-entry field
	#	HAS: a label, a fieldname, a value, an HTML representation,
	#		a validation procedure, and knowledge of whether
	#		it is required to have a value
	#	DOES: knows how to set/get instance variables, to validate
	#		itself, to set its value based on a set of input
	#		parameters, and to represent itself using HTML

	def __init__ (self,
		fieldname,		# string; name of the field (internal)
		label,			# string; name to display to the user
		required = OPTIONAL,	# is the field OPTIONAL or REQUIRED?
		value = None		# string; initial value for the field
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables
		# Throws: nothing

		self.fieldname = fieldname
		self.label = label
		self.required = required
		self.value = value
		self.errors = []	# list of errors from validation()
		return

	def getErrors (self):
		# Purpose: return the list of errors discovered when this
		#	Field was last validated()
		# Returns: list of string error messages, may be empty
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.errors

	def getLabel (self):
		# Purpose: return this Field's label (the name to be displayed
		#	to the user)
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.label

	def getValue (self):
		# Purpose: return this Field's value
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.value

	def getHTML (self):
		# Purpose: return an HTML representation of this Field
		# Returns: string with HTML markups
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: subclasses should generally override this method

		return '<B>%s</B>: %s<BR>' % (self.label, self.value)

	def isRequired (self):
		# Purpose: return OPTIONAL or REQUIRED, indicating whether
		#	this Field is required to have a value
		# Returns: integer -- OPTIONAL or REQUIRED
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return self.required

	def setValue (self,
		value		# string; new value for this Field
		):
		# Purpose: set the value for this Field object to be that
		#	given in 'value'
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates self.value and runs the validation()
		#	method to update self.errors
		# Throws: nothing

		self.value = value
		self.validate()
		return

	def setLabel (self,
		label		# string; new label for this Field
		):
		# Purpose: set this Field's label to be that given in 'label'
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates self.label
		# Throws: nothing

		self.label = label
		return

	def set (self,
		parms		# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: take a set of parameters ('parms') from an HTML
		#	form, and if this Field's fieldname is one of the
		#	included fields, get its new value from 'parms'
		# Returns: nothing
		# Assumes: nothing
		# Effects: may update self.value and call the validate()
		#	function to update self.errors
		# Throws: nothing

		if parms.has_key (self.fieldname):
			self.value = parms[self.fieldname]
		self.validate()
		return

	def validate (self):
		# Purpose: ensure that the current value of this field is
		#	valid, and if not, update the list of errors
		#	accordingly.
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates self.errors
		# Throws: nothing
		# Notes: The only validation rule is that required fields
		#	must contain a value.

		if self.required and not self.value:
			self.errors = ['%s is a required field.' % self.label]
		else:
			self.errors = []
		return

class HiddenField (Field):
	# Concept:
	#	IS: a Field which should not be displayed to the user in an
	#		HTML form, but which should have its value passed
	#		along as a hidden field
	#	HAS: see Field
	#	DOES: see Field

	def getHTML (self):
		# Purpose: return the HTML representation of this HiddenField
		# Returns: string with HTML markups
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return '<INPUT TYPE=hidden NAME="%s" VALUE="%s">' % \
			(self.fieldname, self.value)

class OneLineTextField (Field):
	# Concept:
	#	IS: a Field which should appear in an HTML form as a one-line
	#		box for text input
	#	HAS: see Field
	#	DOES: see Field

	def __init__ (self,
		fieldname,		# string; name of the field (internal)
		label,			# string; name to display to the user
		required = OPTIONAL,	# is the field OPTIONAL or REQUIRED?
		value = None,		# string; initial value for the field
		width = None,		# integer; width of displayed box
		maxSize = None		# integer; max number of chars allowed
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables
		# Throws: nothing
		# Notes: We call the parent class's constructor first, then
		#	add additional instance variables.

		Field.__init__ (self, fieldname, label, required, value)
		self.width = width
		self.maxSize = maxSize
		return

	def getHTML (self):
		# Purpose: return an HTML representation of this object
		# Returns: string with HTML markups
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: We must handle the optional width, maxSize, and
		#	value instance variables appropriately.

		s = 'INPUT TYPE=text NAME="%s"' % self.fieldname
		if self.width:
			s = s + ' SIZE=%s' % self.width
		if self.maxSize:
			s = s + ' MAXLENGTH=%s' % self.maxSize
		if self.value:
			s = s + ' VALUE="%s"' % self.value
		return '<%s>' % s

class MultiLineTextField (Field):
	# Concept:
	#	IS: a Field which should appear in an HTML form as a multi-
	#		line box for text input
	#	HAS: see Field
	#	DOES: see Field

	def __init__ (self,
		fieldname,		# string; name of the field (internal)
		label,			# string; name to display to the user
		required = OPTIONAL,	# is the field OPTIONAL or REQUIRED?
		value = None,		# string; initial value for the field
		height = None,		# integer; height of displayed box
		width = None		# integer; width of displayed box
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables
		# Throws: nothing
		# Notes: We call the parent class's constructor first, then
		#	add additional instance variables.

		Field.__init__ (self, fieldname, label, required, value)
		self.height = height
		self.width = width
		return

	def getHTML (self):
		# Purpose: return an HTML representation of this object
		# Returns: string with HTML markups
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: We must handle the optional width, height, and
		#	value instance variables appropriately.

		s = 'TEXTAREA NAME="%s"' % self.fieldname
		if self.width:
			s = s + ' COLS=%s' % self.width
		if self.height:
			s = s + ' ROWS=%s' % self.height
		if self.value:
			s = '<%s>%s</TEXTAREA>' % (s, self.value)
		else:
			s = '<%s></TEXTAREA>' % s
		return s


class AssaySubjectField (OneLineTextField):
	# Concept:
	#	IS: a OneLineTextField which represents the subject for
	#		an Assay page
	#	HAS: see Field
	#	DOES: see Field; also provides a new method whereby we can
	#		set the field's value given an assay's accession ID

	def setByAcc (self,
		parms		# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: set the value of this AssaySubjectField based on
		#	an accession number ('accID') which may be contained
		#	in 'parms'
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates self.value and calls the validate() method
		#	which updates self.error
		# Throws: nothing
		# Notes: We set the value of this field to be as detailed
		#	as possible, depending on whether 'parms' includes an
		#	'accID' parameter and whether we can find an allele
		#	subject value corresponding to a specified
		#	accession number.

		subj = 'RE: Assay'
		if parms.has_key ('accID'):
			subj = '%s (%s)' % (subj, parms['accID'])
		self.value = subj
		self.validate()
		return


class AlleleSubjectField (OneLineTextField):
	# Concept:
	#	IS: a OneLineTextField which represents the subject for
	#		an Allele page
	#	HAS: see Field
	#	DOES: see Field; also provides a new method whereby we can
	#		set the field's value given an allele's accession ID

	def setByAcc (self,
		parms		# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: set the value of this AlleleSubjectField based on
		#	an accession number ('accID') which may be contained
		#	in 'parms'
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates self.value and calls the validate() method
		#	which updates self.error
		# Throws: nothing
		# Notes: We set the value of this field to be as detailed
		#	as possible, depending on whether 'parms' includes an
		#	'accID' parameter and whether we can find an allele
		#	subject value corresponding to a specified
		#	accession number.

		subj = 'RE: Allele'
		if parms.has_key ('accID'):
			result = homelib.sql ('''
				select a.symbol
				from ALL_Allele a, ACC_Accession acc
				where acc._MGIType_key = %d
					and acc._Object_key = a._Allele_key
					and acc.accID = "%s"
					''' % \
				(ALLELE_TYPE, parms['accID']), 'auto')
			if len(result) > 0:
				subj = '%s %s (%s)' % (subj,
							result[0]['symbol'],
							parms['accID'])
			else:
				subj = '%s (%s)' % (subj, parms['accID'])
		self.value = subj
		self.validate()
		return

class MarkerSubjectField (OneLineTextField):
	# Concept:
	#	IS: a OneLineTextField which represents the subject for
	#		a Marker page
	#	HAS: see Field
	#	DOES: see Field; also provides a new method whereby we can
	#		set the field's value given a marker's accession ID

	def setByAcc (self,
		parms		# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: set the value of this MarkerSubjectField based on
		#	an accession number ('accID') which may be contained
		#	in 'parms'
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates self.value and calls the validate() method
		#	which updates self.error
		# Throws: nothing
		# Notes: We set the value of this field to be as detailed
		#	as possible, depending on whether 'parms' includes an
		#	'accID' parameter and whether we can find a marker
		#	subject and type corresponding to a specified
		#	accession number.

		if parms.has_key ('accID'):
			result = homelib.sql ('''
				select m.symbol, t.name
				from MRK_Marker m,
					ACC_Accession a,
					MRK_Types t
				where a._MGIType_key = %d
					and a._Object_key = m._Marker_key
					and a.accID = "%s"
					and m._Marker_Type_key =
						t._Marker_Type_key
				''' % (MARKER_TYPE, parms['accID']), 'auto')
			if len(result) > 0:
				subj = 'RE: %s %s (%s)' % (result[0]['name'],
							result[0]['symbol'],
							parms['accID'])
			else:
				subj = 'RE: Marker (%s)' % (parms['accID'])
		else:
			subj = 'RE: Marker'
		self.value = subj
		self.validate()
		return

class UserInput:
	# Concept:
	#	IS: a set of input from the user, corresponding to a
	#		feedback form (with its fields and their respective
	#		values)
	#	HAS: a collection of Field objects, including firstName,
	#		lastName, institution, email, subject, accID,
	#		dataDate, and referer.
	#	DOES: has public methods to print a form to collect the user's
	#		input, to set Field values according to CGI input,
	#		to validate the input, to send e-mail to the Remedy
	#		system, and to print a confirmation page for the user
	# Implementation:
	#	Each Field is an instance variable in the object.

	###--- Public Methods ---###

	def __init__ (self,
		parms = {}	# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables and updates their
		#	values according to any 'parms' passed in
		# Throws: nothing

		# basic data entry fields

		self.subject = OneLineTextField ('subject', 'Subject',
			REQUIRED, 'A suggestion', width=45)
		self.firstName = OneLineTextField ('firstname', 'First Name',
			REQUIRED, width=30)
		self.lastName = OneLineTextField ('lastname', 'Last Name',
			REQUIRED, width=30)
		self.email = OneLineTextField ('email', 'E-mail address',
			REQUIRED, width=30)
		self.institution = OneLineTextField ('institution',
			'Institution', OPTIONAL, width=30)

		# hidden fields set by the system, for context information

		self.accID = HiddenField ('accID', 'MGI Acc ID', OPTIONAL)
		self.dataDate = HiddenField ('dataDate', 'Data Dump Date',
			OPTIONAL)
		self.referer = HiddenField ('referer', 'Referring Page',
			OPTIONAL)

		# If we received any parameters, use them to set the values
		# of the instance variables.

		if parms:
			self.setFields (parms)

		# if the referring page wasn't passed in as a parameter, and
		# if we have information about it, then set it.

		if not self.referer.getValue() and \
				os.environ.has_key ('HTTP_REFERER'):
			self.referer.setValue (os.environ['HTTP_REFERER'])
		return

	def setFields (self,
		parms		# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: take the set of 'parms' and uses them to update
		#	the values of this object's instance variables
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates the values of this object's instance
		#	variables
		# Throws: nothing
		# Notes: We pass the parameters along to the set() method of
		#	any instance variable that is an object.  Each object
		#	knows how to updates its value based on 'parms'.

		for key in self.__dict__.keys():
			if isInstanceOf (self.__dict__[key], Field):
				self.__dict__[key].set (parms)
		return

	def sendMail (self):
		# Purpose: send an e-mail containing the user's input to a
		#	designated e-mail address
		# Returns: nothing
		# Assumes: nothing
		# Effects: sends an e-mail
		# Throws: nothing

		# check to see if we have a developer override for email

		if config.has_key('CGI_MAILTARGET'):
                	RECIPIENT = config['CGI_MAILTARGET']
		# send the mail

		fd = os.popen ('%s -t' % config['SENDMAIL'], 'w')
		fd.write (MAIL_HEADER % (self.email.getValue(),
					RECIPIENT,
					self.subject.getValue()))
		fd.write (REMEDY_MESSAGE % self.getEmailString())
		fd.close()
		return

	def validate (self):
		# Purpose: validate the values of this object's Fields and
		#	return a list of errors found
		# Returns: list of error strings (may be an empty list)
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: Each Field validates itself whenever its value is
		#	set.  We just collect the error messages here.

		errorList = []
		for key in self.__dict__.keys():
			if isInstanceOf (self.__dict__[key], Field):
				errorList = errorList + \
					self.__dict__[key].getErrors()
		return errorList

	def printInputPage (self):
		# Purpose: send to stdout an HTML page with form fields
		#	for the user to submit his/her input
		# Returns: nothing
		# Assumes: the CGI script that processes the form is in
		#	the current directory and is named "feedback.cgi"
		# Effects: builds an HTML page and writes it to stdout
		# Throws: nothing

		# build the top of the page, above the first data fields

		topOfPage = [
			'<HTML><HEAD><TITLE>Your Input Welcome</TITLE>',
			'</HEAD><BODY bgcolor=ffffff>',
			header.bodyStart(),
			header.headerBar('Your Input Welcome'),
			'''We want to hear from you.  Use this form to submit
			updates to the information in our
			database.  Please enter the contact information in the
			fields below so we can respond to you.  Be as detailed
			in your message as possible, and please include
			references as appropriate.  We appreciate your input
			and comments, and will review them promptly.''',
			'<FORM METHOD=post ACTION=feedback.cgi>',
			]

		# build the top of the form, with the fields which are
		# standard at the top of each Your Input page

		topOfForm = [ '<TABLE>',
			'<TR><TD>%s<TD>%s</TABLE>' % (self.subject.getLabel(),
						self.subject.getHTML()),
			'<H3>From</H3>',
			'<TABLE>',
			]
		for item in [ self.firstName, self.lastName,
				self.institution, self.email ]:
			topOfForm.append ('<TR><TD>%s<TD>%s' % \
				(item.getLabel(), item.getHTML()))
		topOfForm.append ('</TABLE>')

		for item in [ self.accID, self.dataDate, self.referer ]:
			if item.getValue():
				topOfForm.append (item.getHTML())

		# build the bottom of the page, including the buttons at the
		# bottom of the form and any footer info

		bottomOfPage = [ '<HR>',
			'<INPUT TYPE=submit VALUE=Submit>',
			'<INPUT TYPE=reset>',
			'<INPUT TYPE=button VALUE="Cancel" ',
			'	onClick="window.close()">',
			'</FORM><HR>',
			header.bodyStop(),
			'</BODY></HTML>' ]

		# print the complete page to stdout

		print string.join (topOfPage, '\n')
		print string.join (topOfForm, '\n')
		self.printFormExtra()
		print string.join (bottomOfPage, '\n')
		return

	def printConfirmationPage (self):
		# Purpose: send to stdout an HTML page which confirms the
		#	values submitted by the user
		# Returns: nothing
		# Assumes: nothing
		# Effects: writes an HTML page to stdout
		# Throws: nothing

		pageItems = [
			'<HTML><HEAD><TITLE>Confirmation</TITLE></HEAD>',
			'<BODY bgcolor=ffffff>',
			header.bodyStart(),
			header.headerBar('Confirmation'),
			'<BR>',
			'Thank you for contacting the Mouse Genome Database.',
			'We appreciate your input and comments, and will ',
			'review them promptly.<P>',
			'<HR><PRE>',
			self.getPlainText (),
			'</PRE><HR>',
			header.bodyStop(), 
			'</BODY></HTML>' ]
		print string.join (pageItems, '\n')
		return

	###--- Private Methods ---###

	def printFormExtra (self):
		# Purpose: print to stdout any extra form fields, in addition
		#	to the standard set already printed within the
		#	printInputPage method
		# Returns: nothing
		# Assumes: nothing
		# Effects: writes HTML-formatted text to stdout
		# Throws: nothing
		# Notes: In this class, this method is a no-op.  It is
		#	intended to be defined in subclasses as needed to
		#	support extra fields.

		return

	def getEmailString (self):
		# Purpose: build and return a string which defines the data
		#	Fields and their values, in a format that Remedy can
		#	understand
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: This very odd format is patterned after that which
		#	currently exists in the tjl_submit_inbox.cgi script,
		#	so we can have this data go into the same Remedy
		#	schema.

		lines = []		# will add one string per Field

		# each item in 'fields' is a tuple containing:
		#	(Remedy fieldname, Remedy field ID, field value,
		#		function to use to format it)

		fields = [
			('title', '536870924', '', style20),
			('F_Name', '536870913', self.firstName.getValue(),
				style20),
			('L_Name', '536870914', self.lastName.getValue(),
				style20),
			('em', '536870915', self.email.getValue(), style20),
			('in-ph', '536870920', '', style20),
			('in-fax', '536870922', '', style20),
			('inst', '536870921', self.institution.getValue(),
				style20),
			('Position', '536870925', '', style20),
			('Request Summary', '8', self.subject.getValue(),
				style20),
			('Request Details', '536870916', self.getDetails(),
				style20),
			('Submitter', '2', 'webmail', style21),
			('Status', '7', 'New', style21),
			('ATTN', '536870923', '', style20),
			('jax_domain', '536870919', 'MGI', style20),
			]
		for (remedyName, remedyID, value, style) in fields:
			lines.append (style (remedyName, remedyID, value))
		return string.join (lines, '\n')

	def getDetails (self):
		# Purpose: build and return a string which includes a string
		#	of "details" to go in the e-mail message.  This should
		#	probably include any field not submitted separately
		#	in self.getEmailString()
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: The Remedy schema does not have separate fields for
		#	each Field in this UserInput.  This method bundles up
		#	those without Remedy support so they may be included
		#	in Remedy's "Request Details" field.

		list = []
		for field in [ self.accID, self.dataDate, self.referer ]:
			list.append ('%s: %s' % (field.getLabel(),
				field.getValue()))
		return string.join (list, '\n')

	def getPlainText (self,
		fields = ['subject',	# fieldnames to include in the text
			'firstName',
			'lastName',
			'institution',
			'email']
		):
		# Purpose: build and return a string containing the field
		#	label and field value for the given set of 'fields'
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: We specify the list of fields as a parameter to
		#	allow for easy overriding in subclasses.  (with no
		#	extra coding).  We do need to escape the field values
		#	so that any < and > characters will appear correctly.

		lines = []
		for fieldname in fields:
			item = self.__dict__[fieldname]
			if item.getValue():
				value = cgi.escape (homelib.wrapLines (
					item.getValue(),  60))
				if len(value) > 60:
					value = '\n' + value
				lines.append ('%s: %s' % (item.getLabel(),
					value))
		return string.join (lines, '\n')

class SimpleTextUserInput (UserInput):
	# Concept:
	#	IS: a UserInput object which has an additional multi-line
	#		text field for "Your Comments" and some associated
	#		instructions
	#	HAS: see UserInput (and IS)
	#	DOES: see UserInput

	def __init__ (self,
		parms = {}	# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables
		# Throws: nothing

		# Note that we do not pass 'parms' to the superclass
		# constructor.  This is so that we only set the parameter
		# values once -- at the end of this method.

		UserInput.__init__ (self)
		self.comments = MultiLineTextField (
			'comments',
			'Your Comments',
			OPTIONAL,
			height=8,
			width=60)
		self.commentInstructions = ''	# instr. to go w/self.comment
		self.setFields (parms)
		return

	def printFormExtra (self):
		# Purpose: print to stdout the extra section for "Your
		#	Comments"
		# Returns: nothing
		# Assumes: nothing
		# Effects: writes HTML-formatted text to stdout
		# Throws: nothing

		extras = [ '<H3>Your Comments:</H3>',
			self.commentInstructions,
			self.comments.getHTML(),
			]
		print string.join (extras, '\n')
		return

	def getDetails (self):
		# Purpose: build and return a string which includes a string
		#	of "details" to go in the e-mail message.  This should
		#	probably include any field not submitted separately
		#	in self.getEmailString()
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: We use the superclass's getDetail() method to build
		#	the basic string, and then simply add the "Your
		#	Comments" field to it.

		list = [ UserInput.getDetails (self),
			'%s: %s' % (self.comments.getLabel(),
				self.comments.getValue()),
			]
		return string.join (list, '\n')

	def getPlainText (self):
		# Purpose: build and return a string containing the field
		#	label and field value for the given set of 'fields'
		# Returns: string
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing
		# Notes: This is simply a wrapper over the superclass's
		#	getPlainText() method.

		return UserInput.getPlainText (self, fields = [ 'subject',
			'firstName', 'lastName', 'institution', 'email', 
			'comments' ])

class AssayUserInput (SimpleTextUserInput):
	# Concept:
	#	IS: a SimpleTextUserInput object which has a set of "Your
	#		Comment" instructions particular to assays, and
	#		a subject field which is assays-specific
	#	HAS: see SimpleTextUserInput (and IS)
	#	DOES: see SimpleTextUserInput

	def __init__ (self,
		parms = {}	# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables
		# Throws: nothing
		# Notes: Take note of the order in which we do things here.
		#	We first call the superclass constructor to set up
		#	the standard instance variables.  We then set a new
		#	value for the commentInstructions, and change the
		#	subject attribute to be an AssaySubjectField.  We
		#	set its value according to any accID which was passed
		#	in.  Finally, we use the parameters to set the new
		#	values for all instance variables.  This ensures that
		#	any values submitted by the user override the default
		#	values.

		SimpleTextUserInput.__init__ (self)
		self.commentInstructions = '''Use this space to enter comments
		    regarding the annotation of this assay; your comments will
		    be reviewed and appropriate action taken.  For comments or 
		    suggestions regarding the content of the Gene Expression 
		    Database, contact <a href="%ssupport/tjl_inbox.shtml">User Support</a>.<BR>'''\
			% config['MGIHOME_URL']
		self.subject = AssaySubjectField ('subject', 'Subject',
			REQUIRED, width=45)
		self.subject.setByAcc (parms)
		self.setFields (parms)
		return


class AlleleUserInput (SimpleTextUserInput):
	# Concept:
	#	IS: a SimpleTextUserInput object which has a set of "Your
	#		Comment" instructions particular to alleles, and
	#		a subject field which is allele-specific
	#	HAS: see SimpleTextUserInput (and IS)
	#	DOES: see SimpleTextUserInput

	def __init__ (self,
		parms = {}	# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables
		# Throws: nothing
		# Notes: Take note of the order in which we do things here.
		#	We first call the superclass constructor to set up
		#	the standard instance variables.  We then set a new
		#	value for the commentInstructions, and change the
		#	subject attribute to be an AlleleSubjectField.  We
		#	set its value according to any accID which was passed
		#	in.  Finally, we use the parameters to set the new
		#	values for all instance variables.  This ensures that
		#	any values submitted by the user override the default
		#	values.

		SimpleTextUserInput.__init__ (self)
		self.commentInstructions = '''Use this space to suggest
			modifications and additions to the annotations for
			this allele (e.g., allele synonyms, allele-specific
			sequence identifiers, references, phenotypes).  For
			new allele submissions, please use the
			<a href="../nomen/allmut_form.shtml">Allele and New
			Mutant Submission Form</a>.
			For all other comments and suggestions, contact 
			<a href="%ssupport/tjl_inbox.shtml">User
			Support</a>.<BR>''' % config['MGIHOME_URL']
		self.subject = AlleleSubjectField ('subject', 'Subject',
			REQUIRED, width=45)
		self.subject.setByAcc (parms)
		self.setFields (parms)
		return

class MarkerUserInput (SimpleTextUserInput):
	# Concept:
	#	IS: a SimpleTextUserInput object which has a set of "Your
	#		Comment" instructions particular to markers, and
	#		a subject field which is marker-specific
	#	HAS: see SimpleTextUserInput (and IS)
	#	DOES: see SimpleTextUserInput

	def __init__ (self,
		parms = {}	# dictionary; parms[fieldname] = fieldvalue
		):
		# Purpose: constructor
		# Returns: nothing
		# Assumes: nothing
		# Effects: initializes instance variables
		# Throws: nothing
		# Notes: Take note of the order in which we do things here.
		#	We first call the superclass constructor to set up
		#	the standard instance variables.  We then set a new
		#	value for the commentInstructions, and change the
		#	subject attribute to be an MarkerSubjectField.  We
		#	set its value according to any accID which was passed
		#	in.  Finally, we use the parameters to set the new
		#	values for all instance variables.  This ensures that
		#	any values submitted by the user override the default
		#	values.

		SimpleTextUserInput.__init__ (self)
		self.commentInstructions = '''Use this space to suggest
			modifications and additions to the annotations for
			this marker (e.g., synonyms, sequence identifiers,
			references, gene ontology terms).  For new allele
			submissions, please use the
			<a href="../nomen/allmut_form.shtml">Allele and New
			Mutant Submission Form</a>.
			For all other comments and suggestions, contact 
			<a href="%ssupport/tjl_inbox.shtml">User
			Support</a>.<BR>''' % config['MGIHOME_URL']
		self.subject = MarkerSubjectField ('subject', 'Subject',
			REQUIRED, width=45)
		self.subject.setByAcc (parms)
		self.setFields (parms)
		return

###--- Functions ---###

def getInputObj (
	parms = {}		# dictionary; parameters from CGI
	):
	# Purpose: return a UserInput object or an object of the appropriate
	#	subclass for the given 'parms'
	# Returns: a UserInput object (or an object of a UserInput subclass)
	# Assumes: nothing
	# Effects: queries the database to learn the MGI Type corresponding to
	#	the input 'parms', then builds and returns an object
	# Throws: propagates any exceptions raised by homelib.sql()

	# if we do not have an accession ID, then just fall back on the
	# SimpleTextUserInput form, containing the basic fields and a big
	# text box for "Your Comments".
	
	inp = SimpleTextUserInput (parms)
	
	result = homelib.sql ('''select _MGIType_key
			from ACC_Accession
			where accID = "%s"''' % parms['accID'],
			'auto')

	for mgiType in result:
		if mgiType['_MGIType_key'] in ALLOWED_TYPES:
			# return an object of the appropriate
			# subclass.  (or fall back on the default if no
			# special subclass is defined)

			if mgiType['_MGIType_key'] == MARKER_TYPE:
				inp = MarkerUserInput (parms)

			elif mgiType['_MGIType_key'] == ALLELE_TYPE:
				inp = AlleleUserInput (parms)

			elif mgiType['_MGIType_key'] == ASSAY_TYPE:
				inp = AssayUserInput (parms)

			# add handling here for other MGI Types as needed...

			else:
				inp = SimpleTextUserInput (parms)
	return inp
