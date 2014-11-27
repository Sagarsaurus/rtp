class util:

	def checksum(self, data):
		sum1 = 0
		sum2 = 0

		for i in range(0, len(data)):

			sum1 = (sum1 + ord(data[i])) % 255
			sum2 = (sum1 + sum2) % 255

		return self.int2bin((sum2 << 8) | sum1)

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



