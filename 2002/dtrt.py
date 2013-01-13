#!/usr/bin/python2.2
"""
ADTRT: Aaron's Do The Right Thing
A CGI script to get you where you want to go.

For IE5/Mac Users: http://www.macslash.com/articles/01/10/10/1828238.shtml
Your Magic String: http://www.aaronsw.com/2002/dtrt.cgi?secret=one&q=%s
Concept by Gerald: http://impressive.net/services/dtrt/
Implementation by: Aaron Swartz <http://www.aaronsw.com/>
Special Thanks To: HTTP GET, and those who build services with it
"""

__license__ = "(C) 2002 Aaron Swartz. This is free software."

mapping = { 
	'amazon:': 'http://www.amazon.com/exec/obidos/external-search?keyword=', 
	'define:': 'http://dictionary.com/cgi-bin/dict.pl?term=',
	'd:': 'http://dictionary.com/cgi-bin/dict.pl?term=',
	'display:': 'http://www.aaronsw.com/2002/display.cgi?t=',
	'dtrt:': 'http://impressive.net/services/dtrt/dtrt?',
	'mid:':'http://www.aaronsw.com/2002/mid.cgi?q=',
	'pgp:':'http://pgp.dtype.org:11371/pks/lookup?op=vindex&search=',
	'gpg:':'http://search.keyserver.net:11371/pks/lookup?op=vindex&search=',
	'ag:':'http://audiogalaxy.com/list/searches.php?searchStr=',
	'archive:':'http://web.archive.org/web/',
	'validate:':'http://validator.w3.org/check?uri=',
	'v:':'http://validator.w3.org/check?uri=',
	'p:':'http://plexnames.com/uri?plexname=',
	'catalogs:':'http://catalogs.google.com/catalogs?q=',
	'news:':'http://news.google.com/news?q=',
	'groups:':'http://groups.google.com/groups?q=',
	'directory:':'http://www.google.com/search?q=',
	'images:':'http://images.google.com/images?q=',
	'?':'http://www.google.com/search?btnI=1&q=',
	'':"http://www.google.com/search?q="
}
prefixes = mapping.keys(); prefixes.sort(lambda x,y: cmp(len(y), len(x)))

def dtrt(q):
	for p in prefixes:
		l = len(p)
		if q[:l] == p: return mapping[p] + q[l:]

if __name__ == '__main__':
	import cgi, cgitb
	cgitb.enable()
	c = cgi.FieldStorage()
	if 'q' not in c.keys():
		r = 'http://www.aaronsw.com/2002/dtrt'
	else:
		q = c['q'].value
		r = dtrt(q)
	print 'Status: 302 Helpful Redirect'
	print 'Content-Type: text/html'
	print 'Location: ' + r
	print
	print 'Wherever you go <a href="'+ r +'">there you are</a>.'
	
