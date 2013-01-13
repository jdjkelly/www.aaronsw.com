#!/usr/bin/python2.2
import random, tramp, rdflib.TripleStore as rts, cgi
from namespaces import rss, rdf, Namespace
import cgitb; cgitb.enable()
x=cgi.FieldStorage()
if x.has_key("url"): url = x["url"].value
else: url = "http://swordfish.rdfweb.org/calendar/events/swevents.rss"

ev = Namespace("http://purl.org/rss/1.0/modules/event/")

store = rts.TripleStore()
store.load(url)
channel = tramp.Thing(list(store.triples(None, rdf.type, rss.channel))[0][0], store)
print "Content-type: text/plain"
print
print """BEGIN:VCALENDAR
VERSION
 :2.0
PRODID
 :PRODID:-//hacksw/rss2ical.py//NONSGML v1.0//EN"""

for item in channel[rss.items]:
    print "BEGIN:VEVENT\nUID\n :" + str(random.randint(1,100000))
    print "SUMMARY\n :" + item[rss.title]
    print "DTSTART\n :" + item[ev.startdate].replace("-", "")
    print "DTEND\b :" + item[ev.enddate].replace("-", "")
    print "END:VEVENT"

print "END:VCALENDAR"
