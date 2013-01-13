"""Python wrapper for Technorati's Web API."""

import xmltramp # http://www.aaronsw/2002/xmltramp/
import urllib

# LICENSE_KEY = "insert your license key here"

def cosmos(url, tipe, start=0, format="xml", version=None):
	"""Get incoming links (cosmos) for url."""
	args = {'url':url, 'type':tipe, 'start':start, 'format':format, 
	        'key':LICENSE_KEY}
	if version: args['version'] = version
	url = "http://api.technorati.com/cosmos?" + urllib.urlencode(args)
	return xmltramp.load(url)

def bloginfo(url, format="xml", version=None):
	"""Get information about a blog."""
	args = {'url':url, 'format':format, 'key':LICENSE_KEY }
	if version: args['version'] = version
	url = "http://api.technorati.com/bloginfo?" + urllib.urlencode(args)
	return xmltramp.load(url)

def outbound(url, format="xml", version=None):
	args = {'url':url, 'format':format, 'key':LICENSE_KEY }
	if version: args['version'] = version
	url = "http://api.technorati.com/outbound?" + urllib.urlencode(args)
	return xmltramp.load(url)

