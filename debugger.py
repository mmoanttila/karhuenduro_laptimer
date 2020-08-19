#! /usr/bin/env python
# -*- coding: utf-8
"""Loki parseri

parameters:
    date = minkä päivän lokia ihmetellään (oletus tämänpäiväinen)
    tagfilter = regex, jonka pitää matchata epc:en, jotta se näytetään (oletus BAD0....)
"""
import cgi, cgitb
import csv
import os, sys
from datetime import timedelta, datetime
from pprint import pprint
import json
import time
import re
import fnmatch
import unicodedata

log_dir = "../web/ajanotto/"
tagfile = "tags.csv"

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
    print '<table style="width:400px">'
    print "  <tr>"
    print "    <th style=\"width:20px;\">Port</th>"
    print "    <th>EPC</th>"
    print "    <th style=\"width:100px;\">Time</th>"
    print "    <th style=\"width:30px;\">Rssi</th>"
    print "  </tr>"

def table_row(entry):
    print ("  <tr>")
    print ("    <td>" + str(entry['antennaPort']) + "</td>")
    print ("    <td>" + entry['tag'] + "</td>")
    print ("    <td>" + str(entry['localtime']) + "</td>")
    print ("    <td>" + str(entry['peakRssi']) + "</td>")
    print ("  </tr>")

def table_stop():
    print ("</table")

def print_html_table(data):
    table_start()
    for row in data:
        table_row(row)
    table_stop
 
# {u'antennaPort': 2,
#   u'epc': u'BAD00058',
#   u'firstSeenTimestamp': 1584178803057737,
#   u'isHeartBeat': False,
#   u'peakRssi': -71
# }
def time_to_localtime (utime):
    return (time.strftime( '%H:%M:%S', time.localtime(utime/1000000)))

def read_tags():
    my_tags = {}
    with open( tagfile, "r" ) as csvfile:
        csvreader = csv.reader( csvfile, delimiter=',' )
        for row in csvreader:
            my_tags[row[2]] = row[1] 
    return my_tags

def print_tag (tag):
    if tags.has_key (tag):
        return tags[tag]
    else:
        return tag

# This should return 10 latest logfiles as a list
def read_logs():
	files = fnmatch.filter(os.listdir(log_dir),"????????.txt")
	files.sort(reverse=True)
	return files[:10]

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
        allowed_tag = re.search(tagfilter, entry['epc'])
        # Use tagfilter form-parameter
        if (not allowed_tag):
            if (debug):
                print ("Tagi ei matchaa filtteriin: ", tagfilter)
            continue
        entry['epc'] = unicodedata.normalize('NFKD', entry['epc']).encode('ascii','ignore')
        entry['tag'] = print_tag(entry['epc'])
        entry['localtime'] = time_to_localtime (entry['firstSeenTimestamp'])
        entry['id'] = len (reads)
        if (debug):
            print ("Löysin leimauksen :")
            pprint (entry)
        reads.append(entry)

def print_line(line):
    pprint (line)

def write_csv (data):
    with open("debug.csv", "wb") as debug:
        csvwriter = csv.writer(debug, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for line in data:
            row = line['id'], line['tag'], line['localtime'], line['antennaPort']
            csvwriter.writerow(row)

# check for debug cmd parameter
if ( len(sys.argv) > 1 and '-d' in sys.argv ):
    print "Debugging Enabled!"
    debug = True
else:
    debug = False

#cgitb.enable()
form = cgi.FieldStorage()

# Let's use current date if not given on url
current_date=datetime.now().strftime('%Y%m%d')
date = form.getvalue('date', current_date)
tagfilter = form.getvalue('tagfilter', "^BAD0....")
#date = os.getenv('date', current_date)
logfile = log_dir + date + '.txt'

if (debug):
   print ("Trying to open: ", logfile)

if (os.path.exists(logfile)):
    if (debug):
        print ("Loysin logfilen: ", logfile)
    tags = read_tags()
    with open(logfile, 'r') as contents:
        for line in contents:
            parse_line(line)
    #write_csv(reads)
    html_header()
    print_html_table(reads)
    html_footer()
    #    print (json.dumps(reads)) 

