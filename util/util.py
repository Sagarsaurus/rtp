from packet import *

class util:

	def checksum(self, packet):
		
		data = ''
		data += self.int2bin(packet.src_port).encode('utf-8')
		data += self.int2bin(packet.dest_port).encode('utf-8')
		data += self.int2bin(packet.seq_num).encode('utf-8')
		data += self.int2bin(packet.ack_num).encode('utf-8')
		data += self.int2bin(packet.syn).encode('utf-8')
		data += self.int2bin(packet.ack).encode('utf-8')
		data += self.int2bin(packet.sync).encode('utf-8')
		data += self.int2bin(packet.fin).encode('utf-8')
		data += self.int2bin(packet.last).encode('utf-8')
		data += self.int2bin(packet.get).encode('utf-8')
		data += self.int2bin(packet.post).encode('utf-8')
		data += self.int2bin(packet.fcw).encode('utf-8')
		data += (packet.data).encode('utf-8')

		sum1 = 0
		sum2 = 0

		for i in range(0, len(data)):

			sum1 = (sum1 + ord(data[i])) % 255
			sum2 = (sum1 + sum2) % 255

		retVal = self.int2bin((sum2 << 8) | sum1)

		if (len(retVal) < 16):
			retVal = (16 - len(retVal))*'0' + retVal

		return retVal

	def int2bin(self, n):
	    res = ''
	    while n > 0:
	        res += str(n & 1)
	        n = n >> 1     
	    return res[::-1]

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



p=packet(1234, 1234, 1234, 0, 1, 0, 0, 0, 0, 0, 0, 1234, 50, '')

u = util()
print u.checksum(p)

# f.close();



