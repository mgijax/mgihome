#!./python

# Program: nomination_submit.cgi
# Purpose: to process data submitted on the "KOMP Gene Nomination" form,
#	intended to help prioritize genes to be knocked out by the KOMP
#	project.  We check to see that all mandatory fields are present; if
#	not, we give an error message.  If they are, we build all the fields
#	and values into a message that is echoed back to the user and is saved
#	to a directory in the file system.  The user is also allowed to upload
#	a file, which we save to the same directory.  (Each submission gets
#	its own directory.)

import sys
if '.' not in sys.path:
	sys.path.insert (0, '.')
import types
import os
import cgi
import tempfile
import config
import homelib
import header
import formMailer

###------------------------###
###--- Global Variables ---###
###------------------------###

# list of fieldnames required to have values submitted by the user
required_fields = [ 'lastname', 'firstname', 'email',
		'pi', 'institute',
		'address1', 'city', 'state', 'zip',
		'country', 'phone', 'fax', 'funding',
		]

# maps from actual fieldnames to the corresponding label:
labels = {
	# contact info

        'lastname'      : 'Last name',
        'firstname'     : 'First name & middle initial(s)',
        'email'         : 'E-mail address',
	'pi'		: 'Laboratory PI',
        'institute'     : 'Institute/Organization',
        'address1'      : 'Address',
        'address2'      : 'Address',
        'city'          : 'City',
        'state'         : 'State/Province',
        'zip'		: 'Postal Code',
        'country'       : 'Country',
        'phone'         : 'Telephone Number',
        'fax'           : 'Fax Number',

	# miscellaneous

	'fileUpload'	: 'File Upload',
	'funding'	: 'Funding source(s)',
	'otherFunding'	: 'Other funding source(s)',
	}

# order in which fields should be included in the e-mail.  This is a list of
# tuples, where each tuple is: (section name, [ fieldnames in order ])
field_order = [
	('Contact Information', [
	        'lastname', 'firstname', 'email',
        	'pi', 'institute',
		'address1', 'address2', 'city', 'state', 'zip',
		'country', 'phone', 'fax',
		]),

	('Funding', [ 'funding', 'otherFunding' ]),

	('File Upload', [ 'fileUpload' ]),
	]

###-----------------###
###--- Functions ---###
###-----------------###

def bailout (message):
    # Purpose: send an HTML page with the given error 'message' to the user,
    #	then exit this script.
    # Returns: nothing
    # Assumes: nothing
    # Effects: writes to stdout
    # Throws: SystemExit to exit the script after writing the error message

    formMailer.handleError (message, 'KOMP Gene Nomination Form',
        header.bodyStart(), header.bodyStop())
    sys.exit(0)

###------------------------------------------------------------------------###

def setup():
    # Purpose: get needed values from the config file, and get the user's
    #	input parameters.
    # Returns: (string KOMP submission directory, FieldStorage object)
    # Assumes: nothing
    # Modifies: nothing
    # Throws: SystemExit if an error is found and we have sent an error
    #	message to the user.

    KOMP_DIR = config.lookup ('KOMP_NOMINATION_DIR')
    if KOMP_DIR is None:
	bailout ('Configuration error in mgihome:' + \
		'KOMP_NOMINATION_DIR is undefined')

    # get the user's input parameters
    parms = cgi.FieldStorage()

    return KOMP_DIR, parms

###------------------------------------------------------------------------###

def checkRequiredFields(parms):
    # Purpose: check that all required fields were submitted in 'parms'; if
    #	not, give an error message.
    # Returns: nothing
    # Assumes: nothing
    # Modifies: nothing
    # Throws: SystemExit if an error is found and we have sent an error
    #	message to the user.

    missing_fields = []
    for key in required_fields:
	if not parms.has_key(key) or \
		(type(parms[key]) == types.StringType and \
		parms[key].value == ''):
            missing_fields.append (labels[key])

    if missing_fields:
	err_message = '''The following required fields are missing.
		Please go back and try again.<P><UL><LI>%s</LI></UL>'''
	bailout (err_message % '</LI><LI>'.join(missing_fields))
    return

###------------------------------------------------------------------------###

