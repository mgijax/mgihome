#!./python

# Program: strain_submit.cgi
# Purpose: accept submission data from strain_form.shtml, do input validation,
#       send an e-mail to the strain curators and the submitter, and 
#       provide appropriate feedback to the user.

import sys                              # standard Python libraries
if '.' not in sys.path:
        sys.path.insert (0, '.')
import os
import string

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import homelib
import formMailer

###--- Global Variables ---###

# mapping from internal fieldnames (passed from the browser) 
# to labels for the user: passed to strainMailer constructor
labels = {
        'method'        : 'Strain Name New or Revised',
        'strain_name'   : 'Strain Name',
        'gene_symbols'  : 'Gene Symbols',
        'Prefix'        : 'Prefix',
        'instituteID'   : 'Strain Accession ID',
        'status'        : 'Strain Public or Private',
        'category'      : 'Categories',
        'synonyms'      : 'Synonyms',
        'references'    : 'References',
        'notes'         : 'Notes',
        'firstname'     : 'First Name',
        'lastname'      : 'Last Name',
        'email'         : 'E-Mail Address',
        }

# list of required internal fieldnames: passed to strainMailer constructor
required_fields = [ 'firstname','lastname', 'method', 'status','email' ]

# sections list containing display order for e-mails:
# each tuple contains (section heading string, list of internal fieldnames
#       to include in that section)
# passed to strainMailer constructor
sections = [
        ('Strain Info',
                [ 'method', 'Prefix','instituteID','strain_name', 
                  'gene_symbols', 'status', 'category' ]),
        ('Additional Info',
                [ 'synonyms', 'references', 'notes' ]),
        ('Contact Info',
                [ 'firstname', 'lastname', 'email' ]),
        ]

###--- Classes ---###

class strainMailer (formMailer.formMailer):
        # IS:   a formMailer that interacts with strain_form.shtml
        #       strain submission form
        # HAS:  see formMailer
        # DOES: see formMailer

        def doPostValidationProcessing(self):
                # Purpose: Convert any submitted multi-line field to a list
                #          of strings 
                # Returns: nothing
                # Assumes: nothing
                # Effects: alters self.parms
                # Throws:  nothing
                # Notes:   The four possible multi-line fields are defined in
                #          the 'fields' variable below.  Even if one of these
                #          fields contains only a single line, we will convert
                #          it to a list for consistency.

                fields = [ 'notes', 'references', 'synonyms', 'gene_symbols' ]
                for field in fields:
                        if self.parms.has_key (field):
                                self.parms[field] = string.split (
                                        self.parms[field], '\n')

                return

        def doValidations(self):
                # Purpose: Perform validation of submitted data
                # Returns: List of tuples; 
                #          Each tuple is (fieldname, error string).  
                #          An empty list means no errors were found.
                # Assumes: nothing
                # Effects: nothing
                # Throws:  nothing
                # Notes:   For now, we do two validations - check that the
                #          e-mail address contains an '@' sign, and check that
                #          the username in the e-mail address matches that of
                #          the person logged in using the htaccess mechanism.

                errors = []

		if self.parms["method"] == 'REVISED' and\
		   (not self.parms.has_key("synonyms") or len(self.parms["synonyms"]) == 0):
			errors.append( ('synonyms', "If this is a revised strain name, you must list the old strain name in the synonyms section."))

                # ensure e-mail address contains a '@'                
                if self.parms.has_key ('email'):
                        atPos = string.find (self.parms['email'], '@')
                        if atPos == -1:
                                errors.append ( ('email',
                                        'Invalid e-mail address') )
                return errors

###--- Main Program ---###

# set up the 'To' address for the submission, and allow it to be over-ridden
# in the configuration file for testing.
curator_addr = 'strains@informatics.jax.org'

if config.has_key('CGI_MAILTARGET'):
        curator_addr = config['CGI_MAILTARGET']
 

# construct the strainMailer object, and let it run...
strainMailerCGI = strainMailer ('Strain',
        curator_addr,
        labels,
        required_fields,
        sections
        )

# the go() method is inherited from the CGI class, in the CGI.py module
# it simply wraps the formMailer.main() in error handling
strainMailerCGI.go()

