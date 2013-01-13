#!/usr/bin/python2.2
"""HTML Diff
Rough code, badly documented. Please send me comments: me@aaronsw.com."""

import difflib, string, cgitb
cgitb.enable()

class SM (difflib.SequenceMatcher):
	def __helper(self, alo, ahi, blo, bhi, answer):
		# slightly modified from difflib to ignore blocks of one elt
		# this prevents weird ones like <del>Whe</><ins>Ocasio</>n<ins>ally</>
		i, j, k = x = self.find_longest_match(alo, ahi, blo, bhi)
		# a[alo:i] vs b[blo:j] unknown
		# a[i:i+k] same as b[j:j+k]
		# a[i+k:ahi] vs b[j+k:bhi] unknown
		if k:
			if alo < i and blo < j:
				self.__helper(alo, i, blo, j, answer)
			if k > 1: answer.append(x)
			if i+k < ahi and j+k < bhi:
				self.__helper(i+k, ahi, j+k, bhi, answer)

	_SequenceMatcher__helper = _SM__helper # python name mangling funniness

def isTag(x): return x[0] == "<" and x[-1] == ">"

def stringDiff(a, b):
	"""@@@"""
	out = ''
	chars = 0
	a, b = ' '.join(html2list(a)), ' '.join(html2list(b))
	s = SM(None, a, b)
	a = ' '.join(html2list(a, b=1))
	for e in s.get_opcodes():
		if e[0] == "replace":
			out += "<del>" + a[e[1]:e[2]] + "</del>"
			out += "<ins>" + b[e[3]:e[4]] + "</ins>"
		elif e[0] == "delete":
			out += "<del>"+ a[e[1]:e[2]] +"</del>"
		elif e[0] == "insert":
			out += "<ins>"+b[e[3]:e[4]] +"</ins>"
		elif e[0] == "equal":
			chunk = b[e[3]:e[4]]
			if len(chunk) > chars: chars = len(chunk)
			out += chunk
		else: 
			raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
	return out

def textDiff(a, b):
	"""Takes in strings a and b and returns a human-readable HTML diff."""

	out = []
	a, b = html2list(a), html2list(b)
	s = difflib.SequenceMatcher(isTag, a, b)
	for e in s.get_opcodes():
		if e[0] == "replace":
			# @@ need to do something more complicated here
			# call textDiff but not for html, but for some html... ugh
			# gonna cop-out for now
			out.append("<del>"+' '.join(a[e[1]:e[2]]) + "</del><ins>"+' '.join(b[e[3]:e[4]])+"</ins>")
		elif e[0] == "delete":
			out.append("<del>"+ ' '.join(a[e[1]:e[2]]) + "</del>")
		elif e[0] == "insert":
			out.append("<ins>"+' '.join(b[e[3]:e[4]]) + "</ins>")
		elif e[0] == "equal":
			out.append(' '.join(b[e[3]:e[4]]))
		else: 
			raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
	return ' '.join(out)

def html2list(x, b=0):
	mode = 'char'
	cur = ''
	out = []
	for c in x:
		if mode == 'tag':
			if c == '>': 
				if b: cur += ']'
				else: cur += c
				out.append(cur); cur = ''; mode = 'char'
			else: cur += c
		elif mode == 'char':
			if c == '<': 
				out.append(cur)
				if b: cur = '['
				else: cur = c
				mode = 'tag'
			elif c in string.whitespace: out.append(cur); cur = ''
			else: cur += c
	out.append(cur)
	return filter(lambda x: x is not '', out)

def htmlDiff(a, b):
	f1, f2 = a.find('</head>'), a.find('</body>')
	ca = a[f1+len('</head>'):f2]
	
	f1, f2 = b.find('</head>'), b.find('</body>')
	cb = b[f1+len('</head>'):f2]
	
	r = textDiff(ca, cb)
	hdr = '<style type="text/css"><!-- ins{color: green} del{color:red}--></style></head>'
	return b[:f1] + hdr + r + b[f2:]


