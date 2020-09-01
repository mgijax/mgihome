#!./python

#
# Processes Nomenclature Submission Form
#
# 1.  Sends email message to 'nomen@jax.org'
# 2.  Provides user w/ HTML reflection of email message
#


# Imports
# =======

import sys
if '.' not in sys.path:
        sys.path.insert(0, '.')

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)
import homelib

import sys
import os 
import mgi_utils
import mgi_html
import formMailer
import template

reply_message = template.Template(config['TEMPLATE_PATH'])

SP = ' '
HT = '\t'
NL = '\n'

def errorStop (message):
        print('Content-type: text/html\n')
        formMailer.handleError (message, 'MGI Nomen Form')
        sys.exit(0)

nomen_addr = 'nomen@jax.org'  # MGD Nomen Coordinator Email Account

# developer override for mailtarget 
if config.has_key('CGI_MAILTARGET'):
        nomen_addr = config['CGI_MAILTARGET']

subject = 'Nomenclature Request'

reply_message.setTitle('MGD: Nomenclature Request')
reply_message.setHeaderBarMainText('Thank You')

body = ' <BR>\
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

captcha_element = ''
if config.has_key('CAPTCHA_ELEMENT'):
        captcha_element = config['CAPTCHA_ELEMENT']
captcha_timeout = ''
if config.has_key('CAPTCHA_TIMEOUT'):
        captcha_timeout = config['CAPTCHA_TIMEOUT']
captche_hide = ''
if config.has_key('CAPTCHA_HIDE'):
        captcha_hide = config['CAPTCHA_HIDE']

if (captcha_element in fields):
        if int(fields[captcha_element]) < int(captcha_timeout):
                missing_fields.append("Required fields are missing")

if (captcha_hide in fields):
        if fields[captcha_hide] != '':
                missing_fields.append("Required fields are missing.")
        
if ('lastname' in fields):
        username = fields['lastname']
else:
        username = ''
        missing_fields.append('Last Name')
 
if ('firstname' in fields):
        username = username + ',' + SP + fields['firstname']
        message = message + 'Submitter Name:\t\t' + username + NL
else:
        missing_fields.append('First Name & Middle Name(s)')

if ('emailaddr' in fields):
        submitter_addr = fields['emailaddr']
else:
        missing_fields.append('E-mail address')

for key in field_sort:
        if (key in fields):
                if (key in field_trans):
                        message = message + field_trans[key] + fields[key] + NL
                else:
                        message = message + key + ' = ' + fields[key] + NL

#
# Format Symbol Information
#

locussect = NL

if 'symbol' in fields:
        locussect = locussect + 'Requested Symbol:' + HT + fields['symbol'] + NL
        subject = fields['symbol']

if 'name' in fields:
        locussect = locussect + 'Requested Name:' + 2*HT + fields['name'] + NL

if 'chromosome' in fields:
        locussect = locussect + 'Chromosome:' + 2*HT + fields['chromosome'] + NL

if 'pub_status' in fields:
        locussect = locussect + 'Publication Status:' + HT + fields['pub_status'] + NL

if 'symbol_status' in fields:
        locussect = locussect + 'Symbol Status:' + 2*HT + fields['symbol_status'] + NL

# We now handle symbols requested in up to three species.  (TR 1175)

species = []
for fieldname in [ 'requestMouse', 'requestHuman', 'requestRat' ]:
        if fieldname in fields:
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
                                        (HT, ', '.join (species), NL)

# We also now handle up to three sources.  (TR 1175)

sources = []
for fieldname in [ 'source1', 'source2', 'source3', 'source4' ]:
        if fieldname in fields:
                sources.append (fields[fieldname])
if sources:
        locussect = locussect + "Sources Checked:%s%s%s" % \
                                        (HT, ', '.join (sources), NL)

if 'locusName' in fields:
        locussect = locussect + '\nName/Phenotypic effect:' + NL + fields['locusName'] + NL

