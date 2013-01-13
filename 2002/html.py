"""HTML Tools: Making it easier to deal with HTML from Python.
based on code by Ka-Ping Yee <http://zesty.ca/>
cleaned up by Aaron Swartz <http://www.aaronsw.com/>
"""

import re

## Fun Tools

def plural(number, suffix='s'):
    return (number != 1) and suffix or ''

tagpat = re.compile(r'<[^>]*>')
def strip(text):
    return re.sub(tagpat, '', text).replace(
        '&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

def escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
def intEnt(m):
	m = int(m.groups(1)[0])
	if m > 128: return "&" + `m` + ";"
	else: return chr(m)

def xEnt(m):
	m = int(m.groups(1)[0], 16)
	if m > 128: return "&x" + m.groups(1) + ";"
	else: return chr(m)

def unescape(text):
	text = text.replace("&lt;", "<")
	text = text.replace("&gt;", ">")
	text = text.replace("&quot;", '"')
	text = text.replace("&ob;", "{")
	text = text.replace("&cb;", "}")
	text = text.replace("&middot;", "*")
	text = re.sub("&([aeiou])(grave|acute|circ|tilde|uml|ring);", lambda m: m.groups(1)[0], text)
	text = re.sub(r'&#(\d+);', intEnt, text)
	text = re.sub(r'&#[Xx](\w+);', xEnt, text)
	text = re.sub("&(#169|copy);", "(C)", text)
	text = re.sub("&(mdash|[xX]2014);", "--", text)
	return text

## HTML Builder
# Python complains if you use class as an attribute, workaround:
r = lambda x: {'c': 'class', 'klass':'class'}.get(x,x)

def _attrs(d): return ''.join([(' ' + r(k) + '="' + d[k] + '"') for k in d])

def _mktag(name, f='', m='', e=''): return lambda *stuff, **attrs: \
	f + '<'+name+_attrs(attrs)+'>' + m + flatten(stuff) + '</'+name+'>' + e
	
def _mkempty(name, f='', e=''): return lambda *stuff, **attrs: \
	f + '<'+name+_attrs(attrs)+' />' + e

def flatten(stuff):
    if type(stuff) in [list, tuple]: return ''.join(map(flatten, stuff))
    else: return str(stuff)

block = 'html head body table tr td address'.split()
cntnt = 'pre p div h1'.split()
attrb = 'title link'.split()
inner = 'a span b i strong em'.split()
empty = 'img br'.split()

for t in block: globals()[t] = _mktag(t, '', '\n', '\n')
for t in cntnt: globals()[t] = _mktag(t, '', '', '\n')
for t in attrb: globals()[t] = _mktag(t, '    ', '', '\n')
for t in inner: globals()[t] = _mktag(t)
for t in empty: globals()[t] = _mktag(t)

## TEST:
assert html(head(
	title("This is a page.")), 
	body(
		h1("This is a page.", c="fool"), 
		p("This ", em('is'), " a paragraph.")
	)
) == """<html>
<head>
    <title>This is a page.</title>
</head>
<body>
<h1 class="fool">This is a page.</h1>
<p>This <em>is</em> a paragraph.</p>
</body>
</html>
"""
