import socket
from struct import *
import sys
sys.path.append('../util')
from util import *
from packet import *
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
	u=None
	message = "This entire message must reach the server completely intact, hopefully it does this properly, this is just to add more to it in an attempt to mess with it"
	finacked = False
	closed = False



	def __init__(self, port, dest_port, dest_ip):

		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.client_socket.bind(('', port))
		self.port=port
		self.dest_port=dest_port
		self.dest_ip=dest_ip
		self.u=util()
	#def connect(dest_port, dest_ip):

	def connect(self, port, dest_port, dest_ip, get, post):
		self.client_socket.settimeout(2)
		ack_packet_sequence_number = None
		requestAcknowledged = False
		requestHandled = False
		while not self.synacked:
			try: 	
				#these can remain hardcoded, these will stay constant for the beginning, but later on must change
				#checksum must be calculated for original packets, and flow control window must be updated later
				initialPacket = packet(port, dest_port, self.seq_num, 0, 1, 0, 0, 0, 0, 0, 0, '', 50, 's')
				packed = pack('iiiiiiiiiii16sis', port, dest_port, self.seq_num, 0, 1, 0, 0, 0, 0, 0, 0, self.u.checksum(initialPacket), 50, 's')
				self.client_socket.sendto(packed, ('', dest_port))
				response, address = self.client_socket.recvfrom(512)
				response = unpack('iiiiiiiiiii16sis', response)
				#perform checksum for ack
				#check to see if syn and ack AND values for sequence number and ack fields match with what we expect
				ack_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
				if ack_packet.checksum != self.u.checksum(ack_packet):
					continue
				self.expected_sequence_number=ack_packet.seq_num
				if ack_packet.syn==1 and ack_packet.ack==1 and ack_packet.ack_num==(initialPacket.seq_num+1):
					self.synacked=True
					self.seq_num+=1
					while not self.connected:
						try:
							finalConnectionPacket = packet(port, dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 0, 0, get, post, '', 50, 'a')
							connectionPacket = pack('iiiiiiiiiii16sis', port, dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 0, 0, get, post, self.u.checksum(finalConnectionPacket), 50, 'a')
							self.client_socket.sendto(connectionPacket, ('', self.dest_port))
							shouldBeNull, addr = self.client_socket.recvfrom(512)
							continue
						except socket.timeout:
							print 'Nothing came through in 2 seconds, we are now connected'
							self.connected=True
							self.seq_num+=1
							self.expected_sequence_number+=1

			except socket.timeout:
				continue

			if self.synacked and self.connected:
				return True
			else:
				return False


	def receiveMessage(self):
		if not self.connected:
			print "You cannot receive a message without connecting first"
			return False
		self.client_socket.settimeout(2)
		message=""
		dataReceived = False
		lastInOrderPacket=0
		messageEntirelyReceived = False
		#must ack first, next value will be data
		#print 'ready to receive data from post request'
		while not messageEntirelyReceived:
			try:
				data, address = self.client_socket.recvfrom(512)
				payload = data[(4*12+16):]
				unpackingOffset = len(payload)
				unpackingFormat = 'iiiiiiiiiii16si'+str(unpackingOffset)+'s'
				#check for corruption
				request = unpack(unpackingFormat, data)
				#print request
				client_packet=packet(request[0], request[1], request[2], request[3], request[4], request[5], request[6], request[7], request[8], request[9], request[10], request[11], request[12], request[13])
				if client_packet.checksum != self.u.checksum(client_packet):
					continue
				if client_packet.seq_num==self.expected_sequence_number:
					self.expected_sequence_number+=1
					message+=client_packet.data
					if client_packet.last:
						messageEntirelyReceived=True
				else:
					#force timeout due to all packets
					while True:
						self.client_socket.recvfrom(512)
					#continue
				#check if data is corrupted, if it is, send a NACK
			except socket.timeout:
				responsePacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 1, 0, 0, 0, 0, 0, '', 50, 'a')
				response = pack('iiiiiiiiiii16sis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 1, 0, 0, 0, 0, 0, self.u.checksum(responsePacket), 50, 'a')
				#print response
				self.client_socket.sendto(response, ('', self.dest_port))
				continue

		return message

	def sendMessage(self, message):
		if not self.connected:
			print 'You cannot send a message without connecting first!'
			return False
		self.client_socket.settimeout(10)
		self.fullyTransmitted=False
		print 'Will now send message'
		packets = self.u.packetize(message, self.packet_size)
		lastPacketInOrder = self.seq_num
		offset = self.seq_num
		upperBound = lastPacketInOrder+self.window_size-offset
		while not self.fullyTransmitted:
			try:
				if lastPacketInOrder+self.window_size-offset>len(packets):
					upperBound=len(packets)
				else:
					upperBound = lastPacketInOrder+self.window_size-offset
				for i in range(lastPacketInOrder-offset, upperBound):
					packingSetup = 'iiiiiiiiiii16si'
					item = packets[i]
					packingSetup+=str(len(item))+'s'
					if i == len(packets)-1:
						toSendPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 1, 0, 0, '', 50, item)
						toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 1, 0, 0, self.u.checksum(toSendPacket), 50, item)
					else:					
						toSendPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 0, 0, '', 50, item)
						toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 0, 0, self.u.checksum(toSendPacket), 50, item)
					self.client_socket.sendto(toSend, ('', self.dest_port))
					self.seq_num+=1
				ack, address = self.client_socket.recvfrom(512)
				unpackingFormat = 'iiiiiiiiiii16si'+str(len(ack[4*12+16:]))+'s'
				response = unpack(unpackingFormat, ack)
				ack_packet = packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
				if ack_packet.checksum != self.u.checksum(ack_packet):
					continue			
				lastPacketInOrder = response[3]
				self.seq_num=lastPacketInOrder
				if response[3]==len(packets)+offset:
					self.fullyTransmitted=True
			except socket.timeout:
				if self.fullyTransmitted:
					return True
				else:
					return False
			#check for corruption, if so timeout and resend entire window

	def setWindowSize(self, window_size):
		self.window_size = window_size

	def close(self):
		self.client_socket.settimeout(2)
		while not self.finacked:
			try: 	
				initialPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 1, 0, 0, 0, '', 50, 's')
				packed = pack('iiiiiiiiiii16sis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 1, 0, 0, 0, self.u.checksum(initialPacket), 50, 's')
				self.client_socket.sendto(packed, ('', self.dest_port))
				response, address = self.client_socket.recvfrom(512)
				response = unpack('iiiiiiiiiii16sis', response)
				#perform checksum for ack
				#check to see if syn and ack AND values for sequence number and ack fields match with what we expect
				ack_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
				if ack_packet.checksum != self.u.checksum(ack_packet):
					continue
				if ack_packet.fin==1 and ack_packet.ack==1 and ack_packet.ack_num==(initialPacket.seq_num+1):
					self.finacked=True
					self.seq_num+=1
					while not self.closed:
						try:
							fin, address = self.client_socket.recvfrom(512)
							fin = unpack('iiiiiiiiiii16sis', fin) 
							fin_packet=packet(fin[0], fin[1], fin[2], fin[3], fin[4], fin[5], fin[6], fin[7], fin[8], fin[9], fin[10], fin[11], fin[12], fin[13])
							if fin_packet.checksum != self.u.checksum(fin_packet):
								continue
							finAckPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 1, 0, 0, 0, '', 50, 'a')
							connectionPacket = pack('iiiiiiiiiii16sis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 1, 0, 0, 0, self.u.checksum(finAckPacket), 50, 'a')
							while True:
								try:
									self.client_socket.sendto(connectionPacket, ('', self.dest_port))
									shouldBeNull, addr = self.client_socket.recvfrom(512)
								except socket.timeout:
									self.closed=True
									self.client_socket.close()
									print 'closed'
									return True
									
						except socket.timeout:
							continue

			except socket.timeout:
				continue

			if self.synacked and self.connected:
				return True
			else:
				return False

#client_object = client(4000, 8000, '')
#client_object.connect(4000, 8000, '', 0, 0)
# # client_object.connect(4000, 8000, '', 0, 1)
#client_object.sendMessage("This entire message must reach the server completely intact, hopefully it does this properly, this is just to add more to it in an attempt to mess with it")
# message = client_object.receiveMessage()
# print message
#client_object.close()


