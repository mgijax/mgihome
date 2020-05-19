# Name: formMailer.py
# Purpose: provide classes to facilitate accepting the submission of an HTML
#       form, performing any necessary validations, providing user feedback,
#       and mailing the submission contents to a specified e-mail address.

import types            # standard Python modules

import CGI              # MGI-written Python modules
import Configuration
import mgi_utils
import mgi_html
import template

###--- Global Variables/Constants ---###

# messages produced when incorrect or insufficient data is submitted and
# detected:  primarily used with the handleError() function

config = Configuration.Configuration('Configuration', 1)

MISSING_FIELDS = '''These required fields are missing: %s<BR>
        Please go back and try again.<P>'''

FAILED_CHECKS = '''The following field(s) contained errant values:<BR>
        <DL>
        %s
        </DL>
        Please go back and try again.<P>'''

###--- Functions ---###

def handleError (
        message,        # string; message describing the error
        title           # string; name of the form being submitted
        ):
        # Purpose: send to the user an HTML page describing an error which
        #       was detected
        # Returns: nothing
        # Assumes: nothing
        # Effects: writes to stdout
        # Throws: nothing
        
        
        error_template = template.Template(config['TEMPLATE_PATH'])
        error_template.setContentType('')
        error_template.setTitle(title)
        error_template.setHeaderBarMainText('%s Submission Error' % title)
        error_template.setBody(message)
        
        print(error_template.getFullDocument())
        
        return

###--- Classes ---###

