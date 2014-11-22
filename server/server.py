import socket
from struct import *

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
	expected_seq_number=0
	expected_ack_number=0
	seq_num=100
	connected = False
	server_socket = None

	def __init__(self, port, dest_port, dest_ip):

		self.port = port
		self.dest_port = dest_port
		self.dest_ip = dest_ip

		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			self.server_socket.bind(('', port))
		except:
			print "failed bind"

	def connect(self):
		self.server_socket.settimeout(2)
		p, address = self.server_socket.recvfrom(512)
		response = unpack('iiiiiiiiiiis', p)
		client_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11])
		firstDataReceived=None
		#check checksum
		#make sure all values match up: is syn packet, then assign acknum field with seq+1
		while not self.connected:
			try:
				if client_packet.syn==1:
					expected_seq_number=client_packet.seq_num+1
					expected_ack_number=self.seq_num+1
					#acceptable for this packet to be hardcoded right now but later on it must be replaced with more variables
					response = pack('iiiiiiiiiiis', 4001, 4000, self.seq_num, client_packet.seq_num+1, 1, 1, 0, 0, 0, 1432, 50, 'synack packet')
					self.server_socket.sendto(response, ('', 4000))
					checkPacket, address = self.server_socket.recvfrom(512)
					self.seq_num+=1
					firstDataReceived=checkPacket
					#check again for corruption
					response = unpack('iiiiiiiiiiis', checkPacket)
					print response
					client_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11])

				elif client_packet.ack==1:
					self.connected=True

			except socket.timeout:
				continue
		self.beginTransmission(firstDataReceived)

	def beginTransmission(self, firstData):
		print "yay we're connected"





	def receive(self):

		received = False
		# Just initialized
		message = None

		while not received:

			# Check if the data is a packet or not
			p, address = self.server_socket.recvfrom(512)
			response = unpack('iiiiiiiiiiis', p)
			syn_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11])


			# Perform checksum stuff
			# init random seq_num
			seq_num = 0 #initialize to random
			checksum = 0 #Need to calculate
			fcw = 0# Need to init
			data = 0 #Need to init

			#if (data.syn == 1):
			#	ack_packet = packet(port, dest_port, seq_num, data.seq_num + 1, 1, 1, 0, 0, 0, checksum, fcw, data)
			#	server_socket.sendto(ack_packet, address)


s = server(4001, 7000, "143.215.129.100");
s.connect()