def compileOutputTop(parms):
    # Purpose: compile the top of the output page, based on the user input in
    #	'parms'.  This should include everything except the nominations.
    # Returns: (list of output strings, string -- uploaded filename,
    #	string -- uploaded file contents)
    # Assumes: nothing
    # Modifies: nothing
    # Throws: nothing

    message = []		# list of strings, each a line to output
    ulFileName = None		# name of uploaded file
    ulFileContents = None	# contents of uploaded file

    # walk through section-by-section
    for (heading, fieldlist) in field_order:

	# section heading line
        section = [
                '-' * len(heading),
                heading,
                '-' * len(heading),
                ]

	# special handling for an uploaded file (grab the name and contents)

        if heading == "File Upload" :
            for field in fieldlist :
                if parms.has_key(field) and parms[field].value != '':
                    ulFileName = parms[field].filename
		    section.append('File Uploaded\n\t%s' % ulFileName)
                    ulFileContents = parms[field].value
        else:
	    # for other fields, just echo them

            for field in fieldlist:
                if parms.has_key(field):
                    section.append (labels[field])
                    if type(parms[field]) == types.ListType:
                        for item in parms[field]:
                            section.append ('\t%s' % item.value)
                    else:
                            section.append ('\t%s' % parms[field].value)

	# if we added anything to the 'section' other than the header lines,
	# then add it to the message

        if len(section) > 3:
                message = message + section

    return message, ulFileName, ulFileContents

###------------------------------------------------------------------------###

def compileOutputBottom (parms):
    # Purpose: Compile a tab-delimited section for the nominated genes, with
    #	one line per nomination.  If no nominations were included, then bail
    #	out with an error message.
    # Returns: list of strings, each one tab-delimited line
    # Assumes: The user will submit 1-10 nominations.
    # Modifies: nothing
    # Throws: SystemExit if we have given an error message to the user and
    #	need to exit the script

    # templates for fieldnames for each nomination.  Fill in %d with 1-10, as
    # the form allows up to ten nominations per submission.

    fields = [ 'approach%d', 'symbol%d', 'synonym%d',
		    'mgi%d', 'genbank%d', 'entrez%d', 'ensembl%d', ]

    section = []	# list of tab-delimited strings, one per nomination
    errors = []		# list of strings, each one an error message

    for i in range(1,11):	# walk through nominations 1-10

	line = []		# list of strings, one per item in 'fields'

	symbol = None	# gene or allele symbol for this nomination
	ids = []	# list of all IDs for this nomination
	synonym = None	# synonym for this nomination
	isEmpty = True	# is this an empty nomination?

	for field in fields:
	    fieldname = field % i

	    # if this field was submitted and is non-empty, then append its
	    # value to 'line'.  Otherwise, append an empty string for its
	    # corresponding column.

	    if parms.has_key(fieldname) and parms[fieldname].value != '':
		line.append (parms[fieldname].value)

		# update our caches of data about this nomination

		if fieldname[:8] != 'approach':
			# Since 'approach' is a radio button, it will always
			# have a value.  If this is any other field, then this
			# nomination is non-empty.

			isEmpty = False

		if fieldname[:6] == 'symbol':
		    symbol = parms[fieldname].value
	        elif fieldname[:7] == 'synonym':
		    synonym = parms[fieldname].value
		elif fieldname[0] in ('m', 'g', 'e'):
		    ids.append (parms[fieldname].value)
	    else:
		line.append ('')

	# If all nomination fields are empty, then just ignore this
	# nomination.  Otherwise, we need to do some error checking.

	if not isEmpty:
	    # A valid nomination must have both a symbol and at least one
	    # ID.  If either or both are not present, then we have an
	    # error to report.

	    if symbol != None:
		if not ids:
		    # We have a symbol, but no IDs.

		    errors.append (
			    'No ID was found for line %d, with symbol/name %s' % \
			    	(i, symbol))
		else:
		    # We have a symbol and we have IDs, so this is a valid
		    # nomination.

		    section.append ('\t'.join(line))

	    elif ids:
		# We have IDs, but no symbol.

		errors.append (
			'No symbol was found for line %d, with IDs %s' % \
				(i, ', '.join(ids)))

	    elif synonym:
		# We have neither IDs nor symbol, but we do have a synonym
		# on this line.

		errors.append ('Neither a symbol nor IDs were found ' + \
			'for line %d, synonym %s.' % (i, synonym))

    # If we have error messages, then give them.

    if errors:
	bailout ('The following nomination errors were encountered.  ' + \
	    'Please go back and try again.<P><UL><LI>%s</LI></UL>' % \
	    '</LI><LI>'.join (errors))

    # If there were no errors, but we had no nominations attempted, give an
    # error message.

    elif not section:
	bailout ('No nominations were submitted.  Please go back and ' + \
	    'enter information for genes you would like to nominate.')

    else:
	message = [
	    '---------------------------',
	    'Nominations (tab delimited)',
	    '---------------------------',
	    'Approach\tSymbol/Name\tSynonyms\tMGI\tGenBank\t' + \
		'EntrezGene\tEnsembl'
	    ] + section

    return message 

