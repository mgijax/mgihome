#!./python

import string
import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

def banner ():
   return [ ' <TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="100%">',
            '<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="20%%" VALIGN="center" ALIGN="left"><A HREF="%s" border=0><IMG SRC="images/mgi_logo_small.jpg" border=0 ALT="MGI"></A></TD>' % config['WI_URL'],
            '<TD WIDTH="60%" ALIGN="center" VALIGN="center" BGCOLOR="#ffffff">',
            '<FONT COLOR="#000000" SIZE=5 FACE="Arial,Helvetica">',
             'GEN-Registration Error',
             '</FONT></TD><TD WIDTH="20%" VALIGN="center" ALIGN="center" BGCOLOR="#ffffff">&nbsp;</TD></TR>',
             '<TR BGCOLOR="blue"><TD COLSPAN=3><FONT face="Arial,Helvetica" color="#ffffff">',
             '<B>&nbsp;Mouse Genome Informatics</B></TD></TR>',
             '<TR><TD BGCOLOR="#ffffff"><FONT SIZE=-1 FACE="Arial,Helvetica"><CENTER><A HREF="%s">MGI Home</A>&nbsp;&nbsp;&nbsp;' % config['WI_URL'],
             '<a href="%shelp/help.shtml">Help' % config['MGIHOME_URL'],
             '</A></FONT></CENTER></TD></TR>',
             '</TABLE></TD></TR>',
             '</TABLE>',
             '<HR>' ]

def bannerok ():
   return [ ' <TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="100%">',
            '<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="20%%" VALIGN="center" ALIGN="left"><A HREF="%s" border=0><IMG SRC="images/mgi_logo_small.jpg" border=0 ALT="MGI"></A></TD>' % config["WI_URL"],
            '<TD WIDTH="60%" ALIGN="center" VALIGN="center" BGCOLOR="#ffffff">',
            '<FONT COLOR="#000000" SIZE=5 FACE="Arial,Helvetica">',
             'GEN-Registration Confirmation',
             '</FONT></TD><TD WIDTH="20%" VALIGN="center" ALIGN="center" BGCOLOR="#ffffff">&nbsp;</TD></TR>',
             '<TR BGCOLOR="blue"><TD COLSPAN=3><FONT face="Arial,Helvetica" color="#ffffff">',
             '<B>&nbsp;Mouse Genome Informatics</B></TD></TR>',
             '<TR><TD BGCOLOR="#ffffff"><FONT SIZE=-1 FACE="Arial,Helvetica"><CENTER><A HREF="%s">MGI Home</A>&nbsp;&nbsp;&nbsp;' % config["WI_URL"],
             '<a href="%shelp/help.shtml">Help' % config['MGIHOME_URL'],
             '</A></FONT></CENTER></TD></TR>',
             '</TABLE></TD></TR>',
             '</TABLE>',
             '<HR>' ]

def footer ():

	return  [
		'<SMALL>',
		'Send questions and comments to <a href="mailto:gen@jax.org">gen@jax.org</a><BR>',
		'The Gene Expression Database (GXD) Project is supported by <a href="http://www.nih.gov/">NIH</a> grant <a href="http://projectreporter.nih.gov/project_info_description.cfm?aid=7763602&icde=6960199">HD062499</a><BR>',
		'<a href="%sother/copyright.shtml">Warranty Disclaimer &amp; Copyright Notice</a><BR>' % config['MGIHOME_URL'],
		'</SMALL>'
		]

