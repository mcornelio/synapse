__author__ = 'mcornelio'

import sys
import SocketServer
from paramsdict import *

class MyTCPHandler(SocketServer.StreamRequestHandler):
	"""
	The request handler class for our server.

	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	"""

	def handle(self):
		# self.request is the TCP socket connected to the client
		client = "%s:%s" % (self.client_address[0], self.client_address[1])
		print "connect({})".format(client)
		buf = ""
		cnt = 0
		while(True):
			self.data = self.rfile.readline()
			if not self.data: break
			buf = buf + self.data
			if buf.endswith('\n\n'):
				try:
					pd = paramsdict(buf)
					pd.ack()
					self.wfile.write(pd._string())
				except:
					print 'invalid message:{}'.format(buf)
					break;
				finally:
					cnt = cnt + 1
					buf = ''
		print "disconnect({}); {} messages".format(client,cnt)

if __name__ == "__main__":
	HOST, PORT = "0.0.0.0", 10000

	# Create the server, binding to localhost on port 9999
	server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print ' ... KeyboardInterrupt received -- exiting'