def test():
	b = """
<html><head>
<title>The History of Alcohol, Part II</title>
</head>
<body bgcolor="#FFFFFF">
<table width="100%" border = "0"><tr><td>
	<h1>The History of Alcohol, Part II</h1>
	<big>by <A HREF = "http://www.theinfo.org/view/user.adp?name=aswartz">aswartz</A>, Author<BR><A HREF = "http://www.theinfo.org/view/user.adp?name=beadmomsw">beadmomsw</A>, Author<BR><br>
<big>[ <A HREF="http://add.theinfo.org/alcohol/1.3">edit me</a> | <a href="/alcohol/1.3/advanced">advanced mode</a> ]</big></big>
</td><td align="right">
<div class="logo">
	<big><big><big><big>get.info</big></big></big></big><br>
	<big><big><A HREF="http://www.theinfo.org/login/?return_url=http%3a%2f%2fget%2etheinfo%2eorg%2falcohol%2f1%2e3%3f">Log In</A> to the <a href="http://www.theinfo.org">Info Network</a></big></big>
</div>
</table>
<hr noshade>
Continued from <A HREF="http://get.theinfo.org/alcohol1">The History of Alcohol, Part I</A><br>
<br>
Condemnation of drinking by the Christian church as sinful and immoral came into being in the 17th and 18th centuries with the Protestant Reformation.  The preaching of temperance by Calvin and Luther had a profound effect on not only Europe, but upon Colonial America, which was just being settled by pilgrims of these faiths.<br>
<br>
Until the 18th century, wine, beer and ale had satisfied most of the civilized desire for alcoholic beverages.  These produced excesses, of course, but not like those of the variety and seriousness which came later.  The excesses of drink became a matter of public concern when the art of distillery graduated into an industry.<br>
<br>
The beginning of the present-day alcohol problem probably dates from these earliest distilling days.  It was then that the breakdown in family life, licentiousness, and public inebriety became commonly associated.  Public leaders everywhere--doctors, ministers, artists, and writers--began to inveigh against the excesses of alcohol.<br>
<br>
Many scholars think that, despite the severity of the problems associated with excessive drinking, national prohibition did not succeed then for precisely the same reasons--social, economic, and political--that it fails today.  Back then, instead of prohibiting excessive drinking, dilution of alcoholic beverages was encouraged.<br>
<br>
In 18th century England, distillation as an industrial process was encouraged.  England's traditional animosity toward France culminated during this time in the imposition of heavy tariffs on French wine imports.  As a substitute for the light wines of France, the British government encouraged the importation of heavy wines from Portugal.  The smuggling of Dutch gin became a major industry until English production of distilled spirits got underway.  Then, within a short period of time, the English changed from a dilute alcohol drinking nation to a relatively "hard liquor" drinking nation.  The drinking pattern suddenly changed from beer and ale (containing 8% alcohol) to port (18%-22% alcohol) to gin (35%-45% alcohol).  Gin was cheap and every encouragement was given to the people to purchase it.  At best, life in urban England (and, in fact, in most of Europe in those days) was a sorry gin-sodden affair.<br>
<br>
By the middle of the 18th century, England came to regret its earlier policy of encouraging the production of gin and other  distilled spirits.  The government embarked on a permanent program of coping with drinking excesses by levying higher and higher taxes on distilled spirits.  Along with these increasingly prohibitive costs to consumers, came more rigid regulations concerning the manner, times and terms of sale of alcohol, and the licensing of pubs.  The success of these laws and regulations can be proven by the fact that today England is once again primarily a dilute alcohol drinking nation, a country of beer and ale drinkers.<br>
<br>
In the United States, we were as precocious in our drinking as in all other things.  Founded precisely at the time when distillation was rapidly becoming an important industry in other parts of the world, America immediately became a "hard liquor" drinking nation in which gin and whiskies played an important part.  Although the early colonists had to satisfy their meager drinking wants mostly with home-brewed beer, ale and wine, by the late 1600's, rum was imported from the Caribbean islands and the distillation industry was established and encouraged.<br>
<br>
The history of New England is noted for its laws involving a wide variety of prohibitions and penalties.  The laws of Colonial America preempted those of the church.   Drunkenness, defined as a sin by church law, was translated in precisely those terms into secular law, where it has remained practically unchanged to today.  Punishment--fines, flogging, imprisonment, censure--instead of treatment, has likewise remained the primary discouragement to excessive drinking.<br>
<br>
By 1779, the state of Connecticut had passed 80 major statutes concerning alcoholic beverages.  Many were aimed at the control of the manufacture, sale and traffic of these beverages.  Other laws were passed to insure propriety in inns, taverns and other places selling alcohol. Heavy penalties were levied on innkeepers who permitted gambling and drunkenness.  But, true to European tradition, colonial lawmakers were motivated more by economic and political considerations surrounding the property value and revenues from the manufacture and sale of alcoholic beverages, than by the intrinsic value of maintaining the public health.  Neither the physical causes nor the effects of excessive drinking were concerns of theirs.<br>
<br>
Laws notwithstanding, drinking excesses mounted throughout the last half of the 18th century.  Communities all over Ameria were manufacturing their own distilled whiskies.  The people west of the Allegheny Mountains were cut off from the supplies of gin on the eastern seaboard and also from supplies of rum from the islands.  So they discovered a way of distilling alcohol from their bulk products--corn and grain--by converting them into a kind of liquid gold.  The bourbon whisky they distilled was small in bulk, relatively easy to transport, and had a high money value.  It became much more than mere spirits; it actually became a medium of exchange, to the extent that bottles of bourbon were occasionally placed in church coffers instead of cash.<br>
<br>
The American Revolution gave important impetus to the temperanace movement.  Here began some of the most important medical and social contributions to the early temperance movement in the United States.  Throughout the 19th century, drinking excesses mounted but our social attitudes remained relatively fixed.  The few sporadic efforts made by humanitarians, reformers and physicians to break away from the traditions of the past were doomed to failure.<br>
<br>
Before the Civil War, Americans of drinking age drank large amounts of hard liquor, primarily rum, whisky and gin, and small amounts of beer and wine.  After the Civil War, coinciding with the immigration of German and Scandinavian beer-drinking peoples, a radical change in American drinking patterns became evident.   By 1915, Americans were consuming large amounts of beer and much smaller amounts of hard liquor.<br>
<br>
The American drinking style has remained much the same to this day.  Despite brief flirtations with such hard drink as the 1920s "bathtub gin" and the 1980s designer vodkas and single malt whiskies, Americans generally remain content with the consumption of softer products such as beer and wine.  The popularity of alcohol is likely to continue despite the regular eruption of temperance movements; this and the current 20th century's focus on the illegality of drugs seems to predict that national alcohol prohibition will never again be attempted in the United States.  One encouraging note is the recent consideration of alcoholism as a disease and the emphasis placed not on punishment, but on treatment of alcoholics.<br>
<P><I>Version 1.3</I>
</body>
</html>
"""
	a = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"><html><head><title>The History of Alcohol, Part 2</title></head>
