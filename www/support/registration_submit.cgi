#!./python

# Program: registration_submit.cgi
# Purpose: handle the parameters submitted by the user from the "user
#	registration" form , do error checking, send a specially-formatted
#	e-mail to Remedy, and give the user a confirmation page.

import sys
if '.' not in sys.path:
	sys.path.insert (0, '.')

import string
import types
import os

import config
import feedbacklib	# used for style20() and style21() functions
import homelib
import CGI
import errorlib
import mgi_utils

###--- Aliases ---###

style20 = feedbacklib.style20		# alias for formatting
style21 = feedbacklib.style21		# alias for formatting

###--- Globals ---###

RECIPIENT = 'arsystem@jax.org'		# recipient of Remedy e-mail message
REPLY_TO = 'ps@informatics.jax.org'	# who to reply to?  (legacy)
BLANK = ''				# no default value for field

MAIL_HEADER = '''Reply-to: %s
Subject: Express Mail

'''

# 'fields' is sorted according to the order of fields in the Remedy message
# we are to compose.  Each entry includes:
#	(web label, web fieldname, web required?, default value,
#		Remedy fieldname, Remedy ID, format for Remedy using...)

fields = [
	(None, None, 0, 'MGI',				# Remedy-only
		'Client Type', '536870935', style20),
	('Last name', 'lastname', 1, BLANK,
		'L_name', '536870914', style20),
	('First name', 'firstname', 1, BLANK,
		'First Name', '536870913', style20),
	('Middle initial', 'mi', 0, BLANK,
		'MI', '536870915', style20),
	('Title', 'prof-title', 1, BLANK,
		'title', '536870927', style20),
	('Position', 'position', 0, BLANK,
		'Position', '536870936', style20),
	('Other Position', 'otherpos', 0, BLANK,	# Web-only
		None, None, None),
	('Institution', 'tute', 1, BLANK,
		'Inst', '536870916', style20),
	('Institution Type', 'intype', 1, BLANK,
		'inst_type', '536870932', style20),
	('Department', 'Dept', 0, BLANK,
		'Dept', '536870917', style20),
	('Street 1', 'st', 0, BLANK,
		'St', '536870918', style20),
	('Street 2', 'st2', 0, BLANK,
		'St2', '536870928', style20),
	('City', 'cty', 0, BLANK,
		'cty', '536870919', style20),
	('State/Province', 'state', 0, BLANK,
		'state', '536870920', style20),
	('Postal Code', 'zip', 0, BLANK,
		'zip', '536870922', style20),
	('Country', 'ctry', 0, BLANK,
		'ctry', '536870921', style20),
	('E-mail address', 'emailaddr', 0, BLANK,
		'em', '536870923', style20),
	('Phone', 'ph', 1, BLANK,
		'ph', '536870924', style20),
	('Fax #', 'fx', 0, BLANK,
		'fx', '536870925', style20),
	('Purchase TJL Mice?', 'mice', 0, "n/a",
		'comments', '536870938', style20),
	('Computer', 'damncmptrs', 0, BLANK,
		'Computers', '536870930', style20),
	('Other Computer', 'spec', 0, BLANK,		# Web-only
		None, None, None),
	('Operating System', 'opsys', 0, BLANK,
		'opsys', '536870940', style20),
	('WWW Browser', 'browser', 0, "Netscape",
		'browsers', '536870931', style20),
	('Internet Connection', 'net', 1, BLANK,
		'internet_acc', '536870934',
		style20),
	(None, None, 0, "webmail",			# Remedy-only
		'Submitter', '2', style21),
	(None, None, 0, BLANK,				# Remedy-only
		'Status', '7', style21),
	]

###--- Functions ---###

