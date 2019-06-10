#!/usr/bin/python
import json
import time
from pprint import pprint
import urllib
#from urllib import request
import unicodedata
from collections import defaultdict
from datetime import timedelta, datetime
import csv
import os
import sys

startports = [1, 3]
endports = [2, 4]

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
    print '</head>'
    print '<style>'
    print '  table {border-collapse: collapse;}'
    print '  tr:nth-child(odd) {background-color: #f2f2f2;}'
    print '  td.laptime { padding: 5px; }'
    print '</style>'
    print '<body><pre>'
    import cgi, cgitb
    # Enable CGI-debugging output to html
    cgitb.enable()
    cgitb.enable(display=0, logdir="/worktmp/mmoa/karhu/logs/")

    # Lets prepare to read GET-variables
    form = cgi.FieldStorage()
    # Let's use current date if not given on url
    #date = form.getvalue('date', datetime.now().strftime('%Y%m%d'))
    date = form.getvalue('date', '20190602')
    start = form.getvalue('start')
    end = form.getvalue('end')
else:
    cgi = False
    from cgi import parse_qs
    date = os.environ.get('date', '')
    start =os.environ.get('start', '') 
    end = os.environ.get('end', '') 
#    contents = open('20190530.txt',mode = 'r')

try:
    if (debug):
        print ("Generating url = http://karhu.serveftp.net:5000/Ajanotto/" + date + ".txt")
    url = "http://karhu.serveftp.net:5000/Ajanotto/" + date + ".txt"
    contents = urllib.urlopen( url )
except IOError:
    print ("URLia ", url, " ei onnistuttu resolvoimaan!")
    print ("Tai sitten osoite ei vaan vastaa!")



data = []
maxlaps = 0

def print_laptime (usec):
    if (debug):
        td = timedelta( milliseconds=usec/1000 )
        secs,msecs = int(td.total_seconds()),td.total_seconds()-int(td.total_seconds())
        print "Converting", usec, "usec to ", round( td.total_seconds(),1) , "secs."
        print "Also secs=", secs, "msecs=", msecs
    return str( timedelta( milliseconds=usec//1000 ) )

def read_tags (tagfile):
    my_tags ={}
    with open( tagfile ) as csvfile:
        csvreader = csv.reader( csvfile, delimiter=',' )
        for row in csvreader:
            my_tags[row[0]] = row[1]
    return my_tags

def print_tag (tag):
    if tags.has_key (tag):
        return tags[tag]
    else:
        return tag

def time_to_localtime (utime):
    return (time.strftime( '%H:%M:%S', time.localtime(utime/1000000)))

def newtime_to_ctime (utime):
    strtime = unicodedata.normalize('NFKD', utime).encode('ascii','ignore')
    # print ("Tulkitaan ", strtime)
    # pprint (time.mktime(time.strptime(strtime,"%Y-%m-%dT%H:%M:%S.%fZ")))
    return (time.mktime(time.strptime(strtime,"%Y-%m-%dT%H:%M:%S.%fZ")))
    # 2019-03-24T20:19:03.872083Z

tags = read_tags( 'tags.csv')

#with open('20190530.txt',mode = 'r') as contents:

#  try:

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
#except TypeError:
#    print ("Lokin analysoinnissa tuli tyyppivirhe!")
#    print ("Tarkoittanee, etta se sisaltaa jotain odottamatonta moskaa!")

print "Ajettu", maxlaps, "kierrosta."
if (cgi):
    print "</pre>"
    print "<table border=\"1\">"
    for epc, times in laptimes.iteritems():
        print "  <tr>"
        print "    <td colspan=\"", maxlaps, "\">", print_tag( epc ), "</td>"
        print "    <td>Total</td>"
        print "  </tr>"
        print "  <tr>"
        total = 0.0
        for col in range(0,len(times)):
            total = total + times[col]
            if ( (col == len(times)-1 ) ):
                print "    <td class=\"laptime\" colspan=\"", maxlaps-col, "\">", print_laptime( times[col] )[:-3], "</td>"
            else: 
                print "    <td class=\"laptime\">", print_laptime( times[col] )[:-3], "</td>"
        print "    <td>", print_laptime( total )[:-3], "</td>"
        print "  </tr>"
    print "</table>"
    print "<pre>"
else:
    print "Laptimes per epc"
    for epc, times in laptimes.iteritems():
        print print_tag(epc), ": "
        total = 0.0
        for col in range(0,len(times)):
            total = total + times[col]
            print "    ", print_laptime( times[col] )[:-3], "secs"
        print "Total:", print_laptime( total )[:-3] 

#pprint(laptimes)

if (cgi):
    print '</pre>'
    print '</html>'
#print (type(parsed['tag_reads']))
#with open('log.txt') as f:
#    data = json.load(f)

#for msg in data:
