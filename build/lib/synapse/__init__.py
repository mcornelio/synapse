import sys
import os
import time
import logging
import socket
import string
import collections
import logging
import atexit

__version__ = "1.1.19"
__all__ = ['main','amqp']

class client_interface(object):

	def get_cell(self, key, value=None):
		"""Returns the contents of the cell"""
		raise NotImplementedError("""get_cell(self, key, value=None)""")

	def set_cell(self, key, value=None):
		"""Set the contents of the cell"""
		raise NotImplementedError("""set_cell(self, key, value=None)""")

	def get_prop(self, key, prop, value=None):
		"""Returns the contents of the cell"""
		raise NotImplementedError("""get_prop(self, key, prop, value=None)""")

	def set_prop(self, key, prop, value=None):
		"""Set the contents of the cell"""
		raise NotImplementedError("""set_prop(self, key, prop, value=None)""")

def emergency_exit(status=1, msg=None, ):
	"""Force an exit"""
	if msg:
		print msg
	os._exit(status)

def trace_log_info(f, *args, **kw):
	"""Trace function invocation"""
	logger.info("calling %s with args %s, %s" % (f.__name__, args, kw))
	return f(*args, **kw)

class base_dictionary(collections.MutableMapping):
	"""A dictionary that applies an arbitrary key-altering
	function before accessing the keys"""

	def __init__(self, *args, **kwargs):
		self.store = dict()
		self.update(dict(*args, **kwargs))  # use the free update to set keys

	def __getitem__(self, key):
		return self.store[self.__keytransform__(key)]

	def __setitem__(self, key, value):
		self.store[self.__keytransform__(key)] = value

	def __delitem__(self, key):
		del self.store[self.__keytransform__(key)]

	def __iter__(self):
		return iter(self.store)

	def __len__(self):
		return len(self.store)

	def __keytransform__(self, key):
		return key.lower()

synapse = base_dictionary()
synapse_process_id = "%s-%d" % (socket.gethostname(), os.getpid())
synapse_title = "Synapse Console Interface v" + __version__
synapse_ps1 = 'sc> '
synapse_ps2 = '.... '
synapse_prompts = {'ps1':'sc> ', 'ps2':'.... '}
synapse_exit_prompt = "Use exit() plus Return to exit."
synapse_dict_list = []
synapse_sheets = {}
synapse_current_cell_engine_context = None
synapse_current_cell_engine = None
get_logger_file = 'synapse.log'
get_logger_level = logging.WARNING

def initialize_logger(name, file=get_logger_file, level=get_logger_level):
# create logger with 'name'
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	# create file handler which logs even debug messages
	if file:
		fh = logging.FileHandler(file)
		fh.setLevel(logging.DEBUG)
	# create console handler with a higher log level
	ch = logging.StreamHandler()
	ch.setLevel(level)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	if file:
		fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	# add the handlers to the logger
	if file:
		logger.addHandler(fh)
	logger.addHandler(ch)
	return logger

def get_logger():
	"""Returns the current logger"""
	global logger
	return logger;

