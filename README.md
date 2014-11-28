rtp
===

Running instructions

We had trouble connecting the the server so you'll have to run the NetEmu server locally. Start the NetEmu server on any port. Let's call that neport.

Application Server:
	Navigate to app-server
	In terminal type:

		python fta-server.py
		>>> 
		Options:
			1. fta-server 4001 (or another odd port) '' neport 
			(You'll need to connect a client, which will take you to a prompt like this, until then it's blocked here)
			2. terminate -> will terminate the server

		>>> (Type y to continue):
			Options:
			1. y -> you'll go to receive for any client related work like post, get, disconnect
			2. window size -> The window will be set to the size value
			3. terminate -> Will not terminate until client is terminated

Application Client:
	Navigate to app-server
	In terminal type:
		python fta-client.py
		>>>
		Options:
			1. fta-client 4000 (or another even port) '' neport
			2. connect
			3. post filename (file has to be in directory)
			4. get filename (file has to be in severs directory)
			5. window size -> The window will be set to the size value
			6. disconnect




