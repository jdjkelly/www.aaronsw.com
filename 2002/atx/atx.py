#!/usr/bin/python2.2
import re

### from ruby's mombo:

def escape(x): return x.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def sanitize(body):
	body=escape(body)

	# passthru <a href>, <em>, <i>, <b>, <blockquote>, <br/>, <p>
	body=re.sub('&lt;a href="([^"]*)"&gt;([^&]*)&lt;/a&gt;',
		    '<a href="\\1">\\2</a>', body)
	body=re.sub('&lt;a href=\'([^\']*)\'&gt;([^&]*)&lt;/a&gt;',
		    '<a href="\\1">\\2</a>', body)
	return body

def handle(x): 
	rd = (("``", '“'), ("''",'”'), ("`", '‘'), ("'", '\xe2\x80\x99'), ('---', '\xe2\x80\x93'), ('--', '\xe2\x80\x94'), (' \n',' '), ('\n','<br />\n'))
	      # @@ these two are sorta backwards, but huffman coded...
	      # @@ need some way to escape and ignore in <code>/<pre>
	for k,v in rd: x = x.replace(k, v)

	x = re.sub(r'\b_(.*?)_\b', r'<em>\1</em>', x)

	# @@ I have no idea why I have to use \B here and \b back there:
	x = re.sub(r'\B\*(.*?)\*\B', r'<strong>\1</strong>', x)
	x = re.sub(r'\B\|(.*?)\|\B', r'<code>\1</code>', x)

	return x

def atx(x, full=1):
	#x = sanitize(x)
	if x and x[-1] == "\n": x = x[:-1] # trim closing \n if exists

	paras = x.split('\n\n') #@@ requires all in memory
	nextp, title = None, ''
	for i in xrange(len(paras)): 
		p = paras[i]
		
		if p == '': continue # blank line

		elif p[0] == '$' or nextp == 'pre': # <pre>
			p = "<pre>"+p+"</pre>"
			nextp = None

		elif re.match(r'^\#+ ', p): # <h?>
			n=0
			while p[n] == '#': n+=1
			if n==1: title = p[n:].strip()
			p = "<h"+`n`+">"+handle(p[n:].strip())+"</h"+`n`+">"

		elif re.match(r'^ *(\*|\d+\.) ', p): # <ul>/<ol>
			#@@ should really do <li><p> for paragraphed lists
			if p.strip()[0] == '*': mode = 'ul'
			else: mode = 'ol'
			
			lines = p.split('\n')

			li = 0
			while li < len(lines):
				l = lines[li]
							
				if (mode == 'ul' and l[0] != '*' and l[:2] != ' *') or \
				   (mode == 'ol' and not re.match(r'^ *\d+\.', l)):
					del lines[li]
					lines[li-1] = lines[li-1] + l
				else:
					li += 1
					
			for li in xrange(len(lines)):
				l = lines[li].strip()

				if mode == 'ul' and l[0] == '*': l = l[1:]
				else: l = re.sub(r'^ *\d+\.', '', l)
				l = '  <li>'+handle(l.strip())+'</li>'

				lines[li] = l

			p = '<'+mode+'>\n'+'\n'.join(lines)+'\n</'+mode+'>'
			
		elif p[:3] == '   ': # <blockquote>
			p = "<blockquote>"+handle(p)+"</blockquote>"
			
		else: # <p>
			if p[-2:] == '::': nextp = "pre"; p = p[:-1]
			p = "<p>"+handle(p)+"</p>"
		
		paras[i] = p
		
	doc = '\n\n'.join(paras)
	if full: doc = """<html xmlns="http://www.w3.org/1999/xhtml"><head>
  <title>"""+title+"""</title>
  <link rel="stylesheet" type="text/css" href="/style.css" />
</head><body>

"""+'\n\n'.join(paras) + """

</body></html>"""
  
	return doc

if __name__ == "__main__":
	import sys
	if len(sys.argv) <= 1 or sys.argv[1] == "-": 
		print atx(sys.stdin.read()),
	else:
		print atx(open(sys.argv[1]).read()),
		

"""
TODO: smarter pants, generalized phrasals, prime characters (4'3", 80's)
"""
