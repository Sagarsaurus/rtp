import sys
sys.path.append('../server')
from server import *

class appserver:

	terminated = False
	
	def __init__(self):
		self.port = 0
		# Network address of NetEmu
		self.dest_port = 0
		self.dest_ip = 0
		self.server_socket = 0

		terminated = False

		while (not terminated):

			inputs = raw_input('>>> ')
			inputs = inputs.split()

			if (inputs[0] == 'fta-server'):
				self.port = inputs[1]
				self.dest_ip = inputs[2]
				self.dest_port	= inputs[3]

				self.server_socket = server(self.port, self.dest_port, self.dest_ip)

			elif (inputs[0] == 'terminate')
				terminated = True

