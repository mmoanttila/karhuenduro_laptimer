#!/usr/bin/env python3
"""
This is subprogram to update results-page for some time (defaulting to 3h) after starting.
"""

import time
import urllib2

def loadWebPage(myUrl):
	try:
		req = urllib2.Request(url=myUrl)
	except urllib2.HTTPError:
		pass

debug = True

if (debug):
    stime = time.ctime()
    print ("Skriptin suoritus alkoi: ", stime) 

# epoch in seconds
now = int(time.time())
# now + 3h
#stop = now+10800
# use little lower time for testing
stop = now+180

while ( now < stop ):
    time.sleep(60)
    now = int(time.time())

if (debug):
    stime = time.ctime()
    print ("Skriptin suoritus paattyi: ", stime)
