#!/usr/bin/python2.2
import re, cgitb, urllib, html
cgitb.enable()
zurl = "http://www.zooko.com/log"
doc = urllib.urlopen(zurl).read(10000)
reg = re.compile("<h3>(.*?)</h3>(.*?)<a name", re.S)
m = reg.findall(doc)

print "Content-type: application/xml"
print
print """
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:sy="http://purl.org/rss/1.0/modules/syndication/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns="http://purl.org/rss/1.0/">
<channel rdf:about="http://www.aaronsw.com/2002/zooko">
  <title>Zooko Log</title>
  <link>""" + zurl + """</link>
  <description>yummy current events, made fresh daily!</description>
  <language>en-US</language>
  <items><rdf:Seq>"""
for item in m:
	zuri = zurl + "#d" + item[0].split(" ")[0]
	print '    <rdf:li rdf:resource="' + zuri + '" />'
print """  </rdf:Seq></items>
</channel>"""

for item in m:
	zuri = zurl + "#d" + item[0].split(" ")[0]
	print '<item rdf:about="' + zuri + '">'
	print "  <title>" + html.strip(item[0]) + "</title>"
	print "  <description>" + html.escape(item[1]) + "</description>"
	print "</item>"
print "</rdf:RDF>"