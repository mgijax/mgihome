#!./python

# Program: amsp_submission.cgi
# Purpose: to handle display and processing of a form for users to submit
#	mutant allele, phenotype, and strain data to MGI.

import sys
if '.' not in sys.path:
	sys.path.insert (0, '.')
import os
import cgi
import Cookie
import time
import random
import pickle
import types
import re
import string
import tempfile
import traceback

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import feedbacklib
import runCommand
import template
import homelib

###------------------------###
###--- global variables ---###
###------------------------###

# standard exception raised within this script
error = 'Exception'

# email address to receive notice of completed submission
SUBMISSIONS = 'mgi-submissions@jax.org'
if config.has_key('CGI_MAILTARGET'):
	SUBMISSIONS = config['CGI_MAILTARGET']

# cookie data for preserving user's contact info across multiple submissions
MY_COOKIE = Cookie.SimpleCookie()

# where do we store the contact info for the ID stored in the cookie?  There
# are ten files using this as the base, each with a different extension.
BASE_COOKIE_FILE = '/tmp/submissionCookies.'

# short-hand for flagging which Field objects are required to have a value
REQUIRED = feedbacklib.REQUIRED

# string; the ID passed to us by the user from a previously-set cookie
COOKIE_ID = None

# dictionary of fieldnames which had validation errors
ERRANT_FIELDS = {}

# list of dictionaries, one per file; each entry has keys 'filename',
# 'length', and 'contents'
UPLOADED_FILES = []

# should we show the allele submission section by default?
SHOW_ALLELE = False

# should we show the strain submission section by default?
SHOW_STRAIN = False

# should we show the phenotype submission section by default?
SHOW_PHENOTYPE = False

# should we show the file upload section by default?
SHOW_FILES = False

###--- groups of Field objects, one per form section ---###

# fields for the contact information section
CONTACT_FIELDS = [
	feedbacklib.OneLineTextField ('lastName', 'Last Name', REQUIRED,
		width = 40, tabIndex = 1),
	feedbacklib.OneLineTextField ('firstName', 'First Name', REQUIRED,
		width = 40, tabIndex = 2),
	feedbacklib.OneLineTextField ('email', 'Email Address', REQUIRED,
		width = 40, tabIndex = 3),
	feedbacklib.OneLineTextField ('email2', 'Email Address (repeat)',
		REQUIRED, width = 40, tabIndex = 4),
	feedbacklib.OneLineTextField ('labPI', 'Laboratory PI', width = 40,
		tabIndex = 5),
	feedbacklib.OneLineTextField ('institute', 'Institute/Organization',
		width = 40, tabIndex = 6),
	feedbacklib.OneLineTextField ('streetAdd', 'Street Address', width = 40,
		tabIndex = 7),
	feedbacklib.OneLineTextField ('city', 'City', width = 40,
		tabIndex = 8),
	feedbacklib.OneLineTextField ('state', 'State/Province', width = 40,
		tabIndex = 9),
	feedbacklib.OneLineTextField ('zip', 'Postal Code', width = 40,
		tabIndex = 10),
	feedbacklib.OneLineTextField ('country', 'Country', width = 40,
		tabIndex = 11),
	feedbacklib.OneLineTextField ('phone', 'Telephone', width = 40,
		tabIndex = 12),
	feedbacklib.OneLineTextField ('fax', 'Fax', width = 40,
		tabIndex = 13),
]

# fields for the reference/citation section
CITING_FIELDS = [
	feedbacklib.RadioButtonGroup ('isPublished',
		'Are your data published?',
 		items = [ [ ('yes', 'yes'), ('no', 'no') ] ]),
	feedbacklib.RadioButtonGroup ('makePublicNow',
		'You would prefer that your data ',
		items = [ [ ('publicNow', 'be public at the MGI website now'),
			('waitForPaper', 'be held private until publication')
			] ] ),
	feedbacklib.MultiLineTextField ('references', 'References',
		height = 2, width = 85),
	feedbacklib.OneLineTextField ('url', 'URL for website with data',
		width = 50),
]

# fields for the allele submission section
ALLELE_FIELDS = [
	feedbacklib.OneLineTextField ('alleleSymbol',
		'Suggested Mutation Symbol/Name', width = 60),
	feedbacklib.OneLineTextField ('gene', 'Gene Symbol/MGI ID',
		width = 20),
	feedbacklib.OneLineTextField ('nicknames', 'Nicknames', width = 60),
	feedbacklib.CheckboxGroup ('alleleClass', 'Class of Allele', items = [
		# row 1
		[ ('spontaneous', 'spontaneous'),
			('enuInduced', 'ENU induced'),
			('chemical', 'chemical (non-ENU) induced'),
			('irradiation', 'irradiation induced'),
			('transgenic', 'transgenic'),
			('geneTrapped', 'gene trapped'),
			('targeted', 'targeted'),
			],
		# row 2
		[ ('conditional', 'conditional/targeted'),
			('recombinase',
				'recombinase (cre or other) containing'),
			('transposon', 'transposon induced'),
			('other', 'other (specify)', 20),
			] ] ),
	feedbacklib.OneLineTextField ('promoter', 'Transgene Promoter',
		width = 35),
	feedbacklib.OneLineTextField ('esCellLine', 'ES cell line',
		width = 35),
	feedbacklib.OneLineTextField ('mutantEsCellLine',
		'Mutant ES cell line', width = 35),
	feedbacklib.RadioButtonGroup ('inheritance', 'Inheritance',
#		value = [ '' ],
		items = [ [ ('dominant', 'dominant'),
			('codominant', 'codominant'),
			('semidominant', 'semidominant'),
			('recessive', 'recessive'),
			('X-linked', 'X-linked'),
			('other', 'other (specify)', 30),
			('unknown', 'unknown/not applicable') ] ] ),
	feedbacklib.OneLineTextField ('strainBackground', 'Strain background',
		width = 35),
	feedbacklib.MultiLineTextField ('location',
		'Genome Location and Molecular Detail',
		height = 3, width = 90),
	feedbacklib.CheckboxGroup ('nomenHelp',
		'Request help with allele nomenclature',
		items = [ [ ('yes', '') ] ]),
]

# fields for the strain submission section
STRAIN_FIELDS = [
	feedbacklib.OneLineTextField ('strain', 'Suggested strain name',
		width = 75),
	feedbacklib.MultiLineTextField ('genes',
		'Gene symbols for alleles on this strain',
		height = 4, width = 20),
	feedbacklib.OneLineTextField ('repository', 'Repository of strain',
		width = 50),
	feedbacklib.OneLineTextField ('repositoryID',
		'Repository ID or MGI ID of strain', width = 20),
	feedbacklib.CheckboxGroup ('strainCategory', 'Strain categories',
		items = [
		# column 1
		[ ('inbred', 'inbred strain'),
			('segregatingInbred', 'segregating inbred'),
			('mutantStrain', 'mutant strain'),
			('mutantStock', 'mutant stock'),
		],
		# column 2
		[
			('wildDerived', 'wild-derived'),
			('outbred', 'outbred'),
			('coisogenic', 'coisogenic'),
			('congenic', 'congenic'),
			('consomic', 'consomic'),
		],
		# column 3
		[
			('RI', 'recombinant inbred (RI)'),
			('RC', 'recombinant congenic (RC)'),
			('MHC', 'major histocompatibility congenic'),
			('mHC', 'minor histocompatibility congenic'),
			('other', 'other, specify', 20),
		] ] ),
	feedbacklib.CheckboxGroup ('strainHelp',
		'Request help with strain nomenclature',
		items = [ [ ('yes', '') ] ]),
]

# fields for the phenotype submission section
PHENOTYPE_FIELDS = [
	feedbacklib.MultiLineTextField ('allelePairs', 'Allele pairs',
		height = 4, width = 40),
	feedbacklib.MultiLineTextField ('additionalInfo',
		'Additional allele information', height = 3, width = 80),
	feedbacklib.OneLineTextField ('geneticBackground',
		'Strain/Genetic Background on which phenotypes were analyzed',
		width = 60),
	feedbacklib.MultiLineTextField ('crosses',
		'Other Strain/Background Information',
		height = 4, width = 65),
	feedbacklib.CheckboxGroup ('phenoHelp',
		'Request help with genetic background',
		items = [ [ ('yes', '') ] ]),
	feedbacklib.MultiLineTextField ('phenoDescription',
		'Phenotype Description',
		height = 12, width = 90),
	feedbacklib.MultiLineTextField ('disease', 'Human disease',
		height = 3, width = 90),
	feedbacklib.MultiLineTextField ('otherPhenoInfo',
		'Other known information',
		height = 3, width = 90),
]

# fields for the comments section
COMMENTS_FIELDS = [
	feedbacklib.MultiLineTextField ('finalComments',
		'Additional Comments or Information about your data',
		height = 2, width = 80),
]

CAPTCHA_FIELDS = [feedbacklib.OneLineTextField ('street', 'street'),
	feedbacklib.MultiLineTextField ('business', 'business'),]
	
