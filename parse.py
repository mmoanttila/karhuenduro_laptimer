#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
from pprint import pprint
import urllib2
#from urllib import request
import unicodedata
from collections import defaultdict
from datetime import timedelta, datetime
from operator import itemgetter
import csv
import re
import os
import sys

# Some settings for code
startports = [1, 3]
endports = [2, 4]
log_url = "https://www.karhuenduro.fi/ajanotto/"
csv_url = "https://docs.google.com/spreadsheets/d/1dtqQQ6azJ5J0VBEHnnKLAkp3SlUK_6OzSk2RQivY6L0/export?format=csv&id=1dtqQQ6azJ5J0VBEHnnKLAkp3SlUK_6OzSk2RQivY6L0&gid=0"
tag_filter = "^0000...."
log_dir = "../web/ajanotto/"
output_dir = "../web/tulokset/"
output_file_name = ""

# End of settings

# Parameters:
#
# date esim. 2019-10-01
#   pvm, jonka lokia parsitaan (mm. tiedostonnimi)
# mode = <laptime|>
#   tapa jolla kierros- tai patka-ajat lasketaan:
#   laptime: yksi lukija kaytossa ja kierros lasketaan aina edelliseen leimaukseen verrattuna
#   laptime2: yhdella lukijalla, mutta ekakierros alkaa kellon mukaan (starttime)
#   stage: kaksi lukijaa ja kierrosaika lasketaan aina edelliseen ykkosleimaukseen verrattuna

# offset = 0 
#   montako kierrosta alusta jatetaan laskematta

# dict contains lists of timestamps indexed by epc
starttimes = defaultdict(list)
endtimes = defaultdict(list)
laptimes = defaultdict(list)
results = []
filter_tags = True
static_output = False

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
    print '  <title>Kierrosajat</title>'
    print '  <meta charset="UTF-8">'
    print '  <meta http-equiv="refresh" content="300">'
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
    current_time=datetime.now().strftime('%F %T')
    date = form.getvalue('date', '20190602')
    mode = form.getvalue('mode', 'laptime')
    numlaps = int(form.getvalue('laps', 0))
    offset = int(form.getvalue('offset', 0))

    if ( '-' in date ):
        date = date.replace("-","")
    myfilter = form.getvalue('bad', 'True')
    if ( myfilter == 'False' or myfilter == 'false' or myfilter == 0 ):
        filter_tags = False

    mydebug = form.getvalue('debug', 'False')
    if ( mydebug == 'True' or mydebug == 'true' or mydebug == 1 ):
        debug = True

    my_static_output = form.getvalue('static_output', 'False')
    if ( my_static_output  == 'True' or my_static_output == 'true' or my_static_output == 1 ):
        static_output = True
        # Only use output filename, when we need it
        defaultfilename = "tulokset-" + date + ".html"
        output_file_name = form.getvalue('output_file_name', defaultfilename)
        # Lets make sure we have correct ending.
        if (output_file_name[-5:] <> ".html" ):
            output_file_name=output_file_name + ".html"

    if (debug):
        print ("Kaytetty date: " + date)
        print ("Laskentatapa: " + mode)
        print ("Kierrosmaara: " + str(numlaps))
        print ("Lampparit: " + str(offset))
        if (static_output):
            print ("Tallennan lopulliset tulokset nimellä" + output_file_name)
        else:
            print ("En tallenna lopullisia tuloksia")

    race_start = int( time.mktime( time.strptime( date + " " + form.getvalue('start','10:00'), "%Y%m%d %H:%M")) ) * 1000000
    race_end = int( time.mktime( time.strptime( date + " " + form.getvalue('end','23:59'), "%Y%m%d %H:%M")) ) * 1000000
else:
    use_cgi = False
    from cgi import parse_qs
    date = os.getenv('date', '20190602')
    mode = os.getenv('mode', 'laptime')
    race_start = int( time.mktime( time.strptime( date + " " + os.getenv('start','10:00'), "%Y%m%d %H:%M")) ) * 1000000
    numlaps = int(os.getenv('laps', 0))
    offset = int(os.getenv('offset', 0))
    if (debug): 
        print ("Converting :" + date + " " + os.getenv('start','10:00') + " as %Y%m%d %H:%M")
        print ("Race start time: " + str(race_start))
        print ("Mode: " + mode)
        print ("Numlaps: " + str(numlaps))
        print ("Offset: " + str(offset))
    race_end = int( time.mktime( time.strptime( date + " " + os.getenv('end','23:59'), "%Y%m%d %H:%M")) ) * 1000000

#try:
#    if (debug):
#        print ("Generating url = " + log_url + date + ".txt")
#    url = log_url + date + ".txt"
#    contents = urllib2.urlopen( url )
#    if (debug):
#        print ("Logfile last modified :" + contents.headers['last-modified'] )
#except IOError:
#    print ("URLia ", url, " ei onnistuttu resolvoimaan!")
#    print ("Tai sitten osoite ei vaan vastaa!")

