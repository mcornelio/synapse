import sys
import os
import time
import logging
import socket
import string
import collections
import logging

__version__ = "1.1.0"

class synapse_client_interface(object):

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

def synapse_emergency_exit(status=1, msg=None, ):
	"""Force an exit"""
	if msg:
		print msg
	os._exit(status)

def synapse_trace_log_info(f, *args, **kw):
	global synapse
	synapse.logger.info("calling %s with args %s, %s" % (f.__name__, args, kw))
	return f(*args, **kw)

class synapse_dictionary(collections.MutableMapping):
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

synapse = synapse_dictionary()
synapse.process_id = "%s-%d" % (socket.gethostname(), os.getpid())
synapse.title = "Synapse Console Interface v" + __version__
synapse.prompts = {'ps1':'sc> ', 'ps2':'.... '}
synapse.exit_prompt = "Use exit() plus Return to exit."
synapse.dict_list = []
synapse.sheets = {}
synapse.current_cell_engine_context = None
synapse.current_cell_engine = None
synapse.log_file = 'synapse.log'
synapse.log_level = logging.WARNING

def synapse_logger(name, file=synapse.log_file, level=synapse.log_level):
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

def synapse_log():
	global logger
	return logger;

class synapse_cell_dictionary(synapse_dictionary,synapse_client_interface):
	"""synapse Dictionary with Formulas and Guards"""

	__formulas__ = synapse_dictionary()
	__guards__ = synapse_dictionary()
	__props__ = synapse_dictionary()
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
			self.__props__[key] = synapse_dictionary()
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
			self.__props__[key] = synapse_dictionary()
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
			self.__props__[key] = synapse_dictionary()
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

def synapse_get_cell_engine(context='root'):
	"""Create a new CellEngine"""
	global synapse
	lname = context.lower()
	synapse.current_cell_engine_context = lname
	if lname in synapse.sheets:
		return synapse.sheets[lname]
	synapse.current_cell_engine = synapse.sheets[lname] = synapse_cell_dictionary()
	return synapse.current_cell_engine

def exit(status=0):
	"""
	Exit Synapse
	:param status: the status to return to the shell
	:return: does not return
	"""
	os._exit(status)

def quit(status=0):
	"""
	Exit Synapse
	:param status: the status to return to the shell
	:return: does not return
	"""
	exit(status)

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

class synapse_cell_engine(object):
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
		:param cells: a synapse_client_interface instance. If not specified, set to the current synapse_dictionary
		"""
		if not cells:
			cells = synapse_get_cell_engine()
		if not isinstance(cells,synapse_client_interface):
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
	
def synapse_help():
	print string.replace("""
	#++
	# synapse Adapters can act as servers or clients
	# or both servers and clients simultaneously
	#--
	=============( Server )==============
	# Start synapse http service
	c = synapse_server(port=port, host=host)
	
	# Set an get arbitrary cell value
	c.mycell = 3.14159
	my_value = my_eng.mycell
	
	=============( Client )==============
	# Connect to remote synapse http service
	r = synapse_connect(port=port, host=host)

	# Get arbitrary cell velues remotely
	v = r.mycell

	# Set arbitrary cell velues remotely
	r.mycell = 3.1416
	
	""", '\t', '')
	
synapse.cells = synapse_cell_engine
synapse.help = synapse_help
synapse_dict = synapse_dictionary
synapse_cells = synapse_cell_engine
synapse_spreadsheet = synapse_get_cell_engine

#############################

import cherrypy
import json
import requests
import threading

synapse.http = synapse_dictionary()
synapse.http.port = 8888
synapse.http.host = "127.0.0.1"

logger = None
protocol = 'http'


class synapse_http_root_service(object):

	def __init__(self,title="synapse Web Service"):
		self.__title = title

	@cherrypy.expose
	def index(self):
		return self.__title

class synapse_http_rest_service(object):

	exposed = True
	name = 'rest'
	vdir = '/rest'
	conf = {
		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
		'tools.sessions.on': True,
		'tools.response_headers.on': True,
		'tools.response_headers.headers': [('Content-Type', 'application/json')]
	}

	__cells = synapse_get_cell_engine()

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
		if not context or not context in synapse.sheets:
			raise cherrypy.HTTPError("400 Bad Request", "Invalid Context specified (%s)" % context)

		self.__cells = synapse_get_cell_engine(context)

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
		if not context or not context in synapse.sheets:
			raise cherrypy.HTTPError("400 Bad Request", "Invalid Context specified (%s)" % context)

		self.__cells = synapse_get_cell_engine(context)

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

class synapse_http_server(object):
	"""Starts a local synapse HTTP Web Service."""

	thread = None
	root = None
	conf = None
	rest = None

	def __init__(self,port=synapse.http.port,title='synapse Web Service',log_screen=False,services=[]):
		global logger
		logger = synapse_logger('http',file="synapse_%d_%d.log" % (port, os.getpid()))

		self.root = synapse_http_root_service("%s on port %d" % (title, port))
		self.rest = synapse_http_rest_service(name='rest')
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

class synapse_http_client(synapse_client_interface):
	"""Creates a new HTTP Client"""

	__url__ = None
	response = None
	trust_env = False
	context = 'root'

	def __init__(self, port=synapse.http.port, host=synapse.http.host, trust_env=False, context='root'):
		self.trust_env = trust_env
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

#	def __getattr__(self, key):
#		return self.get_cell(key)

#	def __setattr__(self, key, value):
#		return self.set_cell(key, value)

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

def synapse_http_cell_engine(port=synapse.http.port, host=synapse.http.host, trust_env=False, context='root'):
	"""Returns a cell engine from a new HTTP_Client"""
	return synapse_cell_engine(synapse_http_client(port=port, host=host, trust_env=trust_env, context=context))

synapse.http.service = synapse_http_server
synapse.http.cells = synapse_http_cell_engine

def synapse_server(port=synapse.http.port):
	return synapse_http_server(port)

def synapse_client(port=synapse.http.port, host=synapse.http.host,context='root'):
	return synapse_http_cell_engine(port=port,host=host,context=context)
