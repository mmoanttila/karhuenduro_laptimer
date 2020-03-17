#! /usr/bin/env python
# -*- coding: utf-8
"""Loki parseri

parameters:
    date = minkä päivän lokia ihmetellään (oletus tämänpäiväinen)
"""
import cgi, cgitb
import csv
import os, sys
from datetime import timedelta, datetime
from pprint import pprint
import json
import time
import unicodedata

log_dir = "../web/ajanotto/"
# This will contain all read timestamps
reads = list()

def html_header():
    print "Content-type: text/html"
    print
    print "<html>"
    print "<head>"
    print "  <title>Loki-editori</title>"
    print '  <meta charset="UTF-8">'
    print "</head>"
    print "<style>"
    print "  table {border-collapse: collapse;}"
    print "  tr:nth-child(odd) {background-color: #f2f2f2;}"
    print "  td.laptime { padding: 5px; }"
    print "</style>"
    print "<body>"
 
def html_footer():
    print "</body>"
    print "</html>"

def table_start():
    print '<table style="width:100%">'
    print "  <tr>"
    print "    <th>Port</th>"
    print "    <th>EPC</th>"
    print "    <th>Time</th>"
    print "    <th>Rssi</th>"
    print "  </tr>"

def table_row(entry):
    print ("  <tr>")
    print ("    <td>" + entry['antennaPort'] + "</td>")
    print ("    <td>" + entry['epc'] + "</td>")
    print ("    <td>" + entry['firstSeenTimestamp'] + "</td>")
    print ("    <td>" + entry['peakRssi'] + "</td>")
    print ("  </tr>")

def table_end():
    print ("</table")

# {u'antennaPort': 2,
#   u'epc': u'BAD00058',
#   u'firstSeenTimestamp': 1584178803057737,
#   u'isHeartBeat': False,
#   u'peakRssi': -71
# }
def time_to_localtime (utime):
    return (time.strftime( '%H:%M:%S', time.localtime(utime/1000000)))

def parse_line(line):
    # First let's skip logfile timestamp
    jsonline=line.split(",",2)
    # Let's read json content to list of dicts
    try:
        parsed=json.loads(jsonline[2])
        if (debug):
            print ("Löysin json:ia riviltä:", parsed)
    except ValueError:
        if (debug):
            print ("Riviltä: ", line, "\n")
            print ("ei onnistuttu parsimaan json:ia.")
    # We might have several tagreads per line
    # That's why we loop
    for entry in parsed['tag_reads']:
        if (debug):
            print ("Parsin leimausta:ta: ", entry)
        # Skip heartbeats
        if (entry['isHeartBeat']):
            if (debug):
                print ("Skippaan HeartBeatin.")
            continue
        entry['epc'] = unicodedata.normalize('NFKD', entry['epc']).encode('ascii','ignore')
        entry['firstSeenTimestamp'] = time_to_localtime (entry['firstSeenTimestamp'])
        entry['id'] = len (reads)
        if (debug):
            print ("Löysin leimauksen :")
            pprint (entry)
        reads.append(entry)

def print_line(line):
    pprint (line)

# check for debug cmd parameter
if ( len(sys.argv) > 1 and '-d' in sys.argv ):
    print "Debugging Enabled!"
    debug = True
else:
    debug = False

#cgitb.enable()
#form = cgi.FieldStorage()

# Let's use current date if not given on url
current_date=datetime.now().strftime('+%Y%m%d')
#date = form.getvalue('date', current_date)
date = os.getenv('date', current_date)
logfile = log_dir + date + '.txt'

if (debug):
   print ("Trying to open: ", logfile)

if (os.path.exists(logfile)):
    if (debug):
        print ("Loysin logfilen: ", logfile)
    with open(logfile, 'r') as contents:
        for line in contents:
            parse_line(line)

