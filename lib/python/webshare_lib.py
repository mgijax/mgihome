import config
import webshare
import os

try:
	COMPONENTS = webshare.SharedComponents(os.path.join
(config.lookup('MGIHOME_PATH'),'webshare.rcd'))
except webshare.error, message:
	sys.stderr.write ('Error in mgihome/lib/python/webshare_lib.py:%s' % message)
	COMPONENTS = None
	
###----------------------------------------------------------------------###
def webshareLookup(name):
    if COMPONENTS != None:
        component = COMPONENTS.get(name)
        if component != None:
            return component.getHtmlTag()
    return '&lt;%s&gt;' % name
	
