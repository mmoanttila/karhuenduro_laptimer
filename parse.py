#! /usr/bin/env python
import json
import time
from pprint import pprint
import urllib2
#from urllib import request
import unicodedata
from collections import defaultdict
from datetime import timedelta, datetime
import csv
import os
import sys

# Some settings for code
startports = [1, 3]
endports = [2, 4]
log_url = "http://karhu.serveftp.net:5000/Ajanotto/"
csv_url = "https://docs.google.com/spreadsheets/d/1dtqQQ6azJ5J0VBEHnnKLAkp3SlUK_6OzSk2RQivY6L0/export?format=csv&id=1dtqQQ6azJ5J0VBEHnnKLAkp3SlUK_6OzSk2RQivY6L0&gid=0"

# End of settings

# dict contains lists of timestamps indexed by epc
starttimes = defaultdict(list)
endtimes = defaultdict(list)
laptimes = defaultdict(list)
laps = defaultdict() 
total = defaultdict()

# check for debug cmd parameter
if ( len(sys.argv) > 1 and '-d' in sys.argv ):
    print "Debugging Enabled!"
    debug = True
else:
    debug = False

# If called as CGI, we'll use html output
if "HTTP_USER_AGENT" in os.environ:
    use_cgi = True
    print "Content-type: text/html"
    print
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

    if (debug):
        print ("CGI-tulostus kaytossa")
    # Lets prepare to read GET-variables
    form = cgi.FieldStorage()
    # Let's use current date if not given on url
    #date = form.getvalue('date', datetime.now().strftime('%Y%m%d'))
    date = form.getvalue('date', '20190602')
    if ( '-' in date ):
        date = date.replace("-","")
    mydebug = form.getvalue('debug', 'False')
    if ( mydebug == 'True' or mydebug == 'true' or mydebug == 1 ):
        debug = True

    if (debug):
        print ("Kaytetty date: " + date)
    race_start = int( time.mktime( time.strptime( date + " " + form.getvalue('start','10:00'), "%Y%m%d %H:%M")) ) * 1000000
    race_end = int( time.mktime( time.strptime( date + " " + form.getvalue('end','23:59'), "%Y%m%d %H:%M")) ) * 1000000
else:
    use_cgi = False
    from cgi import parse_qs
    date = os.getenv('date', '20190602')
    race_start = int( time.mktime( time.strptime( date + " " + os.getenv('start','10:00'), "%Y%m%d %H:%M")) ) * 1000000
    if (debug): 
        print ("Converting :" + date + " " + os.getenv('start','10:00') + " as %Y%m%d %H:%M")
        print ("Race start time: " + str(race_start))
    race_end = int( time.mktime( time.strptime( date + " " + os.getenv('end','23:59'), "%Y%m%d %H:%M")) ) * 1000000

try:
    if (debug):
        print ("Generating url = " + log_url + date + ".txt")
    url = log_url + date + ".txt"
    contents = urllib2.urlopen( url )
    if (debug):
        print ("Logfile last modified :" + contents.headers['last-modified'] )
except IOError:
    print ("URLia ", url, " ei onnistuttu resolvoimaan!")
    print ("Tai sitten osoite ei vaan vastaa!")

if (debug):
    print (contents.info())

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
    try:
        if (debug):
            print ("Trying to read .csv from " + csv_url )
        csvfile = urllib2.urlopen( csv_url )
       # if (debug):
       #     print ("CSV last modified :" + csvfile.headers['last-modified'] )

    except IOError:
        print ("URLia ", csv_url, " ei onnistuttu resolvoimaan!")
        print ("Tai sitten osoite ei vaan vastaa!")

    my_tags ={}
    # with open( tagfile ) as csvfile:
    csvreader = csv.reader( csvfile, delimiter=',' )
    for row in csvreader:
        if (debug):
            print "Luin tagin: " + row[2] + " = " + row[1]
        my_tags[row[2]] = row[1]
    return my_tags

def print_tag (tag):
    if tags.has_key (tag):
        return tags[tag]
    else:
        return tag

def time_to_localtime (utime):
    return (time.strftime( '%H:%M:%S', time.localtime(utime/1000000)))