SUBMISSION_FIELDS = [feedbacklib.RadioButtonGroup ('isCopyrighted',
		'Are the file(s) that you submitted copyrighted?',
 		items = [ [ ('yes', 'yes'), ('no', 'no') ] ]),]

# note that file upload fields are not represented in feedbacklib, but are
# instead handled directly in this script

# dictionary of all Field objects, for quick access by name; maps from
# fieldname to Field object
ALL_FIELDS = {}

# name of all Fields whose values may be cached using a cookie; used to
# pre-fill the page for future submissions
CACHE_FIELDS = [ 'lastName', 'firstName', 'email', 'email2', 'labPI',
	'institute', 'streetAdd', 'city', 'state', 'zip', 'country', 'phone',
	'fax' ]

# list of strings, each of which is an error message found during verification
ERRORS = []

# string; subdirectory name for submission
SUBMISSION_SUBDIR = None

###-----------------###
###--- functions ---###
###-----------------###

def log (
	message		# string; message to be written to Apache's error.log
	):
	# Purpose: write a message to the error log, stamped with the filename
	# Returns: nothing
	# Modifies: writes to Apache's error.log
	# Assumes: nothing
	# Throws: nothing

	sys.stderr.write ('amsp_submission.cgi : %s\n' % message)
	return

def label (
	fieldname, 	# string; internal fieldname for a Field object
	labelStr	# string; displayed label for a Field object
	):
	# Purpose: to do highlighting of labels for errant fields
	# Returns: string; returns 'labelStr' as-is if the field had no
	#	errors, or highlighted if it had validation errors
	# Modifies: nothing
	# Assumes: global ERRANT_FIELDS has been populated by a validation
	#	process
	# Throws: nothing

	if not ERRANT_FIELDS.has_key(fieldname):
		return labelStr
	return '<SPAN STYLE="background-color: yellow">%s</SPAN>' % labelStr

def randomString (
	length		# integer; number of characters in our random string
	):
	# Purpose: returns a string of a given 'length', filled with random 
	#	letters and numbers
	# Returns: string
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	chars = chars + chars.lower() + '0123456789'

	s = ''

	for i in range(0, length):
		s = s + random.choice(chars)
	return s

def getJavascript():
	# Purpose: return the Javascript section needed for our HTML page
	# Returns: string; a <SCRIPT> section for our HTML page
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	items = [
	    '<SCRIPT LANGUAGE="Javascript">',
	    'function addFile() {',
		'var elem;',
		'for (i = 2; i <= 10; i++) {',
			'elem = document.getElementById("f" + i);',
			'if (elem == null) { continue; }',
			'if (elem.style.display != "") {',
				'elem.style.display = "";',
				'return;'
			'}',
		'}',
	    '}',
	    'function toggle(i) {',
	    	'var elem = document.getElementById(i);',
	    	'if (elem == null) { return false; }',
	    	'var status = (elem.style.display == "");',
	    	'if (status) { elem.style.display = "none"; }',
	    	'else { elem.style.display = ""; }',
	    	'return true;',
	    '}',
	    '</SCRIPT>',
	    ]
	return '\n'.join(items)

def encodeCacheString():
	# Purpose: examine the parameters we will cache for a user cookie, and
	#	bundle them into a string
	# Returns: string; first character indicates the delimiter used to
	#	separate between fieldnames and their values
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing
	# Notes: The encoding in this function is paired with the decoding in
	#	the decodeCacheString() function.

	# uncommon characters that we can use as a delimiter, in order of
	# preference
	specialChars = '!@#$%^&*()-_+=[]{}|:;<>/?,.0123456789qwzxQWZX`'

	# build a list of fields and values to cache

	items = []		# list of (fieldname, value) tuples

	for fieldname in CACHE_FIELDS:
		field = getField (fieldname)
		if not field.isEmpty():
			items.append ( (fieldname, field.getValue()) )

	# find a delimiter which does not appear in any of our fieldnames or
	# field values

	delim = None			# string; our delimiter character
	for char in specialChars:
		found = False
		for (fieldname, fieldvalue) in items:
			if (fieldname and (char in fieldname)) or \
				(fieldvalue and (char in fieldvalue)):
				found = True
				break
		if not found:
			delim = char
			break

	# if we couldn't find an unused delimiter (which would be odd), then
	# just don't bother with caching

	if not delim:
		log ('could not find unused character for delimiter')
		return None
	
	# finally, build our encoded string; delimiter is the first character
	# and then a series of delimited fieldnames and values

	s = ''
	for (fieldname, fieldvalue) in items:
		if fieldname and fieldvalue:
			s = s + delim + fieldname + delim + fieldvalue
	return s

def decodeCacheString (
	s		# string; to be decoded into its fields and values
	):
	# Purpose: to decode a string encoded by encodeCacheString() function
	# Returns: dictionary of fieldname : value pairs
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	dict = {}			# the dictionary to be populated
	if not s:
		return dict

	# first character is the delimiter for 's', which is then used to
	# separate fieldnames and values

	delim = s[0]
	items = s[1:].split(delim)

	# populate 'dict' with fieldnames and values found in 'items'

	i = 0
	while i < len(items):
		fieldname = items[i]
		fieldvalue = items[i+1]

		dict[fieldname] = fieldvalue
		i = i + 2
	return dict

def getField (
	fieldname			# string; name of a Field object
	):
	# Purpose: to retrieve a Field object with the given 'fieldname'
	# Returns: a Field object
	# Modifies: populates global 'ALL_FIELDS'
	# Assumes: nothing
	# Throws: nothing

	global ALL_FIELDS

	# if we didn't populate the cache yet (mapping fieldname to Field
	# object), then do it

	if not ALL_FIELDS:
		for group in [ CONTACT_FIELDS, CITING_FIELDS, ALLELE_FIELDS,
			STRAIN_FIELDS, PHENOTYPE_FIELDS, COMMENTS_FIELDS, CAPTCHA_FIELDS, SUBMISSION_FIELDS]:
			for field in group:
				if ALL_FIELDS.has_key(field.getFieldname()):
					# should not happen; this would be a
					# programming error
					raise 'ERROR', \
						'Duplicate fieldname: %s' % \
						field.getFieldname()

				ALL_FIELDS[field.getFieldname()] = field

	# now, retrieve the cached Field with the requested name

	if ALL_FIELDS.has_key(fieldname):
		return ALL_FIELDS[fieldname]

	# or, log that we couldn't find it.  This would also be an unexpected
	# programming error.

	log ('requested unknown fieldname: %s' % fieldname)
	return None

def sectionTitle (
	s, 				# string; the title of the section
	hasRequiredFields = True	# boolean; do we need an asterisk?
	):
	# Purpose: provide a properly formatted section title for 's'
	# Returns: string; HTML-encoded title for a section, with an
	#	asterisk-ed "required field" explanation, if necessary
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	s = '<H3>%s:' % s
	if hasRequiredFields:
		s = s + ' &nbsp;&nbsp;&nbsp;&nbsp;' + \
			'<FONT SIZE="-2"><FONT COLOR="red">*</FONT> ' + \
			'= required field</FONT>'
	s = s + '</H3>'
	return s

def getContactSection():
	# Purpose: get the HTML necessary for the 'Contact Details' section
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	# Fields are arranged in a two-column table

	items = [ sectionTitle('Contact Details'),
		'<TABLE>',
		'<TR><TD>%s</TD><TD><FONT COLOR="red">*</FONT>' % \
			label('lastName', 'Last name:'),
		getField('lastName').getHTML(),
		'</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('streetAdd', 'Street Address:'),
		getField('streetAdd').getHTML(),
		'</TD></TR>',

		'<TR><TD>%s</TD><TD>' % label('firstName', 
			'First name (&amp; middle initial):'),
		'<FONT COLOR="red">*</FONT>',
		getField('firstName').getHTML(),
		'</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('city', 'City:'),
		getField('city').getHTML(),
		'</TD></TR>',

		'<TR><TD>%s</TD><TD><FONT COLOR="red">*</FONT>' % \
			label('email', 'E-mail address:'),
		getField('email').getHTML(),
		'</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('state', 'State/Province:'),
		getField('state').getHTML(),
		'</TD></TR>',

		'<TR><TD>%s</TD>' % label('email2',
			'E-mail address (repeat):'),
		'<TD><FONT COLOR="red">*</FONT>',
		getField('email2').getHTML(),
		'</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('zip', 'Postal Code:'),
		getField('zip').getHTML(),
		'</TD></TR>',

		'<TR><TD>%s</TD>' % label('labPI', 'Laboratory PI:'),
		'<TD>&nbsp;&nbsp;',
		getField('labPI').getHTML(),
		'</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('country', 'Country:'),
		getField('country').getHTML(),
		'</TD></TR>',

		'<TR><TD>%s</TD>' % label('institute',
			'Institute/Organization:'),
		'<TD>&nbsp;&nbsp;',
		getField('institute').getHTML(),
		'</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('phone', 'Telephone:'),
		getField('phone').getHTML(),
		'</TD></TR>',

		'<TR><TD>&nbsp;</TD><TD>&nbsp;</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('fax', 'Fax:'),
		getField('fax').getHTML(),
		'</TD></TR></TABLE>',
		]
	return ''.join(items)