class cell_dictionary(base_dictionary,client_interface):
	"""synapse Dictionary with Formulas and Guards"""

	__formulas__ = base_dictionary()
	__guards__ = base_dictionary()
	__props__ = base_dictionary()
	__engine__ = None
	
	def set_formula(self, name, formula):
		"""
		Sets the formula function for a cell.
		:param name: the name of the cell as string
		:param formula: a function that takes (key,value) where key=cell, value an optional value
		:return: None
		"""
		if formula == None:
			del self.__formulas__[name]
		else:
			self.__formulas__[name] = formula

	def set_guard(self, name, guard):
		"""
		Sets a guard function for a cell.
		:param name: the name of the cell as string
		:param guard: a function that takes (key,value) where key=cell, and value=value for the cell
		:return: None
		"""
		if guard == None:
			del self.__guards__[name]
		else:
			self.__guards__[name] = guard

	def set_cell(self, key, value):
		"""
		Set the value of a cell
		:param key: the name of the cell
		:param value: the value for the cell
		:return: the current value cell
		"""
		self.__setitem__(key, value)
		return self.__getitem__(key, value)

	def get_cell(self, key, value=None):
		"""
		Returns the current value of a cell
		:param key: the name of the cell as a string
		:param value: an optional value that may be passed to the cell's formula
		:return: the current value of the cell
		"""
		return self.__getitem__(key, value)

	def set_prop(self, key, prop, value):
		"""
		Sets a cell's named property to a value
		:param key: the name of the cell as a string
		:param prop: the name of the property as a string
		:param value: the current value of the property
		:return:
		"""
		key = self.__keytransform__(key)
		if not(key in self.__props__):
			self.__props__[key] = base_dictionary()
		props = self.__props__[key]
		props[prop] = value
		return props[prop]

	def get_prop(self, key, prop):
		"""
		Returns the current value of a cell's property
		:param key: the name of the cell as a string
		:param prop: the name of the property as a string
		:return: the current value of the property
		"""
		key = self.__keytransform__(key)
		if not(key in self.__props__):
			self.__props__[key] = base_dictionary()
		props = self.__props__[key]
		if (prop in props):
			return props[prop]
		else:
			return None

	def get_props(self, key):
		"""
		Returns all the properties of a cell
		:param key: the name of the cell as string
		:param prop:
		:return: all the properties as a string
		"""
		key = self.__keytransform__(key)
		if not(key in self.__props__):
			self.__props__[key] = base_dictionary()
		return self.__props__[key]

	def __getitem__(self, key, value=None):
		"""
		Returns the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: an optional value
		:return: the value of the cell
		"""
		key = self.__keytransform__(key)
		if key in self.__formulas__:
			self.store[key] = self.__formulas__[key](key,value)
		if not(key in self.store):
			self.store[key] = None
		return self.store[key]

	def __setitem__(self, key, value):
		"""
		Sets the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: the new value for the cell
		:return: the value of the cell
		"""
		if key in self.__guards__:
			self.store[key] = self.__guards__[key](key,value)
		else:
			self.store[self.__keytransform__(key)] = value

	def __delitem__(self, key):
		"""
		Deletes a cell when referenced as an item
		:param key: the name of the cell as a string
		:return: None
		"""
		key = self.__keytransform__(key)
		if key in self.__formulas__:
			del self.__formulas__[key]
		if key in self.__guards__:
			del self.__guards__[key]
		if not(key in self.store):
			return None
		del self.store[self.__keytransform__(key)]

def get_cell_engine(context='root'):
	"""Create a new CellEngine"""
	global synapse
	lname = context.lower()
	synapse_current_cell_engine_context = lname
	if lname in synapse_sheets:
		return synapse_sheets[lname]
	synapse_current_cell_engine = synapse_sheets[lname] = cell_dictionary()
	return synapse_current_cell_engine

def wait_for_ctrlc(seconds=1):
	"""
	Wait for ctrlc interrupt from the board
	:param seconds: sleep time per loop in seconds
	:return:
	"""
	try:
		while True:
			time.sleep(seconds)
	except KeyboardInterrupt:
		pass

