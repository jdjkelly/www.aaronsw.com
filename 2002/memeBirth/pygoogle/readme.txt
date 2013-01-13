PyGoogle - an easy-to-use wrapper for Google's web API
Copyright (c) 2002 Mark Pilgrim (f8dy@diveintomark.org)
Open source, same license as Python itself

SUMMARY
-------
This module allows you to access Google's web APIs through SOAP,
to do things like search Google and get the results programmatically.
This API is described here:
  http://www.google.com/apis/
  
IMPORTANT NOTE
--------------
You need a Google-provided license key to use these services.
Follow the link above to get one, then set the LICENSE_KEY variable
in google.py before using any of the functions.

INSTALLATION
------------
Copy google.py and SOAP.py to your site-packages directory, or anywhere
else in your Python library path.  You must use the included version of 
SOAP.py; all previous versions are incompatible with Python 2.2.

USAGE
-----
>>> import google
>>> google.LICENSE_KEY = '...' # must get your own!
>>> data = google.doGoogleSearch('python')
>>> data.meta.searchTime
0.043221000000000002
>>> dir(data.meta)
['directoryCategories', 'documentFiltering', 'endIndex', 'estimateIsExact',
'estimatedTotalResultsCount', 'searchComments', 'searchQuery', 'searchTime',
'searchTips', 'startIndex']
>>> data.results[0].URL
'http://www.python.org/'
>>> data.results[0].title
'<b>Python</b> Language Website'
>>> dir(data.results[0])
['URL', 'cachedSize', 'directoryCategory', 'directoryTitle', 'hostName',
'relatedInformationPresent', 'snippet', 'summary', 'title']

----------------

Revision history:
0.3 of 4/11/2002
  - included copy of SOAP.py updated for Python 2.2 compatibility (between
    2.1 and 2.2, type("").__name__ changed from "string" to "str", thus 
    causing the marshalling to fail in SOAPBuilder.dump)
0.2 of 4/11/2002
  - fixed typo (_assertLicense)
0.1 of 4/11/2002
  - initial release
