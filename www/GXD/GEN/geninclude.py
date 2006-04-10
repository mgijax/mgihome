#!./python

import string
import config

def banner ():
   return [ ' <TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="100%">',
            '<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="20%%" VALIGN="center" ALIGN="left"><A HREF="%s" border=0><IMG SRC="images/mgi_logo_small.jpg" border=0 ALT="MGI"></A></TD>' % config.lookup('WI_URL'),
            '<TD WIDTH="60%" ALIGN="center" VALIGN="center" BGCOLOR="#ffffff">',
            '<FONT COLOR="#000000" SIZE=5 FACE="Arial,Helvetica">',
             'GEN-Registration Error',
             '</FONT></TD><TD WIDTH="20%" VALIGN="center" ALIGN="center" BGCOLOR="#ffffff">&nbsp;</TD></TR>',
             '<TR BGCOLOR="blue"><TD COLSPAN=3><FONT face="Arial,Helvetica" color="#ffffff">',
             '<B>&nbsp;Mouse Genome Informatics</B></TD></TR>',
             '<TR><TD BGCOLOR="#ffffff"><FONT SIZE=-1 FACE="Arial,Helvetica"><CENTER><A HREF="%s">MGI Home</A>&nbsp;&nbsp;&nbsp;' % config.lookup('WI_URL'),
             '<a href="%shelp/help.shtml">Help' % config.lookup('MGIHOME_URL'),
             '</A></FONT></CENTER></TD></TR>',
             '</TABLE></TD></TR>',
             '</TABLE>',
             '<HR>' ]

def bannerok ():
   return [ ' <TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="100%">',
            '<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>',
            '<TR><TD WIDTH="20%%" VALIGN="center" ALIGN="left"><A HREF="%s" border=0><IMG SRC="images/mgi_logo_small.jpg" border=0 ALT="MGI"></A></TD>' % config.lookup("WI_URL"),
            '<TD WIDTH="60%" ALIGN="center" VALIGN="center" BGCOLOR="#ffffff">',
            '<FONT COLOR="#000000" SIZE=5 FACE="Arial,Helvetica">',
             'GEN-Registration Confirmation',
             '</FONT></TD><TD WIDTH="20%" VALIGN="center" ALIGN="center" BGCOLOR="#ffffff">&nbsp;</TD></TR>',
             '<TR BGCOLOR="blue"><TD COLSPAN=3><FONT face="Arial,Helvetica" color="#ffffff">',
             '<B>&nbsp;Mouse Genome Informatics</B></TD></TR>',
             '<TR><TD BGCOLOR="#ffffff"><FONT SIZE=-1 FACE="Arial,Helvetica"><CENTER><A HREF="%s">MGI Home</A>&nbsp;&nbsp;&nbsp;' % config.lookup("WI_URL"),
             '<a href="%shelp/help.shtml">Help' % config.lookup('MGIHOME_URL'),
             '</A></FONT></CENTER></TD></TR>',
             '</TABLE></TD></TR>',
             '</TABLE>',
             '<HR>' ]

def footer ():

	return  [
		'<SMALL>',
		'Send questions and comments to <a href="mailto:GEN@informatics.jax.org">GEN@informatics.jax.org</a><BR>',
		'The Gene Expression Database (GXD) Project is supported by <a href="http://www.nih.gov/">NIH</a> grant <a href="http://crisp.cit.nih.gov/crisp/CRISP_LIB.getdoc?textkey=6363398&p_grant_num=5R01HD033745-05&p_query=&ticket=430962&p_audit_session_id=3171719&p_keywords=">HD33745</a><BR>',
		'<a href="%sother/copyright.shtml">Warranty Disclaimer &amp; Copyright Notice</a><BR>' % config.lookup('MGIHOME_URL'),
		'</SMALL>'
		]

