__author__ = 'mcornelio'

import socket
import sys
import threading
from paramsdict import paramsdict

class synapse_tcp_server:
	sock = None

	def __init__(self, port):
		def start_server():
			def handle_client(connection):
				print >>sys.stderr, 'client.open(%s)' % connection
				try:
					msg = ''
					while True:
						print >>sys.stderr, 'connection.recv',
						data = connection.recv(4096)
						if data:
							print >>sys.stderr, 'recv>%s' % data
							msg = msg + data
							if msg.endswith('\n\n'):
								try:
									pd = paramsdict(msg)
									pd.ack()
									#print >>sys.stderr, 'End of message'
									connection.sendall(pd._string())
								except:
									print >>sys.stderr, 'msg error'
									break;
								finally:
									msg = ''
						else:
							break
				finally:
					print >>sys.stderr, 'client.close(%s)' % connection.client_address
					connection.close()

			print >>sys.stderr, 'starting up on %s port %s' % self.server_address
			self.sock.bind(self.server_address)
			self.sock.listen(1)

			while True:
				print >>sys.stderr, 'Waiting for a connection'
				connection, client_address = self.sock.accept()
				print >>sys.stderr, 'client connected:', client_address
				thread = threading.Thread(target=handle_client,args=(connection,))
				thread.daemon = True
				thread.start()

		# Create a TCP/IP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Bind the socket to the address given on the command line
		self.server_name = '0.0.0.0'
		self.port = port
		self.server_address = (self.server_name, self.port)

		self.server_thread = threading.Thread(target=start_server)
		self.server_thread.daemon = True
		self.server_thread.start()

if __name__ == '__main__':
	x = synapse_tcp_server(10000)