def parse_parameters (
	parms		# dictionary mapping each fieldname to either a
			# string (single-valued fields) or a list of strings
			# (for multi-valued fields)
	):
	# Purpose: parse the given 'parms' to update the default values for
	#	fields as specified in 'fields'.  do simple error checking.
	# Returns: (dict, errors) -- see local variable defs below
	# Assumes: nothing
	# Effects: nothing
	# Throws: nothing
	# Notes: The "special handling" section of this function is coupled 
	#	to certain web and Remedy fieldnames, as they are defined in
	#	'fields'.

	missing = []	# list of labels for fields which are required, but
			#	not specified by the user
	dict = {}	# dictionary mapping remedy fieldname to value, to be
			#	built and returned
	errors = []	# list of errors detected while parsing parameters

	###--- standard handling for fields ---###

	# go through the list of 'fields' and update 'dict' accordingly

	for (www_label, www_fieldname, www_required, default_value,
			rem_fieldname, rem_id, format_function) in fields:

		dict[rem_fieldname] = default_value
		if www_label is None:
			continue

		if not parms.has_key (www_fieldname):
			if www_required:
				missing.append (www_label)

		elif type (parms[www_fieldname]) == types.StringType:
			dict[rem_fieldname] = parms[www_fieldname]

		elif type (parms[www_fieldname]) == types.ListType:
			dict[rem_fieldname] = string.join ( \
				parms[www_fieldname], ', ')

		else:
			dict[rem_fieldname] = 'Unknown parameter type'

	# if any required fields were missing, add an error for them:

	if missing:
		errors.append ('''Please fill in the following required
			fields: %s''' % string.join (missing, ', '))

	###--- special handling for a few fields ---###

	# prepend a phrase to the 'comments' field:

	dict['comments'] = 'mice buyer: ' + dict['comments']

	# If the user specifies an 'Other' Position, handle it:

	if parms.has_key ('otherpos'):
		if dict['Position'] != 'Other':
			errors.append ('''Please <I>either</I> choose one of
				the standard Positions <I>or</I> choose
				'Other' and enter a non-standard one.''')
		else:
			dict['Position'] = parms['otherpos']

	# If the user specifies an 'Other' Computer, handle it:

	if parms.has_key ('spec'):
		if parms.has_key ('damncmptrs'):
			errors.append ('''Please <I>either</I> choose one of
				the standard computer types <I>or</I> enter a
				non-standard one.  Do not do both.''')
		else:
			dict['Computers'] = parms['spec']

	return dict, errors

def sendRemedyMail (remedy_dict):
	# Purpose: compose and send a message to the Remedy system based on
	#	the contents of 'remedy_dict'
	# Returns: nothing
	# Assumes: nothing
	# Effects: sends an e-mail
	# Throws: nothing

	# start with the standard Remedy message header:

	lines = [
		'#',
		'#  %s' % mgi_utils.date(),
		'#',
		'#AR-Message-Begin             Do Not Delete This Line',
		'Schema: TJL-ClientProfile',
		'Server: arserver.jax.org',
		'Login: webmail',
		'Password: webuser1',
		'Action: Submit',
		'# Values: Submit, Query',
		'Format: Short',
		'# Values: Short, Full',
		'',
		]

	# add lines for the data:

	for (www_label, www_fieldname, www_required, default_value,
			rem_fieldname, rem_id, format_function) in fields:
		if rem_fieldname:
			lines.append (format_function (rem_fieldname, rem_id,
				remedy_dict[rem_fieldname]))		

	# add standard Remedy footer:

	lines.append ('')
	lines.append ('#AR-Message-End             Do Not Delete This Line')

	# check to see if we have a developer override for email

	if config.lookup ('CGI_MAILTARGET') is None:
		destination = RECIPIENT
	else:
		destination = config.lookup ('CGI_MAILTARGET')

	# send the mail

	fd = os.popen ('%s -t %s' % \
		(config.lookup ('SENDMAIL'), destination), 'w')
	fd.write (MAIL_HEADER % REPLY_TO)
	fd.write (string.join (lines, '\n') + '\n')
	fd.close()

	return

def printConfirmationPage (remedy_dict):
	# Purpose: compose and send a confirmation web page about the user's
	#	submission
	# Returns: nothing
	# Assumes: nothing
	# Effects: prints a web page to stdout
	# Throws: nothing

	# start with the banner at the page top

	lines = [
		'<HTML>',
		'<HEAD><TITLE>TJL HelpDesk User Registration</TITLE></HEAD>',
		'<BODY bgcolor=ffffff>',
		] + \
		homelib.banner() + \
		[
		'<H1>TJL HelpDesk User Registration Report</H1>',
		'<HR>',
		'<H1>Thank you.</H1>',
		'''Your registration has been forwarded to the appropriate TJL
			support staff.<P><HR>''',
		] + \
		homelib.footer() + [ '</BODY></HTML>' ]
	print string.join (lines, '\n')
	return

###--- Classes ---###

class RegistrationCGI (CGI.CGI):
	# Concept:
	#	IS: a CGI object with a main() method for handling input from
	#		the "user registration" form
	#	HAS: see CGI
	#	DOES: see CGI for the basics.  In this subclass, we get the
	#		input, validate it, send an error page if needed, or
	#		send e-mail to Remedy and a confirmation page to the
	#		user if no error occurred.

	def main (self):
		remedy_dict, errors = parse_parameters (self.get_parms())
		if errors:
			errorlib.show_error (
				'<UL><LI>%s</UL>' % \
					string.join (errors, '\n<LI>'),
				1, 'MGI User Registration Form',
				string.join (homelib.banner(), '\n '),
				string.join (homelib.footer(), '\n '))
			sys.exit (0)
		else:
			sendRemedyMail (remedy_dict)
			printConfirmationPage (remedy_dict)
		return

###--- Main Program ---###

if __name__ == '__main__':
	mycgi = RegistrationCGI()
	mycgi.go()
