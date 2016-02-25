__author__ = 'mcornelio'

class synapse_dictionary(object):
	"""Parses or creates a synapse_message"""
	def __init__(self, msg=None):
		if (not msg == None):
			self.msg_dict = self.parse(msg)

	def parse(self,msg):
		if (not msg.endswith('\n\n')):
			raise Exception("Invalid message terminator. Message does not end with \\n\\n")
		self.lines = lines = msg.rstrip('\n').split('\n')
