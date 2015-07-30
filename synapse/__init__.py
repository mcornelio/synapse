import sys
import os
import time
import logging
import socket
import string
from urlparse import urlparse
from decorator import decorator
import collections
import logging


class nexus_client_interface(object):

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

def nexus_emergency_exit(status=1, msg=None, ):
	"""Force an exit"""
	if msg:
		print msg
	os._exit(status)

@decorator
def nexus_trace_log_info(f, *args, **kw):
	global nexus
	nexus.logger.info("calling %s with args %s, %s" % (f.__name__, args, kw))
	return f(*args, **kw)

class nexus_dictionary(collections.MutableMapping):
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

nexus = nexus_dictionary()
nexus.process_id = "%s-%d" % (socket.gethostname(), os.getpid())
nexus.title = "Synapse Console Interface v1.0"
nexus.prompts = {'ps1':'sc> ', 'ps2':'.... '}
nexus.exit_prompt = "Use exit() plus Return to exit."
nexus.dict_list = []
nexus.log_file = 'synapse.log'
nexus.log_level = logging.WARNING

def nexus_logger(name, file=nexus.log_file, level=nexus.log_level):
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

def nexus_log():
	global logger
	return logger;

class nexus_cell_dictionary(nexus_dictionary,nexus_client_interface):
	"""Nexus Dictionary with Formulas and Guards"""

	__formulas__ = nexus_dictionary()
	__guards__ = nexus_dictionary()
	__props__ = nexus_dictionary()
	__engine__ = None
	
	def set_formula(self, name, formula):
		if formula == None:
			del self.__formulas__[name]
		else:
			self.__formulas__[name] = formula

	def set_guard(self, name, guard):
		if guard == None:
			del self.__guards__[name]
		else:
			self.__guards__[name] = guard

	def set_cell(self, key, value):
		self.__setitem__(key, value)
		return self.__getitem__(key, value)

	def get_cell(self, key, value=None):
		return self.__getitem__(key, value)

	def set_prop(self, key, prop, value):
		key = self.__keytransform__(key)
		if not(key in self.__props__):
			self.__props__[key] = nexus_dictionary()
		props = self.__props__[key]
		props[prop] = value
		return props[prop]

	def get_prop(self, key, prop):
		key = self.__keytransform__(key)
		if not(key in self.__props__):
			self.__props__[key] = nexus_dictionary()
		props = self.__props__[key]
		if (prop in props):
			return props[prop]
		else:
			return None

	def get_props(self, key, prop):
		key = self.__keytransform__(key)
		if not(key in self.__props__):
			self.__props__[key] = nexus_dictionary()
		return self.__props__[key]

	def __getitem__(self, key, value=None):
		key = self.__keytransform__(key)
		if key in self.__formulas__:
			self.store[key] = self.__formulas__[key](key,value)
		if not(key in self.store):
			self.store[key] = None
		return self.store[key]

	def __setitem__(self, key, value):
		if key in self.__guards__:
			self.store[key] = self.__guards__[key](key,value)
		else:
			self.store[self.__keytransform__(key)] = value

	def __delitem__(self, key):
		key = self.__keytransform__(key)
		if key in self.__formulas__:
			del self.__formulas__[key]
		if key in self.__guards__:
			del self.__guards__[key]
		if not(key in self.store):
			return None
		del self.store[self.__keytransform__(key)]

def nexus_create_cell_engine():
	"""Create a new CellEngine"""
	global nexus
	tmp = nexus_cell_dictionary()
	nexus.dict_list.append(tmp)
	return tmp

def nexus_append_dictionary(engine):
	"""Add the specified engine to the engine list"""
	nexus.dict_list.append(engine)

def nexus_get_current_dictionary():
	"""Return the current CellEngine"""
	global nexus
	last_index = len(nexus.dict_list) - 1
	if last_index < 0:
		return nexus_create_cell_engine()
	else:
		return nexus.dict_list[last_index]

def exit(status=0):
	os._exit(status)

def quit(status=0):
	exit(status)

def wait_for_ctrlc(seconds=1):
	try:
		while True:
			time.sleep(seconds)
	except KeyboardInterrupt:
		pass

class nexus_cell_engine(object):

	def __set(self,key,value):
		self.__dict__[key] = value

	def __get(self,key):
		return self.__dict__[key]

	def __init__(self,cells=None):

		if not cells:
			cells = nexus_get_current_dictionary()
		if not isinstance(cells,nexus_client_interface):
			raise RuntimeError("%s is not a subclass of NEXUS_AbstractClient" % type(cells))
		self.__set('__cells', cells)

	def cells(self):
		return self.__get('__cells')
	
	def get_cell(self,key,value=None):
		return self.__get('__cells').get_cell(key,value)
	
	def set_cell(self,key,value=None):
		return self.__get('__cells').set_cell(key,value)

	def set_formula(self,key,formula):
		return self.cells().set_formula(key,formula)

	def set_guard(self,key,guard):
		return self.cells().set_guard(key,guard)
	
	def set_prop(self,key,prop,value):
		return self.cells().set_prop(key,prop,value)
	
	def get_prop(self,key,prop):
		return self.cells().get_prop(key,prop)
	
	def __delattr__(self,key):
		del self.cells()[key]

	def __getattr__(self, key):
		return self.__get('__cells').get_cell(key)

	def __setattr__(self, key, value):
		return self.__get('__cells').set_cell(key, value)

	def __getitem__(self, key):
		return self.__get('__cells').get_cell(key)

	def __setitem__(self, key, value):
		return self.__get('__cells').set_cell(key, value)

	def __len__(self):
		return len(self.cells())
	
	def close():
		pass
	
