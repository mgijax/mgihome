#!./python

# Program: feedback_form.cgi
# Purpose: present a "Your Input" form corresponding to the input parameters
#	(show a form specific to Markers in an input MGI # is for a marker,
#	for an allele if the input MGI # is for an allele, etc.)
# Usage: This script takes two optional parameters:
#	accID - specifies an accession ID which prompted this invocation
#		(so we can show a "Your Input" screen corresponding to a
#		certain data type)
#	dataDate - specifies the date of the data dump which was used to
#		load the database (so we know how out of date the data is,
#		when we receive "Your Input" submissions via mirror sites

import sys
if '.' not in sys.path:
	sys.path.insert (0, '.')

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import feedbacklib
import CGI
import homelib

class InputFormCGI (CGI.CGI):
	# Concept:
	#	IS: a CGI object which presents a form for "Your Input"
	#	HAS: see CGI
	#	DOES: see CGI (and IS)

	def main (self):
		# Purpose: serves as the main program for this CGI object
		# Returns: nothing
		# Assumes: nothing
		# Effects: reads input, gets a UserInput object, and prints
		#	an input page for the user
		# Throws: propagates any errors raised by
		#	feedbacklib.getInputObj()
		# Notes: The CGI.go() method serves as a wrapper around this
		#	method to provide exception handling and logging.

		parms = self.get_parms()

		if parms.has_key('accID'):
			parms['accID'] = homelib.sanitizeID(parms['accID'])

		if parms.has_key('dataDate'):
			parms['dataDate'] = homelib.sanitizeDate(parms['dataDate'])

		inp = feedbacklib.getInputObj (parms)
		inp.printInputPage ()
		return

###--- Main Program ---###

if __name__ == '__main__':
	mycgi = InputFormCGI()
	mycgi.go()
