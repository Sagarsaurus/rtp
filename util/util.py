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
		data += self.int2bin(packet.nack).encode('utf-8')
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

		retVal = int2bin(self.int2bin((sum2 << 8) | sum1))

		if (len(retVal) < 16):
			retVal = (16 - len(retVal))*'0' + retVal

		return retVal

	def int2bin(self, n):
	    res = ''
	    while n > 0:
	        res += str(n & 1)
	        n = n >> 1     
	    return res[::-1]




# f = open('../app-client/file.txt', "rb");
# stream = 'file.txt'.encode('utf-8') + '/' + f.read();
# print stream

# u = util()
# print u.checksum(stream)

# f.close();



