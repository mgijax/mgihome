#!/usr/local/bin/python

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

import config
import homelib
import header
import CGI
import errorlib
import formMailer

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
        'allelename'    : 'Allele Name',
        'synonyms'      : 'Other Names/Synonyms',
        'nomenHelp'     : 'Nomenclature Help Requested',

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
required_fields = [ 'lastname', 'firstname', 'email' ]

# sections list containing display order for e-mails:
# each tuple contains (section heading string, list of internal fieldnames
#       to include in that section)
# Passed to allmutMailer constructor
sections = [
        ('Nomenclature',
                ['genesymbol','allele','allelename','synonyms','nomenHelp']),
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
                        'remarks','citations']
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
                return errors

###--- Main Program ---###

# set up the 'To' address for the submission, and allow it to be over-ridden
# in the configuration file for testing.

curator_addr = 'mutants@informatics.jax.org'

dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
        curator_addr = dev_email

# construct the allmutMailer object, and let it run...
allmutMailerCGI = allmutMailer ('Allele and Mutant',
        curator_addr,
        header.bodyStart(),
        header.bodyStop(),
        labels,
        required_fields,
        sections
        )

# the go() method is inherited from the CGI class, in the CGI.py module
# it simply wraps the formMailer.main() in error handling
allmutMailerCGI.go()