logfile = log_dir + date + ".txt"
if (debug):
    print ("parsing logfile = " + log_dir + date + ".txt")

if (os.path.exists(logfile)):
    contents = open (logfile, "r")
else:
    print ("Couldn't open logfile: " + logfile)
    try:
        if (debug):
            print ("Generating url = " + log_url + date + ".txt")
        url = log_url + date + ".txt"
        contents = urllib2.urlopen( url )
    except IOError:
        print ("Ei saatu avattu timestamppeja, lopetetaan")
        sys.exit(99)

if (debug):
    print (contents.info())

data = []
maxlaps = 0

def send_csvfile (data, filename="tulokset.csv"):
    if (debug):
        print ("Trying to return csv-file to browser as " + filename )
    # First suitable headers
    print ("Content-Type:text/csv; name=\"" + filename + "\"\r\n")
    print ("Content-Disposition: attachment; filename=\"" + filename + "\"\r\n\n")

def print_laptime (usec):
    if (debug):
        td = timedelta( milliseconds=usec/1000 )
        secs,msecs = int(td.total_seconds()),td.total_seconds()-int(td.total_seconds())
        print "Converting", usec, "usec to ", round( td.total_seconds(),1) , "secs."
        print "Also secs=", secs, "msecs=", msecs
    return str( timedelta( milliseconds=usec//1000 ) )

def read_tags (tagfile):
    # only use local-cache, if it's newer than one hour
    if ( not os.path.exists (tagfile ) or time.time() - os.path.getmtime (tagfile) > 3600 ):
        try:
            if (debug):
                print ("Trying to read .csv from " + csv_url )
            csvfile = urllib2.urlopen( csv_url )
        # if (debug):
        #     print ("CSV last modified :" + csvfile.headers['last-modified'] )

        except IOError:
            print ("URLia ", csv_url, " ei onnistuttu resolvoimaan!")
            print ("Tai sitten osoite ei vaan vastaa!")
            if (os.path.exists(tagfile)):
                print ("Kaytetaan paikallista kopioita: " , tagfile)
                csvfile = open(tagfile, "r")
        if (debug): 
            print ("Updating local tags.csv cache")
        with open(tagfile, 'wb') as csvcache:
            csvwriter = csv.writer(csvcache, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            csvreader = csv.reader( csvfile, delimiter=',' )
            for row in csvreader:
                csvwriter.writerow(row)
    if (debug):
        print ("Using local tag-csv-cache: " + tagfile)
    csvfile = open(tagfile, "r")
    my_tags ={}
    # with open( tagfile ) as csvfile:
    if (debug):
        print ("Parsin tagilistaa CSV:sta")
    csvreader = csv.reader( csvfile, delimiter=',' )
    for row in csvreader:
        if (debug):
            print "Luin tagin: " + row[2] + " = " + row[1]
        my_tags[row[2]] = row[1] + " | " + row[0]
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

def double_print (FO, line):
    print (line)
    if ( FO ):
        FO.write (line + "\n")

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
        if (debug):
            print ("Rivilta: ", line, "\n")
            print ("ei onnistuttu parsimaan json:ia.")

    # We might have several tagreads per line
    # That's why we loop
    for read in parsed['tag_reads']:
        if (debug):
            print ("Parsin leimausta:ta: ", read)
        # Skip heartbeats
        if (read['isHeartBeat']):
            if (debug):
                print ("Skippaan HeartBeatin.")
            continue
        epc = unicodedata.normalize('NFKD', read['epc']).encode('ascii','ignore')
        allowed_tag = re.search(tag_filter, epc)
        if (not allowed_tag and filter_tags):
            if (debug):
                print (epc, " ei ole meidan tagi.")
            continue
        if (debug):
            print ("Loysin EPC:n ", epc)
            print ("Testaan onko ", read['antennaPort'], " in ", startports)
            print ("  ja onko ", read['firstSeenTimestamp'], "(", time_to_localtime_debug(read['firstSeenTimestamp']), ") >", race_start, " (", time_to_localtime_debug(race_start), ")" )
            print ("  ja onko ", read['firstSeenTimestamp'], "(", time_to_localtime_debug(read['firstSeenTimestamp']), ") <", race_end, " (", time_to_localtime_debug(race_end), ")" )
        if (read['antennaPort'] in startports and read['firstSeenTimestamp'] > race_start and read['firstSeenTimestamp'] < race_end):
            # If starting with starttime (mode=laptime2), we should add one timestamp for that
            if ( mode == 'laptime2' and len (starttimes[epc]) == 0 ):
                if (debug):
                    print ("Lisataan lahtoleima := start_time ", time_to_localtime_debug(race_start) )
                starttimes[epc].append(race_start)

            if (debug):
                print ("Lahto: ", epc, " ", time_to_localtime(read['firstSeenTimestamp']) )
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
            try:
                if (debug):
                    print ("Laptime for ", epc, " : ", (read['firstSeenTimestamp'] - starttimes[epc][-1])/1000000, " secs") 
                laptimes[epc].append(read['firstSeenTimestamp']-starttimes[epc].pop() )
            except IndexError:
                if (debug):
                    print ("Loytyi ylimaarainen maalileimaus: ", time_to_localtime(read['firstSeenTimestamp']) )
                continue
            if (len (laptimes[epc])) > maxlaps:
                maxlaps += 1
        else:
            if (debug):
                print ("Ei huomioitavaa rivilla")

# Yritetaan laskea vahan statistiikkaa tuloksista.
for epc, times in laptimes.iteritems():
    # Jos patka-ajat ja number of laps given
    if (numlaps <> 0 and len(times) > numlaps+offset):
        if (debug):
            print ("Tagilla " + epc + " on ylimaaraisia kierroksia " + str(len(times)) )
        results.append ( (epc, numlaps, sum(times[offset:(numlaps+offset)]) ) ) # Vain ekat numlaps kierrosta vaikuttavat tuloksiin
    elif ( (len(times) - offset) < 1 ):
        if (debug):
            print ("Tagilla " + epc + " on pelkka lammittelykierros.")
        results.append ( (epc, 0, sum(times[offset:]) ) ) # List of tuples (epc, laps, total)
    else:
        results.append ( (epc, len(times)-offset, sum(times[offset:]) ) ) # List of tuples (epc, laps, total)
    if (debug):
        print (epc + ": laps=" + str(len (times)-offset) + " total=" + str(sum(times)) )

# results =: list of:
#   epc, no_laps, kokonaisaika

# Kaksi-vaiheinen sorttaus
s = sorted (results, key=itemgetter(2)) # sort on secondary key
results_sorted = sorted (s, key=itemgetter(1), reverse=True) # Sort on primary key descending

if (debug):
    print ("Sorttauksen tulokset:")
    pprint (results_sorted)
    print "Ajettu", maxlaps, "kierrosta."

if (use_cgi):
    print "</pre>"
    if (static_output):
        try: 
            FH = open (output_dir + output_file_name, "w")
            FH.write("<html><head>\n<title>Tulokset " + date + "</title>\n<meta charset=\"UTF-8\">\n</head>\n<body>\n")
            FH.write("<!-- tulokset.py&date=" + date + "&start=" + time.strftime( '%H:%M', time.localtime(race_start/1000000)) + "&mode=" + mode + "&laps=" + str(numlaps) + "&offset=" + str(offset) + "-->")
        except IOError:
            FH = False
    else:
        FH = False
    double_print (FH,"<!-- " + os.environ['REQUEST_URI'] + " -->\n")
    double_print (FH, "<h2>Tulokset " + date[6:8] + "." + date[4:6] + "." + date[0:4] + "</h2>")
    double_print (FH, "<h4>" + output_file_name + "</h4>")
    double_print (FH, "<table border=\"1\">")
    my_number=1
    for epc, mylaps, mytotal in results_sorted:
        double_print (FH, "  <tr>")
        double_print (FH, "    <td colspan=\"3\">" + str(my_number) + ". " + print_tag( epc ) + "</td>")
        double_print (FH, "    <td>" + str(mylaps) + " kierrosta</td>")
        double_print (FH, "    <td colspan=\"" + str(maxlaps-4) + "\">Total: " + print_laptime( mytotal )[:-3] + "</td>")
        double_print (FH, "  </tr>")
        double_print (FH, "  <tr>")
        my_number=my_number+1
        for col in range(offset,len(laptimes[epc])):
            if ( (col == len(laptimes[epc])-1 ) ):
                double_print (FH, "    <td class=\"laptime\" colspan=\"" + str(maxlaps-col) + "\">" + print_laptime( laptimes[epc][col] )[:-3] + "</td>")
            else: 
                double_print (FH, "    <td class=\"laptime\">" + print_laptime( laptimes[epc][col] )[:-3] + "</td>")
        double_print (FH, "  </tr>")
    double_print (FH, "</table>")
else:
    print "Kierrosajat"
    my_number=1
    for epc, mylaps, mytotal in results_sorted:
        #times = laptimes[epc]
        if (debug):
            print ("Trying to print epc " + epc + " with laps=" + str(mylaps))
        print (str(my_number) + ". ")
        my_number=my_number+1
        print (print_tag(epc) + ": " + str(mylaps) + " kierrosta Total: " + print_laptime( mytotal )[:-3])
        for col in range(offset,len(laptimes[epc])):
            print "    ", print_laptime( laptimes[epc][col] )[:-3], "secs"
    
if (use_cgi):
    if ( static_output == True ):
        print ("<br>\n<hr>\n<a href=\"/tulokset/" + output_file_name + "\">Valmiit tulokset</a>")
    double_print (FH, "<P><I>Last updated: " + current_time + "</I></P>")
    double_print (FH, "</html>")
    if (FH):
        FH.close()
#print (type(parsed['tag_reads']))
#with open('log.txt') as f:
#    data = json.load(f)

#for msg in data:
