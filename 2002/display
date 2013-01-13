#!/usr/bin/python2.2
import cgi
q = cgi.FormContentDict()

if q.has_key('ct'): print 'Content-Type: text/html; charset=UTF-8'
else: print 'Content-Type: text/html'
print

if q.has_key('mhe'): print '<meta http-equiv="content-type" value="text/html; charset=utf-8" />'

if q.has_key('t'): print q['t'][0]

print
print "<hr />"
print '<p>This is display.cgi (<a href="display.py">source</a>).'
print "It takes some text you enter into a form, and displays it for you"
print "as HTML. This is a great way to see how some HTML code looks in your"
print "(or someone else's) browser. So paste 'n go:</p>"

if q.has_key('method'): method = 'post'
else: method = 'get'
print '<form method="'+method+'" action=""><textarea style="width: 100%; height: 75%" name="t"></textarea>'
print '<input type="submit" /></form>'