class cell_engine(object):
	"""
	The Synapse Cell Engine class.
	"""
	def __set(self,key,value):
		"""
		Sets the value of a cell
		:param key: the name of the cell as a string
		:param value: the value for the cell
		:return: None
		"""
		self.__dict__[key] = value

	def __get(self,key):
		"""
		Returns the value of a cell
		:param key: the name of the cell as a string
		:return: the value of the cell
		"""
		return self.__dict__[key]

	def __init__(self,cells=None):
		"""
		Constructor for a Synapse Cell Engine
		:param cells: a client_interface instance. If not specified, set to the current base_dictionary
		"""
		if not cells:
			cells = get_cell_engine()
		if not isinstance(cells,client_interface):
			raise RuntimeError("%s is not a subclass of synapse_AbstractClient" % type(cells))
		self.__set('__cells', cells)

	def cells(self):
		"""
		Returns the cell dictionary for this instance
		"""
		return self.__get('__cells')
	
	def get_cell(self,key,value=None):
		"""
		Returns the current value of a cell
		:param key: the name of the cell as a string
		:param value: an optional value that may be passed to the cell's formula
		:return: the current value of the cell
		"""
		return self.__get('__cells').get_cell(key,value)
	
	def set_cell(self,key,value=None):
		"""
		Set the value of a cell
		:param key: the name of the cell
		:param value: the value for the cell
		:return: the current value cell
		"""
		return self.__get('__cells').set_cell(key,value)

	def set_formula(self,key,formula):
		"""
		Sets the formula function for a cell.
		:param name: the name of the cell as string
		:param formula: a function that takes (key,value) where key=cell, value an optional value
		:return: None
		"""
		return self.cells().set_formula(key,formula)

	def set_guard(self,key,guard):
		"""
		Sets a guard function for a cell.
		:param name: the name of the cell as string
		:param guard: a function that takes (key,value) where key=cell, and value=value for the cell
		:return: None
		"""
		return self.cells().set_guard(key,guard)
	
	def set_prop(self,key,prop,value):
		"""
		Sets a cell's named property to a value
		:param key: the name of the cell as a string
		:param prop: the name of the property as a string
		:param value: the current value of the property
		:return:
		"""
		return self.cells().set_prop(key,prop,value)
	
	def get_prop(self,key,prop):
		"""
		Returns the current value of a cell's property
		:param key: the name of the cell as a string
		:param prop: the name of the property as a string
		:return: the current value of the property
		"""
		return self.cells().get_prop(key,prop)
	
	def get_props(self,key):
		"""
		Returns the current value of a cell's property
		:param key: the name of the cell as a string
		:param prop: the name of the property as a string
		:return: the current value of the property
		"""
		return self.cells().get_props(key)

	def __delattr__(self,key):
		del self.cells()[key]

	def __getattr__(self, key):
		return self.__get('__cells').get_cell(key)

	def __setattr__(self, key, value):
		return self.__get('__cells').set_cell(key, value)

	def __getitem__(self, key):
		"""
		Returns the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: an optional value
		:return: the value of the cell
		"""
		return self.__get('__cells').get_cell(key)

	def __setitem__(self, key, value):
		"""
		Sets the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: the new value for the cell
		:return: the value of the cell
		"""
		return self.__get('__cells').set_cell(key, value)

	def __len__(self):
		"""
		Returns the number of cells in the cell engine.
		"""
		return len(self.cells())
	
	def close(self):
		pass

	
#synapse.cells = cell_engine
#synapse.help = synapse_help
#synapse_dict = base_dictionary
#synapse_cells = cell_engine
synapse_spreadsheet = get_cell_engine

#############################

import cherrypy
import json
import requests
import threading

#synapse.http = base_dictionary()
synapse_http_port = 8888
synapse_http_host = "127.0.0.1"

logger = None
protocol = 'http'


class http_root_service(object):

	def __init__(self,title="synapse Web Service"):
		self.__title = title

	@cherrypy.expose
	def index(self):
		return self.__title

class http_rest_service(object):

	exposed = True
	name = 'rest'
	vdir = '/rest'
	conf = {
		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
		'tools.sessions.on': True,
		'tools.response_headers.on': True,
		'tools.response_headers.headers': [('Content-Type', 'application/json')]
	}

	__cells = get_cell_engine()

	def __init__(self,name=None, conf=None, cells=None):
		if cells:
			__cells = cells
		if name:
			self.name = name
		if conf:
			self.conf = conf
		self.vdir = '/' + self.name

	def __get(self, data):
		j = json.loads(data)
		key = j['key']
		prop = j.get('prop')
		value = j.get('value')
		context = j.get('context')
		if not context or not context in synapse_sheets:
			raise cherrypy.HTTPError("400 Bad Request", "Invalid Context specified (%s)" % context)

		self.__cells = get_cell_engine(context)

		if prop:
			j['value'] = self.__cells.get_prop(key, prop)
		else:
			j['value'] = self.__cells.get_cell(key, value)

		return json.dumps(j)

	def __set(self, data):
		j = json.loads(data)
		key = j['key']
		prop = j.get('prop')
		value = j.get('value')
		context = j.get('context')
		if not context or not context in synapse_sheets:
			raise cherrypy.HTTPError("400 Bad Request", "Invalid Context specified (%s)" % context)

		self.__cells = get_cell_engine(context)

		if prop:
			j['value'] = self.__cells.set_prop(key, prop, value)
		else:
			j['value'] = self.__cells.set_cell(key, value)

		return json.dumps(j)

	@cherrypy.tools.accept(media='text/plain')
	def GET(self, data='{}'):
		return self.__get(data)

	@cherrypy.tools.accept(media='text/plain')
	def POST(self, data='{}'):
		return self.__set(data)

	@cherrypy.tools.accept(media='text/plain')
	def PUT(self, data='{}'):
		return self.__set(data)

	@cherrypy.tools.accept(media='text/plain')
	def DELETE(self, data='{}'):
		jdata = json.loads(data)
		return {"from":"delete", "data":jdata}