class formMailer (CGI.CGI):
        # IS: a CGI script which catches input from a form, composes a reply
        #       for the remote user, and includes it in an e-mail to the 
        #       curator and submitter
        # HAS: name of the web form sent, e-mail address to which to send the
        #       e-mail, output page header & footer, a dictionary of
        #       internal fieldnames and corresponding labels, a list of
        #       fieldnames for required fields, and a list of tuples which
        #       specify various sections for the e-mail sent
        # DOES: see IS section

        REPLY_FOOTER = '\n\nWe will mail your accession ID as soon '\
                       'as possible.  If you have questions regarding your '\
                       'submission, please contact. %s  \n'

        def __init__ (self,
                form_name,              # string; name of the form submitted
                curator_address,        # string; where to send the e-mail

                # optional parameters
                labels = {},            # dictionary mapping internal field-
                                        #       names to the labels shown to
                                        #       the user
                required_fields = [],   # list of strings; internal fieldnames
                                        #       of fields required to have a
                                        #       value submitted by the user
                sections = []           # list of tuples; each tuple describes
                                        #       a "section" for the e-mail and
                                        #       has two values: a string title
                                        #       for the section, and a list of
                                        #       string fieldnames to include
                                        #       in the section
                ):
                # Purpose: constructor
                # Returns: nothing
                # Assumes: nothing
                # Effects: gets parameters from the form submission;
                #       constructs a set of labels if one is not given
                # Throws: nothing

                CGI.CGI.__init__ (self)         # parent class's constructor

                self.parms = self.get_parms()

                # initialize the basic attributes, based on parameters
                self.form_name = form_name
                self.curator_address = curator_address
                self.labels = labels
                self.required_fields = required_fields
                self.sections = sections

                # if the user didn't give us a set of labels, then we use the
                # fieldnames submitted to compose a set
                if not self.labels:
                        fields = list(self.parms.keys())
                        for field in fields:
                                self.labels[field] = field
                return

        ###--- Private Methods ---###

        def doValidations(self):
                # Purpose: perform any necessary validations of the parameters
                #       as submitted by the user
                # Returns: list of tuples describing the errors.  each tuple
                #       contains (fieldname, error string)
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: By default, we perform no validations.  This method
                #       should be overridden in subclasses as needed.

                return []

        def doPreValidationProcessing(self):
                # Purpose: perform any necessary pre-processing of parameters
                #       before they may be validated
                # Returns: nothing
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: By default, we perform no pre-processing.  This
                #       method should be overridden in subclasses as needed.

                return

        def doPostValidationProcessing(self):
                # Purpose: perform any necessary post-processing of parameters
                #       after they have been validated
                # Returns: nothing
                # Assumes: nothing
                # Effects: nothing
                # Throws: nothing
                # Notes: By default, we perform no post-processing.  This
                #       method should be overridden in subclasses as needed.

                return
        
        def setFooter(self, value):
                self.REPLY_FOOTER = value

        def main(self):
                # Purpose: main processing loop.  check the parameters for
                #       validity and completeness.  send an e-mail if 
                #       able.  send an HTML reponse to the user.
                # Returns: nothing
                # Assumes: nothing
                # Effects: writes an HTML page to stdout; sends an e-mail
                #       if possible
                # Throws: propagates any exceptions (none caught here)
                

                # responses produced by a valid submission, depending on 
                # whether the e-mail could be sent or not:
                
                MESSAGE_SENT = '''The following information was successfully submitted.
                        <BLOCKQUOTE><PRE>\n%s\n</PRE></BLOCKQUOTE>'''

                MESSAGE_FAILED = '''An error occurred.  Your submission could not be sent.
                        Please try again later.<P>'''
                
                # header and footer of reply email sent to submitter
                REPLY_HEADER = 'Thank you for your %s submission.\n\n'\
                        'Below is a summary of what you have submitted.\n'\
                        'We will contact you if any questions arise '\
                        'concerning your submission.\n'

                # look for any missing fields:  (bail out if any found)
                missing_fields = []
                for field in self.required_fields:
                        if field not in self.parms:
                                missing_fields.append (self.labels[field])
                if missing_fields:
                        handleError (MISSING_FIELDS % \
                                '\n '.join (missing_fields),
                                self.form_name
                                )
                        return

                # do any pre-validation processing
                self.doPreValidationProcessing()

                # validate the input parameters as needed
                failed_checks = self.doValidations()
                if failed_checks:
                        list = []
                        for (field, error) in failed_checks:
                                list.append ('<DT>%s<DD>%s' % \
                                        (self.labels[field], error))
                        handleError (FAILED_CHECKS % '\n'.join (list),
                                self.form_name
                                )
                        return

                # do any post-validation processing
                self.doPostValidationProcessing()

                # Compose the message to be sent, breaking it into sections
                # if we were given any section definitions at instantiation-
                # time.  Note that field values will appear indented on the
                # line below the field label.  For fields with multiple
                # values, each will appear on a separate line indented under
                # the label.

                # list of strings; data sent in email
                message      = [] 
                
                # list of strings; reply header + data + reply footer
                # to be sent back to submitter
                reply_message = []

                if self.sections:
                    # do grouping into sections with headings
                    for (heading, fieldlist) in self.sections:
                        section = [
                            '-' * len(heading),
                            heading,
                            '-' * len(heading),
                            ]
                        for field in fieldlist:
                            if field in self.parms:
                                section.append(self.labels[field])
                                if type(self.parms[field]) == list:
                                    for item in self.parms[field]:
                                        section.append('\t%s' % item)
                                else:
                                    section.append('\t%s' % self.parms[field])

                        # if the section had fields submitted, add it to the
                        # e-mail message
                        if len(section) > 3:
                            message = message + section
                else:
                
                    # no sections - just alphabetize the fields by label
                    fields = list(self.parms.keys())
                    list = []
                    for field in fields:
                        list.append ((self.labels[field], field))
                    list.sort()

                    for (label, field) in list:
                        message.append (self.labels[field])
                        if type(self.parms[field]) == list:
                            for item in self.parms[field]:
                                message.append('\t%s' % item)
                        else:
                            message.append ('\t%s' % self.parms[field])

                # compile the list of strings into a single string to e-mail
                message = '\n'.join (message)
                
                reply_message = (REPLY_HEADER % (self.form_name) + message +
                        self.REPLY_FOOTER % (self.curator_address))

                # send the message to the curator and submitter
                curatorSentCode = mgi_utils.send_Mail (
                        self.parms['email'],
                        self.curator_address,
                        '%s Submission' % self.form_name,
                        message
                        )

                submitterSentCode = mgi_utils.send_Mail (
                        self.curator_address,
                        self.parms['email'],
                        '%s Submission' % self.form_name,
                        reply_message
                        )

                # return appropriate feedback
                page_template = template.Template(config['MGICONFIG_PATH'] + 'web/')
                page_template.setContentType('')
                if (curatorSentCode == 0) and (submitterSentCode == 0):
                    page_template.setTitle('Request Sent')
                    page_template.setHeaderBarMainText('%s Submission Sent' % self.form_name)
                    page_template.setBody(MESSAGE_SENT % (
                            mgi_html.escape(message)))
                    print(page_template.getFullDocument())
                else:
                    page_template.setTitle('Request Not Sent')
                    page_template.setHeaderBarMainText('%s Submission Not Sent' % self.form_name)
                    page_template.setBody(MESSAGE_FAILED)
                    print(page_template.getFullDocument())

                return

###--- Example Usage ---###

#       myCGI = formMailer.formMailer ('Address Submission',
#                       'test@informatics.jax.org',
#                       { 'first' : 'First Name',
#                         'mid'   : 'Middle Initial',
#                         'last'  : 'Last Name',
#                         'street': 'Street',
#                         'city'  : 'City',
#                         'state' : 'State/Province',
#                         'zip'   : 'ZIP/Postal Code'
#                       },
#                       [ 'first', 'last', 'city', 'state', 'zip' ],
#                       [ ('Individual',
#                               [ 'last', 'first', 'mid' ]),
#                         ('Address',
#                               [ 'street', 'city', 'state', 'zip' ])
#                       ])
#       myCGI.go()
