#!/usr/bin/python2.2
import cgi, os, atx, urllib
from xml.dom import minidom

def getText(d, element):
	nodelist = d.firstChild.getElementsByTagName(element)[0].childNodes
	rc = ""
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc = rc + node.data
	return rc

import cgitb; cgitb.enable()

f = cgi.FormContentDict()
meth = os.environ.get('REQUEST_METHOD')

page = atx.atx("""# Universal Trackback

OPENFORM

SENDURL

Title: <input type="text" name="title" />
URL: <input type="url" name="url" />
Source: <input type="text" name="blog_name" />
Excerpt: <textarea name="excerpt"></textarea>

<input type="submit" value="Send" />

CLOSEFORM
""").replace(
	'<p>OPENFORM</p>', '<form method="post" action="trackback">').replace(
	'<p>CLOSEFORM</p>', '</form>').replace(
	'&lt;', '<').replace('&gt;','>')


if meth == 'GET':
	# Just going to print stuff
	print "content-type: text/html"
	print

	if f.has_key('turl'):
		page = page.replace('<p>SENDURL</p>', '')
	else:
		page = page.replace('SENDURL', 'Trackback URL: <input type="text" name="turl" />')
	
	print page
elif meth == 'POST':
	turl = f['turl'][0].strip()
	del f['turl']

	sendf = {}
	for k in f.keys(): sendf[k] = f[k][0]

	u = urllib.urlopen(turl, urllib.urlencode(sendf))
	
	d = minidom.parseString(u.read())
	print 'content-type: text/html'
	print		   
	err = getText(d, 'error')
	if err == '1':
		msg = getText(d, 'message')
		print atx.atx('''# TrackBack failed

Sorry, it looks like something went wrong. The server reported an error, and said: "''' + msg + '".')

	else:
		print atx.atx("""# TrackBack sent successfully

Your trackback was sent to the server successfully.""")