def getCitingSection():
	# Purpose: get the HTML necessary for the 'Citing your data' section
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	# Fields are left-aligned (no table structure)

	items = [ sectionTitle('Citing your data', False),
		'Are your data published?&nbsp;&nbsp;&nbsp;',
		getField('isPublished').getHTML(),
		'<P>',
		'If no, would you prefer that your data:&nbsp;&nbsp;&nbsp;',
		getField('makePublicNow').getHTML(),
		'<P>',
		'Provide reference(s) or PubMed IDs for published data ',
		'or authors &amp; descriptive title for unpublished data:',
		'<BR>',
		getField('references').getHTML(),
		'<P>',
		'If data are available from a website, please list URL:',
		getField('url').getHTML(),
		]
	return ''.join(items)

def getAlleleSection():
	# Purpose: get the HTML necessary for the 'Enter Allele Data' section
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing
	# Notes: only fields which can be validated have their labels run
	#	through the label() function, as the others would never be
	#	highlighted for errors

	# Fields are left-aligned (no table structure)

	items = [ sectionTitle('Enter Allele Data'),
		'Suggest %s for this mutation: ' % label ('alleleSymbol',
			'<B>symbol</B> and/or <B>name</B>'),
		'<FONT COLOR="red">*</FONT>',
		getField('alleleSymbol').getHTML(),
		'<P>',
		'If this mutation is an allele of a <B>known gene</B> ',
		'enter the %s ' % label('gene',
			'<B>gene symbol</B> or <B>MGI ID</B>:'),
		getField('gene').getHTML(),
		' (<I><B>Check by</B></I> <A HREF="%smarker/" '\
			% config['FEWI_URL'],
		'TARGET="_blank">searching MGI</A>.)<P>',
		'Common nicknames for this mutant allele ',
		getField('nicknames').getHTML(),
		'<P>',
		'%s (check all that apply): &nbsp;' % label ('alleleClass',
			'Class of Allele'),
		'<FONT COLOR="red">*</FONT>',
		'<BLOCKQUOTE>',
		getField('alleleClass').getHTML(),
		'<P>',
		'For transgenes, specify transgene promoter: ',
		getField('promoter').getHTML(),
		'<BR>',
		'For targeted mutations or gene traps, specify ES cell line ',
		'used: ',
		getField('esCellLine').getHTML(),
		' <I>(<B>Example</B>: E14.1, JM8A3)</I><BR>',
		'For gene traps, specify the resulting mutant ES cell line: ',
		getField('mutantEsCellLine').getHTML(),
		' <I>(<B>Example</B>: AD0888)</I><BR>',
		'</BLOCKQUOTE><P>',
		'Inheritance: ',
		getField('inheritance').getHTML(),
		'<P>',
		'Strain background in which the mutation occurred ',
		getField('strainBackground').getHTML(),
		'<I>(<B>Examples</B>: C57BL/6J, 129P2/OlaHsd)</I><P>',
		'Genome Location (Chromosome, genome coordinates, cM) ',
		'and molecular detail about this allele, such as "exon ',
		'1 deletion, etc.": ',
		getField('location').getHTML(),
		'<UL><LI>For hints on mutant allele nomenclature, see ',
		'<A HREF="%snomen/allmut_quickhelp.shtml" ' % \
			config['MGIHOME_URL'],
		'TARGET="_blank">',
		'Quick Guide to Nomenclature for Alleles and Mutations</A>.',
		'</LI><LI><A ',
		'HREF="http://dels.nas.edu/global/ilar/lab-codes" ',
		'TARGET="_blank">',
		'Lab codes</A> are available from ILAR (Institute of ',
		'Laboratory Animal Resources).</LI>',
		'<LI><B>If you would like assistance with allele ',
		'nomenclature:</B></LI> ',
		getField('nomenHelp').getHTML(),
		' Check the box here and continue with your submission. We ',
		'will contact you about nomenclature for this mutation.</UL>',
		]
	return ''.join(items)

def getStrainSection():
	# Purpose: get the HTML necessary for the 'Register a New Mouse
	#	Strain' section
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing
	# Notes: only fields which can be validated have their labels run
	#	through the label() function, as the others would never be
	#	highlighted for errors

	# Fields are left-aligned (no table structure)

	items = [ sectionTitle('Register a New Mouse Strain'),
		'Enter a suggested <B>%s</B>.<BR>' % label (
			'strain', 'strain name'),
		'When mutant alleles are part of the strain name, use ',
		'&lt; &gt; to indicate the superscripted alleles.<BR>',
		'<I>Example:</I> <B>C57BL/6J-Kit<SUP>W-39J</SUP></B> should ',
		'be entered as <B>C57BL/6J-Kit&lt;W-39J&gt;</B><BR>',
		'<FONT COLOR="red">*</FONT>',
		getField('strain').getHTML(),
		'<P>',
		'Enter the <B>%s</B> corresponding to alleles ' % label (
			'genes', 'gene symbols'),
		'carried on this strain.<BR>',
		'<I>Example:</I> for the strain ',
		'<B>NOD/LtSz-Prkdc&lt;scid&gt; B2m&lt;tm1Unc&gt;</B>, the ',
		'gene symbols entered into this box would be <B>Prkdc</B> ',
		'and <B>B2m</B>.<BR>',
		'(one gene symbol per line)',
		getField('genes').getHTML(),
		'<P>',
		'If this strain is in a repository, please list the ',
		'repository ',
		getField('repository').getHTML(),
		' 	(<B><I>View</I></B>: list of <A HREF="',
		'%sfetch?page=imsrStrainRepositories" ' % config['IMSRURL'],
                'TARGET="_blank">',
                'repositories</A>)'
		'<BR>',
		'Enter its repository ID or MGI ID for this strain, if known ',
		getField('repositoryID').getHTML(),
		'<P>',
		'<B>%s</B>: Choose one or more. ' % label ('strainCategory',
			'Strain categories'),
		'<FONT COLOR="red">*</FONT><BLOCKQUOTE>',
		getField('strainCategory').getHTML(True),
		'</BLOCKQUOTE><P>',
		'<UL><LI>For hints on strain nomenclature, see ',
		'<A HREF="%snomen/strains.shtml" ' % config['MGIHOME_URL'],
		'TARGET="_blank">',
		'Guidelines for Nomenclature of Mouse and Rat Strains</A>.',
		'</LI><LI><A ',
		'HREF="http://dels.nas.edu/global/ilar/lab-codes" ',
		'TARGET="_blank">',
		'Lab codes</A> are available from ILAR (Institute of ',
		'Laboratory Animal Resources).</LI>',
		'<LI><B>If you would like assistance with strain ',
		'nomenclature:</B></LI> ',
		getField('strainHelp').getHTML(),
		' Check the box  and continue with your submission. We ',
		'will contact you about nomenclature for this strain.</UL>',
		]
	return ''.join(items)

