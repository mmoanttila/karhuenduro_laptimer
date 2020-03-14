#! /usr/bin/env python
"""CGI-script for editing csv-file

parameters:
    filename = editoitavan tiedoston nimi
"""
import cgi, cgitb
import csv
import os, sys

def html_header():
    print "Content-type: text/html"
    print
    print "<html>"
    print "<head>"
    print "  <title>CSV-editor</title>"
    print "  <meta charset="UTF-8">"
    print "</head>"
    print "<style>"
    print "  table {border-collapse: collapse;}"
    print "  tr:nth-child(odd) {background-color: #f2f2f2;}"
    print "  td.laptime { padding: 5px; }"
    print "</style>"
    print "<body><pre>"
 
cgitb.enable()
form = cgi.FieldStorage()
filename = form.getvalue('filename', 'tags.csv')

with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        print row