<body bgcolor="#FFFFFF">
<table width="100%" border = "0"><tr><td>
	<h1>The History of Alcohol, Part 2</h1>
	<big>by <A HREF = "http://www.theinfo.org/view/user.adp?name=aswartz">aswartz</A>, Author<BR><A HREF = "http://www.theinfo.org/view/user.adp?name=beadmomsw">beadmomsw</A>, Author<BR><br>
<big>[ <A HREF="http://add.theinfo.org/alcohol/1.2">edit me</a> | <a href="/alcohol/1.2/advanced">advanced mode</a> ]</big></big>
</td><td align="right">
<div class="logo">
	<big><big><big><big>get.info</big></big></big></big><br>
	<big><big><A HREF="http://www.theinfo.org/login/?return_url=http%3a%2f%2fget%2etheinfo%2eorg%2falcohol%2f1%2e2%3f">Log In</A> to the <a href="http://www.theinfo.org">Info Network</a></big></big>
</div>
</table>
<hr noshade>
Continued from <A HREF="http://get.theinfo.org/alcohol">The History of Alcohol, Part I</A>


Condemnation of drinking bye the Christian church as sinful and immoral came into being in the 17th and 18th centuries with the Protestant Reformation.  The preaching of temperance by Calvin and Luther had a profound effect on not only Europe, but upon Colonial America, which was just being settled by pilgrims of these faiths.