def getPhenotypeSection():
	# Purpose: get the HTML necessary for the 'Submit Phenotype Data'
	#	section
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing
	# Notes: only fields which can be validated have their labels run
	#	through the label() function, as the others would never be
	#	highlighted for errors

	# Fields are left-aligned (no table structure)

	items = [
		sectionTitle('Submit Phenotype Data'),
		'<B>Mutant allele(s)</B> analyzed.<P>',
		'List one or more allele pairs analyzed in the animal (one ',
		'allele pair per line, with the alleles comma separated).<BR>',
		'When entering mutant alleles, use &lt; &gt; to indicate ',
		'the superscripted portion of an allele.<P>',
		'<I><B>Example:</B></I><BR>',
		'If you phenotyped animals that were heterozygous for ',
		'<B>Kit<SUP>W-39J</SUP></B> and homozygous for ',
		'<B>Tec<SUP>tm1Welm</SUP></B>, they should be entered as<BR>',
		'<TABLE BORDER="1" CELLPADDING="0" CELLSPACING="0" ',
		'WIDTH="30%"><TR><TD>',
		'Kit&lt;W-39J&gt;, Kit&lt;+&gt;<br>',
		'Tec&lt;tm1Welm&gt;, Tec&lt;tm1Welm&gt;',
		'</TD></TR></TABLE><P>',
		'Enter %s of your phenotyped animals: ' % label (
			'allelePairs', 'allele pairs'),
		'<FONT COLOR="red">*</FONT><BR>',
		getField('allelePairs').getHTML(),
		'(Find the correct allele symbol by <A HREF=',
		'"%ssearches/allele_form.shtml" TARGET="_blank">searching MGI</A>.)' % \
			config['WI_URL'],
		'<P>',
		'Additional allele information not currently in MGI (allele ',
		'synonyms, ES cell line, strain of origin, mutation type, ',
		'molecular description, etc.):<BR>',
		getField('additionalInfo').getHTML(),
		'<P>',
		'<B>Genetic Background:</B> Genetic background can have a ',
		'significant effect on phenotype.<P>',
		'Enter the %s on which phenotypes were analyzed: ' % label (
			'geneticBackground', 'Strain/Genetic Background'),
		'<FONT COLOR="red">*</FONT>',
		getField('geneticBackground').getHTML(),
		'<P>',
		'Other Strain/Background Information (e.g. specify ',
		'crosses): Click here for an <A ',
		'HREF="%snomen/alleleform_strainex.shtml" TARGET="_blank">' % \
			config['MGIHOME_URL'],
		'example</A>.<BR>',
		getField('crosses').getHTML(),
		'<P><UL>',
		'<LI><B>If you would like assistance with the Genetic ',
		'Background Section:</B></LI> ',
		getField('phenoHelp').getHTML(),
		' Check the box here and continue with your submission. We ',
		'will contact you about determining the correct genetic ',
		'background.</UL>',
		sectionTitle('Phenotype', False),
		'%s (enter text, describing details of ' % \
			label ('phenoDescription', 'Phenotypic Description'),
		'phenotypes observed, etc.): <FONT COLOR="red">*</FONT><BR>',
		'Click here for an <A ',
		'HREF="%snomen/alleleform_phenoex.shtml" TARGET="_blank">' % \
			config['MGIHOME_URL'],
		'example</A>.',
		' You may browse the <A HREF="%ssearches/MP_form.shtml" ' % \
			config['WI_URL'],
		'TARGET="_blank">Mammalian Phenotype Ontology</A> and use ',
		'these terms to describe the phenotype.<P>',
		getField('phenoDescription').getHTML(),
		'<P>',
		'If this genotype + genetic background is a model for a ',
		'human disease based on phenotypic similarity, please name ',
		'the disease and include any associated information:<BR>',
		getField('disease').getHTML(),
		'<P>',
		'Other known information (gene function/pathway, available ',
		'clones, GenBank numbers, etc.) that will enhance these ',
		'data:<BR>',
		getField('otherPhenoInfo').getHTML(),
		]
	return ''.join(items)

def getFileReportingSection():
	# Purpose: provide a textual report of files already uploaded
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: global UPLOADED_FILES is non-empty
	# Throws: nothing

	items = [ sectionTitle('File submissions', False),
		getField('isCopyrighted').getLabel(),
		getField('isCopyrighted').getHTML() + '<BR>',
		'If you have entered copyrighted information we will contact you.<br><BR>'
		'The following files were received and have been saved as ',
		'part of your submission:',
		'<UL>',
		]
	for dict in UPLOADED_FILES:
		items.append ('<LI>%s (%d bytes)</LI>' % (dict['filename'],
			dict['length']))
	items.append ('</UL>')
	return '\n'.join(items)

def getFileUploadSection():
	# Purpose: get the HTML necessary for the 'File submissions' section
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	# if we already received files, then we should just report on them

	if UPLOADED_FILES:
		return getFileReportingSection()

	# Fields are left-aligned (no table structure); we initially show
	# only one file submission field, but can accommodate up to ten.

	# Note that file submission fields are always submitted by some
	# browsers, whether or not the user actually selected anything.

	items = [
		sectionTitle('File submissions', False),
		'You may submit a limited number of files using this form. ',
		'Please limit file size to &lt;5 MB.<BR>',
		'If you have larger files, or many files to submit, please ',
		'contact us at: ',
		'<a href="mailto:mgi-submissions@jax.org">',
		'mgi-submissions@jax.org</a>.<P>',
		getField('isCopyrighted').getLabel(),
		getField('isCopyrighted').getHTML(),
		'<br>If you have entered copyrighted information we will contact you.<br><BR>'
		'Upload your data files (images, text descriptions, Excel, ',
		'or text data):<BR>',
		'File 1: <INPUT NAME="file1" TYPE="file">',
		'<INPUT TYPE="button" onClick="addFile()" NAME="addFileButton" VALUE="Submit more files">',
		'<P>',
		'<SPAN ID="f2" STYLE="display: none;">File 2: <INPUT NAME="file2" TYPE="file"><P></SPAN>',
		'<SPAN ID="f3" STYLE="display: none;">File 3: <INPUT NAME="file3" TYPE="file"><P></SPAN>',
		'<SPAN ID="f4" STYLE="display: none;">File 4: <INPUT NAME="file4" TYPE="file"><P></SPAN>',
		'<SPAN ID="f5" STYLE="display: none;">File 5: <INPUT NAME="file5" TYPE="file"><P></SPAN>',
		'<SPAN ID="f6" STYLE="display: none;">File 6: <INPUT NAME="file6" TYPE="file"><P></SPAN>',
		'<SPAN ID="f7" STYLE="display: none;">File 7: <INPUT NAME="file7" TYPE="file"><P></SPAN>',
		'<SPAN ID="f8" STYLE="display: none;">File 8: <INPUT NAME="file8" TYPE="file"><P></SPAN>',
		'<SPAN ID="f9" STYLE="display: none;">File 9: <INPUT NAME="file9" TYPE="file"><P></SPAN>',
		'<SPAN ID="f10" STYLE="display: none;">File 10: <INPUT NAME="file10" TYPE="file"> (limit is 10 files)<P></SPAN>',
		'See <A HREF="%ssubmissions/amsp_submission_examples.shtml" TARGET="_blank">examples and templates</A> for file submissions.' % config['MGIHOME_URL'],
		]
	return ''.join(items)

def getCommentsSection():
	# Purpose: get the HTML necessary for the 'Completing your submission'
	#	section
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	items = [
		sectionTitle('Completing your submission', False),
		'Are there any additional commments or information you ',
		'would like to convey about your data?<BR>',
		getField('finalComments').getHTML(),
		]
	return ''.join(items)

def hiddenStyle (
	isVisible			# boolean; should item be visible?
	):
	# Purpose: get HTML style necessary to make an item visible or not
	# Returns: string
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing
	# Notes: to make an item visible we need no styling, so an empty
	#	string is returned in that case

	if isVisible:
		return ''
	return ' STYLE="display:none;"'

def getMainForm(fromVerify):
	# Purpose: get the main part of the submission form (the part with the
	#	fields, except for file submissions)
	# Returns: string of HTML, for the contact section through the
	#	comments section
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	# The three major sections (allele, strain, phenotype) are hidden by
	# default, but will be made visible if they contain validation errors.
	# All other sections are displayed always.
	
	captchaJS = ''
	captchaForm = ''
	
	captchaJSfile = open('./include/captchajs.html', 'r')
	for line in captchaJSfile:
		captchaJS = captchaJS + line
		
	captchaFormFile = open('./include/captchaform.html', 'r')
	for line in captchaFormFile:
		captchaForm = captchaForm + line

	captchaJSfile.close()
	captchaFormFile.close()	
	
	if fromVerify == True:
		# We are in the second pass, where we don't want to output the captcha stuff
		# So blank them out.
		captchaForm = ''
		captchaJS = ''
	
	items = [
		getContactSection(),
		'<HR>',
		getCitingSection(),
		'<HR>',
		'<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" ',
		'WIDTH="100%"><TR><TD ALIGN="left" BGCOLOR="#d0e2f3">', 
		'<B>Choose information type(s) to submit.</B><BR>',
		'Click a heading to open or close its respective section.',
		'</TD></TR>',
		'<TR><TD ALIGN="left" BGCOLOR="#d0e2f3">',
		'&nbsp;&nbsp;&nbsp;&nbsp;<B><A HREF="" ',
		'''onClick="toggle('alleleSection'); return false;">''',
		'Allele</A></B>&nbsp;&nbsp;',
		'Name and describe a new allele, mutation, or transgene',
		'</TD></TR>',
		'<TR ID="alleleSection"%s><TD>' % hiddenStyle(SHOW_ALLELE),
		getAlleleSection(),
		'</TD></TR>',
		'<TR><TD ALIGN="left" BGCOLOR="#d0e2f3">',
		'&nbsp;&nbsp;&nbsp;&nbsp;<B><A HREF="" ',
		'''onClick="toggle('strainSection'); return false;">''',
		'Strain</A></B>&nbsp;&nbsp;',
		'Register a new mouse strain',
		'</TD></TR>',
		'<TR ID="strainSection"%s><TD>' % hiddenStyle(SHOW_STRAIN),
		getStrainSection(),
		'</TD></TR>',
		'<TR><TD ALIGN="left" BGCOLOR="#d0e2f3">',
		'&nbsp;&nbsp;&nbsp;&nbsp;<B><A HREF="" ',
		'''onClick="toggle('phenotypeSection'); return false;">''',
		'Phenotypes</A></B>&nbsp;&nbsp;',
		'Submit phenotype data for given genotypes',
		'</TD></TR>',
		'<TR ID="phenotypeSection"%s><TD>' % \
			hiddenStyle(SHOW_PHENOTYPE),
		getPhenotypeSection(),
		'</TD></TR>',
		'<TR><TD ALIGN="left" BGCOLOR="#d0e2f3">',
		'&nbsp;&nbsp;&nbsp;&nbsp;<B><A HREF="" ',
		'''onClick="toggle('fileSection'); return false;">''',
		'File Submissions</A></B>&nbsp;&nbsp;',
		'Submit data files (e.g. images, text files, Excel, or ',
		'bulk data)',
		'</TD></TR>',
		'<TR ID="fileSection"%s><TD>' % \
			hiddenStyle(SHOW_FILES),
		getFileUploadSection(),
		'</TD></TR>',
		'<TR ID="commentsSection"><TD>',
		'<HR>',
		getCommentsSection(),
		'</TD></TR></TABLE>',
		captchaForm,
		captchaJS,
		]
	return ''.join (items)

