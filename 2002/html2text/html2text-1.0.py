#!/usr/bin/python2.2
"""HTML2Text: Converts HTML to clean and readable plain text."""

__author__ = "Aaron Swartz, based on code by Aaron Swartz and Lars Pind"
__copyright__ = "(C) 2002 Aaron Swartz. GNU GPL 2"

import re, urlparse
re_ftag = re.compile(r'(/?)([^\s]+)(.*)', re.I|re.M|re.S)
re_href = re.compile(r'(href|src)\s*=\s*["\']([^"\']+)["\']', re.I|re.M|re.S)
re_href2 = re.compile(r'(href|src)\s*=\s*([^ ]+)', re.I|re.M|re.S)
re_title = re.compile(r'(title|alt)\s*=\s*["\']([^"\']+)["\']', re.I|re.M|re.S)
re_title2 = re.compile(r'(title|alt)\s*=\s*([^ ]+)', re.I|re.M|re.S)
re_comments = re.compile(r'<!--.*?-->', re.I|re.M|re.S)

def intEnt(m):
	m = int(m.groups(1)[0])
	return unichr(m).encode('utf-8')

def xEnt(m):
	m = int(m.groups(1)[0], 16)
	return unichr(m).encode('utf-8')

def expandEntities(text):
	text = text.replace("&lt;", "<")
	text = text.replace("&gt;", ">")
	text = text.replace("&quot;", '"')
	text = text.replace("&ob;", "{")
	text = text.replace("&cb;", "}")
	text = text.replace("&middot;", "*")
	text = re.sub("&[rl]squo;", "'", text)
	text = re.sub("&[rl]dquo;", '"', text)
	text = re.sub("&([aeiou])(grave|acute|circ|tilde|uml|ring);", lambda m: m.groups(1)[0], text)
	text = re.sub(r'&#(\d+);', intEnt, text)
	text = re.sub(r'&#[Xx](\w+);', xEnt, text)
	text = re.sub("&(#169|copy);", "(C)", text)
	text = re.sub("&mdash;", "--", text)
	return text

