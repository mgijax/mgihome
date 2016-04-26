#!./python

# Program: allele_submit.cgi
# Purpose: to process data submitted on the "New Allele and Mutant Submission
#       Form" within the MGI Home product.  Basically, we check to see that
#       some mandatory fields are present.  If not, we give an error message.
#       If they are, we build all the fields and values into an e-mail message
#       to send to a mail alias specified below.

import sys
if '.' not in sys.path:
        sys.path.insert (0, '.')
import string
import types
import os

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import homelib
import CGI
import formMailer
import db
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)
import re

###--- Global Variables ---###

# mapping from internal fieldnames (passed from the browser) 
# to labels for the user: Passed to allmutMailer constructor
labels = {
        'lastname'      : 'Last name',                  # Contact Details
        'firstname'     : 'First name & middle initial(s)',
        'email'         : 'E-mail address',
        'organization'  : 'Institute/Organization',
        'address1'      : 'Address',
        'address2'      : 'Address',
        'city'          : 'City',
        'state'         : 'State/Province',
        'zip'           : 'Postal Code',
        'country'       : 'Country',
        'phone'         : 'Telephone Number',
        'fax'           : 'Fax Number',

        'published'     : 'Currently Published',        # References
        'publicize'     : 'Make Public',
        'citations'     : 'Citations',                  
        'alleleURL'     : 'Allele URL',


        'description'   : 'Description',                # Phenotype
        'remarks'       : 'Other Remarks',

        'genesymbol'    : 'Gene Symbol',                # Nomenclature
        'allele'        : 'Allele Symbol',
        'accid'    	: 'MGI Accession ID',
        'synonyms'      : 'Other Names/Synonyms',
        'nomenHelp'     : 'Nomenclature Help Requested',
        'alleleremarks' : 'Additional Allele Information',

                                                        # Strain
        'strainMutation': 'Strain Background (where mutation arose)',
        'strainPhenotype': 'Strain Background (where phenotype analyzed)',
        'strainInfo'    : 'Other Strain Information',
        'strainHelp'    : 'Genetic Background Help Requested',

                                                        # Mutation
        'method'        : 'Method of Allele Generation',
        'othermethod'   : '"Other" Specification',
        'promoter'      : 'Transgene Promoter',
        'celline'       : 'ES Cell Line',
        'mode'          : 'Mode of Inheritance',
        'othermode'     : '"Other" Mode of Inheritance',


        'chromosome'    : 'Chromosome Location',        # Mapping data
        'location'      : 'Other Genome Location Information',
        }

# list of required internal fieldnames: Passed to allmutMailer constructor
required_fields = [ 'lastname', 'firstname', 'email', 'allele', 'accid']

# sections list containing display order for e-mails:
# each tuple contains (section heading string, list of internal fieldnames
#       to include in that section)
# Passed to allmutMailer constructor
sections = [
        ('Nomenclature',
                ['genesymbol','allele','accid','synonyms','nomenHelp', 'alleleremarks']),
        ('About this Mutation',
                ['method', 'othermethod', 'promoter', 'celline',
                'mode', 'othermode','chromosome','location']),
        ('Genetic Background',
                ['strainMutation', 'strainPhenotype', 'strainInfo', 
                'strainHelp',]),
        ('Phenotype',
                ['description', 'remarks']),
        ('References',
                [ 'published', 'publicize', 'citations', 'alleleURL' ]),
        ('Contact Details',
                [ 'firstname', 'lastname', 'email', 'organization',
                        'address1', 'address2', 'city', 'state', 'zip',
                        'country', 'phone', 'fax' ]),
        ]

###--- Classes ---###

class allmutMailer (formMailer.formMailer):
        # IS:   a formMailer that deals specifically with the mutant allele
        #         submission form
        # HAS:  see formMailer
        # DOES: see formMailer

        def doPostValidationProcessing(self):
                # Purpose: convert any submitted multi-line field to be a list
                #       of strings (with each string being a single line)
                # Returns: nothing
                # Assumes: nothing
                # Effects: alters self.parms
                # Throws:  nothing
                # Notes:   The five possible multi-line fields are defined in
                #          the 'fields' variable below.  Even if one of these
                #          fields contains only a single line, we will convert
                #          it to a list for consistency.

                fields = ['location','strainInfo','description',
                        'citations', 'remarks', 'alleleremarks']
                for field in fields:
                        if self.parms.has_key (field):
                                self.parms[field] = string.split (
                                        self.parms[field], '\n')
                return

        def doValidations(self):
                # Purpose: perform validation of submitted data
                # Returns: list of tuples; each tuple is (fieldname, error
                #       string).  An empty list means no errors were found.
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: Check that the e-mail address contains an '@'

                errors = []

                # check that the e-mail address contains a '@'
                if self.parms.has_key ('email'):
                        atPos = string.find (self.parms['email'], '@')
                        if atPos == -1:
                                errors.append ( ('email',
                                        'Invalid e-mail address') )
                if self.parms.has_key('accid'):
                	if self.checkMGIAccID(self.parms['accid']) == 0:
                		errors.append(('accid', 'Invalid MGI Accession ID'))
                return errors

 	def checkMGIAccID (self, id):
	    	# Purpose: return true if we have a valid accession ID.
	    	# Returns: true or false
	    	# Assumes: nothing
	    	# Effects: nothing
	    	# Throws: db module may throw DB exceptions
	    	# Check to see whether the given ID string is a valid
	    	# MGI acc id.
	
	    	mgiID = re.compile(r'^MGI')
	
	    	if  mgiID.match(id):
	
	        	# We have a valid MGI Acc ID string
	
	        	db.useOneConnection(1)
	        	db.set_sqlUser(config["DB_USER"])
	        	db.set_sqlPassword(config["DB_PASSWORD"])
	        	db.set_sqlServer(config["DB_SERVER"])
	        	db.set_sqlDatabase(config["DB_DATABASE"])
	        	cmds = [] # SQL command list
	        	cmds.append(string.join([
	        	'SELECT accID from ACC_Accession where lower(accID) = lower(\'%s\')' % id
	        	]))
	
	        	#  Excecute queries
	        	results = db.sql(cmds, 'auto')
	
	        	db.useOneConnection(0)
	        	if results != [[]]:
	        	        return 1
	        	else:
	        	        return 0
	    	else:
	        	return 0
	        	# We didn't have a valid MGI Acc ID string



###--- Main Program ---###

# set up the 'To' address for the submission, and allow it to be over-ridden
# in the configuration file for testing.

curator_addr = 'phenotypes@informatics.jax.org'

if config.has_key('CGI_MAILTARGET'):
        curator_addr = config['CGI_MAILTARGET']


# construct the allmutMailer object, and let it run...
allmutMailerCGI = allmutMailer ('Phenotype Data',
        curator_addr,
        labels,
        required_fields,
        sections
        )

allmutMailerCGI.setFooter('\n\nThank you for your contribution. '\
                          'If you have questions regarding your '\
                          'submission, please contact: %s  \n')

# the go() method is inherited from the CGI class, in the CGI.py module
# it simply wraps the formMailer.main() in error handling
allmutMailerCGI.go()

