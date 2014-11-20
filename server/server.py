import socket

# Packet Header
class packet:

	def __init__(self, src_port, dest_port, seq_num, ack_num, syn, ack, nack, fin, last, checksum, fcw, data):
		# fcw = flow control window
		self.src_port = src_port
		self.dest_port = dest_port
		self.seq_num = seq_num
		self.ack_num = ack_num
		self.syn = syn
		self.ack = ack
		self.nack = nack
		self.fin = fin
		self.last = last
		self.checksum = checksum
		self.fcw = fcw
		self.data = data


class server:

	connected = False
	server_socket = None

	def __init__(self, port, dest_port, dest_ip):

		self.port = port
		self.dest_port = dest_port
		self.dest_ip = dest_ip

		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			self.server_socket.bind(('', 4001))
		except:
			print "failed bind"


	def receive(self):
		print 'got here'

		received = False
		# Just initialized
		message = None

		while not received:

			# Check if the data is a packet or not
			p, address = self.server_socket.recvfrom(512)

			# Perform checksum stuff
			# init random seq_num
			seq_num = 0 #initialize to random
			checksum = 0 #Need to calculate
			fcw = 0# Need to init
			data = 0 #Need to init

			#if (data.syn == 1):
			#	ack_packet = packet(port, dest_port, seq_num, data.seq_num + 1, 1, 1, 0, 0, 0, checksum, fcw, data)
			#	server_socket.sendto(ack_packet, address)

			print p


s = server(4001, 7000, "143.215.129.100");
s.receive()
