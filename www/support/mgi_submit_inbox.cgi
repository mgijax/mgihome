#!./python

# MGDquest

"""CGI script to process User Support Express Mail form.

This script generates a confirmation (or error) message, processes a form
and sends mail to User Support via Remedy.
schema: TJL-Inbox
forms: mgi_inbox.shtml

version 1.0 9/98
revised 1/14/1999

"""

import sys
if '.' not in sys.path:
        sys.path.insert(0, '.')

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import cgi
import os
import mgi_utils
import errorlib
import template

reply_message = template.Template(config['TEMPLATE_PATH'])

NL = '\n'
SP = ' '
HT = '\t'

REQUIRED_FIELDS = [ 'lastname',
        'firstname',
        'subject',
        'message',
        'emailaddr'
        ]

RECIPIENT = 'jaxmgi@service-now.com'
# developer override for mailtarget 
if config.has_key('CGI_MAILTARGET'):
        RECIPIENT = config['CGI_MAILTARGET']

def hd():
        reply_message.setTitle('User Support Express Mail Results')
        reply_message.setHeaderBarMainText('User Support <I>Express</I> Mail Results')
        return

def main():
        hd()
        
        captcha_element = ''
        if config.has_key('CAPTCHA_ELEMENT'):
                captcha_element = config['CAPTCHA_ELEMENT']
                REQUIRED_FIELDS.append(captcha_element)
        captcha_timeout = ''
        if config.has_key('CAPTCHA_TIMEOUT'):
                captcha_timeout = config['CAPTCHA_TIMEOUT']
        captche_hide = ''
        if config.has_key('CAPTCHA_HIDE'):
                captcha_hide = config['CAPTCHA_HIDE']
                REQUIRED_FIELDS.append(captcha_hide)
                
        form = cgi.FieldStorage()
        
        err = 0
        
        for field in REQUIRED_FIELDS:
                if field not in form:
                        if (field != captcha_hide):
                                err = 1
                                break
                else:
                        if (field == captcha_element):
                                if int(form[captcha_element].value) < int(captcha_timeout):
                                        err = 1
                                        break
                        if (field == captcha_hide):
                                if form[captcha_hide].value != '':
                                        err = 1
                                        break
        
        if err != 0 :
                error_message = """<H1>Sorry...</H1>Please fill in required fields: 
                        First Name, Last Name, E-mail address, Subject and Message. Then 
                        send the message.  Please fill in required fields: First Name, 
                        Last Name, E-mail address, Subject and Message. Then send the 
                        message."""
                reply_message.setTitle('User Support Express Mail - Error')
                reply_message.appendBody(error_message)
        else:
                if 'title' in form:
                        title = form['title'].value
                else:
                        title = ""
                firstname = form['firstname'].value
                lastname = form['lastname'].value
                if 'inst' in form:
                        inst = form['inst'].value
                else:
                        inst = ""
                if 'positn' in form:
                        positn = form['positn'].value
                else:
                        positn = ""
                emailaddr = form['emailaddr'].value
                if 'ph' in form:
                        ph = form['ph'].value
                else:
                        ph = ""

                if 'fx' in form:
                        fax = form['fx'].value
                else:
                        fax = ""
                subject = form['subject'].value
                message = form['message'].value
                attnto = form['attnto'].value
                domain = form['domain'].value

                msg =   mgi_utils.date() + NL \
                        + 'FirstName: ' + firstname + NL \
                        + 'LastName: ' + lastname + NL \
                        + 'From: ' + emailaddr + NL \
                        + 'ph: ' + ph + NL \
                        + 'inst: ' + inst + NL + NL \
                        + 'Request Summary: ' + subject + NL + NL \
                        + 'Request Details: ' + message + NL + NL \
                        + 'ATTN' + attnto + NL 
                
                body = """
                        <H1>Thank you.</H1>
                        Your message has been received and is being forwarded to our
                        <A HREF="support.shtml">User Support Group</A>."""
                        
                reply_message.appendBody(body)

                mail_header = 'Subject: Express Mail' + NL
                fd = os.popen('%s -t %s' % (config['SENDMAIL'], \
                        RECIPIENT), 'w')
                fd.write( mail_header + msg + NL + '.' + NL )
                fd.close()
                
        print(reply_message.getFullDocument())
                
        return

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
#    Copyright (c) 1996 The Jackson Laboratory All Rights Reserved 
#
