#!./python

#
# Processes Nomenclature Submission Form
#
# 1.  Sends email message to 'nomen@informatics.jax.org'
# 2.  Provides user w/ HTML reflection of email message
#


# Imports
# =======

import sys
if '.' not in sys.path:
	sys.path.insert(0, '.')
import config
import homelib

import sys
import string
import os 
import mgi_utils
import mgi_html
import errorlib
import header

SP = ' '
HT = '\t'
NL = '\n'

def errorStop (message):
	print 'Content-type: text/html\n'
	errorlib.show_error (message, 1, 'MGI Nomen Form',
		header.bodyStart(),
		header.bodyStop())
	sys.exit(0)

nomen_addr = 'nomen@informatics.jax.org'  # MGD Nomen Coordinator Email Account

# developer override for mailtarget 
dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
	nomen_addr = dev_email

subject = 'Nomenclature Request'

htmlheader = \
'Content-type: text/html' + NL + NL + \
'<HTML> \
<HEAD> \
<TITLE> \
MGD: Nomenclature Request\
</TITLE> \
</HEAD> \
<BODY BGCOLOR="#FFFFFF">'

htmlheader = htmlheader + header.bodyStart() + header.headerBar('Thank You')

htmlheader = htmlheader + ' <BR>\
Your Nomenclature request has been sent to the MGD Nomenclature Support Staff.'

field_sort = [ \
'emailaddr',\
'tute',\
'add1',\
'add2',\
'cty',\
'sta',\
'po',\
'cn',\
'ph',\
'fx']

field_trans = { \
	'emailaddr' : 'Email address:\t\t', \
	'tute' : 'Institution:\t\t', \
	'add1' : 'Address:\t\t', \
	'add2' : 'Address:\t\t', \
	'cty' : 'City:\t\t\t', \
	'sta' : 'State/Province:\t\t', \
	'po' : 'Postal Code:\t\t', \
	'cn' : 'Country:\t\t', \
	'ph' : 'Phone:\t\t\t', \
	'fx' : 'FAX:\t\t\t'}

fields = mgi_html.get_fields()
types = fields[2]
operators = fields[1]
fields = fields[0]

#
# Format Contact Information
#

message = 'Submission Date:' + HT + mgi_utils.date() + 2*NL
missing_fields = []

if (fields.has_key('lastname')):
	username = fields['lastname']
else:
	username = ''
	missing_fields.append('Last Name')
 
if (fields.has_key('firstname')):
	username = username + ',' + SP + fields['firstname']
	message = message + 'Submitter Name:\t\t' + username + NL
else:
	missing_fields.append('First Name & Middle Name(s)')

if (fields.has_key('emailaddr')):
	submitter_addr = fields['emailaddr']
else:
	missing_fields.append('E-mail address')

for key in field_sort:
	if (fields.has_key(key)):
		if (field_trans.has_key(key)):
			message = message + field_trans[key] + fields[key] + NL
		else:
			message = message + key + ' = ' + fields[key] + NL

#
# Format Symbol Information
#

locussect = NL

if fields.has_key('symbol'):
	locussect = locussect + 'Requested Symbol:' + HT + fields['symbol'] + NL
	subject = fields['symbol']

if fields.has_key('name'):
	locussect = locussect + 'Requested Name:' + 2*HT + fields['name'] + NL

if fields.has_key('chromosome'):
	locussect = locussect + 'Chromosome:' + 2*HT + fields['chromosome'] + NL

if fields.has_key('pub_status'):
	locussect = locussect + 'Publication Status:' + HT + fields['pub_status'] + NL

if fields.has_key('symbol_status'):
	locussect = locussect + 'Symbol Status:' + 2*HT + fields['symbol_status'] + NL

# We now handle symbols requested in up to three species.  (TR 1175)

species = []
for fieldname in [ 'requestMouse', 'requestHuman', 'requestRat' ]:
	if fields.has_key (fieldname):
		species.append (fields[fieldname])
if species:
	if (len (species) == 1) and (species[0] == 'human'):
		errorStop ('''You requested a symbol only
			in Human.  We do not process Human-only symbols.  If
			you wish to request a Human-only symbol, please go to
			the <A
			HREF="http://www.gene.ucl.ac.uk/nomenclature/">Human
			Nomenclature Page</A>.  If you intended to specify
			other species, you may go back to the previous page
			and make corrections.''')
	locussect = locussect + "Symbol Requested in:%s%s%s" % \
					(HT, string.join (species, ', '), NL)

# We also now handle up to three sources.  (TR 1175)

sources = []
for fieldname in [ 'source1', 'source2', 'source3', 'source4' ]:
	if fields.has_key (fieldname):
		sources.append (fields[fieldname])
