"""RDF FOAF Whitelist Generator
Takes a newline-separated list of email address on stdin and outputs an RDF
file."""

__license__ = "(C) 2002 Aaron Swartz. This is free software, share and enjoy."

import sys, sha

print """<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">"""

for l in sys.stdin:
            print '  <foaf:NonSpamMailboxURI foaf:sha1Value="' +sha.new('mailto:' + l[:-1]).hexdigest()  + '" />'

print '</rdf:RDF>'
            