###------------------------------------------------------------------------###

def saveNomination (message, ulFileName, ulFileContents, KOMP_DIR):
    # Purpose: save the nomination submitted by the user, including form
    #	fields and an optional uploaded file
    # Returns: nothing
    # Assumes: nothing
    # Modifies: creates a file system directory and adds 1-2 files to it
    # Throws: SystemExit if we have given the user an error message and need
    #	to exit the script

    # add the user's IP address, if available, and build the copy of the
    # message that we are to save

    messageCopy = message[:]

    if os.environ.has_key('REMOTE_ADDR'):
	messageCopy.insert(0, 'IP address: %s\n' % os.environ['REMOTE_ADDR'])
    fileText = '\n'.join(messageCopy)

    # create a new directory to hold this submission

    try:
        tempfile.tempdir = KOMP_DIR
        dirName = tempfile.mktemp()
        os.mkdir(dirName)
    except:
	bailout ('System error: failed to create directory.  Please try ' + \
		'again later.')

    # if there was an uploaded file, save it to the directory

    if ulFileName != None :
	try:
	    fd = open(os.path.join(dirName, ulFileName),'w')
            fd.write(ulFileContents)
            fd.flush()
            fd.close()
	except:
	    bailout ('System error: failed to save uploaded file.  Please ' +\
		'try again later.')

    # save the user's form fields

    try:
	fd2 = open(os.path.join(dirName, 'kompNomination'),'w')
	fd2.write(fileText)
	fd2.flush()
	fd2.close()
    except:
	bailout ('System error: failed to save submission file.  Please ' + \
		'try again later.')
    return

###------------------------------------------------------------------------###

def sendUserConfirmation (message):
    # Purpose: send an HTML confirmation page to the user's browser
    # Returns: nothing
    # Assumes: nothing
    # Modifies: writes to stdout
    # Throws: nothing

    # build the copy of the message to echo to the user

    messageText = '\n'.join(message)

    print '<HTML><HEAD><TITLE>KOMP Gene Nomination Form</TITLE></HEAD>'
    print '<BODY bgcolor=ffffff>'
    print header.bodyStart()
    print header.headerBar('KOMP Gene Nomination Sent!')
    print 'The following information was successfully submitted:'
    print '<PRE>\n%s\n</PRE>' % messageText
    print '<HR>'
    print header.bodyStop()

    return

###------------------------------------------------------------------------###

def main():
    # Purpose: main logic of the script
    # Returns: nothing
    # Assumes: nothing
    # Modifies: writes to stdout, saves files to file system
    # Throws: SystemExit if an error is found and we have sent an error
    #	message to the user.

    KOMP_DIR, parms = setup()
    checkRequiredFields (parms)

    message, ulFileName, ulFileContents = compileOutputTop(parms)
    message = message + compileOutputBottom(parms)

    saveNomination (message, ulFileName, ulFileContents, KOMP_DIR)
    sendUserConfirmation (message)

    return

###------------------------------------------------------------------------###

################
# MAIN PROGRAM #
################
print "Content-type: text/html"
print
try:
    main()
except SystemExit: 
    pass