Until the 18th century, wine, beer and ale had satisfied most of the civilized desire for alcoholic beverages.  These produced excesses, of course, but not like those of the variety and seriousness which came later.  The excesses of drink became a matter of public concern when the art of distillery graduated into an industry.

The beginning of the present-day alcohol problem probably dates from these earliest distilling days.  It was then that the breakdown in family life, licentiousness, and public inebriety became commonly associated.  Public leaders everywhere--doctors, ministers, artists, and writers--began to inveigh against the excesses of alcohol.

Many scholars think that, despite the severity of the problems associated with excessive drinking, national prohibition did not succeed then for precisely the same reasons--social, economic, and political--that it fails today.  Back then, instead of prohibiting excessive drinking, dilution of alcoholic beverages was encouraged.

In 18th century England, distillation as an industrial process was encouraged.  England's traditional animosity toward France culminated during this time in the imposition of heavy tariffs on French wine imports.  As a substitute for the light wines of France, the British government encouraged the importation of heavy wines from Portugal.  The smuggling of Dutch gin became a major industry until English production of distilled spirits got underway.  Then, within a short period of time, the English changed from a dilute alcohol drinking nation to a relatively "hard liquor" drinking nation.  The drinking pattern suddenly changed from beer and ale (containing 8% alcohol) to port (18%-22% alcohol) to gin (35%-45% alcohol).  Gin was cheap and every encouragement was given to the people to purchase it.  At best, life in urban England (and, in fact, in most of Europe in those days) was a sorry gin-sodden affair.

By the middle of the 18th century, England came to regret its earlier policy of encouraging the production of gin and other  distilled spirits.  The government embarked on a permanent program of coping with drinking excesses by levying higher and higher taxes on distilled spirits.  Along with these increasingly prohibitive costs to consumers, came more rigid regulations concerning the manner, times and terms of sale of alcohol, and the licensing of pubs.  The success of these laws and regulations can be proven by the fact that today England is once again primarily a dilute alcohol drinking nation, a country of beer and ale drinkers.

In the Unyted States, we were as precocious in our drinking as in all other things.  Founded precisely at the time when distillation was rapidly becoming an important industry in other parts of the world, America immediately became a "hard liquor" drinking nation in which gin and whiskies played an important part.  Although the early colonists had to satisfy their meager drinking wants mostly with home-brewed beer, ale and wine, by the late 1600's, rum was imported from the Caribbean islands and the distillation industry was established and encouraged.

The history of the state of New England is noted for its laws involving a wide variety of prohibitions and penalties.  The laws of Colonial America preempted those of the church.   Drunkenness, defined as a sin by church law, was translated in precisely those terms into secular law, where it has remained practically unchanged to today.  Punishment--fines, flogging, imprisonment, censure--instead of treatment, has likewise remained the primary discouragement to excessive drinking.

By 1779, Connecticut had passed 80 major statutes concerning alcoholic beverages.  Many were aimed at the control of the manufacture, sale and traffic of these beverages.  Other laws were passed to insure propriety in inns, taverns and other places selling alcohol. Heavy penalties were levied on innkeepers who permitted gambling and drunkenness.  But, true to European tradition, colonial lawmakers were motivated more by economic and political considerations surrounding the property value and revenues from the manufacture and sale of alcoholic beverages, than by the intrinsic value of maintaining the public health.  Neither the physical causes nor the effects of excessive drinking were concerns of theirs.

