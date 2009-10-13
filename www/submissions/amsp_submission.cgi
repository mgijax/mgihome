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

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import feedbacklib
import runCommand
import template
import homelib

###--- basic global variables ---###

MY_COOKIE = Cookie.SimpleCookie()
BASE_COOKIE_FILE = '/tmp/submissionCookies.'
REQUIRED = feedbacklib.REQUIRED
COOKIE_ID = None
ERRANT_FIELDS = {}

###--- groups of Field objects, one per form section ---###

CONTACT_FIELDS = [
	feedbacklib.OneLineTextField ('lastName', 'Last Name', REQUIRED,
		width = 40),
	feedbacklib.OneLineTextField ('firstName', 'First Name', REQUIRED,
		width = 40),
	feedbacklib.OneLineTextField ('email', 'Email Address', REQUIRED,
		width = 40),
	feedbacklib.OneLineTextField ('email2', 'Email Address (repeat)',
		REQUIRED, width = 40),
	feedbacklib.OneLineTextField ('labPI', 'Laboratory PI', width = 40),
	feedbacklib.OneLineTextField ('institute', 'Institute/Organization',
		width = 40),
	feedbacklib.OneLineTextField ('street', 'Street Address', width = 40),
	feedbacklib.OneLineTextField ('city', 'City', width = 40),
	feedbacklib.OneLineTextField ('state', 'State/Province', width = 40),
	feedbacklib.OneLineTextField ('zip', 'Postal Code', width = 40),
	feedbacklib.OneLineTextField ('country', 'Country', width = 40),
	feedbacklib.OneLineTextField ('phone', 'Telephone', width = 40),
	feedbacklib.OneLineTextField ('fax', 'Fax', width = 40),
]

CITING_FIELDS = [
	feedbacklib.RadioButtonGroup ('isPublished',
		'Is your data published?',
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
		items = [ [ ('dominant', 'dominant'),
			('codominant', 'codominant'),
			('semidominant', 'semidominant'),
			('recessive', 'recessive'),
			('X-linked', 'X-linked'),
			('other', 'other (specify)', 30) ] ] ),
	feedbacklib.OneLineTextField ('strainBackground', 'Strain background',
		width = 35),
	feedbacklib.MultiLineTextField ('location',
		'Genome Location and Molecular Detail',
		height = 3, width = 90),
	feedbacklib.CheckboxGroup ('nomenHelp',
		'Request help with allele nomenclature',
		items = [ [ ('yes', '') ] ]),
]

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

FILE_FIELDS = [
	# TBD
]

COMMENTS_FIELDS = [
	feedbacklib.MultiLineTextField ('finalComments',
		'Additional Comments or Information about your data',
		height = 2, width = 80),
]

###--- dictionary of all Field objects, for quick access by name ---###
ALL_FIELDS = {}

###--- name of all Fields whose values may be cached using a cookie ---###
CACHE_FIELDS = [ 'lastName', 'firstName', 'email', 'email2', 'labPI',
	'institute', 'street', 'city', 'state', 'zip', 'country', 'phone',
	'fax', 'isPublished', 'makePublicNow', 'references', 'url' ]

###--- functions ---###

def log(message):
	sys.stderr.write ('amsp_submission.cgi : %s\n' % message)
	return

def label(fieldname, labelStr):
	if not ERRANT_FIELDS.has_key(fieldname):
		return labelStr
	return '<SPAN STYLE="background-color: yellow">%s</SPAN>' % labelStr

def randomString (length):
	chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	chars = chars + chars.lower() + '0123456789'

	s = ''

	for i in range(0, length):
		s = s + random.choice(chars)
	return s

def getJavascript():
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
	specialChars = '!@#$%^&*()-_+=[]{}|:;<>/?,.0123456789qwzxQWZX`'

	items = []
	for fieldname in CACHE_FIELDS:
		field = getField (fieldname)
		if not field.isEmpty():
			items.append ( (fieldname, field.getValue()) )

	delim = None
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

	if not delim:
		log ('could not find unused character for delimiter')
		return None
	
	s = ''
	for (fieldname, fieldvalue) in items:
		if fieldname and fieldvalue:
			s = s + delim + fieldname + delim + fieldvalue
	return s

