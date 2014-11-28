import socket
from struct import *
import sys
sys.path.append('../util')
from util import *
from packet import *

class server:
	expected_seq_number=0
	expected_ack_number=0
	seq_num=100
	state = None
	connected = False
	server_socket = None
	requestAcknowledged=False
	entireMessageReceived=False
	window_size=7
	packet_size = 20
	message = "This entire message must reach the server completely intact, hopefully it does this properly, this is just to add more to it in an attempt to mess with it"
	fullyTransmitted=False
	u=None


	def __init__(self, port, dest_port, dest_ip):

		self.port = port
		self.dest_port = dest_port
		self.dest_ip = dest_ip
		self.u = util()
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			self.server_socket.bind(('', port))
		except:
			print "failed bind"

	def connect(self):
		syncPacket = None
		requestAcknowledged = False
		requestHandled = False
		self.server_socket.settimeout(2)
		while True:
			try:
				p, address = self.server_socket.recvfrom(512)
				response = unpack('iiiiiiiiiii16sis', p)
				client_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
				if client_packet.checksum != self.u.checksum(client_packet):
					client_packet=None
				break
			except socket.timeout:
				continue	
		#check checksum
		#make sure all values match up: is syn packet, then assign acknum field with seq+1
		while not self.connected:
			try:
				if client_packet is None:
					nextPacket, address = self.server_socket.recvfrom(512)
					response = unpack('iiiiiiiiiii16sis', nextPacket)
					client_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
					if client_packet.checksum!=self.u.checksum(client_packet):
						client_packet=None
						continue

				elif client_packet.syn==1:
					self.expected_seq_number=client_packet.seq_num+1
					self.expected_ack_number=self.seq_num+1
					#acceptable for this packet to be hardcoded right now but later on it must be replaced with more variables
					responsePacket = packet(4001, 4000, self.seq_num, client_packet.seq_num+1, 1, 1, 0, 0, 0, 0, 0, '', 50, 'a')
					response = pack('iiiiiiiiiii16sis', 4001, 4000, self.seq_num, client_packet.seq_num+1, 1, 1, 0, 0, 0, 0, 0, self.u.checksum(responsePacket), 50, 'a')
					self.server_socket.sendto(response, ('', self.dest_port))
					checkPacket, address = self.server_socket.recvfrom(512)
					self.seq_num+=1
					#check again for corruption
					response = unpack('iiiiiiiiiii16sis', checkPacket)
					temp_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
					if temp_packet.checksum != self.u.checksum(temp_packet):
						continue
					client_packet = temp_packet

				elif client_packet.ack==1:
					print 'yay we are connected'
					self.connected=True
					self.expected_seq_number+=1
					self.server_socket.recvfrom(512)
					return True

			except socket.timeout:
				continue


		client_packet = None
		while not requestAcknowledged:
			try:
				if client_packet is None:
					nextPacket, address = self.server_socket.recvfrom(512)
					response = unpack('iiiiiiiiiii16sis', nextPacket)
					client_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
					if client_packet.checksum!=self.u.checksum(client_packet):
						client_packet=None
						continue

				elif client_packet.sync==1:
					self.expected_seq_number=client_packet.seq_num+1
					self.expected_ack_number=self.seq_num+1
					#acceptable for this packet to be hardcoded right now but later on it must be replaced with more variables
					responsePacket = packet(4001, 4000, self.seq_num, client_packet.seq_num+1, 0, 1, 1, 0, 0, 0, 0, '', 50, 'a')
					response = pack('iiiiiiiiiii16sis', 4001, 4000, self.seq_num, client_packet.seq_num+1, 0, 1, 1, 0, 0, 0, 0, self.u.checksum(responsePacket), 50, 'a')
					self.server_socket.sendto(response, ('', self.dest_port))
					checkPacket, address = self.server_socket.recvfrom(512)
					self.seq_num+=1
					#check again for corruption
					response = unpack('iiiiiiiiiii16sis', checkPacket)
					temp_packet=packet(response[0], response[1], response[2], response[3], response[4], response[5], response[6], response[7], response[8], response[9], response[10], response[11], response[12], response[13])
					if temp_packet.checksum != self.u.checksum(temp_packet):
						continue
					client_packet = temp_packet

				elif client_packet.ack==1:
					if client_packet.get:
						self.state = 'post'
					else:
						self.state = 'post'
					print 'yay fixed state'
					requestAcknowledged=True
					self.expected_seq_number+=1
					self.server_socket.recvfrom(512)
					return True

			except socket.timeout:
				continue


	def sendMessage(self, message):
		if not self.connected:
			print 'You cannot send a message without connecting first'
			return False
		self.server_socket.settimeout(10)
		print 'will now send message'
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
					if i == upperBound-1:
						toSendPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 0, 0, 0, 1, 0, 0, '', 50, item)
						toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 0, 0, 0, 1, 0, 0, self.u.checksum(toSendPacket), 50, item)
					else:					
						toSendPacket = packet(self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 0, 0, 0, 0, 0, 0, '', 50, item)
						toSend = pack(packingSetup, self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 0, 0, 0, 0, 0, 0, self.u.checksum(toSendPacket), 50, item)
					self.server_socket.sendto(toSend, ('', self.dest_port))
					self.seq_num+=1
				ack, address = self.server_socket.recvfrom(512)
				response = unpack('iiiiiiiiiii16sis', ack)
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

	def receive(self):
		if not self.connected:
			print "You cannot receive a message without connecting first"
			return False
		self.server_socket.settimeout(2)
		message=""
		dataReceived = False
		lastInOrderPacket=0
		messageEntirelyReceived = False
		#must ack first, next value will be data
		print 'ready to receive data from post request'
		while not messageEntirelyReceived:
			try:
				data, address = self.server_socket.recvfrom(512)
				payload = data[(4*12+16):]
				unpackingOffset = len(payload)
				unpackingFormat = 'iiiiiiiiiii16si'+str(unpackingOffset)+'s'
				#check for corruption
				request = unpack(unpackingFormat, data)
				print request
				#print request
				client_packet=packet(request[0], request[1], request[2], request[3], request[4], request[5], request[6], request[7], request[8], request[9], request[10], request[11], request[12], request[13])
				if client_packet.checksum != self.u.checksum(client_packet):
					continue
				if client_packet.seq_num==self.expected_seq_number:
					self.expected_seq_number+=1
					message+=client_packet.data
					if client_packet.last:
						messageEntirelyReceived=True
					print message
				else:
					#force timeout due to all packets
					while True:
						self.server_socket.recvfrom(512)
					#continue
				#check if data is corrupted, if it is, send a NACK
			except socket.timeout:
				responsePacket = packet(self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 1, 0, 0, 0, 0, 0, '', 50, 'a')
				response = pack('iiiiiiiiiii16sis', self.port, self.dest_port, self.seq_num, self.expected_seq_number, 0, 1, 0, 0, 0, 0, 0, self.u.checksum(responsePacket), 50, 'a')
				#print response
				self.server_socket.sendto(response, ('', self.dest_port))
				continue

		return message

server_object = server(4001, 8000, '')
server_object.connect()
server_object.connect()
message = server_object.receive()
print message
server_object.sendMessage("This entire message must reach the server completely intact, hopefully it does this properly, this is just to add more to it in an attempt to mess with it")
