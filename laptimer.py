#! /usr/bin/env python
# -*- coding: utf-8 -*-

def send_csvfile (data, filename="tulokset.csv"):
    """Will send csv-file to browser. (Currently not used) """
    if (debug):
        print ("Trying to return csv-file to browser as " + filename )
    # First suitable headers
    print ("Content-Type:text/csv; name=\"" + filename + "\"\r\n")
    print ("Content-Disposition: attachment; filename=\"" + filename + "\"\r\n\n")

def print_laptime (usec):
    """ Will convert usec's to seconds as float """
    if (debug):
        td = timedelta( milliseconds=usec/1000 )
        secs,msecs = int(td.total_seconds()),td.total_seconds()-int(td.total_seconds())
        print "Converting", usec, "usec to ", round( td.total_seconds(),1) , "secs."
        print "Also secs=", secs, "msecs=", msecs
    return str( timedelta( milliseconds=usec//1000 ) )

def print_tag (tag):
    """ Returns name associated with tag if it exists, else returns tag back """
    if tags.has_key (tag):
        return tags[tag]
    else:
        return tag

def time_to_localtime (utime):
    """ Converts msec's since EPOCH time to current time """
    return (time.strftime( '%H:%M:%S', time.localtime(utime/1000000)))

def time_to_localdate (utime):
    """ Converts msec's since EPOCH time to current date & time """
    return (time.strftime( '%F %H:%M:%S', time.localtime(utime/1000000)))

def double_print (FO, line):
    """ Print line to stdout as well as to file """
    print (line)
    if ( FO ):
        FO.write (line + "\n")