def decodeCacheString(s):
	dict = {}
	if not s:
		return dict

	delim = s[0]
	items = s[1:].split(delim)

	i = 0
	while i < len(items):
		fieldname = items[i]
		fieldvalue = items[i+1]

		dict[fieldname] = fieldvalue
		i = i + 2
	return dict

def getField (fieldname):
	global ALL_FIELDS

	# if we didn't populate the cache yet, then do it
	if not ALL_FIELDS:
		for group in [ CONTACT_FIELDS, CITING_FIELDS, ALLELE_FIELDS,
			STRAIN_FIELDS, PHENOTYPE_FIELDS, FILE_FIELDS,
			COMMENTS_FIELDS ]:
			for field in group:
				if ALL_FIELDS.has_key(field.getFieldname()):
					raise 'ERROR', \
						'Duplicate fieldname: %s' % \
						field.getFieldname()
				ALL_FIELDS[field.getFieldname()] = field

	if ALL_FIELDS.has_key(fieldname):
		return ALL_FIELDS[fieldname]

	log ('requested unknown fieldname: %s' % fieldname)
	return None

def sectionTitle (s, hasRequiredFields = True):
	s = '<H3>%s:' % s
	if hasRequiredFields:
		s = s + ' &nbsp;&nbsp;&nbsp;&nbsp;' + \
			'<FONT SIZE="-2"><FONT COLOR="red">*</FONT> ' + \
			'= required field</FONT>'
	s = s + '</H3>'
	return s