Laws notwithstanding, drinking excesses mounted throughout the last half of the 18th century.  Communities all over Ameria were manufacturing their own distilled whiskies.  The people west of the Allegheny Mountains were cut off from the supplies of gin on the eastern seaboard and also from supplies of rum from the islands.  So they discovered a way of distilling alcohol from their bulk products--corn and grain--by converting them into a kind of liquid gold.  The bourbon whisky they distilled was small in bulk, relatively easy to transport, and had a high money value.  It became much more than mere spirits; it actually became a medium of exchange, to the extent that bottles of bourbon were occasionally placed in church coffers instead of cash.

The American Revolution gave important impetus to the temperanace movement.  Here began some of the most important medical and social contributions to the early temperance movement in the United States.  Throughout the 19th century, drinking excesses mounted but our social attitudes remained relatively fixed.  The few sporadic efforts made by humanitarians, reformers and physicians to break away from the traditions of the past were doomed to failure.

Before the Civil War, Americans of drinking age drank large amounts of hard liquor, primarily rum, whisky and gin, and small amounts of beer and wine.  After the Civil War, coinciding with the immigration of German and Scandinavian beer-drinking peoples, a radical change in American drinking patterns became evident.   By 1915, Americans were consuming large amounts of beer and much smaller amounts of hard liquor.

The American drinking style has remained much the same to this day.  Despite brief flirtations with such hard drink as the 1920s "bathtub gin" and the 1980s designer vodkas and single malt whiskies, Americans generally remain content with the consumption of softer products such as beer and wine.  The popularity of alcohol is likely to continue despite the regular eruption of temperance movements; this and the current 20th century's focus on the illegality of drugs seems to predict that national alcohol prohibition will never again be attempted in the United States.  One encouraging note is the recent consideration of alcoholism as a disease and the emphahsis placed on punishment, but on treatment of alcoholics.


<P><I>Version 1.2</I>
</body>
</html>"""
	print htmlDiff(a, b)
	
if __name__ == "__main__":
	import cgi
	f = cgi.FieldStorage()
	if f.has_key('old') and f.has_key('new'):
		import urllib
		a = urllib.urlopen(f['old'].value).read()
		b = urllib.urlopen(f['new'].value).read()
		print "Content-Type: text/html"
		print
		print htmlDiff(a, b)
	else:
		print "Content-Type: text/html"
		print
		print """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" lang="en-US">
<head>
  <title>HTML Diff</title>
  <link rel="stylesheet" type="text/css" href="/style.css" />
</head>
<body>
<div id="banner">
  <h1>HTML Diff</h1>
  <span class="description">Highlights the differences between two HTML pages.</span>
</div>
<div class="content">

<p>(<a href="diff.py">source code</a> | <a href="http://www.aaronsw.com/2002/diff?old=http%3A%2F%2Fdev.w3.org%2Fcvsweb%2F%7Echeckout%7E%2F2000%2F10%2Fswap%2FOverview.html%3Frev%3D1.35%26content-type%3Dtext%2Fhtml&new=http%3A%2F%2Fdev.w3.org%2Fcvsweb%2F%7Echeckout%7E%2F2000%2F10%2Fswap%2FOverview.html%3Frev%3D1.20%26content-type%3Dtext%2Fhtml">complex example</a>)</p>

<form action="" method="GET">
<strong>Old:</strong> <input name="old" type="text" /><br />
<strong>New:</strong> <input name="new" type="text" /><br />
<input type="submit" value="Diff!" />
</form>
</div>
<div class="footer">
  <address><a href="http://www.aaronsw.com/">Aaron Swartz</a> (<a href="mailto:\
me@aaronsw.com">me@aaronsw.com</a>)</address>
<a href="http://validator.w3.org/check/referer">Valid HTML</a>
</div></body>
</html>"""
