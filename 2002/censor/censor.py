#!/usr/bin/env python
"""Usage: python censor.py [[--kill | --help | port] [HTTP-PROXY]]
A CIPA-compliant http proxy server.

  --kill       Kill all other proxies and exit
  port         The port on which to run the proxy (default %(PORT)d)
  HTTP-PROXY   The URL of another HTTP proxy to use"""

__version__ = "0.01 (First Version)"
__author__ = "Aaron Swartz <http://www.aaronsw.com/>"
__credits__ = "based on http://logicerror.com/archiverProxy"
__copyright__ = "This program is free software."

#####################################################################
# Start user configuration
#####################################################################

blockprefixes = ['http://www.microsoft.com/']

# default port if none specified on command line
PORT = 8000

# debugging level,
#	0 = no debugging, only notices
#	1 = access and error debugging
#	2 = full debugging
#	3 = really full debugging
DEBUG_LEVEL = 0
ALLOW_DEBUG_ON_WIN32 = 1

SHOW_ERRORS = 0

# the address to bind the server to
ADDR_TO_BIND_TO = '127.0.0.1'

#####################################################################
# End of user configuration
#####################################################################

SERVER_URL = "http://logicerror.com/archiverProxy"


import sys
import os
import time
import string
import re
import random
import binascii
import traceback
import stat
from md5 import md5

import BaseHTTPServer
import urlparse
import mimetools
from stat import ST_MTIME
from cStringIO import StringIO

import socket
import asyncore
import asynchat


###############################################################################
def log(s, v=1, args=None):
	if v <= DEBUG_LEVEL:
		if args:
			sys.stdout.write(s % args)
		else:
			sys.stdout.write(s)

def dummylog(s, v=1, args=None):
	pass

if sys.platform == 'win32' and not ALLOW_DEBUG_ON_WIN32:
	log = dummylog

def handle_error(self):
	if (sys.exc_type == socket.error and (sys.exc_value[0] == 32 or sys.exc_value[0] == 9)) or (
		sys.exc_type == AttributeError):
		# ignore these errors
		self.handle_close() # something is pretty broken, close it
		return
	if DEBUG_LEVEL > 0 or SHOW_ERRORS:
		print time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(time.time())), "An error has occurred: \r\n"
		traceback.print_exception(sys.exc_type,sys.exc_value, sys.exc_traceback)
	else:
		e = open('errors.txt','a')
		e.write(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(time.time())) + ' An error has occurred: \r\n')
		traceback.print_exception(sys.exc_type,sys.exc_value, sys.exc_traceback, file=e)
		e.write('\r\n')
		e.close()
		log('An error occurred, details are in errors.txt\n', v=0)
		
###############################################################################
def sameHost(host, port, HOST, PORT):
	if port == PORT and (
		(HOST == '' and (host == '127.0.0.1' or string.lower(host) == 'localhost')) 
		or string.lower(host) == string.lower(HOST)):
		return 1
	else: return 0

###############################################################################
class AsyncProxyError(StandardError): pass


###############################################################################
class AsyncHTTPProxySender(asynchat.async_chat):
	def __init__(self, receiver, id, host, port):
		asynchat.async_chat.__init__(self)
		self.receiver = receiver
		self.id = id
		self.set_terminator(None)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = host
		self.port = port
		try:
			self.connect( (host, port) )
		except socket.error, e:
			log('(%d) XXX %s\n' % (self.id, e))
			self.receiver.sender_connection_error(e)
			self.close()
			return

	def handle_connect(self):
		log('(%d) S handle_connect\n' % self.id, 3)
		try:
			if sys.platform != 'win32':
				self.socket.recv(0)  # check for any socket errors during connect
			self.receiver.sender_is_connected()
		except socket.error, e:
			log('(%d) OOO %s\n' % (self.id, e))
			if hasattr(self, 'receiver'):
				self.receiver.sender_connection_error(e)
			self.close()
			return
		log('(%d) sender connected\n' % self.id, 2)

	def return_error(self, e):
		log('(%d) sender got socket error: %s\n', args=(self.id, e), v=2)
		if isinstance(e, socket.error) and type(e.args) == type(()) and len(e.args) == 2:
			e = e.args[1]  # get the error string only
		self.receiver.error(404, 'Error connecting to <em>%s</em> on port <em>%d</em>: <b>%s</b>' % (self.host, self.port, e), response=str(e))
		self.close()

	def collect_incoming_data(self, data):
		if DEBUG_LEVEL >= 3:
			log('==> (%d) %s\n', args=(self.id, repr(data)), v=3)
		else:
			log('==> (%d) %d bytes\n', args=(self.id, len(data)), v=2)
		self.receiver.push(data)

	def handle_close(self):
		log('(%d) sender closing\n' % self.id, v=2)
		if hasattr(self, 'receiver'):
			self.receiver.close_when_done()
			del self.receiver  # break circular reference
		self.close()

	def handle_error(self):
		handle_error(self)
	
	def log(self, message):
		log('(%d) sender: %s\n', args=(self.id, message,), v=1)
	
	def log_info(self, message, type='info'):
		if __debug__ or type != 'info':
			log('%s: %s' % (type, message), v=0)
	

###############################################################################
class AsyncHTTPProxyReceiver(asynchat.async_chat):
	channel_counter = [0]

	def __init__(self, server, (conn, addr)):
		self.id = self.channel_counter[0]  # used during log calls
		try:
			self.channel_counter[0] = self.channel_counter[0] + 1
		except OverflowError:
			self.channel_counter[0] = 0
		asynchat.async_chat.__init__(self, conn)
		self.set_terminator('\n')
		self.server = server
		self.buffer = StringIO()

		# in the beginning there was GET...
		self.found_terminator = self.read_http_request
	
	def collect_incoming_data(self, data):
		self.buffer.write(data)
	
	def push_incoming_data_to_sender(self, data):
		if DEBUG_LEVEL >= 3:
			log('<== (%d) %s\n', args=(self.id, repr(data)), v=3)
		else:
			log('<== (%d) %d bytes\n', args=(self.id, len(data)), v=2)
		self.sender.push(data)

	#### to be used as a found_terminator method
	def read_http_request(self):
		self.request = self.buffer.getvalue()
		self.buffer = StringIO()

		log('%s - %s\n', args=(time.ctime(time.time()), self.request), v=1)

		# client-originated shutdown hack:
		if string.strip(self.request) == 'quit':
			log('External quit command received.\n')
			# On pre python 2.0 this will raise a NameError,
			# but asyncore will handle it well.  On 2.0, it
			# will cause asyncore to exit.
			raise asyncore.ExitNow

		try:
			self.method, self.url, self.protocol = string.split(self.request)
			self.method = string.upper(self.method)
		except:
			self.error(400, "Can't parse request")
		if not self.url:
			self.error(400, "Empty URL")
		if self.method not in ['CONNECT', 'GET', 'HEAD', 'POST', 'PUT']:
			self.error(501, "Unknown request method (%s)" % self.method)
		if self.method == 'CONNECT':
			self.netloc = self.url
			self.scheme = 'https'
			self.path = ''
			params, query, fragment = '', '', ''
		else:
			if self.url[0] == '/':
				self.path = self.url
			else:
				# split url into site and path
				self.scheme, self.netloc, self.path, params, query, fragment = urlparse.urlparse(self.url)
				if string.lower(self.scheme) != 'http':
					self.error(501, "Unknown request scheme (%s)" % self.url) #, self.scheme)

				# find port number
				if ':' in self.netloc:
					self.host, self.port = string.split(self.netloc, ':')
					self.port = string.atoi(self.port)
				else:
					self.host = self.netloc
					if self.method == 'CONNECT':
						self.port = 443  # default SSL port
					else:
						self.port = 80
				self.path = urlparse.urlunparse(('', '', self.path, params, query, fragment))

		### BLOCK CODE ###
		if self.url.startswith('http://www.microsoft.com/'):
			self.show_response(401, 'Sorry, you are not permitted to view this page.', response='Access Denied')
			self.handle_close()
			
		### /BLOCK CODE ###

		self.rawheaders = StringIO()  # a "file" to read the headers into for mimetools.Message
		self.found_terminator = self.read_http_headers

	#### to be used as a found_terminator method
	def read_http_headers(self):
		header = self.buffer.getvalue()
		self.buffer = StringIO()
		if header and header[0] != '\r':
			self.rawheaders.write(header)
			self.rawheaders.write('\n')
		else:
			# all headers have been read, process them
			self.rawheaders.seek(0)
			self.mimeheaders = mimetools.Message(self.rawheaders)
			if (self.method == 'POST' or self.method == 'PUT') and not self.mimeheaders.has_key('content-length'):
				self.error(400, "Missing Content-Length for %s method" % self.method)
			self.length = int(self.mimeheaders.get('content-length', 0))
			del self.mimeheaders['accept-encoding']
			del self.mimeheaders['proxy-connection']
									
			# determine the next hop (another proxy or the remote host) and open a connection
			http_proxy = os.environ.get('http_proxy')
			if not http_proxy :
				http_proxy = os.environ.get('HTTP_PROXY')
			# if we're chaining to another proxy, modify our request to do that
			if http_proxy:
				scheme, netloc, path, params, query, fragment = urlparse.urlparse(http_proxy)
				if string.lower(scheme) == 'http' :
					log('using next http proxy: %s\n' % netloc, 2)
					# set host and port to the proxy
					if ':' in netloc:
						self.host, self.port = string.split(netloc, ':')
						self.port = string.atoi(self.port)
					else:
						self.host = netloc
						self.port = 80
					# replace the path within the request with the full URL for the next proxy
					self.path = self.url

			# create a sender connection to the next hop
			self.sender = AsyncHTTPProxySender(self, self.id, self.host, self.port)

			# send the request to the sender (this is its own method so that the sender can trigger
			# it again should its connection fail and it needs to redirect us to another site)
			self.push_request_to_sender()
	
	def push_request_to_sender(self):
		request = '%s %s HTTP/1.0\r\n%s\r\n' % (self.method, self.path, string.join(self.mimeheaders.headers, ''))

		if http_proxy:
			log('(%d) sending request to the next http proxy:\n' % self.id, v=2)
		else:
			log('(%d) sending request to server:\n' % self.id, v=2)
		log(request, v=2)

		# send the request and headers on through to the next hop
		self.sender.push(request)

		# no more formatted IO, just pass any remaining data through
		self.set_terminator(None)

		# buffer up incoming data until the sender is ready to accept it
		self.buffer = StringIO()
	
	def sender_is_connected(self):
		"""
		The sender calls this to tell us when it is ready for more data
		"""
		log('(%d) R sender_is_connected()\n' % self.id, v=3)
		# sender gave is the OK, give it our buffered data and any future data we receive
		self.push_incoming_data_to_sender(self.buffer.getvalue())
		self.buffer = None
		self.collect_incoming_data = self.push_incoming_data_to_sender
	
	def sender_connection_error(self, e):
		log('(%d) R sender_connection_error(%s) for %s:%s\n' % (self.id, e, self.host, self.port), v=2)
		if isinstance(e, socket.error) and type(e.args) == type(()) and len(e.args) == 2:
			e = e.args[1]  # get the error string only
		self.error(404, 'Error connecting to <em>%s</em> on port <em>%d</em>: <b>%s</b>' % (self.host, self.port, e), response=str(e))

	def handle_close(self):
		log('(%d) receiver closing\n' % self.id, v=2)
		if hasattr(self, 'sender'):
			# self.sender.close() should be fine except for PUT requests?
			self.sender.close_when_done()
			del self.sender  # break circular reference
		self.close()
	
	def show_response(self, code, body, title=None, response=None):
		if not response:
			response = BaseHTTPServer.BaseHTTPRequestHandler.responses[code][0]
		if not title:
			title = str(code) + ' ' + response
		self.push("HTTP/1.0 %s %s\r\n" % (code, response))
		self.push("Server: " + SERVER_URL + "\r\n")
		self.push("Content-type: text/html\r\n")
		self.push("\r\n")
		out = "<html><head>\n<title>" + title + "</title>\n</head>\n"
		out += '<body><h1>' + title +'</h1>\n'
		out += body 
		out += '<hr />\n<address><a href="%s">Proxy %s</a></address>' % (self.server.oururi, __version__)
		out += '\n</body>\n</html>'
		i = 0
		for j in range(len(out) / 512):
			self.push(out[i:i+512]) # push only 512 characters at a time
			i += 512
		self.push(out[i:]) # push out the rest

	def error(self, code, body, response=None):
		self.show_response(code, body, response=response)
		if hasattr(self, 'sender'):
			self.sender.handle_close()
			del self.sender  # break circular reference
		self.close()
		# asyncore.poll() catches this	(XXX shouldn't need this?)
		#raise AsyncProxyError, (code, body)

	def handle_error(self):
		handle_error(self)

	def log(self, message):
		log('(%d) receiver: %s\n', args=(self.id, message,), v=1)

	def log_info (self, message, type='info'):
		if __debug__ or type != 'info':
			log('%s: %s' % (type, message))


###############################################################################
class AsyncHTTPProxyServer(asyncore.dispatcher):
	def __init__(self, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.ouraddr = (ADDR_TO_BIND_TO, port)
		self.oururi = "http://%s:%d/" % self.ouraddr
		log('Starting proxy at %s\n' % self.oururi, 0)
		self.bind(self.ouraddr)
		self.listen(5)

	def handle_accept(self):
		AsyncHTTPProxyReceiver(self, self.accept())
	
	def log(self, message):
		log('server: %s\n', args=(message,), v=1)

	def handle_error(self):
		handle_error()

###############################################################################
def kill_external_proxy():
	"""
	Kills all external instances of the proxy owned by this user.

	This is a wrapper for the platform specific version.
	"""
	log("Stopping external proxies:\n")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		try:
			s.connect(('localhost', 8000))
			s.send('quit\r\n')
		finally:
			s.close()
	except:
		log('Could not connect to locahost 8000, oh well...\n')
	
def kill_external_proxy_win32():
	import win32api, win32pdhutil, win32con
	# XXX This code was taken from the Python1.6 Windows distribution.

	# Change suggested by Dan Knierim, who found that this performed a
	# "refresh", allowing us to kill processes created since this was run
	# for the first time.
	try:
		win32pdhutil.GetPerformanceAttributes(
			'Process','ID Process','archiverproxy')
	except:
		pass

	try:
		pids = win32pdhutil.FindPerformanceAttributesByName('archiverproxy')
	except:
		log("Not enough win32pdh library calls supported on this OS\n")
		log("older archiverproxy processes will not be automatically killed.\n")
		return

	# If _my_ pid in there, remove it!
	try:
		pids.remove(win32api.GetCurrentProcessId())
	except ValueError, e:
		log("Strange, this proxy wasn't in the process list.\n")
		pass

	if pids:
		for pid in pids:
			log("Attempting to terminate pid "+str(pid)+"...\n")
			handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid)
			win32api.TerminateProcess(handle,0)
			win32api.CloseHandle(handle)
	else:
		log("No external proxies found.\n")
	
if __name__ == '__main__':
	# Kill the other proxies:
	kill_external_proxy()
	if len(sys.argv) >= 2 and sys.argv[1] == '--kill':
		log("Exiting.\n")
		raise SystemExit
	elif len(sys.argv) >= 2 and sys.argv[1] == '--help':
		print __doc__ % {'PORT':PORT}
		print
		print "Version: " + __version__
		raise SystemExit

	# get the port if specified
	if len(sys.argv) >= 2:
		PORT = int(sys.argv[1])

	if len(sys.argv) > 3 :	# 3th param: the next-step HTTP proxy can specified here (overrides the environment variable)
		os.environ['http_proxy'] = sys.argv[3]
	# display which proxy we're using
	http_proxy = os.environ.get('http_proxy')
	if not http_proxy :
		http_proxy = os.environ.get('HTTP_PROXY')
	
	if http_proxy :
		log("Next hop proxy: %s\n" % http_proxy, 0)
		scheme, netloc, path, params, query, fragment = urlparse.urlparse(http_proxy)
		# set host and port to the proxy
		if ':' in netloc:
			host, port = string.split(netloc, ':')
			port = string.atoi(port)
		else:
			host = netloc
			port = 80
		
		# do a basic checks to prevent a proxy loop
		if sameHost(host, port, ADDR_TO_BIND_TO, PORT):
			raise SystemExit, "Next hop proxy cannot be myself"

	ps = AsyncHTTPProxyServer(PORT)
	log("Starting service...\n")
	
	asyncore.loop()

