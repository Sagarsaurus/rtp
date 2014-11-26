import socket
from struct import *

# Packet Header
class packet:

	def __init__(self, src_port, dest_port, seq_num, ack_num, syn, ack, nack, fin, last, get, post, checksum, fcw, data):
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
		self.get=get
		self.post=post
		self.checksum = checksum
		self.fcw = fcw
		self.data = data


class server:
	expected_seq_number=0
	expected_ack_number=0
	seq_num=100
	connected = False
	server_socket = None
	requestAcknowledged=False
	entireMessageReceived=False
	window_size=7
	packet_size = 20
	message = "This entire message must reach the server completely intact, hopefully it does this properly, this is just to add more to it in an attempt to mess with it"
	fullyTransmitted=False


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
		response = unpack('iiiiiiiiiiiiis', p)
		client_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
		firstDataReceived=None
		#check checksum
		#make sure all values match up: is syn packet, then assign acknum field with seq+1
		while not self.connected:
			try:
				if client_packet.syn==1:
					expected_seq_number=client_packet.seq_num+1
					expected_ack_number=self.seq_num+1
					#acceptable for this packet to be hardcoded right now but later on it must be replaced with more variables
					response = pack('iiiiiiiiiiiiis', 4001, 4000, self.seq_num, client_packet.seq_num+1, 1, 1, 0, 0, 0, 0, 0, 1432, 50, '')
					self.server_socket.sendto(response, ('', 8000))
					checkPacket, address = self.server_socket.recvfrom(512)
					self.seq_num+=1
					self.expected_seq_number+=1
					#check again for corruption
					response = unpack('iiiiiiiiiiiiis', checkPacket)
					print response
					client_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])

				elif client_packet.ack==1:
					print 'yay we are connected'
					self.connected=True
					self.expected_seq_number+=1
					self.server_socket.recvfrom(512)


			except socket.timeout:
				if client_packet.get:
					self.sendMessage()
					break
				elif client_packet.post:
					self.receive()
					break
				continue
		

	def beginTransmission(self):
		print "yay we're connected"
		while True:
			request, address = self.server_socket.recvfrom(512)
			request = unpack('iiiiiiiiiiiiis', request)
			#check for corruption here
			self.expected_seq_number+=1
			request_packet=packet(request[0], request[1], request[2], request[3], request[4], request[5], request[6], request[7], request[8], request[9], request[10], request[11], request[12], request[13])
			if request_packet.get:
				print 'organize data and send first packet back'
				self.sendMessage()
				break
			elif request_packet.post:
				print 'send back ack within receive and begin looping'
				self.receive()
				break

	def sendMessage(self):
		print 'packing and sending packets'
		packets = self.packetize(self.message, self.packet_size)
		print packets
		lastPacketInOrder = self.seq_num
		offset = self.seq_num
		upperBound = lastPacketInOrder+self.window_size-offset
		while not self.fullyTransmitted:
			if lastPacketInOrder+self.window_size-offset>len(packets):
				upperBound=len(packets)
			else:
				upperBound = lastPacketInOrder+self.window_size-offset
			for i in range(lastPacketInOrder-offset, upperBound):
				packingSetup = 'iiiiiiiiiiiii'
				packet = packets[i]
				packingSetup+=str(len(packet))+'s'
				toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 0, 0, 0, 0, 0, 0, 1234, 50, packet)
				if i == upperBound-1:
					toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 0, 0, 0, 1, 0, 0, 1234, 50, packet)
				self.server_socket.sendto(toSend, ('', 8000))
				self.seq_num+=1
				print toSend
			ack, address = self.server_socket.recvfrom(512)
			response = unpack('iiiiiiiiiiiiis', ack)
			#ack_packet = packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
			lastPacketInOrder = response[3]
			self.seq_num=lastPacketInOrder
			if response[3]==len(packets)+offset:
				self.fullyTransmitted=True
		#we need to make sure this gets there by listening for an ack, then we just need to pipeline sending and that's all that's necessary


	def receive(self):
		message=""
		dataReceived = False
		lastInOrderPacket=0
		messageEntirelyReceived = False
		#must ack first, next value will be data
		print 'ready to receive data from post request'
		while not dataReceived:
			try:
				data, address = self.server_socket.recvfrom(512)
				payload = data[4*13:]
				unpackingOffset = len(payload)
				unpackingFormat = 'iiiiiiiiiiiii'+str(unpackingOffset)+'s'
				#check for corruption
				request = unpack(unpackingFormat, data)
				print request
				client_packet=packet(request[0], request[1], request[2], request[3], request[4], request[5], request[6], request[7], request[8], request[9], request[10], request[11], request[12], request[13])
				message+=client_packet.data
				lastInOrderPacket+=1
				if client_packet.last:
					response = pack('iiiiiiiiiiiiis', 4001, 4000, self.seq_num, lastInOrderPacket+self.expected_seq_number, 0, 1, 0, 0, 0, 0, 0, 1432, 50, 'ack data')
					self.server_socket.sendto(response, ('', 8000))
				print message
				#check if data is corrupted, if it is, send a NACK
			except socket.timeout:
				continue
				
		#while not messageEntirelyReceived:

	def packetize(self, message, packet_size):
		numOfFullPackets = len(message)/packet_size
		index = 0
		packets = []
		for i in range(numOfFullPackets):
			packets.append(message[index : index + packet_size])
			index+=packet_size
		if index < len(message):
			packets.append(message[index:])

		return packets



		#self.expected_seq_number+=1

		#must loop here to handle potential packet loss
		#received = False
		# Just initialized
		#message = None

		#while not received:

			# Check if the data is a packet or not
			#p, address = self.server_socket.recvfrom(512)
			#response = unpack('iiiiiiiiiiis', p)
			#syn_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11])


			# Perform checksum stuff
			# init random seq_num
			#seq_num = 0 #initialize to random
			#checksum = 0 #Need to calculate
			#fcw = 0# Need to init
			#data = 0 #Need to init

			#if (data.syn == 1):
			#	ack_packet = packet(port, dest_port, seq_num, data.seq_num + 1, 1, 1, 0, 0, 0, checksum, fcw, data)
			#	server_socket.sendto(ack_packet, address)


s = server(4001, 7000, "143.215.129.100");
s.connect()
