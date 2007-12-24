#!./python

# Program: nominate_submit.cgi
# Purpose: to process data submitted on the "NIH Mouse Knockout Nominating"
#   within the MGI Home product.  Basically, we check to see that
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
	'symbol1':'Gene/allele symbol/name',
	'nickname1':'Gene/Allele synonyms',
	'mgiid1':'MGI accession ID',
	'genbankid1':'Genbank ID',
	'entrezgeneid1':'EntrezGene ID',
	'ensemblid1':'EnSEMBL Gene ID',
	'pubmedid1':'PubMed ID',
	'comments1':'Additional Comments',
	
	'symbol2':'Gene/allele symbol/name',
	'nickname2':'Gene/Allele synonyms',
	'mgiid2':'MGI accession ID',
	'genbankid2':'Genbank ID',
	'entrezgeneid2':'EntrezGene ID',
	'ensemblid2':'EnSEMBL Gene ID',
	'pubmedid2':'PubMed ID',
	'comments2':'Additional Comments',
	
	'symbol3':'Gene/allele symbol/name',
	'nickname3':'Gene/Allele synonyms',
	'mgiid3':'MGI accession ID',
	'genbankid3':'Genbank ID',
	'entrezgeneid3':'EntrezGene ID',
	'ensemblid3':'EnSEMBL Gene ID',
	'pubmedid3':'PubMed ID',
	'comments3':'Additional Comments',
	
	'symbol4':'Gene/allele symbol/name',
	'nickname4':'Gene/Allele synonyms',
	'mgiid4':'MGI accession ID',
	'genbankid4':'Genbank ID',
	'entrezgeneid4':'EntrezGene ID',
	'ensemblid4':'EnSEMBL Gene ID',
	'pubmedid4':'PubMed ID',
	'comments4':'Additional Comments',
	
	'symbol5':'Gene/allele symbol/name',
	'nickname5':'Gene/Allele synonyms',
	'mgiid5':'MGI accession ID',
	'genbankid5':'Genbank ID',
	'entrezgeneid5':'EntrezGene ID',
	'ensemblid5':'EnSEMBL Gene ID',
	'pubmedid5':'PubMed ID',
	'comments5':'Additional Comments',
	
	'symbol6':'Gene/allele symbol/name',
	'nickname6':'Gene/Allele synonyms',
	'mgiid6':'MGI accession ID',
	'genbankid6':'Genbank ID',
	'entrezgeneid6':'EntrezGene ID',
	'ensemblid6':'EnSEMBL Gene ID',
	'pubmedid6':'PubMed ID',
	'comments6':'Additional Comments',
	
	
	'otherKnockoutInfo':'Other information about this knockout',
	
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
        'fax'           : 'Fax Number'
	}

# order in which fields should be included in the e-mail.  This is a list of
# tuples, where each tuple is: (section name, [ fieldnames in order ])
field_order = [
	('Nomination1',
		[	'symbol1',
	'nickname1',
	'mgiid1',
	'genbankid1',
	'entrezgeneid1',
	'ensemblid1',
	'pubmedid1',
	'comments1']),
	
	('Nomination2',
       ['symbol2',
	'nickname2',
	'mgiid2',
	'genbankid2',
	'entrezgeneid2',
	'ensemblid2',
	'pubmedid2',
	'comments2']),
	
	('Nomination3',
       ['symbol3',
	'nickname3',
	'mgiid3',
	'genbankid3',
	'entrezgeneid3',
	'ensemblid3',
	'pubmedid3',
	'comments3']),
	
	('Nomination4',
       ['symbol4',
	'nickname4',
	'mgiid4',
	'genbankid4',
	'entrezgeneid4',
	'ensemblid4',
	'pubmedid4',
	'comments4']),
	
	('Nomination5',
       ['symbol5',
	'nickname5',
	'mgiid5',
	'genbankid5',
	'entrezgeneid5',
	'ensemblid5',
	'pubmedid5',
	'comments5']),
	
	('Nomination6',
       ['symbol6',
	'nickname6',
	'mgiid6',
	'genbankid6',
	'entrezgeneid6',
	'ensemblid6',
	'pubmedid6',
	'comments6']),
	
	('Other Info',
       ['otherKnockoutInfo',
	
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
	
	 'getmgiid']),
	
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
    reply_message.appendBody('<BLOCKQUOTE><PRE>\n%s\n</PRE></BLOCKQUOTE><HR>' % string.join(message, '\n'))
    
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
    fd2 = open(str(dirName)+"/nominMessage",'w')
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

