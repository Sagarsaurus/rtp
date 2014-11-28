import sys
sys.path.append('../client')
from client import *

class appclient:

	def __init__(self):

		self.port = 0
		# Network address of NetEmu
		self.dest_port = 0
		self.dest_ip = 0
		self.client_socket = 0
		self.established = False
		self.disconnected = False
		# Valid arguments to create a client with a given destination
		args_valid = False

		while (not self.disconnected):

			inputs = raw_input('>>> ')
			inputs = inputs.split()

			if (inputs[0] == 'fta-client'):
				if (len(inputs) == 4):
					self.port = int(inputs[1])
					self.dest_ip = inputs[2]
					self.dest_port = int(inputs[3])
					args_valid = True

				# elif(len(inputs) == 3):
				# 	self.port = int(inputs[1])
				# 	self.dest_ip = ''
				# 	self.dest_port = int(inputs[2])
				# 	args_valid = True

			elif (inputs[0] == 'connect'):
				if (args_valid):
					self.client_socket = self.connect()

			elif (inputs[0] == 'post'):
				self.post(inputs[1])

			elif (inputs[0] == 'disconnect'):
				self.disconnected = True

	def connect(self):

		client_socket = client(self.port, self.dest_port, self.dest_ip)
		established = client_socket.connect(self.port, self.dest_port, self.dest_ip, 0, 0)
		if (established):
			return client_socket
			self.established = established
		else:
			return None

	def post(self, filename):

		f = open(filename, "rb");
		stream = filename.encode('utf-8') + '/' + f.read();
		f.close();
		if (self.established):
			if (self.client_socket.connect(self.port, self.dest_port, self.dest_ip, 0, 1)):
				self.client_socket.sendMessage(stream)


		# Need to init the client from the Transport layer

	def decodeMessage(self, message):

		message = message.split('/')

		f = open(message[0], 'w')
		f.write(message[1])
		f.close()




client = appclient();
