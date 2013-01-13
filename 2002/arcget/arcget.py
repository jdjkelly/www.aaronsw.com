#!/usr/bin/env python
"""arcget: Retrieve a site from the Internet Archive
Usage:
  python arcget.py deadserver.com/mysite
  python arcget.py deadserver.com/mysite 20081011205635
"""
__version__ = "0.9"
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

r_l = re.compile('DATE="(\d+)"')
def _getpage(url, archive, maxd=None):
    if maxd:
        rangespec = '0-' + maxd
    else:
        rangespec = ''
    l = urllib.urlopen("http://"+archive+"/"+rangespec+"*xm_/"+url).read()
    p = None
    dates = r_l.findall(l)
    dates.reverse()
    for u in dates:
        p = validpage("http://"+archive+"/web/"+u+"js_/"+url)
        if p: break
    return p

def getpage(url, maxd=None):
    p = None
    for a in ["web.archive.org"]:#, "archive.bibalex.org"]:
        p = _getpage(url, a, maxd)
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
def writepage(url, maxd=None): # shouldn't include http://
    fn = '.tmp.'+str(os.getpid())
    p = getpage(url, maxd)
    if not p: raise PageNotFound
    open(fn, 'w').write(cleanpage(p))
    os.renames(fn, _tofilename(url))

def _dopage(x, maxd=None):
    try:
        writepage(x, maxd)
    except PageNotFound:
        if VERBOSE: print "FAILED:", x
    except KeyboardInterrupt:
        raise
    except:
        print "ERROR:", x
        traceback.print_exc()
    else:
        if VERBOSE: print x

r_l2 = re.compile(r'"http://web.archive.org/web/(\d+|\*hh_)/(.*?)"')
def getall(urlstart, maxd=None, wwwsame=True, overwrite=False, forcelist=False):
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
        
        _dopage(url, maxd)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__,
    else:
        if len(sys.argv) > 2:
            maxd = sys.argv[2]
        else:
            maxd = None
        print "Grabbing", sys.argv[1], 
        if maxd:
            print "until", maxd,
        print "..."
        getall(sys.argv[1], maxd)