#!/usr/bin/python
import json
import time
from pprint import pprint
import urllib
#from urllib import request
import unicodedata
from collections import defaultdict
import os
import sys

startports = [1, 3]
endports = [0, 2, 4]

# dict contains lists of timestamps indexed by epc
starttimes = defaultdict(list)
endtimes = defaultdict(list)
laptimes = defaultdict(list)

# check for debug cmd parameter
if ( len(sys.argv) > 1 and '-d' in sys.argv ):
    print "Debugging Enabled!"
    debug = True
else:
    debug = False

# If called as CGI, we'll use html output
if "HTTP_USER_AGENT" in os.environ:
    cgi = True
    print "Content-type:text/html\r\n\r\n"
    print '<html>'
    print '<head>'
    print '<title>Kierrosajat</title>'
    print '<body><pre>'
else:
    cgi = False
#try:
#	url = "http://karhu.serveftp.net:5000/Ajanotto/log.txt"
#	contents = urllib.urlopen( url )
#except IOError:
#    print ("URLia ", url, " ei onnistuttu resolvoimaan!")
#    print ("Tai sitten osoite ei vaan vastaa!")

data = []
maxlaps = 0

def time_to_localtime (utime):
    return (time.strftime( '%H:%M:%S', time.localtime(utime/1000000)))

def newtime_to_ctime (utime):
    strtime = unicodedata.normalize('NFKD', utime).encode('ascii','ignore')
    # print ("Tulkitaan ", strtime)
    # pprint (time.mktime(time.strptime(strtime,"%Y-%m-%dT%H:%M:%S.%fZ")))
    return (time.mktime(time.strptime(strtime,"%Y-%m-%dT%H:%M:%S.%fZ")))
    # 2019-03-24T20:19:03.872083Z

#with open('log.txt',mode = 'r') as contents:
with open('20190528.txt',mode = 'r') as contents:

  try:

    for line in contents:
        # First let's skip logfile timestamp
        jsonline=line.split(",",2)
        # Let's read json content to list of dicts
        try:
            parsed=json.loads(jsonline[2])
        except ValueError:
            print ("Rivilta: ", jsonline[2])
            print ("ei onnistuttu parsimaan json:ia.")

        # Skip heartbeats
        if ( not parsed['tag_reads'][0]['isHeartBeat'] ):
            # We might have several tagreads per line
            # That's why we loop
            for read in parsed['tag_reads']:
                epc = unicodedata.normalize('NFKD', read['epc']).encode('ascii','ignore')
                if (read['antennaPort'] in startports ):
                    if (debug):
                        print ("Lahto: ", epc, " ", time_to_localtime(read['firstSeenTimestamp']) )
                        #print ("Lahto: ", read['epc'], " ", newtime_to_ctime(read['firstSeenTimestamp']) )
                        if ( len(starttimes[epc]) > 0 ):
					        print ("Laptime for ", epc, " : ", (read['firstSeenTimestamp'] - starttimes[epc][-1])/1000000, " secs") 
                    if ( len(starttimes[epc]) > 0 ):
                        laptimes[epc].append(read['firstSeenTimestamp']-starttimes[epc][-1])
                    starttimes[epc].append(read['firstSeenTimestamp'])
                elif (read['antennaPort'] in endports ):
                    if (debug):
                        print ("Maali: ", epc, " ", time_to_localtime(read['firstSeenTimestamp']) )
                        # print ("Maali: ", read['epc'], " ", newtime_to_ctime(read['firstSeenTimestamp']) )
                    endtimes[epc].append(read['firstSeenTimestamp'])
                    # Find last start-timestamp for current epc to calculate laptime
                    #pprint (read['firstSeenTimestamp'])
                    #pprint (starttimes[read['epc']][-1])
                    # Assuming last starttime is for current leg
                    if (debug):
                        print ("Laptime for ", epc, " : ", (read['firstSeenTimestamp'] - starttimes[epc][-1])/1000000, " secs") 
                    laptimes[epc].append(read['firstSeenTimestamp']-starttimes[epc][-1])
                    if (len (laptimes[epc])) > maxlaps:
                        maxlaps += 1
                #timestamps[read['epc']].append(read['firstSeenTimestamp'])
                #data.append(read)
                #pprint (read)
                #pprint (type (read))
  except TypeError:
        print ("Lokin analysoinnissa tuli tyyppivirhe!")
        print ("Tarkoittanee, etta se sisaltaa jotain odottamatonta moskaa!")

print ("Ajettu ", maxlaps, " kierrosta.")
if (cgi):
    print "</pre>"
    print "<table>"
    for line in laptimes:
        print "  <tr>"
        print "    <td>", line['epc'], "</td>"
        for col in range(0, maxlaps):
            print "    <td>", line['epc'][col], "</td>"
        print "  </tr>"
    print "</table>"
    print "<pre>"
else:
    print "Laptimes per epc"
    for epc, times in laptimes.iteritems():
        print epc, ": "
        for col in range(0,len(times)):
            print "    ", times[col]/1000000, "secs"

#pprint(laptimes)

if (cgi):
    print '</pre>'
    print '</html>'
#print (type(parsed['tag_reads']))
#with open('log.txt') as f:
#    data = json.load(f)

#for msg in data:
