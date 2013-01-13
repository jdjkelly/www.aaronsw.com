"""CGI Assistance

A wrapper for Python's CGI module to provide something a little more useful to
programmers.
"""

import cgi
c = cgi.FieldStorage()

class Form:
    def __getattr__(self, name):
        return c[name].value

    def __getitem__(self, name):
        return c[name].value

    def __contains__(self, nam):
        return name in c.keys()

    __iter__ = iter(c.keys())

    def __str__(self):
        out = 'Form{'
        for i in self:
            out += '"'+i+'":"'+self[i]+'",'
        out = out[:-1] + '}'
        
    def html(self):
        out = ''
        for i in self:
            out += '<input type="hidden" name="'+i+'" value="'+self[i]
            out += '" />'
