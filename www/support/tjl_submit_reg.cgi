#!./python

# TJLHD_registration

"""CGI script to process User registration form.
Web site users enter demographic information into this form. The
information is sent to the TJL HelpDesk support database within the
Remedy system.
version 1.0 9/98      
revision 1.1 11/98"""

import sys
if '.' not in sys.path:
	sys.path.insert(0, '.')
import config
import homelib

import wi_config 
import cgi
import os
import string
import mgi_utils 
import wi_utils
import errorlib

NL = '\n'
SP = ' '
HT = '\t'
REQUIRED_FIELDS = [ 'lastname',
        'firstname',
	'tute',
        'ph',
        ]

#RECIPIENT = 'mgi-help@informatics.jax.org'
#RECIPIENT = 'mem@jax.org'
RECIPIENT = 'arsystem@jax.org'


# developer override for mailtarget 
dev_email = config.lookup ('CGI_MAILTARGET')
if dev_email is not None:
	RECIPIENT = dev_email

def hd():
        print """<HTML>
        <HEAD>
        <TITLE>TJL HelpDesk User Registration</TITLE>
        </HEAD>
        <BODY BGCOLOR=#FFFFFF>"""

        for line in homelib.banner():
		print line

        print """
        <H1>
        TJL HelpDesk User Registration Report
        </H1>
        <HR>
        """

