"""Securely roll an n-sided die between two parties.
usage: python secroll.py [alice|bob] n"""

__author__ = "Aaron Swartz <http://www.aaronsw.com/>"
__thanks__ = {"Raph Levien": "found several security holes"}
__license__ = "(C) 2002 Aaron Swartz. GNU GPL 2."
__version__ = "2.01" # added some TODOs

# The algorithm is my own invention, an extension of the
# secure coin-flipping algorithm in _Applied Cryptography_.
# 
# I suspect it's secure, but I'm not certain. If you think
# you've found a flaw or bug or have or have seen other comments
# about this code or algorithm, please let me by emailing
# secroll@aaronsw.com. Thanks!
#
# TODO: expand to m-players (due to Wes Felter)
#       each player picks a number, distributes, reveals, and sums mod n
# TOOD: add networking code
#       now you can play by wrapping alice and bob in tcpserver/tcpconnect

import sha, sys
hashf = sha.new
hashbytes = 20

def randnum(length): return stoi(open("/dev/urandom").read(length))

def stoi(s): # Thanks, Raph!
	result = 0L
	for i in xrange(len(s)): result = (result << 8) + ord(s[i])
	return result

def alice(n):
	print n
	assert n == int(sys.stdin.readline().strip())
	
	#@@ Raph points tiny bias at edges...
	num = randnum(hashbytes)
	
	print hashf(`num`).hexdigest()
	sys.stdout.flush()

	guess = int(sys.stdin.readline().strip())
	assert 0 <= guess < n

	print num
	sys.stdout.flush()
	return abs((num%n) - guess)
		
def bob(n):
	print n
	sys.stdout.flush()
	assert int(sys.stdin.readline().strip()) == n
	
	hashn = sys.stdin.readline().strip()
	#@@ need to fix:
	guess = random.randrange(0, n)
	print guess
	sys.stdout.flush()
	
	num = int(sys.stdin.readline().strip())
	assert hashf(`num`).hexdigest() == h
	
	return abs((num%n) - g)

if __name__ == "__main__":
	if len(sys.argv) == 3:
		n = int(sys.argv[2])
		if sys.argv[1] == "alice":
			sys.stderr.write(`alice(n)`)
		elif sys.argv[1] == "bob":
			sys.stderr.write(`bob(n)`)
		else:
			print __doc__
	else:
		print __doc__
	
