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