http_server_running = False

class http_server(object):
	"""Starts a local synapse HTTP Web Service."""

	thread = None
	root = None
	conf = None
	rest = None

	def __init__(self,port=synapse_http_port,title='synapse Web Service',log_screen=False,services=[]):
		global logger
		global http_server_running

		logger = initialize_logger('http',file="synapse_%d_%d.log" % (port, os.getpid()))

		self.root = http_root_service("%s on port %d" % (title, port))
		self.rest = http_rest_service(name='rest')
		self.root.__setattr__(self.rest.name, self.rest)

		self.conf = {
			'/': {
				'tools.sessions.on': True,
				'tools.staticdir.root': os.path.abspath(os.getcwd())
				},
			self.rest.vdir: self.rest.conf
		}

		for svc in services:
			self.root.__setattr__(svc.name, svc)
			self.conf.__setitem__(svc.vdir, svc.conf)

		def worker():
			#cherrypy.log.access_file - 'synapse.http.log'
			cherrypy.log.access_log.level = logging.INFO
			cherrypy.log.error_log.level = logging.ERROR
			cherrypy.log.screen = log_screen
			cherrypy.server.socket_host = '0.0.0.0'
			cherrypy.server.socket_port = port
			cherrypy.quickstart(self.root, '/', self.conf)

		self.thread = threading.Thread(target=worker)
		self.thread.daemon = True
		self.thread.start()
		http_server_running = True;

class http_client(client_interface):
	"""Creates a new HTTP Client"""

	__url__ = None
	response = None
	trust_env = False
	context = 'root'

	def __init__(self, port=synapse_http_port, host=synapse_http_host, context='root'):
		self.context = context
		if not ('NO_PROXY' in os.environ):
			os.environ['NO_PROXY'] = "127.0.0.1,localhost,%s" % socket.gethostname()
		self.__url__ = "http://%s:%d/rest" % (host, port)

	def __response(self):
		if self.response.status_code == 200:
			null = None
			return json.loads(self.response.text)['value']
		else:
			raise requests.exceptions.HTTPError(self.response.status_code)

	def get_cell(self, key, value=None):
		"""Returns the contents of the cell"""
		data = {'action':'get_cell', 'key':key, 'value':value, 'context':self.context}
		self.response = requests.get(self.__url__, params={'data':json.dumps(data)})
		return self.__response()

	def set_cell(self, key, value=None):
		"""Set the contents of the cell"""
		data = {'action':'set_cell', 'key':key, 'value':value, 'context':self.context}
		self.response = requests.post(self.__url__, data={'data':json.dumps(data)})
		return self.__response()

	def get_prop(self, key, prop, value=None):
		"""Returns the contents of the cell"""
		data = {'action':'get_prop', 'key':key, 'prop':prop, 'value':value, 'context':self.context}
		self.response = requests.get(self.__url__, params={'data':json.dumps(data)})
		return self.__response()

	def set_prop(self, key, prop, value=None):
		"""Set the contents of the cell"""
		data = {'action':'set_prop', 'key':key, 'prop':prop, 'value':value, 'context':self.context}
		self.response = requests.post(self.__url__, data={'data':json.dumps(data)})
		return self.__response()

	def __getitem__(self, key):
		"""
		Returns the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: an optional value
		:return: the value of the cell
		"""
		return self.get_cell(key)

	def __setitem__(self, key, value):
		"""
		Sets the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: the new value for the cell
		:return: the value of the cell
		"""
		return self.set_cell(key, value)

	def RaiseError(self):
		raise requests.exceptions.HTTPError(404)

def http_cell_engine(port=synapse_http_port, host=synapse_http_host, context='root'):
	"""Returns a cell engine from a new HTTP_Client"""
	return cell_engine(http_client(port=port, host=host, context=context))

def _server(port=synapse_http_port):
	return http_server(port)

def _client(port=synapse_http_port, host=synapse_http_host,context='root'):
	return http_cell_engine(port=port,host=host,context=context)

