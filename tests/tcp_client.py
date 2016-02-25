__author__ = 'mcornelio'

import socket
import sys
import math
from paramsdict import *

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port on the server given by the caller
server_address = (sys.argv[1], 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:

	for i in range(0,999):
		message = 'python.set-cell\nvar:key%d\nval:%g\n\n' % (i,(i*math.pi))
		print >>sys.stderr, 'sending>%s' % message,
		sock.sendall(message)
		msg = ''
		while not msg.endswith('\n\n'):
			#print >>sys.stderr, 'sock.recv ...',
			data = sock.recv(4096)
			#print >>sys.stderr, '[' + data + '] ok'
			if not data:
				break
			msg = msg + data;

		pd = paramsdict(msg)
		#lines = msg.rstrip('\n').split('\n')
		#head = lines[0];
		#body = lines[1:]
		#hash = {};
		#for i in range(0,len(body)):
		#	pos = body[i].index(":")
		#	key = body[i][:pos]
		#	val = body[i][pos+1:]
		#	hash[key] = val
		print >>sys.stderr, 'received>%s' % pd

finally:
	sock.close()
