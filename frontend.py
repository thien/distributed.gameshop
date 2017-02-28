# Front End

'''

TODO:

- allocate new primary server in the event that it fails.
- deal with failed backup servers

'''

# pryo and related imports
import Pyro4
from Pyro4 import naming
import random
import hashlib
import time
import atexit

# general functions
import core_functions as cf
import json

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
	try:
		server_socket.shutdown(1)
		server_socket.close()
	except:
		pass


	print("Frontend Server Terminated")
# append exit handler in the event that the front-end is closing
atexit.register(exterminate_frontend)

# ------------------------------------
# Methods below are for finding the primary server
# and allocating one in the event that it doesn't
# exist.
# ------------------------------------

def pollServers():
	# check if no primary servers
	primary_server = None

	# get list of servers
	primary_servers = ns.list(metadata_all={"primary"})
	backup_servers = ns.list(metadata_all={"backup"})

	# print("primary servers", primary_servers.keys())
	# print("backup servers", backup_servers.keys())

	if len(primary_servers) is not 0:
		print("theres " + str(len(primary_servers)) + " primary servers")
		if len(primary_servers) > 0:
			primary_server = next (iter (primary_servers.keys()))
	else:
		print("theres no primary servers..")
		# # if none, choose a primary server from one of the backup servers randomly
		# chosen_random_promo = random.choice(list(backup_servers.keys()))
		# # print("random nominated backup:",chosen_random_promo)
		# ns.set_metadata(chosen_random_promo, {"primary"})
		# primary_server = chosen_random_promo
		# print(primary_server, "has been allocated as the primary")
		primary_server = randomPrimary(backup_servers)

	# use name server object lookup uri shortcut
	return Pyro4.Proxy("PYRONAME:" + primary_server) 


def randomPrimary(backups):
	chosen_random_promo = random.choice(list(backups.keys()))
	print("random nominated backup:",chosen_random_promo)
	ns.set_metadata(chosen_random_promo, {"primary"})
	print(chosen_random_promo, "has been allocated as the primary")
	return chosen_random_promo


def allocate_backup():
	"""
	Need to check if the server is still alive.
	if it is, do nothing
	if it isn't, choose a backup server and connect to that.
	"""

	# can't bind; can't reach!
	print("finding backup to promote to primary")
	# will need to connect to a backup server.
	backup_servers = ns.list(metadata_all={"backup"})
	# will need to connect to a backup server.
	new_primary_server = randomPrimary(backup_servers)

	return Pyro4.Proxy("PYRONAME:" + new_primary_server) 


# ------------------------------------
# Methods below are for initialising the RMI servers
# for connection purposes.
# ------------------------------------

# find the name server
ns = Pyro4.locateNS()
# poll the servers.
global server
server = pollServers()

# ------------------------------------
# Methods below are for querying the server
# ------------------------------------

# uid is in the form of a md5(datetime + user_id)
# data is in the form of 
# 	{user: user_id, request:some_request, data:value}


def create_checksum(msg):
	checksum = str(msg)
	checksum = cf.hash_msg(checksum)
	checksum = str(checksum)
	return checksum

def queryServer(msg, server):
	checksum = create_checksum(msg)
	time_str = str(time.time())
	uid = cf.hash_msg(time_str + checksum)

	try:
		resp = server.Query(uid, msg)
	except Pyro4.errors.ConnectionClosedError:

		server = allocate_backup()
		resp = server.Query(uid, msg)

	return resp

# ------------------------------------
# socket functions
# ------------------------------------

def client_function(sock, server):
	# get user id
	user_id = cf.receive_msg(sock)
	print(user_id, "connected")
	# set up variables for interaction
	msg = {}
	data = {}
	resp = 0;

	msg["user"] = user_id

	# send the ok.
	cf.send_socket(sock, "ok")

	# wait for receipt of instruction
	resp = cf.receive_msg(sock)

	if resp:
		resp = cf.split_req(resp)
	else:
		# client is quitting if nothing is sent.
		resp = ["-1"]

	while resp[0] != "-1":
		print(resp)
		if resp[0] == "1":
			# set up message for server
			msg['request'] = 'add'
			data["game"] = resp[1]

			# add data to msg
			msg["data"] = data
			# send item to the server
			print(msg)
			server_resp = queryServer(msg, server)
			
			# print response
			print("server response:",server_resp['response'])
			cf.send_socket(sock, "ok")

		elif resp[0] == "2":
			print("client is asking to view items")
			# send the okay
			# set up request to server
			msg['request'] = "get_history"
			# send request to server
			print(msg)
			server_resp = queryServer(msg, server)

			print("server response:",server_resp['response'])

			server_resp = json.dumps(server_resp['response'])
			# send server_resp to client
			cf.send_socket(sock, server_resp)

		elif resp[0] == "3":
			print("client is asking to remove item")
			# set up request to server
			msg['request'] = "cancel"

			# receive the item id to remove
			item_id = resp[1]

			data["order_id"] = item_id
			msg["data"] = data

			print(msg)
			# ask server to remove item_id from user_id
			server_resp = queryServer(msg, server)

			print("server response:",server_resp['response'])
			cf.send_socket(sock, "ok")
		# resp = cf.receive_msg(sock)
		elif not resp:
			print("received null")
		else:
			print("what is this?")
			print("resp:", resp)

		# wait for it again
		resp = cf.receive_msg(sock)

		if resp:
			resp = cf.split_req(resp)
		else:
			break

	print(user_id, "exited")
	sock.close()

# ------------------------------------
# front-end socket initialisation
# to be used for a client-frontend
# connection.
# ------------------------------------

port = 12042

multicast_group = ('localhost', port)
clients = {}

# create TCP welcoming socket
server_socket = socket(AF_INET,SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 
server_socket.bind(("", port))

# begin listening for incoming TCP requests
server_socket.listen(1)
print ('the front end server is ready to receive goods.')

while 1:
	# # server waits on accept() for incoming requests
	# new socket created on return
	sock, addr = server_socket.accept()
	# commence to interact with client by creating a thread for it.
	thread = Thread(target = client_function, args=(sock,server))
	thread.start()