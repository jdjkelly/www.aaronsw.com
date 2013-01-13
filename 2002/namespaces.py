"""Namespaces: Useful RDF namespaces in an easy-to-access form."""

from rdflib.URIRef import URIRef # get from http://rdflib.net/

class Namespace:
	"""A class so namespaced URIs can be abbreviated (like dc.subject).
	label provides the abbreviation that should be used on output)"""
	
	def __init__(self, prefix, label=''): 
		self.prefix = prefix; self.label = label
	def __getattr__(self, name): return URIRef(self.prefix + name)
	def __getitem__(self, name): return URIRef(self.prefix + name)
        
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'rdf')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#', 'rdfs')
rss = Namespace('http://purl.org/rss/1.0/', 'rss')
daml = Namespace('http://www.daml.org/2001/03/daml+oil#', 'daml')
log = Namespace('http://www.w3.org/2000/10/swap/log#', 'log')
dc = Namespace('http://purl.org/dc/elements/1.1/', 'dc')
foaf = Namespace('http://xmlns.com/foaf/0.1/', 'foaf')
doc = Namespace('http://www.w3.org/2000/10/swap/pim/doc#', 'doc')
cc = Namespace('http://web.resource.org/cc/', 'cc')
ex = Namespace('http://example.org/ns/', 'ex')
