"""TRAMP: Makes RDF look like Python data structures. Harmful to wood rats."""
__copyright__ = "(C) 2002 Aaron Swartz <http://www.aaronsw.com/>. GNU GPL 2."

from __future__ import generators # Upgrade to Python 2.2. It wears a tie.
import aaronrdf as rdf # http://www.aaronsw.com/2002/aaronrdf.py

class Thing:
	"""Takes an RDF object and makes it look like a dictionary."""
	def __init__(self, name, store): self.name, self.store = name, store
	
	def __getitem__(self, v):
		out = [thing(x, self.store)
				  for x in self.store.objects(self.name, v)]

		if len(out) == 1:
			if isinstance(out[0], rdf.Literal):
				return PsuedoLiteral(out[0], self, v)
			else:
				return out[0]
		else: return PsuedoList(out, self, v)
	
	def __setitem__(self, k, v):
		if isinstance(v, Thing): v = v.name
		for triple in self.store.triples((self.name, k, None)):
			self.store.remove((triple[0], triple[1], triple[2]))
					
		if not isinstance(v, list): v = [v]
		for val in v: 
			if not isinstance(val, rdf.URI) and isinstance(val, (unicode, str)):
				val = rdf.Literal(val)
			self.store.add((self.name, k, val))
	
	def __iter__(self):
		i = 1
		while rdf.rdf["_" + `i`] in self: 
			yield self[rdf.rdf["_" + `i`]]
			i += 1

	def __contains__(self, val): return not not self[val]

	def __repr__(self): return repr(self.name)
	def __str__(self): return str(self.name)

	def __eq__(self, other): 
		if isinstance(other, Thing): return self.name == other.name
		else: return self.name == other

def thing(x, store):
	if isinstance(x, rdf.URI): return Thing(x, store)
	if isinstance(x, Thing): return x
	if isinstance(x, (PsuedoLiteral, str, unicode)): return rdf.Literal(x)
	print "E: trying to thingify", x, "instance of", x.__class__
	raise "ThingificationError"

class PsuedoLiteral(unicode):
	def __new__(self, name, thing, item):
		self = unicode.__new__(self, name)
		self._thing, self._item = thing, item
		return self
		
	def append(self, x):
		self._thing[self._item] = [self, x]
		
class PsuedoList(list):
	def __init__(self, name, thing, item):
		self._thing, self._item = thing, item
		list.__init__(self, name)

	def append(self, x):
		self._thing[self._item] = self + [x]

if __name__ == "__main__":
	# Unit tests, baby!
	
	store = rdf.Store(); ex = rdf.Namespace("http://example.org/")
	Aaron = Thing(rdf.URI("http://me.aaronsw.com/"), store)
	Aaron == Thing(rdf.URI("http://me.aaronsw.com/"), store)
	
	Aaron[ex.name] = "Aaron Swartz"
	assert Aaron[ex.name] == "Aaron Swartz"
	Aaron[ex.homepage] = rdf.URI("http://www.aaronsw.com/")
	assert Aaron[ex.homepage] == rdf.URI("http://www.aaronsw.com/")
	
	Aaron[ex.machine] = ["vorpal", "slithy"]
	assert Aaron[ex.machine].sort() == ["vorpal", "slithy"].sort()
	# (we sort because order isn't necessarily preserved)
	Aaron[ex.machine] = ["vorpal"]
	# (this replaces old triples)
	assert Aaron[ex.machine] == "vorpal"
	# (if there's only one, it's returned as itself)
	Aaron[ex.machine].append("slithy")
	# (this adds a triple)
	assert Aaron[ex.machine].sort() == ["vorpal", "slithy"].sort()
	Aaron[ex.machine].append('tumtum')
	assert Aaron[ex.machine].sort() == ["vorpal", "slithy", "tumtum"].sort()
	
	# Lists are hard to make because you shouldn't be making them
	r = rdf.rdf
	f = Aaron[ex.topFiveFrobs] = Thing(ex.frobList9028292, store)
	f[r.type] = r.Seq
	f[r._1], f[r._2], f[r._3], f[r._4], f[r._5] = \
		"John", "Jacob", "Jingle", "Heimer", "Schmidt"
	# but since other people did, we still parse them
	n = 0; frobs = ["John", "Jacob", "Jingle", "Heimer", "Schmidt"]
	for frob in Aaron[ex.topFiveFrobs]:
		assert frob == frobs[n]
		n += 1
	assert n == 5
	
	# "pred in subj" == bool(subj[pred])
	assert ex.children not in Aaron
	# you probably don't need it since subj[pred] returns [], not error
	assert not Aaron[ex.children]

	assert str(Aaron) == "http://me.aaronsw.com/"
	assert str(Aaron[ex.name]) == "Aaron Swartz"
	
# Mark Nottingham's Sparta <http://www.mnot.net/sw/sparta/> inspired TRAMP.
# I am open to an LGPL license if you have a convincing reason.