def exit(status=1):
	global logger
	if http_server_running == True:
		cherrypy.engine.exit()
	if logger != None:
		logging.shutdown()
	print("Goodbye from Synapse")
	sys.exit(status)

def main():
	from . import exit
	sys.ps1 = synapse_ps1
	sys.ps2 = synapse_ps2
	print synapse_title
	print synapse_exit_prompt

	sys.tracebacklimit = 0

	try:
		for file in sys.argv[1:]:
			print "execfile(%s)" % file
			execfile(file)
	finally:
		pass

import rpyc
from rpyc.utils.server import ThreadedServer
import threading

synapse_rpc_port = 9999
synapse_rpc_host = "127.0.0.1"


def rpc_server(port):
	"""Create a new RPC Server"""
	class SynapseRpcService(rpyc.Service):

		def on_connect(self):
			"""Called on connection"""
			pass

		def on_disconnect(self):
			"""Called on disconnection"""
			pass

		def exposed_get_cell(self, key, value=None, context='root'): # Get Cell
			x = get_cell_engine(context)
			return x.get_cell(key, value)

		def exposed_set_cell(self, key, value=None, context='root'): # Set Cell
			x = get_cell_engine(context)
			return x.set_cell(key, value)

		def exposed_get_prop(self, key, prop, context='root'):
			x = get_cell_engine(context)
			return x.get_prop(key, prop)

		def exposed_get_props(self, key, context='root'):
			x = get_cell_engine(context)
			return x.get_props(key)

		def exposed_set_prop(self,key, prop, value=None, context='root'):
			x = get_cell_engine(context)
			return x.set_prop(key, prop, value)

	def server_thread():
		ts = ThreadedServer(SynapseRpcService,port=port)
		ts.start()

	t = threading.Thread(target=server_thread)
	t.daemon = True
	t.start()
	return t

class rpc_client(client_interface):
	"""Creates a new RPC Client"""

	__url__ = None
	response = None
	context = 'root'
	conn = None
	host = None
	port = None

	def __connect(self):
		self.conn = rpyc.connect(self.host,self.port)

	def __init__(self, port=synapse_rpc_port, host=synapse_rpc_host, context='root'):
		self.host = host
		self.port = port
		self.context = context
		self.__url__ = "rpc://%s:%d/rest" % (host, port)
		if not ('NO_PROXY' in os.environ):
			os.environ['NO_PROXY'] = "127.0.0.1,localhost,%s" % socket.gethostname()
		self.__connect()

	def get_cell(self, key, value=None):
		"""Returns the contents of the cell"""
		try:
			return self.conn.root.get_cell(key, value, context=self.context)
		except EOFError:
			self.__connect()
			return self.conn.root.get_cell(key, value, context=self.context)

	def set_cell(self, key, value=None):
		"""Set the contents of the cell"""
		try:
			return self.conn.root.set_cell(key, value, context=self.context)
		except EOFError:
			self.__connect()
			return self.conn.root.set_cell(key, value, context=self.context)

	def get_prop(self, key, prop):
		"""Returns the contents of the cell"""
		try:
			return self.conn.root.get_prop(key, prop, context=self.context)
		except EOFError:
			self.__connect()
			return self.conn.root.get_prop(key, prop, context=self.context)

	def get_props(self, key):
		"""Returns the contents of the cell"""
		try:
			return self.conn.root.get_props(key, context=self.context)
		except EOFError:
			self.__connect()
			return self.conn.root.get_props(key, context=self.context)

	def set_prop(self, key, prop, value=None):
		"""Set the contents of the cell"""
		try:
			return self.conn.root.set_prop(key, prop, value, context=self.context)
		except EOFError:
			self.__connect()
			return self.conn.root.set_prop(key, prop, value, context=self.context)

	def __getitem__(self, key):
		"""
		Returns the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: an optional value
		:return: the value of the cell
		"""
		return self.get_cell(key)

	def __setitem__(self, key, value):
		"""
		Sets the value of a cell when referenced as an item
		:param key: the name of the cell as a string
		:param value: the new value for the cell
		:return: the value of the cell
		"""
		return self.set_cell(key, value)

def rpc_cell_engine(port=synapse_http_port, host=synapse_http_host, context='root'):
	"""Returns a cell engine from a new HTTP_Client"""
	return cell_engine(rpc_client(port=port, host=host, context=context))
