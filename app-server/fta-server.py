import sys
sys.path.append('../server')
from server import *

class appserver:
	
	def __init__(self):
		self.port = 0
		# Network address of NetEmu
		self.dest_port = 0
		self.dest_ip = 0
		self.server_socket = 0

		self.terminated = False
		self.connected = False

		while (not self.connected):

			inputs = raw_input('>>> ')
			inputs = inputs.split()

			if (inputs[0] == 'fta-server'):
				if (len(inputs) == 4):
					self.port = int(inputs[1])
					self.dest_ip = inputs[2]
					self.dest_port	= int(inputs[3])
				elif (len(inputs) == 3):
					self.port = int(inputs[1])
					self.dest_ip = ''
					self.dest_port	= int(inputs[2])

				self.server_socket = server(self.port, self.dest_port, self.dest_ip)
				self.startServer()

		self.running()

	def startServer(self):
		connected = self.server_socket.connect() #Same as listen
		self.connected = connected

	def running(self):

		while not self.terminated:

			inputs = raw_input('>>> (Type y to continue): ')
			inputs = inputs.split()

			if (inputs[0] == 'y'):
				message = self.server_socket.receive()
				print message
				vals = message.split('/')

				if (vals[0] == 'post'):
					# print "Post Received"
					filename = vals[1]
					data = message[len(vals[0]) + 1 + len(vals[1]) + 1:]

					f = open(filename, 'w')
					f.write(data)
					f.close()

				elif (vals[0] == 'get'):

					filename = vals[1]
					f = open(filename, 'rb')
					data = f.read()
					f.close()
					self.server_socket.sendMessage(data)

				elif (vals[0] == 'window'):

					window_size = int(vals[1])
					self.server_socket.setWindowSize(window_size)


server = appserver()

