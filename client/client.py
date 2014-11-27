import socket
from struct import *
import sys
sys.path.append('../util')
from util import *

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
		while not self.synacked:
			try: 	
				#these can remain hardcoded, these will stay constant for the beginning, but later on must change
				#checksum must be calculated for original packets, and flow control window must be updated later
				initialPacket = packet(port, dest_port, self.seq_num, 0, 1, 0, 0, 0, 0, 0, 0, '', 50, 's')
				packed = pack('iiiiiiiiiii16sis', port, dest_port, self.seq_num, 0, 1, 0, 0, 0, 0, 0, 0, self.u.checksum(initialPacket), 50, 's')
				self.client_socket.sendto(packed, ('', 8000))
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
							finalConnectionPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 0, 0, get, post, '', 50, 'a')
							connectionPacket = pack('iiiiiiiiiii16sis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number+1, 0, 1, 0, 0, 0, get, post, self.u.checksum(finalConnectionPacket), 50, 'a')
							self.client_socket.sendto(connectionPacket, ('', 8000))
							shouldBeNull, addr = self.client_socket.recvfrom(512)
							continue
						except socket.timeout:
							print 'nothing came through in 2 seconds, we are now connected'
							self.connected=True
							self.seq_num+=1
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
					getPacket = pack('iiiiiiiiiii16sis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 1, 0, 321, 50, 'get request')
					self.client_socket.sendto(getPacket, ('', 8000))
					response, address = self.client_socket.recvfrom(512)
					#check for corruption
					response = unpack('iiiiiiiiiii16sis', response)
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
					postPacket = pack('iiiiiiiiiii16sis', self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 0, 1, 321, 50, 'post request')
					self.client_socket.sendto(postPacket, ('', 8000))
					response, address = self.client_socket.recvfrom(512)
					#check for corruption
					response = unpack('iiiiiiiiiii16sis', response)
					ack_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
					if ack_packet.ack==1 and ack_packet.ack_num==(self.seq_num+1):
						self.requestAcknowledged=True
						self.sendMessage()
				except socket.timeout:
					continue

	def receiveMessage(self):
		self.client_socket.settimeout(2)
		message=""
		dataReceived = False
		lastInOrderPacket=0
		messageEntirelyReceived = False
		#must ack first, next value will be data
		print 'ready to receive data from get request'
		while not messageEntirelyReceived:
			try:
				data, address = self.client_socket.recvfrom(512)
				payload = data[(4*12+16):]
				unpackingOffset = len(payload)
				unpackingFormat = 'iiiiiiiiiii16si'+str(unpackingOffset)+'s'
				#check for corruption
				request = unpack(unpackingFormat, data)
				#print request
				server_packet=packet(request[0], request[1], request[2], request[3], request[4], request[5], request[6], request[7], request[8], request[9], request[10], request[11], request[12], request[13])
				if server_packet.checksum != self.u.checksum(server_packet):
					continue
				if server_packet.seq_num==self.expected_sequence_number:
					self.expected_sequence_number+=1
					message+=server_packet.data
					if server_packet.last:
						messageEntirelyReceived=True
					print message
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
				self.client_socket.sendto(response, ('', 8000))
				continue

		return message

	def sendMessage(self, message):
		self.client_socket.settimeout(10)
		print 'will now send message'
		packets = self.u.packetize(self.message, self.packet_size)
		lastPacketInOrder = self.seq_num
		offset = self.seq_num
		upperBound = lastPacketInOrder+self.window_size-offset
		while not self.fullyTransmitted:
			if lastPacketInOrder+self.window_size-offset>len(packets):
				upperBound=len(packets)
			else:
				upperBound = lastPacketInOrder+self.window_size-offset
			for i in range(lastPacketInOrder-offset, upperBound):
				packingSetup = 'iiiiiiiiiii16si'
				item = packets[i]
				packingSetup+=str(len(item))+'s'
				if i == upperBound-1:
					toSendPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 1, 0, 0, '', 50, item)
					toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 1, 0, 0, self.u.checksum(toSendPacket), 50, item)
				else:					
					toSendPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 0, 0, '', 50, item)
					toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_sequence_number, 0, 0, 0, 0, 0, 0, 0, self.u.checksum(toSendPacket), 50, item)
				self.client_socket.sendto(toSend, ('', 8000))
				self.seq_num+=1
			ack, address = self.client_socket.recvfrom(512)
			response = unpack('iiiiiiiiiii16sis', ack)
			ack_packet = packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
			if ack_packet.checksum != self.u.checksum(ack_packet):
				continue			
			lastPacketInOrder = response[3]
			self.seq_num=lastPacketInOrder
			if response[3]==len(packets)+offset:
				self.fullyTransmitted=True
			#check for corruption, if so timeout and resend entire window



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