class _html2text:
	def __call__(self, html, basehref, maxlen=80, showtags=0, showlinks=1):
		self.text, self.line, self.maxlen  = '', '', maxlen
		self.pre, self.p, self.br, self.blockquote, self.space = 0, 0, 0, 0, 0
		last_tag_end = 0
		href_urls, href_stack = [], []
		
		# remove comments
		html = re.sub(re_comments, "", html)
		
		i = html.find('<')
		while i != -1:
			self.output(html[last_tag_end:i])
			# we're inside a tag, find the end
			# make i point to the char after the <
			tag_start = i + 1
			in_quote = 0
			for c in html[i:]:
				i += 1
				if c == ">" and not in_quote: break
				if c == '"' and not in_quote: in_quote = 1
				if c == '"' and in_quote: in_quote = 0
			i -= 1
			full_tag = html[tag_start:i]
			s = re.findall(re_ftag, full_tag)
			if s:
				s = s[0]
				slash, tagname, attributes = s[0], s[1], s[2]
				# valid tag
				t = tagname.lower()
				if t in ['p', 'ul', 'ol', 'table', 'div']:
					self.p = 1
				elif t == ["span", 'tbody']: pass
				elif t == 'br':
					self.text += self.line + '\n'
					self.line = "    " * self.blockquote
				elif t in ['tr', 'td', 'th']:
					self.br = 1
				elif t == "title":
					if slash:
						self.p = 1
					else:
						self.output("TITLE: ")
				elif re.match(r'h\d+', t):
					if not slash: self.p = 1
					out = "=" * int(t[1:])
					if slash:
						out = ' ' + out
					else:
						out += ' '
					self.output(out)
					del out
					if slash: self.p = 1
				elif t == 'li':
					self.br = 1
					if not slash:
						self.output(" -")
						self.line += ' '
				elif t in ['strong', 'b']:
					self.output('*')
				elif t in ['em', 'i', 'cite']:
					self.output('_')
				elif t == 'a' and showlinks:
					if not slash:
						href = re.findall(re_href, attributes) or re.findall(re_href2, attributes)
						title = re.findall(re_title, attributes) or re.findall(re_title2, attributes)
						if href:
							href = href[0][1].replace("\n", "").replace("\r", "")
							href_no = len(href_urls) + 1
							if title: 
								href_urls.append((href, expandEntities(title[0][1])))
							else:
								href_urls.append((href, ""))
							href_stack.append("["+`href_no`+"]")
						else:
							href_stack.append("")
					else:
						if len(href_stack) > 0: 
							if href_stack[-1]:
								self.output(href_stack[-1])
							href_stack.pop()
				elif t == 'pre':
					self.p = 1
					if not slash:
						self.pre += 1
					else:
						self.pre -= 1
				elif t == 'blockquote':
					self.p = 1
					if not slash:
						self.blockquote += 1
					else:
						self.blockquote -= 1
				elif t == "hr":
					self.p = 1
					self.output("-" * maxlen)
					self.p = 1
				elif t == "img":
					self.output("[IMG") 
					href = re.findall(re_href, attributes) or re.findall(re_href2, attributes)
					title = re.findall(re_title, attributes) or re.findall(re_title2, attributes)
					if href:
						href = urlparse.urljoin(basehref, href[0][1].replace("\n", "").replace("\r", ""))
						self.output(": " + href)
						if title: 
							self.output(" ("+ expandEntities(title[0][1]) + ")")
					self.output("]")
				else:
					if showtags:
						self.output("&lt;"+slash+tagname+attributes+"&gt;")
			# set end of last tag to the character following the >
			last_tag_end = i + 1
			i = html.find("<", i)
	
		# append everything after the last tag
		self.output(html[last_tag_end:])
		
		# close all pre tags
		self.pre, self.blockquote = 0, 0
		self.text += self.line + "\n"
		
		if showlinks:
			i = 0
			for u in href_urls:
				i += 1
				self.text += "\n[" + `i` + "]" + (' ' * (len(`len(href_urls)`) - len(`i`) + 1)) + \
				  urlparse.urljoin(basehref, u[0])
				if u[1]: 
					 self.text += "\n   " + (' ' * len(`len(href_urls)`)) + u[1]

		self.text = self.text.replace("&nbsp;", " ")
		self.text = self.text.replace("&amp;", "&")
		return self.text
			
	def output(self, text):
		text = expandEntities(text)
		if self.line == '' and text.isspace(): return
		
		# output the text:
		if self.pre <= 0:
			# we're not inside a PRE tag
			text = re.sub("\s+", " ", text)
			if text == ' ': self.space = 1; return
			if self.space and self.line != "    " * self.blockquote: self.line += " "; self.space = 0			
			i, l = 0, text.split(' ')
			self.dumpbuffer()
			for word in l:
				word = re.sub("&(nsbp|#160);", " ", word)
				if len(self.line) > 0:
					if len(self.line) + 1 + len(word) > self.maxlen:
						# the next word goes past our maxline, break here
						self.text += self.line + '\n'
						self.line = "    " * self.blockquote
				self.line = self.line + word
				if i != (len(l) - 1) and self.line != "    " * self.blockquote: self.line += " "
				i += 1
		else:
			self.text += self.line
			self.line = ''
			self.dumpbuffer()
			# we are inside a pre tag		
			if self.blockquote:
				# break up by lines and indent
				for line in text.split('\n')[:-1]:
					self.text += line + '\n' + ('    ' * self.blockquote)
				self.text += text.split('\n')[-1] # last line, don't add a line break
			else:
				self.text += text

	def dumpbuffer(self):
		if self.p or self.br:
			# we're going to add some newlines, so empty line buffer
			self.text += self.line
			
			if self.text != '': # not the first thing
				if self.p:
					self.text += "\n\n"
				elif self.br:
					self.text += "\n"
			self.line = "    " * self.blockquote
			self.p, self.br = 0, 0
			
html2text = _html2text()

if __name__ == "__main__":
	import cgitb; cgitb.enable()
	import sys, urllib, cgi
	if len(sys.argv) > 1:
		url = sys.argv[1]
	elif 'url' in cgi.FieldStorage().keys():
		import cgitb; cgitb.enable();
		url = cgi.FieldStorage()['url'].value
		print "Content-type: text/plain; charset=utf-8"
		print
	else: 
		print "Content-type: text/plain; charset=utf-8"
		print
		url = "http://www.aaronsw.com/"
	maxlen=80
	if 'maxlen' in cgi.FieldStorage().keys():
		maxlen=cgi.FieldStorage()['maxlen'].value
	print html2text(urllib.urlopen(url).read(), url, maxlen=maxlen).encode('utf-8')
