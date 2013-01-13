#!/usr/bin/python2.2
"""
Googler: All the Googles at your fingertips.

For IE5/Mac Users: http://www.macslash.com/articles/01/10/10/1828238.shtml
Implementation by: Aaron Swartz <http://www.aaronsw.com/>
"""

__license__ = "(C) 2002 Aaron Swartz. This is free software."

mapping = { 
	'mid':'http://groups.google.com/groups?selm=',
	'catalogs:':'http://catalogs.google.com/catalogs?q=',
	'news:':'http://news.google.com/news?q=',
	'groups:':'http://groups.google.com/groups?q=',
	'directory:':'http://www.google.com/search?q=',
	'images:':'http://images.google.com/images?q=',
	'?':'http://www.google.com/search?btnI=1&q=',
	'':"http://www.google.com/search?q="
}
prefixes = mapping.keys(); prefixes.sort(lambda x,y: cmp(len(y), len(x)))

def go(q):
	for p in prefixes:
		l = len(p)
		if q[:l] == p: return mapping[p] + q[l:]

if __name__ == '__main__':
	import cgi, cgitb
	cgitb.enable()
	c = cgi.FieldStorage()
	q = c['q'].value
	r = go(q)
	print 'Status: 302 Helpful Redirect'
	print 'Content-Type: text/html'
	print 'Location: ' + r
	print
	print 'Wherever you go <a href="'+ r +'">there you are</a>.'
	
