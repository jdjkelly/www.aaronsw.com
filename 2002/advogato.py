#!/usr/bin/python2.2
import re, cgitb, urllib, html, sys, cgi
cgitb.enable()
person = cgi.FieldStorage()['person'].value
zurl = "http://www.advogato.org/person/" + person + "/diary.html"
doc = urllib.urlopen(zurl).read()
reg = re.compile('<p> <a name="(\d+)"><b>([^<]+)</b></a>.*?<blockquote>(.*?)</blockquote>', re.S)
reg2 = re.compile('<p> <a name="(\d+)"><b>([^<]+)</b></a>(.*?)<blockquote>', re.S)
try: 
 	m = reg.findall(doc)
except:
	m = reg2.findall(doc)

print "Content-type: application/xml"
print

print """
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:sy="http://purl.org/rss/1.0/modules/syndication/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns="http://purl.org/rss/1.0/">
<channel rdf:about="http://www.aaronsw.com/2002/zooko">
  <title>""" + person + """'s Advogato Diary</title>
  <link>""" + zurl + """</link>
  <language>en-US</language>
  <items><rdf:Seq>"""
for item in m:
	zuri = zurl + "?start=" + item[0]
	print '    <rdf:li rdf:resource="' + zuri + '" />'
print """  </rdf:Seq></items>
</channel>"""

for item in m:
	zuri = zurl + "?start=" + item[0]
	print '<item rdf:about="' + zuri + '">'
	print "  <link>"+zuri+"</link>"
	print "  <title>" + html.strip(item[1]) + "</title>"
	print "  <description>" + html.escape(item[2]) + "</description>"
	print "</item>"
print "</rdf:RDF>"