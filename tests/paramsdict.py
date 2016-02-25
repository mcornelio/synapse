__author__ = 'mcornelio'


class paramsdict(object):
	hash = {}
	def __init__(self, msg):
		lines = msg.rstrip('\n').split('\n')
		self.head = lines[0];
		self.action = self.head.split('.').pop().lower()
		self.body = lines[1:]
		self.hash = {}
		for i in range(0,len(self.body)):
			pos = self.body[i].index(":")
			key = self.__key(self.body[i][:pos])
			val = self.body[i][pos+1:]
			self.hash[key] = val

	def ack(self):
		if not self.head.endswith('.ack'):
			self.head = self.head + '.ack'

	def __key(self,key):
		return key.strip().lower()

	def __getitem__(self, key):
		fkey = self.__key(key)
		if fkey in self.hash:
			return self.hash[fkey]

	def __setitem__(self, key, value):
		fkey = self.__key(key)
		self.hash[fkey] = value
		return value

	def __repr__(self):
		return self._string()

	def _string(self):
		result = self.head + '\n'
		for key in self.hash:
			result = result + "{}:{}\n".format(key,self.hash[key])
		return result + '\n'

