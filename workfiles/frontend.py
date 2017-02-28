# Front End

# Make Replication Transparent
# Interact with Duplicates
# Maintain the Duplicates
# Send/Receive to Replicas
# Collate Responses
# Make sure client doesnt mess up replicas

# pryo and related imports
import Pyro4
from Pyro4 import naming
import random
import hashlib
import time
import atexit

# socket and related imports
from threading import Thread
from socket import *
import struct

# ------------------------------------
# exit handler in the event that the 
# front end needs to be closed (not a force)
# ------------------------------------

def exterminate_frontend():
	"""
	Exit Handler
	gracefully removes itself from server.
	"""
	socket.close(self)
	print("close front end")
# append exit handler in the event that the front-end is closing
atexit.register(exterminate_frontend)

# ------------------------------------
# Threaded function to run the nameserver.
# ------------------------------------

def init_nameserver():
	Pyro4.naming.startNSloop()

n_server = Thread(target = init_nameserver)


# ------------------------------------
# Methods below are for finding the primary server
# and allocating one in the event that it doesn't
# exist.
# ------------------------------------

# find the name server
ns = Pyro4.locateNS()

# check if no primary servers
primary_server = None

primary_servers = ns.list(metadata_all={"primary"})
backup_servers = ns.list(metadata_all={"backup"})

print("primary servers", primary_servers.keys())
print("backup servers", backup_servers.keys())

if len(primary_servers) is not 0:
	print("theres " + str(len(primary_servers)) + " primary servers")
	if len(primary_servers) is 1:
		primary_server = next (iter (primary_servers.keys()))
else:
	print("theres no primary servers..")
	# if none, choose a primary server from one of the backup servers randomly
	chosen_random_promo = random.choice(list(backup_servers.keys()))
	print("random nominated backup:",chosen_random_promo)
	ns.set_metadata(chosen_random_promo, {"primary"})
	primary_server = chosen_random_promo
	print(primary_server, "has been allocated as the primary")

# use name server object lookup uri shortcut
server = Pyro4.Proxy("PYRONAME:" + primary_server)   



# ------------------------------------
# Methods below are for querying the server
# ------------------------------------

# uid is in the form of a md5(datetime + user_id)
# data is in the form of {user: user_id, request:some_request, data:value}

#req keys: "add", "get_history", "cancel", "peek_db"

# "game" "user" "order_id"

# def hash(msg):
	# return hashlib.md5(msg.encode()).hexdigest()


def queryServer(msg):
	checksum = str(hash(frozenset(msg)))
	time_str = str(time.time())
	uid = hash(time_str + checksum)
	return server.Query(uid, msg)

user_id = 1

msg = {}
data = {}
msg["user"] = user_id
msg['request'] = 'add'

data["game"] = "sausages"
data["order_id"] = 1

msg["data"] = data

resp = queryServer(msg)

print("resp1:",resp['response'])
print("msg1:",resp['message'])

msg['request'] = "get_history"

# resp = queryServer(msg)

# print("resp2:",resp['response'])

# ------------------------------------
# socket functions
# ------------------------------------

# def threaded_function(sock):
# 	# print(args)
# 	password = "shut up"
# 	sock.send("password please")
# 	# receive password
# 	user_entry = sock.recv(1024)
# 	if user_entry == password:
# 		# print ("access granted")
# 		sock.send("1")

# 		# add socket to list of clients
# 		clients[sock] = 0
# 		print (clients)

# 		while clients[sock] < 10:
# 			sentence = sock.recv(1024)
# 			capitalizedSentence = sentence.upper()
# 			sock.send(capitalizedSentence)
# 			clients[sock] += 1
# 			sleep(0.5)

# 		sock.send("You've used all your messages. Go away.")
# 		# print("kicked " + str(addr) + "; Reason: Used all Messages")
# 		del clients[sock];
# 		# print (clients)
# 		sock.close()
# 	else:
# 		print (str(addr) + " is denied")
# 		sock.send("0")
# 		sock.close()


# # ------------------------------------
# # front-end socket initialisation
# # to be used for a client-frontend
# # connection.
# # ------------------------------------

# port = 12036
# multicast_group = ('localhost', port)
# clients = {}

# frontend = socket(AF_INET,SOCK_STREAM)
# frontend.settimeout(0.2)
# ttl = struct.pack('b',1)
# frontend.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
# frontend.bind(("", port))

# frontend.listen(1)
# print("Front End Server is ready to receive goods.")


# while 1:
# 	# # server waits on accept() for incoming requests, new socket created on return
# 	sock, addr = serverSocket.accept()
# 	# commence to send goods.. in a thread
# 	thread = Thread(target = threaded_function, args=(sock,))
# 	thread.start()
# 	# thread.join() # blocking statement, can't continue until a thread is executed

