#!./python

# Program: repat_submit.cgi
# Purpose: to process data submitted on the "NIH Mouse Knockout Mice for
#   Repatriation" within the MGI Home product.  Basically, we check to see that
#	some mandatory fields are present.  If not, we give an error message.
#	If they are, we build all the fields and values into an e-mail message
#	to send to a mail alias specified below.

import sys
if '.' not in sys.path:
	sys.path.insert (0, '.')
import string
import types
import os
import posix
import cgi
import tempfile

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import table		# for unescape() function only
import homelib
import formMailer
import template


SURVEY_ROOT_DIRECTORY = '/home/dow/tmp/survey/'
if config.has_key('SURVEY_ROOT_DIRECTORY'):
	SURVEY_ROOT_DIRECTORY = config['SURVEY_ROOT_DIRECTORY']

# maps from actual fieldname to its label, for error reporting
required_fields = ['lastname','firstname','email']

# maps from actual fieldnames to the corresponding label:
labels = {
	'allele':'Gene/allele symbol/name',
	'synonyms':'Allele synonyms',
	'mgiid':'MGI accession ID',
	'dbgss':'dbGSS ID',
	'prevsub':'Previously submitted',
	'toreposit':'contribute to public repository',
	
	'celline':'ES cell line',
	'method':'method of generation',
	'otherGeneration':'Other method of generation',
	'include':'This knockout includes',
	'other reporter':'Reporter',
	'other selectable method':'Selectable marker/promoter',
	'other sitespec recomb':'Site specific recombination site',
	
	'remarks':'Text description',
	'fileUpload' : 'File uploaded',
	'junction' : 'Assays used',
	'other frag' : 'Other assays',
	
	'evidence' : 'Mutation is shown to be a true null by',	
	'other method':'Other expression/transcript assay',
	'other prot':'Other protein type',
	'other assay':'Other assay type',
	
	'published':'Is this knockout published',
	'pubmed id':'PubMed ID',
	'publicize':'The data should be',
	'citations':'Citations',
	'alleleURL':'URL for further data',
	
	'repository':'Is the strain or ES cell line carrying this allele in a repository',
	'name repository':'Holding repository',
	'contribute':'Are you willing to contribute this knockout to a public repository',
	'whynot':'Why not',
	
	'pheno':'Phenotype description',
	'origin':'Strain of origin',
	'phenobackgrd':'background on which mice phenotyped',
	'inbred':'Is the strain now inbred',
	'generations':'number of inbreeding generations',
	
	'otherKnockoutInfo':'Other information about this knockout',
	'comments':'Comments to NIH',
	
        'lastname'      : 'Last name',                  # Contact Details
        'firstname'     : 'First name & middle initial(s)',
        'email'         : 'E-mail address',
        'organization'  : 'Institute/Organization',
        'address1'      : 'Address',
        'address2'      : 'Address',
        'city'          : 'City',
        'state'         : 'State/Province',
        'postalcode'           : 'Postal Code',
        'country'       : 'Country',
        'telephone'         : 'Telephone Number',
        'fax'           : 'Fax Number',
	
	'getmgiid' : 'Accession ID requested',
    'contact' : 'Contact about extensive contribution requested'
	}

# order in which fields should be included in the e-mail.  This is a list of
# tuples, where each tuple is: (section name, [ fieldnames in order ])
field_order = [
	('Answers',
		[	'allele',
	'synonyms',
	'mgiid',
	'dbgss',
	'prevsub',
	'toreposit',
	
	'celline',
	'method',
	'otherGeneration',
	'include',
	'other reporter',
	'other selectable method',
	'other sitespec recomb',
	
	'remarks',
	'junction',
	'other frag',
	
	'evidence',	
	'other method',
	'other prot',
	'other assay',
	
	'published',
	'pubmed id',
	'publicize',
	'citations',
	'alleleURL',
	
	'repository',
	'name repository',
	'contribute',
	'whynot',
	
	'pheno',
	'origin',
	'phenobackgrd',
	'inbred',
	'generations',

	'otherKnockoutInfo',
	'comments',
	
        'lastname',
        'firstname',
        'email',
        'organization',
        'address1',
        'address2',
        'city',
        'state',
        'postalcode',
        'country',
        'telephone',
        'fax',
	
	 'getmgiid',
     'contact']),
	
	 ('File Upload',
	 	['fileUpload'])
	]
# error message string for missing required fields
err_message = '''These required fields are missing: %s<BR>
	Please go back and try again.<P>'''

def main():
    ulFileName = None
    ulFileContents = None
    parms = cgi.FieldStorage()
    missing_fields = []
    for key in required_fields:
        if not parms.has_key (key) or parms[key].value == '':
            missing_fields.append (labels[key])
    if missing_fields:
        print 'Content-type: text/html\n\n'
        formMailer.handleError (
                    err_message % \
                            string.join (missing_fields, ', '),
                    'Survey Form')
        sys.exit (0)
    sys.stderr.write("Survey root dir :" + SURVEY_ROOT_DIRECTORY + "\n")
    message = []
    for (heading, fieldlist) in field_order:
        section = [
                '-' * len(heading),
                heading,
                '-' * len(heading),
                ]
        if heading == "File Upload" :
            for field in fieldlist :
                if parms.has_key(field) and parms[field].value != '':
                    ulFileName =  parms[field].filename
                    section.append('File Uploaded')
                    ulFileContents = parms[field].value
        else:
            for field in fieldlist:
                if parms.has_key(field):
                    section.append (labels[field])
                    if type(parms[field]) == types.ListType:
                        for item in parms[field]:
                            section.append ('\t%s' % item.value)
                    else:
                            section.append ('\t%s' % parms[field].value)
        if len(section) > 3:
                message = message + section
    
    reply_message = template.Template(config['TEMPLATE_PATH'])
    reply_message.setTitle('Survey Results Sent!')
    reply_message.setHeaderBarMainText('Survey Results Sent!')
    reply_message.setBody('The following information was successfully submitted:')
    reply_message.appendBody('<BLOCKQUOTE><PRE>\n%s\n</PRE></BLOCKQUOTE>' % string.join (message, '\n'))
    
    print reply_message.getFullDocument()
    
    tempfile.tempdir = SURVEY_ROOT_DIRECTORY
    dirName = tempfile.mktemp()
    os.mkdir(dirName)
    if ulFileName != None :
        fd = open(str(dirName)+"/"+ulFileName,'w')
        fd.write(ulFileContents)
        fd.flush()
        fd.close()
    ip = []
    ip.append('IP addr\n'+os.environ['REMOTE_ADDR'])
    message = message + ip
    fd2 = open(str(dirName)+"/repatMessage",'w')
    messageText = string.join(message,'\n')
    fd2.write(messageText)
    fd2.flush()
    fd2.close()

################
# MAIN PROGRAM #
################

try:
    main()
except SystemExit: 
    pass