def getContactSection():
	items = [ sectionTitle('Contact Details'),
		'<TABLE>',
		'<TR><TD>%s</TD><TD><FONT COLOR="red">*</FONT>' % \
			label('lastName', 'Last name:'),
		getField('lastName').getHTML(),
		'</TD>',
		'<TD>&nbsp;&nbsp;&nbsp;</TD>',
		'<TD>%s</TD><TD>' % label('street', 'Street Address:'),
		getField('street').getHTML(),
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
	items = [ sectionTitle('Citing your data', False),
		'Is your data published?&nbsp;&nbsp;&nbsp;',
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
	items = [ sectionTitle('Enter Allele Data'),
		'Suggest <B>symbol</B> and/or <B>name</B> for this ',
		'mutation: <FONT COLOR="red">*</FONT>',
		getField('alleleSymbol').getHTML(),
		'<P>',
		'If this mutation is an allele of a <B>known gene</B> ',
		'enter the <B>gene symbol</B> or <B>MGI ID</B>: ',
		getField('gene').getHTML(),
		' (<I><B>Check by</B></I> <A HREF="%sWIFetch?page=markerQF" '\
			% config['JAVAWI_URL'],
		'TARGET="_new">searching MGI</A>.)<P>',
		'Common nicknames for this mutant allele ',
		getField('nicknames').getHTML(),
		'<P>',
		'Class of Allele (check all that apply): &nbsp;',
		'<FONT COLOR="red">*</FONT>',
		'<BLOCKQUOTE>',
		getField('alleleClass').getHTML(),
		'<P>',
		'For transgenes, specify transgene promoter: ',
		getField('promoter').getHTML(),
		'<BR>',
		'For targeted mutations of gene traps, specify ES cell line',
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
		'TARGET="_new">',
		'Quick Guide to Nomenclature for Alleles and Mutations</A>.',
		'</LI><LI><A ',
		'HREF="http://dels.nas.edu/ilar_n/ilarhome/labcode.shtml" ',
		'TARGET="_new">',
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
	items = [ sectionTitle('Register a New Mouse Strain'),
		'Enter a suggested <B>strain name</B>.<BR>',
		'When mutant alleles are part of the strain name, use ',
		'&lt; &gt; to indicate the superscripted alleles.<BR>',
		'<I>Example:</I> <B>C57BL/6J-Kit<SUP>W-39J</SUP></B> should ',
		'be entered as <B>C57BL/6J-Kit&lt;W-39J&gt;</B><BR>',
		'<FONT COLOR="red">*</FONT>',
		getField('strain').getHTML(),
		'<P>',
		'Enter the <B>gene symbols</B> corresponding to alleles ',
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
		'%sfetch?page=imsrStrainRepositories">repositories</A>)' % \
			config['IMSRURL'],
		'<BR>',
		'Enter its repository ID or MGI ID for this strain, if known ',
		getField('repositoryID').getHTML(),
		'<P>',
		'<B>Strain categories</B>: Choose one or more. ',
		'<FONT COLOR="red">*</FONT><BLOCKQUOTE>',
		getField('strainCategory').getHTML(True),
		'</BLOCKQUOTE><P>',
		'<UL><LI>For hints on strain nomenclature, see ',
		'<A HREF="%snomen/strains.shtml" ' % config['MGIHOME_URL'],
		'TARGET="_new">',
		'Quick Guide to Nomenclature for Alleles and Mutations</A>.',
		'</LI><LI><A ',
		'HREF="http://dels.nas.edu/ilar_n/ilarhome/labcode.shtml" ',
		'TARGET="_new">',
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
		'Enter allele pairs of your phenotyped animals: ',
		'<FONT COLOR="red">*</FONT><BR>',
		getField('allelePairs').getHTML(),
		'(Find the correct allele symbol by <A HREF=',
		'"%ssearches/allele_form.shtml">searching MGI</A>.)' % \
			config['WI_URL'],
		'<P>',
		'Additional allele information not currently in MGI (allele ',
		'synonyms, ES cell line, strain of origin, mutation type, ',
		'molecular description, etc.):<BR>',
		getField('additionalInfo').getHTML(),
		'<P>',
		'<B>Genetic Background:</B> Genetic background can have a ',
		'significant effect on phenotype.<P>',
		'Enter the Strain/Genetic Background on which phenotypes ',
		'were analyzed: <FONT COLOR="red">*</FONT>',
		getField('geneticBackground').getHTML(),
		'<P>',
		'Other Strain/Background Information (e.g. specify ',
		'crosses): Click here for an <A HREF="foo" TARGET="_new">'
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
		'Phenotypic Description (enter text, describing details of ',
		'phenotypes observed, etc.): <FONT COLOR="red">*</FONT><BR>',
		'Click here for an <A HREF="foo" TARGET="_new">example</A>.',
		' You may browse the <A HREF="%ssearches/MP_form.shtml" ' % \
			config['WI_URL'],
		'TARGET="_new">Mammalian Phenotype Ontology</A> and use ',
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

def getFileUploadSection():
	items = [
		sectionTitle('File submissions', False),
		'You may submit a limited number of files using this form. ',
		'Please limit file size to &lt;5 MB.<BR>',
		'If you have larger files, or many files to submit, please ',
		'contact us at: ',
		'<a href="mailto:submissions@informatics.jax.org">',
		'submissions@informatics.jax.org</a>.<P>',
		'Upload your data files (images, text descriptions, Excel, ',
		'or text data):<BR>',
		'File 1: <INPUT NAME="file1" VALUE="" TYPE="file">',
		'<INPUT TYPE="button" onClick="addFile()" NAME="addFileButton" VALUE="Allow more files">',
		'<P>',
		'<SPAN ID="f2" STYLE="display: none;">File 2: <INPUT NAME="file2" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f3" STYLE="display: none;">File 3: <INPUT NAME="file3" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f4" STYLE="display: none;">File 4: <INPUT NAME="file4" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f5" STYLE="display: none;">File 5: <INPUT NAME="file5" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f6" STYLE="display: none;">File 6: <INPUT NAME="file6" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f7" STYLE="display: none;">File 7: <INPUT NAME="file7" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f8" STYLE="display: none;">File 8: <INPUT NAME="file8" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f9" STYLE="display: none;">File 9: <INPUT NAME="file9" VALUE="" TYPE="file"><P></SPAN>',
		'<SPAN ID="f10" STYLE="display: none;">File 10: <INPUT NAME="file10" VALUE="" TYPE="file"> (limit is 10 files)<P></SPAN>',
		'See examples and templates for file submissions.',
		]

	return ''.join(items)

def getCommentsSection():
	items = [
		sectionTitle('Completing your submission', False),
		'Are there any additional commments or information you ',
		'would like to convey about your data?<BR>',
		getField('finalComments').getHTML(),
		]
	return ''.join(items)

def getMainForm():
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
		'<TR ID="alleleSection" STYLE="display:none;"><TD>',
		getAlleleSection(),
		'</TD></TR>',
		'<TR><TD ALIGN="left" BGCOLOR="#d0e2f3">',
		'&nbsp;&nbsp;&nbsp;&nbsp;<B><A HREF="" ',
		'''onClick="toggle('strainSection'); return false;">''',
		'Strain</A></B>&nbsp;&nbsp;',
		'Register a new mouse strain',
		'</TD></TR>',
		'<TR ID="strainSection" STYLE="display:none;"><TD>',
		getStrainSection(),
		'</TD></TR>',
		'<TR><TD ALIGN="left" BGCOLOR="#d0e2f3">',
		'&nbsp;&nbsp;&nbsp;&nbsp;<B><A HREF="" ',
		'''onClick="toggle('phenotypeSection'); return false;">''',
		'Phenotypes</A></B>&nbsp;&nbsp;',
		'Submit phenotype data for given genotypes',
		'</TD></TR>',
		'<TR ID="phenotypeSection" STYLE="display:none;"><TD>',
		getPhenotypeSection(),
		'</TD></TR>',
		'<TR ID="commentsSection"><TD>',
		'<HR>',
		getCommentsSection(),
		'</TD></TR></TABLE>',
		]
	return ''.join (items)

def getInitialForm():
	items = [ 
		'Use this Submission Form to describe spontaneous, induced, ',
		'or genetically engineered mutations, to register new mouse ',
		'strains, and to describe phenotypes.<P>',
		'<FORM ACTION="%ssubmissions/amsp_submission.cgi" METHOD="POST">' % config['MGIHOME_URL'],
		getMainForm(),
		'<P>',
		'<B>Use the buttons below to preview your submission ',
		'or reset the entire form.<BR>Thank you!</B><P>',
		'<INPUT VALUE="Verify" TYPE="submit">&nbsp;',
		'<INPUT VALUE="Reset" TYPE="reset">',
		'<INPUT TYPE="hidden" NAME="cameFrom" VALUE="initial">',
		'</FORM>',
		]
	return '\n'.join (items)

def getVerifyForm():
	text = buildText()
	hadErrors = len(ERRANT_FIELDS) > 0

	items = [
		'Please review the text of your submission below.',
		]
		
	if hadErrors:
		items = items + [
			'Errors have been flagged with an asterisk (*) ',
			'in the text summary, and their respective fields ',
			'are highlighted in yellow ',
			'in the submission form.  Please correct flagged ',
			'items and click the Verify button at the bottom of ',
			'the page.',
			]
		preForm = ''
		postForm = ''
	else:
		items = items + [
			'No errors were detected in your submission.  If ',
			'you would like to make any changes, you may open ',
			'the submission form below.  When finished, you may ',
			'go to the bottom, select any files to upload with ',
			'your submission, and click the Submit button.'
			]
		preForm = '\n'.join ([
			'<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" ',
			'WIDTH="100%"><TR><TD BGCOLOR="#d0e2f3">',
			'''<B><A HREF="" onClick="toggle('mainForm'); return false;">''',
			'Submission Form</A></B>&nbsp;&nbsp;Open or close ',
			'your submission form',
			'</TD></TR></TABLE>',
			'<SPAN ID="mainForm" STYLE="display:none;">',
			])
		postForm = '</SPAN>'

	items = items + [
		'<PRE>%s</PRE>' % text,
		'<FORM ACTION="%ssubmissions/amsp_submission.cgi" METHOD="POST">' % config['MGIHOME_URL'],
		preForm,
		getMainForm(),
		postForm,
		'<P>',
		]

	if hadErrors:
		items = items + [
			'<B>Use the buttons below to preview your submission ',
			'or reset the entire form.<BR>Thank you!</B><P>',
			'<INPUT VALUE="Verify" TYPE="submit">&nbsp;',
			'<INPUT VALUE="Reset" TYPE="reset">',
			'<INPUT TYPE="hidden" NAME="cameFrom" VALUE="initial">',
			'</FORM>',
			]
	else:
		items = items + [
			'<HR>',
			getFileUploadSection(),
			'<P>',
			'<B>Use the button below to send your submission. ',
			'<BR>Thank you!</B><P>',
			'<INPUT TYPE="hidden" NAME="cameFrom" VALUE="verify">',
			'<INPUT VALUE="Submit" TYPE="submit">',
			'</FORM>',
		]

	return '\n'.join (items)

def getFilename (id):
	# use 10 different cookie files to try to minimize the chance of
	# conflicts, while still not polluting /tmp too badly

	return BASE_COOKIE_FILE + str(hash(id) % 10)

def readFile(id):
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

	dict = {}
	now = time.time()
	for (key, (expires, value)) in dict.items():
		if expires < now:
			del dict[key]
	return dict

def writeFile(id):
	dict = readFile(id)

	expires = time.time() + 60 * 70			# one hour, ten min.
	dict[id] = (expires, encodeCacheString())

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
	global MY_COOKIE, COOKIE_ID
	if os.environ.has_key('HTTP_COOKIE'):
		log ('found HTTP_COOKIE %s' % os.environ['HTTP_COOKIE'])
		MY_COOKIE.load (os.environ['HTTP_COOKIE'])

	if not MY_COOKIE.has_key('id'):
		log ('received cookie with no id field: %s' % str(MY_COOKIE.keys()))
		return

	id = MY_COOKIE['id'].value
	COOKIE_ID = id

	log ('received id: %s' % id)
	dict = readFile(id)
	log ('read dict with %d IDs' % len(dict))

	if not dict.has_key(id):
		log ('received unknown/expired value for cookie: %s' % id)
		return

	fieldValues = decodeCacheString(dict[id])

	# initialize field values from cached values using cookie ID
	for fieldname in CACHE_FIELDS:
		getField(fieldname).set(fieldValues)
	return

def setCookie():
	global MY_COOKIE

	parms = encodeCacheString()
	if not parms:
		return

	# update existing info, if user already gave us a cookie ID
	if COOKIE_ID:
		id = COOKIE_ID
	else:
		id = randomString(16)

		dict = readFile(id)
		while dict.has_key(id):
			id = randomString(16)
			dict = readFile(id)

	MY_COOKIE['id'] = id
	MY_COOKIE['id']['expires'] = 60			# one hour

	writeFile(id)			# save the values for this cookie ID
	return

def sendInitialForm(output):
	output.setBody(getInitialForm())
	print output.getFullDocument()
	return

def updateFields(parms):
	# update our Field objects, based on values from 'parms'

	dict = {}
	for key in parms.keys():
		if type(parms[key]) == types.ListType:
			dict[key] = []
			for item in parms[key]:
				dict[key].append(item.value)
		else:
			dict[key] = parms[key].value

	getField('lastName')
	for (fieldname, field) in ALL_FIELDS.items():
		field.set(dict)
	return

def checkSection (allFields, requiredFieldnames, sectionName):
	global ERRANT_FIELDS

	foundAny = False
	for field in allFields:
		if field.getValue():
			foundAny = True
			break

	errors = []

	if foundAny:
		for fieldname in requiredFieldnames:
			if not getField(fieldname).getValue():
				errors.append ('If you enter any field in the %s section, you must enter a value for %s' % (
					sectionName, 
					getField(fieldname).getLabel() ) )
				ERRANT_FIELDS[fieldname] = True
	return errors
	
KNOWN_GENES = {}

def isKnownGene (gene):
	global KNOWN_GENES

	if not KNOWN_GENES.has_key(gene):
		results = homelib.sql ('''SELECT m._Marker_key
			FROM MRK_Marker m
			WHERE m._Organism_key = 1
				AND m._Marker_Status_key IN (1,3)
				AND m.symbol = "%s"
			UNION
			SELECT a._Object_key
			FROM ACC_Accession a
			WHERE a._MGIType_key = 2
				AND a._LogicalDB_key = 1
				AND a.accID = "%s"''' % (gene, gene) )
		KNOWN_GENES[gene] = len(results) != 0

	return KNOWN_GENES[gene]

KNOWN_ALLELES = {}

def isKnownAllele (allele):
	global KNOWN_ALLELES

	if not KNOWN_ALLELES.has_key(allele):
		results = homelib.sql ('''SELECT _Allele_key
			FROM ALL_Allele
			WHERE symbol = "%s"''' % allele.strip())
		KNOWN_ALLELES[allele] = len(results) != 0

	return KNOWN_ALLELES[allele]

def doExtraValidation():
	global ERRANT_FIELDS

	errors = []

	# verify email address format (roughly)

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

	# allele symbol/name & class of allele

	e = checkSection (ALLELE_FIELDS, [ 'alleleSymbol', 'alleleClass' ],
		'Enter Allele Data')
	errors = errors + e

	# strain name & strain category

	e = checkSection (STRAIN_FIELDS, [ 'strain', 'strainCategory' ],
		'Register a New Mouse Strain')
	errors = errors + e

	# allele pairs, genetic background, and phenotype description

	e = checkSection (PHENOTYPE_FIELDS, [ 'allelePairs',
		'geneticBackground', 'phenoDescription' ],
		'Submit Phenotype Data')
	errors = errors + e

	# verify gene symbol/ID for allele

	gene = getField('gene').getValue()
	if gene:
		if not isKnownGene(gene):
			ERRANT_FIELDS['gene'] = True
			errors.append ('Invalid gene symbol/ID: %s' % gene) 

	# verify gene symbols for strain

	genes = getField('genes').getValue()
	if genes:
		unknowns = []
		for gene in map(string.strip, genes.split('\n')):
			if not isKnownGene(gene):
				if gene not in unknowns:
					unknowns.append(gene)
		if unknowns:
			ERRANT_FIELDS['genes'] = True
			errors.append ('Invalid gene(s) for strain: %s' % \
				', '.join (unknowns))

	# verify allele symbols from allele pairs

	allelePairs = getField('allelePairs').getValue()
	if allelePairs:
		pairs = allelePairs.split('\n')
		unknowns = []
		for pair in pairs:
			for allele in pair.split(','):
				allele = allele.strip()
				if not isKnownAllele(allele):
					if allele not in unknowns:
						unknowns.append (allele)
		if unknowns:
			ERRANT_FIELDS['allelePairs'] = True
			errors.append ('Invalid alleles in allele pairs: %s' \
				% ', '.join (unknowns))

	return errors

def buildText():
	sections = [ CONTACT_FIELDS, CITING_FIELDS, ALLELE_FIELDS,
		STRAIN_FIELDS, PHENOTYPE_FIELDS, FILE_FIELDS,
		COMMENTS_FIELDS ]
	lines = []

	for section in sections:
		hadOne = False
		for field in section:
			field.validate()
			fieldErrors = field.getErrors()

			if field.getValue() or fieldErrors:
				prValue = cgi.escape(str(field.getValue()))
				if '\n' in prValue:
					prValue = '\n' + prValue
				lines.append ('%s : %s' % (field.getLabel(),
					prValue))

				if fieldErrors:
					lines[-1] = lines[-1] + ' *'
					for error in fieldErrors:
						lines.append ('  * ' + error)
					ERRANT_FIELDS[field.getFieldname()] =\
						True

				hadOne = True

		if hadOne and section != sections[-1]:
			lines.append ('-' * 50)

	moreErrors = doExtraValidation()

	if moreErrors:
		lines.append ('More Validation Errors')
		for error in moreErrors:
			lines.append ('  * ' + error)

	return '\n'.join(lines)

def sendVerifyForm(output):
	output.setBody(getVerifyForm())
	print output.getFullDocument()
	return

def sendConfirmation(output):
	return

def main():
	# get cached values using cookie, if available
	loadCookie()

	# get input parameters from form submission
	parms = cgi.FieldStorage()
	updateFields(parms)

	# initial setup of output page
	myTitle = 'Mutant Alleles, Strains, and Phenotypes Submission Form'
	output = template.Template(config['TEMPLATE_PATH'])
	output.setTitle(myTitle)
	output.setHeaderBarMainText(myTitle)
	output.setJavaScript(getJavascript())

	# cache the user's address and refs info for near-future submissions
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
		sendConfirmation(output)

	return

###--- main program ---###

if __name__ == '__main__':
	main()
