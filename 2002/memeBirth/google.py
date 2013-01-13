"""Python wrapper for Google web APIs

This module allows you to access Google's web APIs through SOAP,
to do things like search Google and get the results programmatically.
Described here:
  http://www.google.com/apis/
  
You need a Google-provided license key to use these services.
Follow the link above to get one, then set the LICENSE_KEY variable
below before using any other functions in this module.

Sample usage:
>>> import google
>>> google.LICENSE_KEY = '...' # must get your own!
>>> data = google.doGoogleSearch('python')
>>> data.meta.searchTime
0.043221000000000002
>>> data.results[0].URL
'http://www.python.org/'
>>> data.results[0].title
'<b>Python</b> Language Website'

See documentation of SearchResultsMetaData and SearchResult classes
for other available attributes.
"""

__author__ = "Mark Pilgrim (f8dy@diveintomark.org)"
__version__ = "$Revision: 1.1.1.1 $"
__date__ = "$Date: 2002/04/12 03:51:11 $"
__copyright__ = "Copyright (c) 2002 Mark Pilgrim"
__license__ = "Python"

import SOAP

# you must register with Google to get a valid license key, or these functions will fail
LICENSE_KEY = '0CMqT0BnpgU2zy7Pjsb+eIZxraUHJElH'

# don't touch the rest of these constants
class NoLicenseKey(Exception): pass
_url = 'http://api.google.com/search/beta2'
_namespace = 'urn:GoogleSearch'
_false = SOAP.booleanType(0)
_true = SOAP.booleanType(1)

def _assertLicense():
    if not LICENSE_KEY:
        raise NoLicenseKey, 'get a license key at http://www.google.com/apis/, then set LICENSE_KEY'

def _marshalBoolean(value):
    if value:
        return _true
    else:
        return _false

class SearchBase:
    def __init__(self, params):
        for k, v in params.items():
            if isinstance(v, SOAP.structType):
                v = v._asdict
            try:
                if isinstance(v[0], SOAP.structType):
                    v = [node._asdict for node in v]
            except:
                pass
            self.__dict__[str(k)] = v

class SearchResultsMetaData(SearchBase):
    """metadata of search query results

    Available attributes:
    documentFiltering - flag indicates whether duplicate page filtering was perfomed in this search
    searchComments - human-readable informational message (example: "'the' is a very common word
        and was not included in your search")
    estimatedTotalResultsCount - estimated total number of results for this query
    estimateIsExact - flag indicates whether estimatedTotalResultsCount is an exact value
    searchQuery - search string that initiated this search
    startIndex - index of first result returned (zero-based)
    endIndex - index of last result returned (zero-based)
    searchTips - human-readable informational message on how to use Google bette
    directoryCategories - list of dictionaries like this:
        {'fullViewableName': Open Directory category,
         'specialEncoding': encoding scheme of this directory category}
    searchTime - total search time, in seconds
    """    
    pass

class SearchResult(SearchBase):
    """search result

    Available attributes:
    URL - URL
    title - title (HTML)
    snippet - snippet showing query context (HTML)
    cachedSize - size of cached version of this result, (KB)
    relatedInformationPresent - flag indicates that the "related:" keyword is supported for this URL
    hostName: When filtering occurs, a maximum of two results from any given host is returned.
        When this occurs, the second resultElement that comes from that host contains
        the host name in this parameter.
    directoryCategory: dictionary like this:
        {'fullViewableName': Open Directory category,
         'specialEncoding': encoding scheme of this directory category}
    directoryTitle: Open Directory title of this result (or blank)
    summary - Open Directory summary for this result (or blank)
    """
    pass

class SearchReturnValue:
    """complete search results for a single query

    Available attributes:
    meta - SearchResultsMetaData
    results - list of SearchResult
    """
    def __init__(self, metadata, results):
        self.meta = metadata
        self.results = results
        
def doGoogleSearch(q, start=0, maxResults=10, filter=1, restrict='',
                   safeSearch=0, language='', inputencoding='', outputencoding=''):
    """search Google

    LICENSE_KEY must be set correctly before calling this function, see
    http://www.google.com/apis/ to get one.
    
    Parameters:
    q - search string.  Anything you could type at google.com, you can pass here.
        See http://www.google.com/help/features.html for examples of advanced features.
    start (optional) - zero-based index of first desired result (for paging through
        multiple pages of results)
    maxResults (optional) - maximum number of results, currently capped at 10
    filter (optional) - set to 1 to filter out similar results, set to 0 to see everything
    restrict (optional) - restrict results by country or topic.  Examples:
        Ukraine - search only sites located in Ukraine
        linux - search Linux sites only
        mac - search Mac sites only
        bsd - search FreeBSD sites only
        See the APIs_reference.html file in the SDK (http://www.google.com/apis/download.html)
        for more advanced examples and a full list of country codes and topics.
    safeSearch (optional) - set to 1 to filter results with SafeSearch (no adult material)
    language (optional) - restricts search to documents in one or more languages.  Example:
        lang_en - only return pages in English
        lang_fr - only return pages in French
        See the APIs_reference.html file in the SDK (http://www.google.com/apis/download.html)
        for more advanced examples and a full list of language codes.
    inputencoding (optional) - sets the character encoding of q parameter
    outputencoding (optional) - sets the character encoding of the returned results
        See the APIs_reference.html file in the SDK (http://www.google.com/apis/download.html)
        for a full list of encodings.

    Returns: SearchMetaData, [SearchResult, SearchResult, ...]
    """    
    _assertLicense()
    remoteserver = SOAP.SOAPProxy(_url, namespace=_namespace)
    filter = _marshalBoolean(filter)
    safeSearch = _marshalBoolean(safeSearch)
    data = remoteserver.doGoogleSearch(LICENSE_KEY, q, start, maxResults, filter, restrict,
                                       safeSearch, language, inputencoding, outputencoding)
    metadata = data._asdict
    del metadata["resultElements"]
    metadata = SearchResultsMetaData(metadata)
    results = [SearchResult(node._asdict) for node in data.resultElements]
    return SearchReturnValue(metadata, results)