def main():
        hd()

        form = cgi.FieldStorage()
        form_ok = 1
        for field in REQUIRED_FIELDS:
                if not form.has_key( field ):
                        form_ok = 0
                        break

        if not form_ok:
                print "<H1>Sorry...</H1>"
                print '<H4>Please fill in required fields before submission.<BR>'
                print 'The required fields are:</H4><P><B>First Name</B><BR><B>Last Name</B><BR><B>Institution</B><BR><B>E-mail address</B><BR><B>Phone</B>.'

        else:
                firstname = form['firstname'].value
                lastname = form['lastname'].value
		if form.has_key('mi'):
                	mi = form['mi'].value
		else:
			mi = ""
                title = form['prof-title'].value
		if form.has_key('position'):
                	positn = form['position'].value
		else:
			positn = ""
		if form.has_key('otherpos'):
                	positn = form['otherpos'].value
		else:
			otherpos = ""
                inst = form['tute'].value
		type = form['intype'].value

		if form.has_key('Dept'):
                	dept = form['Dept'].value
		else:
			dept = ""

		if form.has_key('st'):
                	st = form['st'].value
		else:
			st = ""

		if form.has_key('st2'):
                	st2 = form['st2'].value
		else:
			st2 = ""
		if form.has_key('cty'):
                	cty = form['cty'].value
		else:
			cty = ""

		if form.has_key('state'):
                	state = form['state'].value
		else:
			state = ""

		if form.has_key('zip'):
                	zip = form['zip'].value
		else:
			zip = ""

		if form.has_key('ctry'):
                	ctry = form['ctry'].value
		else:
			ctry = ""

		if form.has_key('emailaddr'):
                	emailaddr = form['emailaddr'].value
		else:
			emailaddr = ""
                ph = form['ph'].value

		if form.has_key('fx'):
                	fax = form['fx'].value
		else:
			fax = ""
		if form.has_key('mice'):
                	mice = form['mice'].value
		else:
			mice = "n/a"

		if form.has_key('damncmptrs'):
                	cmptrs = form['damncmptrs'].value
		else:
			cmptrs = ""

		if form.has_key('opsys'):
                	opsys = form['opsys'].value
		else:
			opsys = ""
                net = form['net'].value

		if form.has_key('browser'):
                	browser = form['browser'].value
		else:
			browser = "Netscape"
		msg = \
                        '#' + NL \
                        + '#' + 2*SP + mgi_utils.date() + NL \
                        + '#' + NL \
                        + '#AR-Message-Begin' + 13*SP \
                                + 'Do Not Delete This Line' + NL \
                        + 'Schema: TJL-ClientProfile' + NL \
                        + 'Server: arserver.jax.org' + NL \
                        + 'Login: webmail' + NL \
                        + 'Password: webuser1' + NL \
                        + 'Action: Submit' + NL \
                        + '# Values: Submit, Query' + NL \
                        + 'Format: Short' + NL \
                        + '# Values: Short, Full' + NL \
                        + NL \
                        + string.rjust( 'Client Type', 20 ) + ' !536870935!:' \
                                + 'MGI' + NL \
                        + string.rjust( 'L_name', 20 ) + ' !536870914!:' \
                                + lastname + NL \
                        + string.rjust( 'First Name', 20 ) + ' !536870913!:' \
                                + firstname + NL \
                        + string.rjust( 'MI', 20 ) + ' !536870915!:' \
                                + mi + NL \
                        + string.rjust( 'title', 20 ) + ' !536870927!:' \
                                + title + NL \
                        + string.rjust( 'Position', 20 ) + ' !536870936!:' \
                                + positn + NL \
                        + string.rjust( 'Inst', 20 ) + ' !536870916!:' \
                                + inst + NL \
                        + string.rjust( 'inst_type', 20 ) + ' !536870932!:' \
                                + type + NL \
                        + string.rjust( 'Dept', 20 ) + ' !536870917!:' \
                                + dept + NL \
                        + string.rjust( 'St', 20 ) + ' !536870918!:' \
                                + st + NL \
                        + string.rjust( 'St2', 20 ) + ' !536870928!:' \
                                + st2 + NL \
                        + string.rjust( 'cty', 20 ) + ' !536870919!:' \
                                + cty + NL \
                        + string.rjust( 'state', 20 ) + ' !536870920!:' \
                                + state + NL \
                        + string.rjust( 'zip', 20 ) + ' !536870922!:' \
                                + zip + NL \
                        + string.rjust( 'ctry', 20 ) + ' !536870921!:' \
                                + ctry + NL \
                        + string.rjust( 'em', 20 ) + ' !536870923!:' \
                                + emailaddr + NL \
                        + string.rjust( 'ph', 20 ) + ' !536870924!:' \
                                + ph + NL \
                        + string.rjust( 'fx', 20 ) + ' !536870925!:' \
                                + fax + NL \
                        + string.rjust( 'comments', 20 ) + ' !536870938!:' \
                                + "mice buyer: " + mice + NL \
                        + string.rjust( 'Computers', 20 ) + ' !536870930!:' \
                                + cmptrs + NL \
                        + string.rjust( 'opsys', 20 ) + ' !536870940!:' \
                                + opsys + NL \
                        + string.rjust( 'browsers', 20 ) + ' !536870931!:' \
                                + browser + NL \
                        + string.rjust( 'internet_acc', 20 ) + ' !536870934!:' \
                                + net + NL \
			+ string.rjust( 'Submitter', 21 ) \
                                + '!        2!: webmail' + NL \
                        + string.rjust( 'Status', 21 ) + \
                                '!        7!: ' + NL \
                        + NL \
                        + '#AR-Message-End' + 13*SP \
                                + 'Do Not Delete This Line' + NL
		print """
<H1>Thank you.</H1>
Your registration has been forwarded to the appropriate TJL Support staff.
"""

                mail_header = 'Reply-to: mem@informatics.jax.org' + NL \
                        + 'Subject: Express Mail' + NL
		fd = os.popen('%s -t %s' % (config.lookup ('SENDMAIL'), \
			RECIPIENT), 'w')
                fd.write( mail_header + msg + NL + '.' + NL )
                fd.close()

        print '<HR>'
        for line in homelib.footer():
		print line
	print '</BODY></HTML>'
	return

print 'Content-type: text/html'
print
try:
        main()
except:
        errorlib.handle_error()


#
# WARRANTY DISCLAIMER AND COPYRIGHT NOTICE 
#
#    THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE 
#    SUITABILITY OR ACCURACY OF THIS SOFTWARE OR DATA FOR ANY 
#    PURPOSE, AND MAKES NO WARRANTIES, EITHER EXPRESS OR IMPLIED, 
#    INCLUDING THE WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#    A PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA 
#    WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, 
#    TRADEMARKS OF OTHER RIGHTS. IT IS PROVIDED "AS IS." 
#
#    This software and data are provided as a service to the scientific 
#    community to be used only for research and educational purposes. Any
#    commercial reproduction is prohibited without the prior written 
#    permission of The Jackson Laboratory. 
#
#    Copyright © 1996 The Jackson Laboratory All Rights Reserved 
#