if 'otherName' in fields:
        locussect = locussect + '\nOther Name(s):' + NL + fields['otherName'] + NL

if 'family' in fields:
        locussect = locussect + '\nLocus Family:' + NL + fields['family'] + NL

if 'notes' in fields:
        locussect = locussect + '\nNotes:' + NL + fields['notes'] + NL

message = message + locussect + NL

###--- Format Sequence Information, per TR 2031 ---###

seqsect = ''

if 'genbankID' in fields:
        seqsect = seqsect + 'GenBank ID:' + 2*HT + fields['genbankID'] + NL

if 'sequence' in fields:
        seqsect = seqsect + NL + 'Sequence:' + NL + fields['sequence'] + NL

### As of TR 2754, we now do not require sequence information...
#if seqsect == '':
#       errorStop ('''You must include either a GenBank ID or Sequence Data.
#               Please go back and try again.''')

if seqsect:
        message = message + seqsect + NL

#
# Format Reference Information
#

refsect = 'Locus References:' + NL

if 'cite1' in fields:
        refsect = refsect + fields['cite1'] + NL
if 'cite2' in fields:
        refsect = refsect + fields['cite2'] + NL
if 'cite3' in fields:
        refsect = refsect + fields['cite3'] + NL

message = message + refsect + NL

#
# Format Homology Information
#

homsect = 'Homology Information:'

if 'hom_symbol_1' in fields:
        if 'hom_species_1' in fields and 'hom_citation_1' in fields:
                homsect = homsect + 2*NL + \
                          'Locus Symbol:' + HT + fields['hom_symbol_1'] + NL + \
                          'Species:' + HT + fields['hom_species_1'] + NL + \
                          'Citation:' + HT + fields['hom_citation_1']
                if 'hom_seq_id_1' in fields:
                        homsect = homsect + NL + 'Sequence ID:' + HT + fields['hom_seq_id_1']
        else:
                missing_fields.append('Species and Short Citation required for each Locus Symbol.')

if 'hom_symbol_2' in fields:
        if 'hom_species_2' in fields and 'hom_citation_2' in fields:
                homsect = homsect + 2*NL + \
                          'Locus Symbol:' + HT + fields['hom_symbol_2'] + NL + \
                          'Species:' + HT + fields['hom_species_2'] + NL + \
                          'Citation:' + HT + fields['hom_citation_2']
                if 'hom_seq_id_2' in fields:
                        homsect = homsect + NL + 'Sequence ID:' + HT + fields['hom_seq_id_2']                                     
        else:
                missing_fields.append('Species and Short Citation required for each Locus Symbol.')

if 'hom_symbol_3' in fields:
        if 'hom_species_3' in fields and 'hom_citation_3' in fields:
                homsect = homsect + 2*NL + \
                          'Locus Symbol:' + HT + fields['hom_symbol_3'] + NL + \
                          'Species:' + HT + fields['hom_species_3'] + NL + \
                          'Citation:' + HT + fields['hom_citation_3']
                if 'hom_seq_id_3' in fields:
                        homsect = homsect + NL + 'Sequence ID:' + HT + fields['hom_seq_id_3']                     
        else:
                missing_fields.append('Species and Short Citation required for each Locus Symbol.')

if missing_fields:
        errorStop ('''Mandatory field(s) missing...  Please enter
                field(s) and try again.<BR>Field(s): %s''' % \
                ', '.join (missing_fields))

message = message + homsect
body += '<BLOCKQUOTE><PRE>' + message + '</PRE></BLOCKQUOTE>'

reply_message.setBody(body)

print(reply_message.getFullDocument())

mailheader = 'From: ' + submitter_addr + NL + 'To: ' + nomen_addr + NL 
mailheader = mailheader + 'Subject: ' + subject + NL + NL
fd = os.popen('%s -t' % config['SENDMAIL'], 'w')
fd.write( mailheader + message )
fd.close()
