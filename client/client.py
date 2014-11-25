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
	requestAcknowledged=False
	packet_size=20
	window_size = 7
	fullyTransmitted=False
	message = "This entire message must reach the server completely intact, hopefully it does this properly, this is just to add more to it in an attempt to mess with it"



	def __init__(self, port, dest_port, dest_ip):

		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.client_socket.bind(('', port))
		self.port=port
		self.dest_port=dest_port
		self.dest_ip=dest_ip
	#def connect(dest_port, dest_ip):

	def connect(self, port, dest_port, dest_ip, get, post):
		self.client_socket.settimeout(2)
		ack_packet_sequence_number = None
		while not self.synacked:
			try: 	
				p=packet(port, dest_port, self.seq_num, 0, 1, 0, 0, 0, 0, 0, 0, 1234, 50, '')
				#these can remain hardcoded, these will stay constant for the beginning, but later on must change
				#checksum must be calculated for original packets, and flow control window must be updated later
				packed = pack('iiiiiiiiiiiiis', port, dest_port, self.seq_num, 0, 1, 0, 0, 0, 0, 0, 0, 1234, 50, '')
				self.client_socket.sendto(packed, ('', 4001))
				response, address = self.client_socket.recvfrom(512)
				response = unpack('iiiiiiiiiiiiis', response)
				#perform checksum for ack
				#check to see if syn and ack AND values for sequence number and ack fields match with what we expect
				ack_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
				self.expected_sequence_number=ack_packet.seq_num
				if ack_packet.syn==1 and ack_packet.ack==1 and ack_packet.ack_num==(p.seq_num+1):
					self.synacked=True
					self.seq_num+=1
					while not self.connected:
						try:
							connectionPacket = pack('iiiiiiiiiiiiis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 0, 0, get, post, 1234, 50, '')
							self.client_socket.sendto(connectionPacket, ('', 4001))
							shouldBeNull, addr = self.client_socket.recvfrom(512)
							continue
						except socket.timeout:
							print 'nothing came through in 2 seconds, we are now connected'
							self.connected=True
							self.expected_sequence_number+=1
							if get:
								self.receiveMessage()
							elif post:
								self.sendMessage()
							break
			except socket.timeout:
				continue


	def send_get_or_post(self, get, post):
		#need to add logic such that first data goes with ack for synack, but if this packet is lost, we will get another synack
		#essentially, we fire off a packet, we listen for an incoming one, if nothing comes, we resend
		print 'begin sending message after successful connection'
		if(get):
			while not self.requestAcknowledged:
				try:
					getPacket = pack('iiiiiiiiiiiiis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 1, 0, 321, 50, 'get request')
					self.client_socket.sendto(getPacket, ('', 4001))
					response, address = self.client_socket.recvfrom(512)
					#check for corruption
					response = unpack('iiiiiiiiiiiiis', response)
					ack_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
					if ack_packet.ack==1 and ack_packet.ack_num==(self.seq_num+1):
						self.requestAcknowledged=True
						self.expected_sequence_number+=1
						self.receiveMessage(response)
				except socket.timeout:
					continue


		elif(post):
			while not self.requestAcknowledged:
				try:
					postPacket = pack('iiiiiiiiiiiiis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 0, 1, 321, 50, 'post request')
					self.client_socket.sendto(postPacket, ('', 4001))
					response, address = self.client_socket.recvfrom(512)
					#check for corruption
					response = unpack('iiiiiiiiiiiiis', response)
					ack_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
					if ack_packet.ack==1 and ack_packet.ack_num==(self.seq_num+1):
						self.requestAcknowledged=True
						self.sendMessage()
				except socket.timeout:
					continue

	def receiveMessage(self):
		message=""
		dataReceived = False
		lastInOrderPacket=0
		messageEntirelyReceived = False
		#must ack first, next value will be data
		print 'ready to receive data from get request'
		while not dataReceived:
			try:
				data, address = self.client_socket.recvfrom(512)
				payload = data[4*13:]
				print payload
				unpackingOffset = len(payload)
				unpackingFormat = 'iiiiiiiiiiiii'+str(unpackingOffset)+'s'
				#check for corruption
				request = unpack(unpackingFormat, data)
				client_packet=packet(request[0], request[1], request[2], request[3], request[4], request[5], request[6], request[7], request[8], request[9], request[10], request[11], request[12], request[13])
				message+=client_packet.data
				lastInOrderPacket+=1
				if client_packet.last:
					response = pack('iiiiiiiiiiiiis', 4001, 4000, self.seq_num, lastInOrderPacket+self.expected_sequence_number, 0, 1, 0, 0, 0, 0, 0, 1432, 50, 'ack data')
					self.client_socket.sendto(response, ('', 4001))
				print message
				#check if data is corrupted, if it is, send a NACK
			except socket.timeout:
				continue

	def sendMessage(self):
		print 'will now send message'
		packets = self.packetize(self.message, self.packet_size)
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
				toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 0, 0, 1234, 50, packet)
				if i == upperBound-1:
					toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 1, 0, 0, 1234, 50, packet)
				self.client_socket.sendto(toSend, ('', 4001))
				self.seq_num+=1
			ack, address = self.client_socket.recvfrom(512)
			response = unpack('iiiiiiiiiiiiis', ack)
			#ack_packet = packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
			lastPacketInOrder = response[3]
			self.seq_num=lastPacketInOrder+offset
			if response[3]==len(packets)+offset:
				self.fullyTransmitted=True
			#check for corruption, if so timeout and resend entire window




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





client_object = client(4000, 7000, '143.215.129.100')
client_object.connect(4000, 4001, '', 1, 0)