def nexus_help():
	print string.replace("""
	#++
	# Nexus Adapters can act as servers or clients
	# or both servers and clients simultaneously
	#--
	=============( Server )==============
	# Start nexus http service
	c = nexus_server(port=port, host=host)
	
	# Set an get arbitrary cell value
	c.mycell = 3.14159
	my_value = my_eng.mycell
	
	=============( Client )==============
	# Connect to remote nexus http service
	r = nexus_connect(port=port, host=host)

	# Get arbitrary cell velues remotely
	v = r.mycell

	# Set arbitrary cell velues remotely
	r.mycell = 3.1416
	
	""", '\t', '')
	
nexus.dict = nexus_get_current_dictionary
nexus.cells = nexus_cell_engine
nexus.help = nexus_help
nexus_dict = nexus_get_current_dictionary
nexus_cells = nexus_cell_engine

#############################

import cherrypy
import json
import requests
import threading

nexus.http = nexus_dictionary()
nexus.http.port = 8888
nexus.http.host = "127.0.0.1"

logger = nexus_logger('http')
protocol = 'http'


class nexus_http_root_service(object):

	def __init__(self,title="Nexus Web Service"):
		self.__title = title

	@cherrypy.expose
	def index(self):
		return self.__title

class nexus_http_rest_service(object):

	exposed = True
	name = 'rest'
	vdir = '/rest'
	conf = {
		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
		'tools.sessions.on': True,
		'tools.response_headers.on': True,
		'tools.response_headers.headers': [('Content-Type', 'application/json')]
	}

	__cells = nexus_get_current_dictionary()

	def __init__(self,name=None, conf=None):
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

class nexus_http_server(object):
	"""Starts a local Nexus HTTP Web Service."""

	thread = None
	root = None
	conf = None
	rest = None

	def __init__(self,port=nexus.http.port,title='Nexus Web Service',log_screen=False,services=[]):
		self.root = nexus_http_root_service("%s on port %d" % (title, port))
		self.rest = nexus_http_rest_service('rest')
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
			#cherrypy.log.access_file - 'nexus.http.log'
			cherrypy.log.access_log.level = logging.INFO
			cherrypy.log.error_log.level = logging.ERROR
			cherrypy.log.screen = log_screen
			cherrypy.server.socket_host = '0.0.0.0'
			cherrypy.server.socket_port = port
			cherrypy.quickstart(self.root, '/', self.conf)

		self.thread = threading.Thread(target=worker)
		self.thread.daemon = True
		self.thread.start()

class nexus_http_client(nexus_client_interface):
	"""Creates a new HTTP Client"""

	__url__ = None
	response = None
	trust_env = False

	def __init__(self, port=nexus.http.port, host=nexus.http.host, trust_env=False):
		self.trust_env = trust_env
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
		data = {'action':'get_cell', 'key':key, 'value':value}
		self.response = requests.get(self.__url__, params={'data':json.dumps(data)})
		return self.__response()

	def set_cell(self, key, value=None):
		"""Set the contents of the cell"""
		data = {'action':'set_cell', 'key':key, 'value':value}
		self.response = requests.post(self.__url__, data={'data':json.dumps(data)})
		return self.__response()

	def get_prop(self, key, prop, value=None):
		"""Returns the contents of the cell"""
		data = {'action':'get_prop', 'key':key, 'prop':prop, 'value':value}
		self.response = requests.get(self.__url__, params={'data':json.dumps(data)})
		return self.__response()

	def set_prop(self, key, prop, value=None):
		"""Set the contents of the cell"""
		data = {'action':'set_prop', 'key':key, 'prop':prop, 'value':value}
		self.response = requests.post(self.__url__, data={'data':json.dumps(data)})
		return self.__response()

	def RaiseError(self):
		raise requests.exceptions.HTTPError(404)

def nexus_http_cell_engine(port=nexus.http.port, host=nexus.http.host, trust_env=False):
	"""Returns a cell engine from a new HTTP_Client"""
	return nexus_cell_engine(nexus_http_client(port=port, host=host, trust_env=trust_env))

nexus.http.service = nexus_http_server
nexus.http.cells = nexus_http_cell_engine

def nexus_server(port=nexus.http.port):
	nexus_http_server(port)
	return nexus_cell_engine()

def nexus_client(port=nexus.http.port, host=nexus.http.host):
	return nexus_http_cell_engine(port,host)

synapse_server = nexus_server
synapse_client = nexus_client
