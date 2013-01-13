#!/usr/bin/python2.2
import re, cgitb, urllib, html
cgitb.enable()
zurl = "http://vitanuova.loyalty.org/latest.html"
doc = urllib.urlopen(zurl).read()

print "Content-type: application/xml"
print
print """
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:sy="http://purl.org/rss/1.0/modules/syndication/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns="http://purl.org/rss/1.0/">
<channel rdf:about="http://www.aaronsw.com/2002/vitanuova">
  <title>Vitanuova</title>
  <link>""" + zurl + """</link>
  <language>en-US</language>
  <items><rdf:Seq>
    <rdf:li rdf:about="http://vitanuova.loyalty.org/latest.html" />
  </rdf:Seq></items>
</channel>

<item rdf:about="http://vitanuova.loyalty.org/latest.html">
  <description>""" + html.escape(doc) + """</description>
</item>
</rdf:RDF>"""