def getResetSpan():
	# Purpose: get an HTML span which provides for a confirmation check
	#	before resetting the entire form
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	# This span is hidden by default, and is made visible when a Reset
	# button on the page is clicked.  (Javascript on each Reset button
	# must show it.)

	items = [
		'<SPAN ID="confirmReset" STYLE="display:none;">',
		'Are you sure you want to reset all values on the page?',
		'''<INPUT TYPE="button" VALUE="No, skip it" NAME="resetSkipped" onClick="toggle('confirmReset');">''',
		'''<INPUT TYPE="button" VALUE="Yes, reset the page" NAME="resetConfirmed" onClick='window.location.href="%ssubmissions/amsp_submission.cgi?blank=1"'>''' % config['MGIHOME_URL'],
		'</SPAN>',
		]
	return '\n'.join(items)

def getInitialForm():
	# Purpose: get the main part of the page for an initial entry to the
	#	page (the first page the user sees)
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	items = [ 
		'Use this Submission Form to describe spontaneous, induced, ',
		'or genetically engineered mutations, to register new mouse ',
		'strains, and to describe phenotypes.<P>',
		'<FORM ACTION="%ssubmissions/amsp_submission.cgi" METHOD="POST" ENCTYPE="multipart/form-data">' % config['MGIHOME_URL'],
		getMainForm(False),
		'<P>',
		'<B>Use the buttons below to verify your data before ',
		'submission or to reset the entire form.<BR>Thank ',
		'you!</B><P>',
		'<INPUT VALUE="Verify" TYPE="submit">&nbsp;',

		# the reset button has a confirmation step
		'''<INPUT VALUE="Reset" TYPE="button" onClick="toggle('confirmReset');">''',
		getResetSpan(),
		'<INPUT TYPE="hidden" NAME="cameFrom" VALUE="initial">',
		'</FORM>',
		]
	return '\n'.join (items)

def getVerifyForm (
	text = None	# string; textual display of fields and values
	):
	# Purpose: get the main part of the verification page (after the user
	#	clicks the Verify button)
	# Returns: string of HTML
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	global SHOW_ALLELE, SHOW_PHENOTYPE, SHOW_STRAIN, SHOW_FILES

	# if we were not given a textual representation (with validation done)
	# then build it now

	if not text:
		text = buildText(True)

	# We need to change our messages (and format, to an extent) based on
	# whether there were any validation errors or not

	hadErrors = len(ERRANT_FIELDS) > 0	# True if we discovered errors

	# list of strings; this is where we're building the output
	items = [
		'Please review the text of your submission below.',
		]
	
	if hadErrors:
		if len(ERRORS) > 1:
			s1 = 'There are %d errors which ' % len(ERRORS)
			s2 = 'need to be fixed; the error messages are '
			s3 = 'items'
		else:
			s1 = 'There is 1 error which needs to be fixed; the '
			s2 = 'error message is '
			s3 = 'item'

		items = items + [
			s1, s2, 
			'listed below under <B>Verification Errors</B>. ',
			'Fields with errors are highlighted in yellow ',
			'in the submission form below.  Please correct the ',
			'indicated %s ' % s3,
			'and click the Verify button at the bottom of ',
			'the page.',
			]
		# no wrapper around form, but show errors
		preForm = '<H3>Verification Errors</H3><UL><LI>%s</LI></UL>' \
			% '</LI><LI>'.join(ERRORS)
		postForm = ''
	else:
		items = items + [
			'No errors were detected in your submission.  If ',
			'you would like to make any changes, you may open ',
			'the submission form below.  When finished, you may ',
			'go to the bottom and click the Submit button to ',
			'complete your submission.'
			]

		# we want to show any sections filled in by the user, so if
		# they choose to show their form, they'll see what they filled
		# in

		if anySubmitted(ALLELE_FIELDS):
			SHOW_ALLELE = True
		if anySubmitted(STRAIN_FIELDS):
			SHOW_STRAIN = True
		if anySubmitted(PHENOTYPE_FIELDS):
			SHOW_PHENOTYPE = True
		if UPLOADED_FILES:
			SHOW_FILES = True

		# we provide a wrapper around the form, so that we can hide it
		# by default when there are no validation errors

		preForm = '\n'.join ([
			'<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" ',
			'WIDTH="100%"><TR><TD BGCOLOR="#d0e2f3">',
			'''<B><A HREF="" onClick="toggle('mainForm'); return false;">''',
			'Edit Your Submission</A></B>&nbsp;&nbsp;Open or ',
			'close your submission form',
			'</TD></TR></TABLE>',
			'<SPAN ID="mainForm" STYLE="display:none;">',
			])
		postForm = '</SPAN>'	

	items = items + [
		'<PRE>%s</PRE>' % text,
		'<FORM ACTION="%ssubmissions/amsp_submission.cgi" ENCTYPE="multipart/form-data" METHOD="POST">' % config['MGIHOME_URL'],
		preForm,
		getMainForm(True),
		postForm,
		'<P>',
		]

	if SUBMISSION_SUBDIR:
		items.append (
			'<INPUT TYPE="hidden" NAME="submission" VALUE="%s">' \
			% SUBMISSION_SUBDIR)

	if hadErrors:
		# with errors, we need to come back to the verification step

		items = items + [
			'<B>Use the buttons below to verify your data before ',
			'submission or to reset the entire form.<BR>Thank ',
			'you!</B><P>',
			'<INPUT VALUE="Verify" TYPE="submit">&nbsp;',
			'''<INPUT VALUE="Reset" TYPE="button" onClick="toggle('confirmReset');">''',
			getResetSpan(),
			'<INPUT TYPE="hidden" NAME="cameFrom" VALUE="initial">',
			'</FORM>',
			]
	else:
		# with no errors, we can actually do the submission

		items = items + [
			'<HR>',
			'<B>Use the button below to send your submission. ',
			'<BR>Thank you!</B><P>',
			'<INPUT TYPE="hidden" NAME="cameFrom" VALUE="verify">',
			'<INPUT VALUE="Submit" TYPE="submit">',
			'</FORM>',
		]

	return '\n'.join (items)

def getFilename (
	id			# string; cookie ID from the user's browser
	):
	# Purpose: find the path to the file which contains the contact info
	#	corresponding to the user's cookie ID
	# Returns: string; full path to the file
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing
	# Notes: We use ten different cookie files to try to minimize the
	#	chance of conflicts, while still not polluting /tmp too badly.

	return BASE_COOKIE_FILE + str(hash(id) % 10)

def readFile (
	id			# string; cookie ID from the user's browser
	):
	# Purpose: read the data file which would contain contact info for the
	#	user's given cookie ID
	# Returns: dictionary; maps from string IDs to their corresponding
	#	encoded strings
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing
	# Notes: Upon reading the file, we remove any expired data before
	#	returning the dictionary.  This is how we keep the files from
	#	growing continuously; when we save the dictionary to the file,
	#	the old entries will be gone.

	filename = getFilename(id)

	if os.path.exists(filename):
		try:
			fp = open (filename, 'r')
			dict = pickle.load(fp)
			fp.close()
		except:
			log ('failed to read cache file %s' % filename)
			return {}
	else:
		return {}

	now = time.time()
	for (key, (expires, value)) in dict.items():
		if expires < now:
			del dict[key]
	return dict

def writeFile (
	id,			# string; cookie ID from the user's browser
	parms			# string; encoded string of contact info
	):
	# Purpose: to write the given 'parms' to the proper file for the given
	#	'id', so we can remember them and pre-populate the contact
	#	information sections in the future
	# Returns: None
	# Modifies: write a file to the file system
	# Assumes: nothing
	# Throws: nothing

	# We re-read the file at this point, to pick up any data that has been
	# added since we read it initially in the loadCookie() function.

	dict = readFile(id)

	# The cookie expires in an hour on the user's side, but we allow an
	# extra ten minutes here in case the user's system time is off a bit.

	expires = time.time() + 60 * 70			# one hour, ten min.
	dict[id] = (expires, parms)

	filename = getFilename(id)
	try:
		fp = open (filename, 'w')
		pickle.dump (dict, fp, 0)
		fp.close()
		runCommand.runCommand ('chmod 664 %s' % filename)
	except:
		log ('failed to write cache file %s' % filename)
	return