def time_to_localtime_debug (utime):
    return (time.strftime( '%F %H:%M:%S', time.localtime(utime/1000000)))

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
    if (debug):
        print ("Luen rivia: ", jsonline[2])
    # Let's read json content to list of dicts
    try:
        parsed=json.loads(jsonline[2])
        if (debug):
            print ("Loysin json:ia rivilta:", parsed)
    except ValueError:
        print ("Rivilta: ", jsonline[2])
        print ("ei onnistuttu parsimaan json:ia.")
    # Skip heartbeats
    if ( not parsed['tag_reads'][0]['isHeartBeat'] ):
        # We might have several tagreads per line
        # That's why we loop
        for read in parsed['tag_reads']:
            if (debug):
                print ("Parsin EPC:ta: ", read)
            epc = unicodedata.normalize('NFKD', read['epc']).encode('ascii','ignore')
            if (debug):
                print ("Loysin EPC:n ", epc)
                print ("Testaan onko ", read['antennaPort'], " in ", startports)
                print ("  ja onko ", read['firstSeenTimestamp'], "(", time_to_localtime_debug(read['firstSeenTimestamp']), ") >", race_start, " (", time_to_localtime_debug(race_start), ")" )
                print ("  ja onko ", read['firstSeenTimestamp'], "(", time_to_localtime_debug(read['firstSeenTimestamp']), ") <", race_end, " (", time_to_localtime_debug(race_end), ")" )
            if (read['antennaPort'] in startports and read['firstSeenTimestamp'] > race_start and read['firstSeenTimestamp'] < race_end):
                if (debug):
                    print ("Lahto: ", epc, " ", time_to_localtime(read['firstSeenTimestamp']) )
                    #print ("Lahto: ", read['epc'], " ", newtime_to_ctime(read['firstSeenTimestamp']) )
                starttimes[epc].append(read['firstSeenTimestamp'])
                # We try to figure if we have end-tags at all
                if ( len(starttimes[epc]) > 1 and len(endtimes[epc]) == 0):
                    if (debug):
                        print ("Laptime for ", epc, " : ", (read['firstSeenTimestamp'] - starttimes[epc][-2])/1000000, " secs") 
                    laptimes[epc].append(read['firstSeenTimestamp'] - starttimes[epc][-2]) 
                    if (len (laptimes[epc])) > maxlaps:
                        maxlaps += 1

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
            else:
                if (debug):
                    print ("Ei huomioitavaa rivilla")

# Yritetaan laskea vahan statistiikkaa tuloksista.
for epc, times in laptimes.iteritems():
    laps[epc] = len(times)
    total[epc] = sum(times)
    if (debug):
        print (epc + ": laps=" + str(len (times)) + " total=" + str(sum(times)) )

print "Ajettu", maxlaps, "kierrosta."
if (use_cgi):
    print "</pre>"
    print "<table border=\"1\">"
    # for epc, times in laptimes.iteritems():
    # tama palauttaa laps-dictin sortattuna valueiden mukaan
    for mylaps, epc in sorted ( ((v,k) for k,v in laps.items()), reverse=True):
        print "  <tr>"
        print "    <td colspan=\"3\">", print_tag( epc ), "</td>"
        print "    <td>", str(mylaps), " kierrosta</td>"
        print "    <td colspan=\"", maxlaps-4, "\">Total: ", print_laptime( total[epc] )[:-3] , "</td>"
        print "  </tr>"
        print "  <tr>"
        for col in range(0,len(laptimes[epc])):
            if ( (col == len(laptimes[epc])-1 ) ):
                print "    <td class=\"laptime\" colspan=\"", maxlaps-col, "\">", print_laptime( laptimes[epc][col] )[:-3], "</td>"
            else: 
                print "    <td class=\"laptime\">", print_laptime( laptimes[epc][col] )[:-3], "</td>"
        print "  </tr>"
    print "</table>"
    print "<pre>"
else:
    print "Kierrosajat"
    # tama palauttaa laps-dictin sortattuna valueiden mukaan
    for mylaps, epc in sorted ( ((v,k) for k,v in laps.items()), reverse=True):
        times = laptimes[epc]
        if (debug):
            print ("Trying to print epc " + epc + " with laps=" + str(mylaps))
        print (print_tag(epc) + ": " + str(mylaps) + " kierrosta Total: " + print_laptime( total[epc] )[:-3])
        for col in range(0,len(laptimes[epc])):
            print "    ", print_laptime( laptimes[epc][col] )[:-3], "secs"

if (use_cgi):
    print '</pre>'
    print '</html>'
#print (type(parsed['tag_reads']))
#with open('log.txt') as f:
#    data = json.load(f)

#for msg in data:
