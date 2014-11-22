import socket
from struct import *

# # creating the socket for TCP
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # variables
# connected = False


# if (not connected):
# 	connect()



class client:
	expected_sequence_number=0
	seq_num=1
	expected_ack_number=0
	connected = False
	client_socket = None
	port=0
	dest_port=0
	dest_ip=0
	synacked=False



	def __init__(self, port, dest_port, dest_ip):

		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.client_socket.bind(('', port))
		self.port=port
		self.dest_port=dest_port
		self.dest_ip=dest_ip
	#def connect(dest_port, dest_ip):

	def connect(self, port, dest_port, dest_ip):
		self.client_socket.settimeout(2)
		ack_packet_sequence_number = None
		while not self.synacked:
			try: 	
				p=packet(port, dest_port, 1, 0, 1, 0, 0, 0, 0, 1234, 50, 'syn packet')
				#these can remain hardcoded, these will stay constant for the beginning, but later on must change
				#checksum must be calculated for original packets, and flow control window must be updated later
				packed = pack('iiiiiiiiiiis', port, dest_port, 1, 0, 1, 0, 0, 0, 0, 1234, 50, 'syn packet')
				expected_ack_number=2
				self.client_socket.sendto(packed, ('', 4001))
				response, address = self.client_socket.recvfrom(512)
				response = unpack('iiiiiiiiiiis', response)
				#perform checksum for ack
				#check to see if syn and ack AND values for sequence number and ack fields match with what we expect
				ack_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11])
				expected_sequence_number=ack_packet.seq_num
				if ack_packet.syn==1 and ack_packet.ack==1 and ack_packet.ack_num==(p.seq_num+1):
					self.synacked=True
					while not self.connected:
						try:
							connectionPacket = pack('iiiiiiiiiiis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 0, 0, 1234, 50, 'final connection')
							self.client_socket.sendto(connectionPacket, ('', 4001))
							shouldBeNull, addr = self.client_socket.recvfrom(512)
							continue
						except socket.timeout:
							print 'nothing came through in 2 seconds, we are now connected'
							self.connected=True
							break
			except socket.timeout:
				continue
		self.send_message()

	def send_message(self):
		#need to add logic such that first data goes with ack for synack, but if this packet is lost, we will get another synack
		#essentially, we fire off a packet, we listen for an incoming one, if nothing comes, we resend
		print 'begin sending message after successful connection'




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





client_object = client(4000, 7000, '143.215.129.100')
client_object.connect(4000, 4001, '')