def loadCookie():
	# Purpose: load data from the user's cookie, if there is one, and
	#	pre-populate the relevant data fields
	# Returns: nothing
	# Modifies: alters globals 'MY_COOKIE' and 'COOKIE_IE'; reads a file
	#	from the file system
	# Assumes: nothing
	# Throws: nothing

	global MY_COOKIE, COOKIE_ID

	# if we were given a cookie, then we need to pull the data into our
	# SimpleCookie object

	if os.environ.has_key('HTTP_COOKIE'):
		MY_COOKIE.load (os.environ['HTTP_COOKIE'])

	# if the cookie is missing the ID field, then just bail out and ignore
	# the cookie

	if not MY_COOKIE.has_key('id'):
		return

	id = MY_COOKIE['id'].value

	# remember this globally so we can update its data later at the end
	COOKIE_ID = id	

	dict = readFile(id)

	if not dict.has_key(id):
		log ('received unknown/expired value for cookie: %s' % id)
		return

	# the 'dict' entry for our 'id' has two fields: the first is an
	# expiration time, and the second is the encoded data

	fieldValues = decodeCacheString(dict[id][1])

	# initialize field values from our cached values

	for fieldname in CACHE_FIELDS:
		getField(fieldname).set(fieldValues)
	return

def setCookie():
	# Purpose: set up a cookie to send to the user, and cache its data in
	#	the relevant data file
	# Returns: nothing
	# Modifies: global 'MY_COOKIE'; reads and writes a data file in the
	#	file system
	# Assumes: nothing
	# Throws: nothing

	global MY_COOKIE

	# encode our cache-able parameters as a string; if none, bail out

	parms = encodeCacheString()
	if not parms:
		return

	# if the user gave us an ID via a cookie, then we should just update
	# the data for that one

	if COOKIE_ID:
		id = COOKIE_ID
	else:
		# Otherwise, we need to assign a new ID.  Check its associated
		# data file to see if we already assigned that ID (which is
		# unlikely, but we'll check).  Repeat until we pick an unused
		# one.

		id = randomString(16)

		dict = readFile(id)
		while dict.has_key(id):
			id = randomString(16)
			dict = readFile(id)

	MY_COOKIE['id'] = id
	MY_COOKIE['id']['max-age'] = 60	* 60		# one hour

	writeFile(id, parms)		# save the values for this cookie ID
	return

def sendInitialForm (
	output		# Template object; handles our page composition
	):
	# Purpose: write out our initial submission form page
	# Returns: nothing
	# Modifies: writes to stdout (the user's browser)
	# Assumes: nothing
	# Throws: nothing

	output.setBody(getInitialForm())
	print output.getFullDocument()
	return

def updateFields (
	parms		# cgi.FieldStorage object; user's input parameters
	):
	# Purpose: update our Field objects, based on the user's input
	# Returns: nothing
	# Modifies: global UPLOADED_FILES, and our Field objects
	# Assumes: nothing
	# Throws: nothing

	global UPLOADED_FILES

	# dictionary mapping a field name to its value, where the value will
	# be either a string or a list of strings, depending on whether the
	# field is multi-valued
	dict = {}

	# convert our FieldStorage object to our 'dict'

	for key in parms.keys():
		
		if type(parms[key]) == types.ListType:
			dict[key] = []
			for item in parms[key]:
				dict[key].append(item.value)
		else:
			dict[key] = parms[key].value

	# request an initial field, so that global ALL_FIELDS gets populated
	getField('lastName')

	# pass our dictionary into each Field, so it can look for its value

	for (fieldname, field) in ALL_FIELDS.items():
		field.set(dict)

	# build a list of dictionaries, one per uploaded data file; each dict
	# will have three keys:  filename, length, and contents

	for i in range(1,11):
		key = 'file' + str(i)
		if parms.has_key(key) and parms[key].value != '':
			filename = parms[key].filename
			contents = parms[key].value

			UPLOADED_FILES.append ( {
				'filename' : filename,
				'length' : len(contents),
				'contents' : contents } )
	return

def anySubmitted (
	allFields 		# list of strings; all fieldnames in section
	):
	# Purpose: determine if a value was submitted for any of 'allFields'
	# Returns: boolean; True if any submitted, False if not
	# Modifies: nothing
	# Assumes: nothing
	# Throws: nothing

	# special handling for inheritance field with unknown default
	inheritance = getField('inheritance')

	for field in allFields:
		if field.getValue():
			if field != inheritance:
				return True

			# special checks for the Inheritance field; to be
			# considered a submitted choice, it should be:
			#   1. not the 'unknown/not applicable' choice
			#   2. not the default '' choice

			if not field.getValue().startswith('unknown'):
				if not field.getValue().strip() == '':
					return True
	return False

def checkSection (
	allFields, 		# list of strings; all fieldnames in section
	requiredFieldnames, 	# list of strings; required fieldnames in sec.
	sectionName		# string; name of the section, for reporting
	):
	# Purpose: if any fields in a section are filled in, then the required
	#	fields for that section must be filled in.  (If no fields were
	#	submitted for that section, then the required fields don't
	#	have to be.)
	# Returns: list of strings, each of which is an error message
	# Modifies: alters global ERRANT_FIELDS
	# Assumes: nothing
	# Throws: nothing

	global ERRANT_FIELDS

	errors = []			# list of error strings

	if anySubmitted(allFields):
		for fieldname in requiredFieldnames:
			if not getField(fieldname).getValue():
				errors.append ('If you enter any field in the %s section, you must enter a value for %s' % (
					sectionName, 
					getField(fieldname).getLabel() ) )
				ERRANT_FIELDS[fieldname] = True
	return errors
	
# dictionary; maps from gene ID/symbol to boolean (True/False) indicating
# whether it is a valid gene ID/symbol
KNOWN_GENES = {}

def isKnownGene (
	gene		# string; gene ID or symbol
	):
	# Purpose: to determine whether 'gene' identifies a valid gene
	# Returns: boolean; True if is a valid gene, False if not
	# Modifies: global 'KNOWN_GENES'
	# Assumes: we can query the database
	# Throws: nothing

	global KNOWN_GENES

	if not KNOWN_GENES.has_key(gene):
		results = homelib.sql ('''SELECT m._Marker_key
			FROM MRK_Marker m
			WHERE m._Organism_key = 1
				AND m._Marker_Status_key IN (1,3)
				AND lower(m.symbol) = lower('%s')
			UNION
			SELECT a._Object_key
			FROM ACC_Accession a
			WHERE a._MGIType_key = 2
				AND a._LogicalDB_key = 1
				AND lower(a.accID) = lower('%s')''' % (gene, gene) )
		KNOWN_GENES[gene] = len(results) != 0

	return KNOWN_GENES[gene]

# dictionary; maps from allele symbol to boolean (True/False) indicating
# whether it is a valid allele symbol
KNOWN_ALLELES = {}

def isKnownAllele (
	allele		# string; allele symbol
	):
	# Purpose: to determine whether 'allele' identifies a valid allele
	# Returns: boolean; True if is a valid allele, False if not
	# Modifies: global 'KNOWN_ALLELES'
	# Assumes: we can query the database
	# Throws: nothing

	global KNOWN_ALLELES

	if not KNOWN_ALLELES.has_key(allele):
		results = homelib.sql ('''SELECT _Allele_key
			FROM ALL_Allele
			WHERE lower(symbol) = lower('%s')''' % allele.strip())
		KNOWN_ALLELES[allele] = len(results) != 0

	return KNOWN_ALLELES[allele]

