import socket

# # creating the socket for TCP
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # variables
# connected = False


# if (not connected):
# 	connect()



class client:

	connected = False
	client_socket = None
	port=0
	dest_port=0
	dest_ip=0


	def __init__(self, port, dest_port, dest_ip):

		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.client_socket.bind(('', port))
		self.port=port
		self.dest_port=dest_port
		self.dest_ip=dest_ip
	#def connect(dest_port, dest_ip):

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

p = packet(4000, 4001, 1, 0, 0, 0, 0, 0, 0, 1234, 0, "message")
client_object = client(4000, 7000, '143.215.129.100')
client_object.client_socket.sendto(p.data, (client_object.dest_ip, client_object.dest_port))











