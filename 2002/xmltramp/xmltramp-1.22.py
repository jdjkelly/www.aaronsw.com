"""xmltramp: Make XML documents easily accessible."""

__version__ = "1.22"
__author__ = "Aaron Swartz"
__copyright__ = "(C) 2003 Aaron Swartz. GNU GPL 2"

class Element:
	def __init__(self, name, attrs=None, children=None):
		self._name = name
		self._attrs = attrs or {}
		self._dir = children or []
		self._text = ''
	
	def __repr__(self, recursive=0):
		name = "<"+self._name
		if self._attrs.keys():
			name += ' ' + ' '.join([key+'="'+self._attrs[key]+'"' 
			  for key in self._attrs.keys()])
		name += ">"
		
		if self._text.strip(): name += self._text
		
		if recursive:
			for element in self._dir:
				name += element.__repr__(1)
		
		if self._text.strip() or recursive: name += "</"+self._name+">"
		
		return name
	
	def __str__(self):
		return ' '.join(self._text.split())
	
	def __getattr__(self, attr):
		for item in self._dir:
			if item._name == attr: return item
		raise KeyError
	
	def __getitem__(self, item):
		if isinstance(item, type(0)): return self._dir[item]
		else: return self._attrs[item]
	

from xml.sax.handler import EntityResolver, DTDHandler, ContentHandler, ErrorHandler

class Seeder(EntityResolver, DTDHandler, ContentHandler, ErrorHandler):
	def __init__(self):
		self.stack = []
		ContentHandler.__init__(self)
	
	def startElement(self, name, attrs):
		self.stack.append(Element(name, attrs))
	
	def characters(self, ch):
		self.stack[-1]._text += ch
	
	def endElement(self, name):
		element = self.stack.pop()
		element._text = element._text.strip()
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
	assert d.tail['type'] == "long"

	d = parse('<bing>  <bang> <bong>center</bong> </bang>  </bing>')
	assert d._name == "bing"
	assert d._text == ''
	assert d.bang.bong._text == "center"
	assert str(d.bang.bong) == "center"
	
	d = parse('<a>\nbaz\nbiz\n</a>')
	d._text == "baz\nbiz"
	str(d) == "baz biz"

	# No guarantees of the this being true if an element 
	# contains both text and child elements or there's extra 
	# whitespace lying around:	
	doc = '<a top="1"><b middle="2"><c bottom="3">d</c></b></a>'
	parse(doc).__repr__(1) == doc