def doExtraValidation():
	# Purpose: do extra validation for fields (more than simply checking
	#	whether the field is empty or not)
	# Returns: list of error strings
	# Modifies: global variables shown in 'global' statement below
	# Assumes: we can query the database
	# Throws: nothing

	global ERRANT_FIELDS, SHOW_ALLELE, SHOW_PHENOTYPE, SHOW_STRAIN
	global KNOWN_ALLELES, file1

	errors = []

	# verify that the copyright question has been answered in the case of a 
	# file submission
	
	copyright = getField('isCopyrighted')
		
	if file1 != '' and file1.value != '' and copyright.getValue() == '':
		ERRANT_FIELDS['isCopyrighted'] = True
		errors.append ('You must answer the copyright question when submitting a file.')

	# verify email address format (roughly); see regex below

	email1 = getField('email').getValue()
	email2 = getField('email2').getValue()

	emailRE = re.compile('.+@.+\..+')			# a@b.c

	if email1 and not emailRE.match(email1):
		ERRANT_FIELDS['email'] = True
		errors.append ('E-mail address is not valid: %s' % email1)
	if email2 and not emailRE.match(email2):
		ERRANT_FIELDS['email2'] = True
		errors.append ('E-mail address is not valid: %s' % email2)

	# email addresses must match

	if email1 and email2 and (email1 != email2):
		ERRANT_FIELDS['email'] = True
		ERRANT_FIELDS['email2'] = True
		errors.append ('E-mail address fields do not match')

	# allele symbol/name & class of allele must be filled in, if any
	# fields in that section were filled in

	e = checkSection (ALLELE_FIELDS, [ 'alleleSymbol', 'alleleClass' ],
		'Enter Allele Data')
	if e:
		SHOW_ALLELE = True
		errors = errors + e

	# strain name & strain category must be filled in, if any fields in
	# that section were filled in

	e = checkSection (STRAIN_FIELDS, [ 'strain', 'strainCategory' ],
		'Register a New Mouse Strain')
	if e:
		SHOW_STRAIN = True
		errors = errors + e

	# allele pairs, genetic background, and phenotype description must be
	# filled in, if any fields in that section were filled in

	e = checkSection (PHENOTYPE_FIELDS, [ 'allelePairs',
		'geneticBackground', 'phenoDescription' ],
		'Submit Phenotype Data')
	if e:
		SHOW_PHENOTYPE = True
		errors = errors + e

	return errors

def buildText(escapeValues = False):
	# Purpose: build a textual representation of the submitted fields
	# Returns: string of pre-formatted text
	# Modifies: alters globals listed in 'global' statement below
	# Assumes: nothing
	# Throws: nothing

	global SHOW_ALLELE, SHOW_PHENOTYPE, SHOW_STRAIN, ERRANT_FIELDS, ERRORS

	# list of sections with Field objects
	sections = [ CONTACT_FIELDS, CITING_FIELDS, ALLELE_FIELDS,
		STRAIN_FIELDS, PHENOTYPE_FIELDS, COMMENTS_FIELDS, CAPTCHA_FIELDS ]

	# list of strings, each one line for pre-formatted text output
	lines = []

	captcha_element = ''
	if config.has_key('CAPTCHA_ELEMENT'):
		captcha_element = config['CAPTCHA_ELEMENT']
	captcha_timeout = ''
	if config.has_key('CAPTCHA_TIMEOUT'):
		captcha_timeout = config['CAPTCHA_TIMEOUT']
	captche_hide = ''
	if config.has_key('CAPTCHA_HIDE'):
		captcha_hide = config['CAPTCHA_HIDE']
	

	for section in sections:
		# did we have at least one line of output for this section?
		hadOne = False

		for field in section:

			# validate each field in the section
			field.validate()
			fieldErrors = field.getErrors()
			
			if field.getFieldname() == captcha_element:
				if field.getValue() != None and int(field.getValue()) < int(captcha_timeout):
					ERRORS.append("You must fill out all required fields")
					ERRANT_FIELDS[field.getFieldname()] = True
			elif (field.getFieldname() == captcha_hide):
				if field.getValue() != '' and field.getValue() != None:
					ERRORS.append("You must fill out all required fields.")
					ERRANT_FIELDS[field.getFieldname()] = True
		
			# if we have a value, we'll need to
			# add to our output 'lines'

			elif field.getValue():
				# handle escaping of < and > characters

				if escapeValues:
					prValue = cgi.escape(str(
						field.getValue()))
				else:
					prValue = str(field.getValue())

				# if we have a multi-line field, then we need
				# to add an initial line break to keep the
				# data together

				if '\n' in prValue:
					prValue = '\n' + prValue

				lines.append ('%s : %s' % (field.getLabel(),
					prValue))

				hadOne = True

			# if there were error messages, add them and
			# flag the field

			if fieldErrors:
				ERRORS = ERRORS + fieldErrors
				ERRANT_FIELDS[field.getFieldname()] = True
				
				# errors in certain sections require
				# that we automatically show them
				# rather than having them hidden

				if section == ALLELE_FIELDS:
					SHOW_ALLELE = True
				elif section == STRAIN_FIELDS:
					SHOW_STRAIN = True
				elif section == PHENOTYPE_FIELDS:
					SHOW_PHENOTYPE = True

		# if we had a line in this section, then we need to add a
		# divider line

		if hadOne and section != sections[-1]:
			lines.append ('-' * 50)

	# do any extra, more complex validations
	moreErrors = doExtraValidation()

	# include data for any uploaded files
	if UPLOADED_FILES:
		lines.append ('-' * 50)
		lines.append ('Uploaded Files')

		# It is possible for a user to select files for upload and to
		# alter previously valid Fields so that they are then errant.
		# In that case, we will not save the uploaded files and we
		# we will send the user back to a new validation page.  This
		# keeps us from having to match up files with complete 
		# submission forms that come later.

		if ERRANT_FIELDS:
			ERRORS.append ('Uploaded files were not saved, ' \
					+ 'due to verification errors')
		else:
			if getField('isCopyrighted') != None:
				lines.append('Copyrighted: ' + str(getField('isCopyrighted').getValue()))
			for file in UPLOADED_FILES:
				lines.append ('Uploaded file: %s (%s bytes)' \
					% (file['filename'],
						file['length'] ) )

	# If we discovered more validation errors, show them below the
	# uploaded file section.
	if moreErrors:
		ERRORS = ERRORS + moreErrors

	return '\n\n'.join(lines)

def sendVerifyForm (
	output		# Template object; handles our page composition
	):
	# Purpose: write out our verification page for a user's submission
	# Returns: nothing
	# Modifies: writes to stdout (the user's browser)
	# Assumes: nothing
	# Throws: nothing

	output.setBody(getVerifyForm())
	print output.getFullDocument()
	return

def checkConfig():
	# Purpose: check that our configuration parameters are okay
	# Returns: nothing
	# Modifies: nothing
	# Assumes: nothing
	# Throws: 'error' if problems are found in the parameters

	if not config.has_key('SUBMISSION_DIRECTORY'):
		raise error, 'No config info for SUBMISSION_DIRECTORY'

	if not os.path.exists(config['SUBMISSION_DIRECTORY']):
		raise error, 'Invalid directory for SUBMISSION_DIRECTORY'

	if not config.has_key('SENDMAIL'):
		raise error, 'Missing SENDMAIL config variable'

	if not os.path.exists(config['SENDMAIL']):
		raise error, 'Invalid path for SENDMAIL'

	return

def createDirectory():
	# Purpose: create a new submission directory
	# Returns: string, path to new directory
	# Modifies: creates a directory in the file system
	# Assumes: nothing
	# Throws: 'error' if we cannot create the directory
	# Notes: prefix of directory name is the day of the month; remainder
	#        is generated by tempfile to create a unique name

	submissionDir = config['SUBMISSION_DIRECTORY']

	year = time.strftime('%Y', time.localtime(time.time()))
	month = time.strftime('%m', time.localtime(time.time()))
	day = time.strftime('%d', time.localtime(time.time()))

	subDirYear = submissionDir + '/' + year
	subDirYearMonth = subDirYear + '/' + month

	# Create the year sub-directory if it doesn't exist.
	if not os.path.exists(subDirYear):
		runCommand.runCommand ('mkdir -p %s' % subDirYear)
		runCommand.runCommand ('chmod 770 %s' % subDirYear)

	# Create the month sub-directory if it doesn't exist.
	if not os.path.exists(subDirYearMonth):
		runCommand.runCommand ('mkdir -p %s' % subDirYearMonth)
		runCommand.runCommand ('chmod 770 %s' % subDirYearMonth)

	# Create the submission directory.
	try:
		newDir = tempfile.mkdtemp(prefix = day + '_', dir = subDirYearMonth)
		runCommand.runCommand ('chmod 770 %s' % os.path.join(newDir))
	except:
		raise error, 'Cannot create new directory using mkdtemp'

	return newDir

def getFileData (
	dir 		# string; name of the submission directory
	):
	# Purpose: get information on the files saved in 'dir'
	# Returns: list of dictionaries, each with two keys:  filename and
	#	length
	# Modifies: reads from the file system
	# Assumes: nothing
	# Throws: nothing

	files = []

	if not os.path.isdir(dir):
		log ('%s is not a directory' % dir)
		return files

	for file in os.listdir(dir):
		try:
			path = os.path.join (dir, file)
			size = os.stat(path)[6]

			files.append ({ 'filename' : file, 'length' : size })
		except:
			pass
	return files

def saveFile (
	dir, 		# string; name of the submission directory
	filename, 	# string; name of the file to save
	contents	# string; contents of the file to be saved
	):
	# Purpose: write the given 'filename' to the given directory 'dir',
	#	containing the given 'contents'
	# Returns: nothing
	# Modifies: writes a file to the file system
	# Assumes: nothing
	# Throws: raises 'error' if we cannot write the file

	try:
		fp = open(os.path.join(dir, filename), 'w')
		fp.write(contents)
		fp.flush()
		fp.close()
		runCommand.runCommand ('chmod 660 %s' % os.path.join(dir,
			filename))
	except:
		raise error, 'Failed to write file: %s' % os.path.join (
			dir, filename)
	return

