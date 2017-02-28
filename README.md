# distributed.gameshop

A simple Python based Gameshop using Sockets and Distributed Systems

To run the program, we'll need to start by initialising `nameserver.py` before running our servers.

	python3 nameserver.py

Then, the servers can now be initialised; you can initialise any number of servers you want. I normally choose three, so I would initialise three python instances of `server.py`.

	# on each terminal window
	python3 server.py

All the servers will default to being an backup server. `frontend.py` will then configure one of the servers to be a primary server, once initialised. This will also create a socket server for a client to communicate with.

	python3 frontend.py

Now, the client program is ready to be run; `client.py` will only interact with `frontend.py`, and `frontend.py` will only interact with a primary instance of `server.py`. The backup servers will only interact with the primary server.

To run the client program, type the following:

	python3 client.py

The system should now work.