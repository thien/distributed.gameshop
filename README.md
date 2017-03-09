# Game Shop

_A simple Python based Gameshop using Sockets and Distributed Systems_

## Prequisites

You will need `Pyro4` and `Python3`. In order to run the programs, you will first need to create several terminal windows (one for the nameserver, at least one for the server(s), one for the front end and at least one for the client(s)). Each of the terminal windows will need to set their directory to be the folder containing the files (where this README.md is found). If you are testing it for grading purposes I have initialised my servers to broadcast themselves on `localhost`. This may interfere with other servers from other students if they are currently running.

## Initialisation

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

The system should now work. In the event that you wish to shut down a server you can either close the terminal window or input `CTRL-C` when the window i selected. 