#!/usr/bin/env python
"""arcget: Retrieve a site from the Internet Archive
Usage:
  python arcget.py deadserver.com/mysite
"""
__version__ = "0.8"
__author__ = "Aaron Swartz <me@aaronsw.com>"
__license__ = "GNU GPL 2"

import urllib, re, os, os.path, sys, traceback, time
VERBOSE = 1

class AppURLopener(urllib.FancyURLopener): version = "arcget/"+__version__
urllib._urlopener = AppURLopener()

def lstrips(text, remove):
    if text.startswith(remove): return text[len(remove):]
    return text    

def validpage(url, n=0):
    p = urllib.urlopen(url).read()
    if ("We're sorry.  Your request failed to connect to our servers." in p or
        "We're sorry.  We were unable to retrieve the requested data." in p or
        "<TITLE>502 Proxy Error</TITLE>" in p):
        if n > 5: return None
        #print '.',
        time.sleep(.3)
        return validpage(url, n+1)
    if "Sorry, but this page does not exist." in p: return None
    if "Sorry, we can't find the archived version of this page." in p: return None
    if "Sorry, we can't find the file containing the archived" in p: return None
    if "Page not found</TITLE>" in p: return None
    return p

r_l = re.compile('"(http://web.archive.org/web/\d+/.*?)"')
def _getpage(url, archive):
    l = urllib.urlopen("http://"+archive+"/*sa_/"+url).read()
    p = None
    for u in r_l.findall(l):
        p = validpage(u)
        if p: break
    return p

def getpage(url, d = None):
    if d: return validpage("http://web.archive.org/web/"+d+"/"+url)
    p = None
    for a in ["web.archive.org"]:#, "archive.bibalex.org"]:
        p = _getpage(url, a)
        if p: break
    return p

r_b = re.compile('<BASE HREF="(.*?)">')
r_s = re.compile('<SCRIPT language="Javascript">\n<!--\n\n// FILE ARCHIVED.*?</SCRIPT>', re.S)
def cleanpage(t):
    t = r_b.sub('', t)
    t = r_s.sub('', t)
    return t

def _tofilename(url):
    url = lstrips(url, "http://")
    if url.endswith('/'): url += 'index.html'
    return url

class PageNotFound(Exception): pass
def writepage(url, d=None): # shouldn't include http://
    fn = '.tmp.'+str(os.getpid())
    p = getpage(url, d)
    if not p: raise PageNotFound
    open(fn, 'w').write(cleanpage(p))
    os.renames(fn, _tofilename(url))

def _dopage(x):
    try: writepage(x) #, d) -- doesn't seem to work
    except PageNotFound:
        if VERBOSE: print "FAILED:", x
    except:
        print "ERROR:", x
        traceback.print_exc()
    else:
        if VERBOSE: print x

r_l2 = re.compile(r'"http://web.archive.org/web/(\d+|\*hh_)/(.*?)"')
def getall(urlstart, wwwsame=True, overwrite=False, forcelist=False):
    # wwwsame: is www.foo.com the same as foo.com?
    # overwrite: reget a page if it already exists?
    # forcelist: don't fallback to getting a single page
    u = 'http://web.archive.org/web/*sr_1nr_300000/'+urlstart+'*'
    l = urllib.urlopen(u).read()
    listing = r_l2.findall(l)
    
    if not forcelist and not listing: return _dopage(urlstart)
            
    for (date, url) in listing:
        if wwwsame: url = lstrips(url, 'www.')
        
        filename = _tofilename(url)
        if not overwrite and os.path.isfile(filename): continue
        
        _dopage(url)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__,
    else:
        print "Grabbing", sys.argv[1], "..."
        getall(sys.argv[1])