if sources:
	locussect = locussect + "Sources Checked:%s%s%s" % \
					(HT, string.join (sources, ', '), NL)

if fields.has_key('locusName'):
	locussect = locussect + '\nName/Phenotypic effect:' + NL + fields['locusName'] + NL

if fields.has_key('otherName'):
	locussect = locussect + '\nOther Name(s):' + NL + fields['otherName'] + NL

if fields.has_key('family'):
	locussect = locussect + '\nLocus Family:' + NL + fields['family'] + NL

if fields.has_key('notes'):
	locussect = locussect + '\nNotes:' + NL + fields['notes'] + NL

message = message + locussect + NL

###--- Format Sequence Information, per TR 2031 ---###

seqsect = ''

if fields.has_key ('genbankID'):
	seqsect = seqsect + 'GenBank ID:' + 2*HT + fields['genbankID'] + NL

if fields.has_key ('sequence'):
	seqsect = seqsect + NL + 'Sequence:' + NL + fields['sequence'] + NL

### As of TR 2754, we now do not require sequence information...
#if seqsect == '':
#	errorStop ('''You must include either a GenBank ID or Sequence Data.
#		Please go back and try again.''')

if seqsect:
	message = message + seqsect + NL

#
# Format Reference Information
#

refsect = 'Locus References:' + NL

if fields.has_key('cite1'):
	refsect = refsect + fields['cite1'] + NL
if fields.has_key('cite2'):
	refsect = refsect + fields['cite2'] + NL
if fields.has_key('cite3'):
	refsect = refsect + fields['cite3'] + NL

message = message + refsect + NL

#
# Format Homology Information
#

homsect = 'Homology Information:'

if fields.has_key('hom_symbol_1'):
	if fields.has_key('hom_species_1') and fields.has_key('hom_citation_1'):
		homsect = homsect + 2*NL + \
			  'Locus Symbol:' + HT + fields['hom_symbol_1'] + NL + \
			  'Species:' + HT + fields['hom_species_1'] + NL + \
			  'Citation' + HT + fields['hom_citation_1']
	else:
		missing_fields.append('Species and Short Citation required for each Locus Symbol.')

if fields.has_key('hom_symbol_2'):
	if fields.has_key('hom_species_2') and fields.has_key('hom_citation_2'):
		homsect = homsect + 2*NL + \
			  'Locus Symbol:' + HT + fields['hom_symbol_2'] + NL + \
			  'Species:' + HT + fields['hom_species_2'] + NL + \
			  'Citation' + HT + fields['hom_citation_2']
	else:
		missing_fields.append('Species and Short Citation required for each Locus Symbol.')

if fields.has_key('hom_symbol_3'):
	if fields.has_key('hom_species_3') and fields.has_key('hom_citation_3'):
		homsect = homsect + 2*NL + \
			  'Locus Symbol:' + HT + fields['hom_symbol_3'] + NL + \
			  'Species:' + HT + fields['hom_species_3'] + NL + \
			  'Citation' + HT + fields['hom_citation_3']
	else:
		missing_fields.append('Species and Short Citation required for each Locus Symbol.')

if missing_fields:
	errorStop ('''Mandatory field(s) missing...  Please enter
		field(s) and try again.<BR>Field(s): %s''' % \
		string.join (missing_fields, ', '))

message = message + homsect
print htmlheader + '<PRE>' + message + '</PRE><HR>'

print header.bodyStop()

print "</BODY></HTML>"

mailheader = 'From: ' + submitter_addr + NL + 'To: ' + nomen_addr + NL 
mailheader = mailheader + 'Subject: ' + subject + NL + NL
fd = os.popen('%s -t' % config.lookup('SENDMAIL'), 'w')
fd.write( mailheader + message )
fd.close()

#
# Warranty Disclaimer and Copyright Notice
# 
#  THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE SUITABILITY OR 
#  ACCURACY OF THIS SOFTWARE OR DATA FOR ANY PURPOSE, AND MAKES NO WARRANTIES, 
#  EITHER EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR A 
#  PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA WILL NOT 
#  INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS, OR OTHER RIGHTS.  
#  THE SOFTWARE AND DATA ARE PROVIDED "AS IS".
# 
#  This software and data are provided to enhance knowledge and encourage 
#  progress in the scientific community and are to be used only for research 
#  and educational purposes.  Any reproduction or use for commercial purpose 
#  is prohibited without the prior express written permission of the Jackson 
#  Laboratory.
# 
# Copyright © 1996, 1999, 2000 by The Jackson Laboratory
# All Rights Reserved
#
