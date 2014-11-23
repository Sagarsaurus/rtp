

class appclient:

	def __init__(self):

		disconnected = False;

		while (not disconnected):

			inputs = raw_input('>>> ');
			inputs = inputs.split();

			if (inputs[0] == 'connect'):
				self.connect();

			elif (inputs[0] == 'post'):
				self.post(inputs[1]);

			elif (inputs[0] == 'disconnect'):
				disconnected = True;

			

	def connect(self):
		#TODO implement
		return;

	def post(self, filename):

		f = open(filename, "rb");
		stream = filename.encode('utf-8') + '/' + f.read();
		f.close();

		# Need to init the client from the Transport layer

	def decodeMessage(self, message):

		message = message.split('/');

		f = open(message[0], 'w');
		f.write(message[1]);
		f.close();




client = appclient();
