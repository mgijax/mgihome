MGI_LIBS = '/usr/local/mgi/live/lib/python'
import sys
if MGI_LIBS not in sys.path:
        sys.path.insert (0, MGI_LIBS)

import Configuration
config = Configuration.get_Configuration ('Configuration', 1)

import webshare
import os

try:
        COMPONENTS = webshare.SharedComponents(os.path.join
(config['MGIHOME_PATH'],'webshare.rcd'))
except (message):
        sys.stderr.write ('Error in mgihome/lib/python/webshare_lib.py:%s' % str(message))
        COMPONENTS = None
        
###----------------------------------------------------------------------###
def webshareLookup(name):
    if COMPONENTS != None:
        component = COMPONENTS.get(name)
        if component != None:
            return component.getHtmlTag()
    return '&lt;%s&gt;' % name
        
