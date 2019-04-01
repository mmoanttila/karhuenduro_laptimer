#!/usr/bin/python
import json
import time
from pprint import pprint
import urllib
#from urllib import request
import unicodedata
import os
from collections import defaultdict

startports = [1, 3]
endports = [2, 4]

# dict contains lists of timestamps indexed by epc
starttimes = defaultdict(list)
endtimes = defaultdict(list)
laptimes = defaultdict(list)


# If called as CGI, we'll use html output
if "HTTP_USER_AGENT" in os.environ:
    print "Content-type:text/html\r\n\r\n"
    print '<html>'
    print '<head>'
    print '<title>Kierrosajat</title>'
    print '<body><pre>'

#try:
#	url = "http://karhu.serveftp.net:5000/Ajanotto/log.txt"
#	contents = urllib.urlopen( url )
#except IOError:
#    print ("URLia ", url, " ei onnistuttu resolvoimaan!")
#    print ("Tai sitten osoite ei vaan vastaa!")

data = []

def time_to_localtime (utime):
    return (time.strftime( '%H:%M:%S', time.localtime(utime/1000000)))

def newtime_to_ctime (utime):
    strtime = unicodedata.normalize('NFKD', utime).encode('ascii','ignore')
    # print ("Tulkitaan ", strtime)
    # pprint (time.mktime(time.strptime(strtime,"%Y-%m-%dT%H:%M:%S.%fZ")))
    return (time.mktime(time.strptime(strtime,"%Y-%m-%dT%H:%M:%S.%fZ")))
    # 2019-03-24T20:19:03.872083Z

with open('log-new.txt',mode = 'r') as contents:

  try:

    for line in contents:
        # First let's skip logfile timestamp
        jsonline=line.split(",",3)
        # Let's read json content to list of dicts
        try:
            parsed=json.loads(jsonline[3])
        except ValueError:
            print ("Rivilta: ", jsonline[3])
            print ("ei onnistuttu parsimaan json:ia.")

        # Skip heartbeats
        if ( not parsed['tag_reads'][0]['isHeartBeat'] ):
            # We might have several tagreads per line
            # That's why we loop
            for read in parsed['tag_reads']:
                if (read['antennaPort'] in startports ):
                    print ("Lahto: ", read['epc'], " ", newtime_to_ctime(read['firstSeenTimestamp']) )
                    starttimes[read['epc']].append(read['firstSeenTimestamp'])
                elif (read['antennaPort'] in endports ):
                    print ("Maali: ", read['epc'], " ", newtime_to_ctime(read['firstSeenTimestamp']) )
                    endtimes[read['epc']].append(read['firstSeenTimestamp'])
                    # Find last start-timestamp for current epc to calculate laptime
                    #pprint (read['firstSeenTimestamp'])
                    #pprint (starttimes[read['epc']][-1])
                    # Assuming last starttime is for current leg
                    print ("Laptime for ", read['epc'], " : ", (read['firstSeenTimestamp'] - starttimes[read['epc']][-1])/1000000, " secs") 
                    laptimes[read['epc']].append(read['firstSeenTimestamp']-starttimes[read['epc']][-1])
                #timestamps[read['epc']].append(read['firstSeenTimestamp'])
                #data.append(read)
                #pprint (read)
                #pprint (type (read))
  except TypeError:
        print ("Lokin analysoinnissa tuli tyyppivirhe!")
        print ("Tarkoittanee, etta se sisaltaa jotain odottamatonta moskaa!")

pprint(laptimes)

if "HTTP_USER_AGENT" in os.environ:
    print '</pre>'
    print '</html>'
#print (type(parsed['tag_reads']))
#with open('log.txt') as f:
#    data = json.load(f)

#for msg in data:
