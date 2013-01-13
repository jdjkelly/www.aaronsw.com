"""xmltramp: Make XML documents easily accessible."""

__version__ = "1.1"
__author__ = "Aaron Swartz"
__copyright__ = "(C) 2003 Aaron Swartz. GNU GPL 2"

def clean(text):
	"""Remove redundant whitespace from a string."""
   	text = ' '.join(text.split())
   	if text.isspace(): text = ''
   	return text

class Element:
	def __init__(self, name, attrs=None, children=None):
		self._name = name
		self._attrs = attrs or {}
		self._dir = children or []
		self._text = ''
	
	def __repr__(self):
		name = "<"+self._name
		if self._attrs.keys():
			name += ' ' + ' '.join([key+'="'+self._attrs[key]+'"' 
			  for key in self._attrs.keys()])
		name += ">"
		if clean(self._text):
			name += self._text
			name += "</"+self._name+">"
		return name
	
	def __str__(self):
		return self._text
	
	def __getattr__(self, attr):
		for item in self._dir:
			if item._name == attr: return item
		raise KeyError
	
	def __getitem__(self, item):
		return self._dir[item]

from xml.sax import saxutils

class Seeder(saxutils.DefaultHandler):
	def __init__(self):
		self.stack = []
		saxutils.DefaultHandler.__init__(self)
		
	def startElement(self, name, attrs):
		self.stack.append(Element(name, attrs))
	
	def characters(self, ch):
		self.stack[-1]._text += ch
	
	def endElement(self, name):
		element = self.stack.pop()
		element._text = clean(element._text)
		if self.stack:
			self.stack[-1]._dir.append(element)
		else:
			self.result = element

from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

def seed(fileobj):
	seeder = Seeder()
	parser = make_parser()
	parser.setFeature(feature_namespaces, 0)
	parser.setContentHandler(seeder)
	parser.parse(fileobj)
	return seeder.result

def parse(text):
	from StringIO import StringIO
	return seed(StringIO(text))

def load(url): 
	import urllib
	return seed(urllib.urlopen(url))

if __name__ == "__main__":
	d = Element("monkey")
	assert repr(d) == "<monkey>"
	d._dir = [Element("head"), Element("body"), Element("tail", {'type':'long'})]
	assert repr(d[1]) == "<body>"
	assert repr(d.tail) == '<tail type="long">'

	d = parse('<bing>  <bang> <bong>center</bong> </bang>  </bing>')
	assert d._name == "bing"
	assert d._text == ''
	assert d.bang.bong._text == "center"
	assert str(d.bang.bong) == "center"
	