def saveUploadedFiles (
	dir		# string; name of the submission directory
	):
	# Purpose: write the user's uploaded files to the submission directory
	# Returns: nothing
	# Modifies: writes files to the file system
	# Assumes: nothing
	# Throws: raises 'error' if we cannot save one or more files

	alreadySaved = {}	# dictionary of filenames already saved
	failedFiles = []	# list of filenames which failed to save

	for file in UPLOADED_FILES:
		filename = file['filename']
		contents = file['contents']

		# trim off any directory separator, to just leave the base
		# filename

		if filename.find('/'):
			filename = filename.split('/')[-1]
		elif filename.find('\\'):
			filename = filename.split('\\')[-1]

		# if we've already saved a file by this name to the submission
		# directory, then add numeric suffix that increments until we
		# generate a new unique name for the file

		if alreadySaved.has_key(filename):
			i = 1
			f2 = filename + '.' + str(i)
			while alreadySaved.has_key(f2):
				i = i + 1
				f2 = filename + '.' + str(i)
			filename = f2

		try:
			saveFile(dir, filename, contents)
		except:
			failedFiles.append (filename)

	if failedFiles:
		raise error, 'Failed to write %d file(s) [%s] to dir %s' % (
			len(failedFiles), ', '.join(failedFiles), dir)
	return

def saveText (
	dir, 		# string; submission directory
	text		# string; text of the submission form fields
	):
	# Purpose: write the user's form fields to a file in the submission
	#	directory
	# Returns: nothing
	# Modifies: writes a file to the file system
	# Assumes: nothing
	# Throws: raises 'error' if we cannot save the file

	saveFile(dir, 'submissionForm.txt', text)
	return

def sendError (
	output,		# Template object; handles our page composition
	message		# string; error message for the user
	):
	# Purpose: write an error message to the user's browser, and logs the
	#	current exception information to Apache's error.log file
	# Returns: does not return; exits the script
	# Modifies: writes to stdout (to the user's browser), and appends to
	#	Apache's error.log
	# Assumes: nothing
	# Throws: raises SystemExit to exit the script

	(exc_type, exc_message, exc_traceback) = sys.exc_info()
	sys.stderr.write ('amsp_submission.cgi : %s : %s\n' % (exc_type,
		exc_message))
	traceback.print_exception (exc_type, exc_message, exc_traceback, None,
		sys.stderr)


	output.setBody ('Error: %s' % message)
	print output.getFullDocument()
	sys.exit(0)

def sendMail (
	text,		# string; text of the submission form fields
	fromAddr,	# string; sending email address
	toAddr,		# string; destination email address
	subject		# string; subject of email message
	):
	# Purpose: send a confirmation email to the user, containing the
	#	'text' of his/her submission
	# Returns: nothing
	# Modifies: invokes sendmail in a shell; may write an exception to
	#	Apache's error.log
	# Assumes: nothing
	# Throws: 'error' if the email cannot be sent

	# message contents
	items = [
		'From: %s' % fromAddr,
		'To: %s' % toAddr,
		'Subject: %s' % subject,
		'',
		text,
		''
		]

	try:
		fd = os.popen('%s -t' % config['SENDMAIL'], 'w')
		fd.write ('\n'.join(items))
		fd.close()
	except:
		(exc_type, exc_message, exc_traceback) = sys.exc_info()
		sys.stderr.write ('amsp_submission.cgi : %s : %s\n' % (
			exc_type, exc_message))
		traceback.print_exception (exc_type, exc_message, 
			exc_traceback, None, sys.stderr)

		raise error, 'Cannot send confirmation email'
	return

def acceptSubmission (
	output		# Template object; handles our page composition
	):
	# Purpose: accept and process a user's submission
	# Returns: nothing
	# Modifies: adds a directory and files to the file system, writes to
	#	stdout (to the user's browser)
	# Assumes: nothing
	# Throws: nothing

	# build a text representation of the submission & validate the fields

	text = buildText(True)
	hadErrors = len(ERRANT_FIELDS) > 0

	# if there were errors, then do not accept the submission; instead,
	# give the user a new verification form with errors indicated

	if hadErrors:
		output.setBody(getVerifyForm(text))
		print output.getFullDocument()
		return

	# no errors, so process submission as follows:
	# 1. look up submission directory, or create it if there's not one
	# 2. save the submission fields as a text file
	# 4. send a confirmation email to the user
	# 5. send a confirmation page to the user's browser

	if SUBMISSION_SUBDIR:
		myDir = os.path.join (config['SUBMISSION_DIRECTORY'],
			SUBMISSION_SUBDIR)
	# HERE
	else:
		try:
			myDir = createDirectory()
		except:
			sendError(output, 'Could not create a directory for '\
				+ 'your submission.  Please try again later.')

	unescapedText = buildText()
	try:
		saveText(myDir, unescapedText)
	except:
		sendError(output, 'Could not save your submission.  ' + \
			'Please try again later.')

	# at this point, the submission has been successfully saved

	items = [
		'The following items have been successfully submitted:<P>',
		'<PRE>%s</PRE>' % text,
		]

	try:
		sendMail(unescapedText, 'mgi-submissions@jax.org',
			getField('email').getValue(),
			'Confirmation of your form submission')
	except:
		items.append ('However, we were unable to send a ' + \
			'confirmation email.  Please print this page as ' + \
			'a record of your submission.')

	try:
		unescapedText = unescapedText + \
			'\n\nSubmission Directory: %s' % myDir + '\n'
		sendMail(unescapedText, getField('email').getValue(),
			SUBMISSIONS,
			'Received AMSP form submission')
	except:
		log ('Failed to send notification email to %s' % SUBMISSIONS)

	items.append ('<P>Would you like to <A HREF="%ssubmissions/amsp_submission.cgi">make another submission</A>?' % config['MGIHOME_URL'])
	output.setBody('\n'.join(items))
	print output.getFullDocument() 
	return

def main():
	# Purpose: main program
	# Returns: nothing
	# Modifies: writes to stderr and stdout
	# Assumes: nothing
	# Throws: nothing

	global UPLOADED_FILES, SUBMISSION_SUBDIR
	global file1

	# initial setup of output page (assume TEMPLATE_PATH is correct)
	myTitle = 'Mutant Alleles, Strains, and Phenotypes Submission Form'
	output = template.Template(config['TEMPLATE_PATH'])
	output.setTitle(myTitle)
	output.setHeaderBarMainText(myTitle)
	output.setJavaScript(getJavascript())

	# check that our config file is set up appropriately; if not, bail out
	try:
		checkConfig()
	except:
		sendError(output, 'Configuration errors were detected.')

	# get input parameters from form submission, and update our Field
	# objects
	parms = cgi.FieldStorage()
	
	if parms.has_key('file1'):
		file1 = parms['file1']
	else: # The file has already been stripped off and converted.
		file1 = ''
		

	# get cached values using cookie from the user, if available, to
	# pre-populate the contact info fields; however, only do this for an
	# initial page request
	if not parms.has_key('cameFrom') and not parms.has_key('blank'):
		loadCookie()

	updateFields(parms)

	# if we received any uploaded files, we need to create a directory
	# and save them.  We need to remember the directory as a hidden field
	# in the next form we write out.

	if UPLOADED_FILES:
		try:
			myDir = createDirectory()
		except:
			sendError(output, 'Could not create a directory ' + \
				'for your submission.  Please try again ' + \
				'later.') 

		try:
			saveUploadedFiles(myDir)
		except:
			sendError(output, 'Could not save some of your ' + \
				'uploaded files.  Please try again later.')

		# To determine the subdirectory for the submission, take the
		# full path to the new directory and remove the first part
		# that is the top level submission directory.
		SUBMISSION_SUBDIR = re.sub(config['SUBMISSION_DIRECTORY'] + '/', '', myDir)

	# otherwise, if we received a parameter which specified a submission
	# directory, then we need to look up info about the files already
	# submitted.

	elif parms.has_key('submission'):
		SUBMISSION_SUBDIR = parms['submission'].value
		UPLOADED_FILES = getFileData (os.path.join (
			config['SUBMISSION_DIRECTORY'], SUBMISSION_SUBDIR))

	# otherwise, we either had no uploaded files, or this is an initial
	# form, so we're okay as-is

	# cache the user's contact info for near-future submissions
	setCookie()

	if MY_COOKIE:
		output.setCookies(str(MY_COOKIE))

	# which output page should we present?

	if not parms.has_key('cameFrom'):
		# initial request for blank form
		sendInitialForm(output)

	elif parms['cameFrom'].value == 'initial':
		# came from initial form, need verify form now
		sendVerifyForm(output)

	elif parms['cameFrom'].value == 'verify':
		# came from verify form, need to process it and send
		# confirmation
		acceptSubmission(output)

	return

###--- main program ---###

if __name__ == '__main__':
	main()
