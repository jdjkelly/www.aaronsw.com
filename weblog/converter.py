import sys, re, htmlentitydefs, time

entry = open(sys.argv[1]).read()

getText = re.compile('<string name="text" value="([^"]*)"', re.S|re.M)
getDate = re.compile('<date name="when" value="([^"]*)', re.S|re.M)
date = time.strftime('%m/%d/%Y %H:%M:%S',
	time.strptime(getDate.search(entry).groups()[0], "%a, %d %b %Y %H:%M:%S GMT"))
body = getText.search(entry).groups()[0]

body = re.sub('&#013;&#010;', '<p />', body)
body = re.sub('&apos;', "'", body)
for e in htmlentitydefs.entitydefs:
	body = re.sub('&'+e+';', htmlentitydefs.entitydefs[e], body)

print "DATE:", date
print "-----"
print "BODY:"
print body
print "--------"
