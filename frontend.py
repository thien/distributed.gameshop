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
# Front End Class
# ------------------------------------

class Frontend:
	def __init__(self):
		self.ns = Pyro4.locateNS()
		self.primary_server = self.pollServers()

	def queryServer(self, msg):
		checksum = cf.create_checksum(msg)
		time_str = str(time.time())
		uid = cf.hash_msg(time_str + checksum)

		try:
			resp = self.primary_server.Query(uid, msg)

		except Pyro4.errors.ConnectionClosedError:

			self.primary_server = self.allocate_backup()
			resp = self.primary_server.Query(uid, msg)

		return resp

	def pollServers(self):
		# check if no primary servers
		prim_server = None

		# get list of servers
		p_servers = self.ns.list(metadata_all={"primary"})
		b_servers = self.ns.list(metadata_all={"backup"})

		if len(p_servers) is not 0:
			print("theres " + str(len(p_servers)) + " primary servers")
			if len(p_servers) > 0:
				prim_server = next (iter (p_servers.keys()))
		else:
			print("theres no primary servers..")
			# # if none, choose a primary server from one of the backup servers randomly
			prim_server = self.randomPrimary(b_servers)

		# use name server object lookup uri shortcut
		return Pyro4.Proxy("PYRONAME:" + prim_server) 

	def randomPrimary(self, backups):
		chosen_random_promo = random.choice(list(backups.keys()))
		print("random nominated backup:",chosen_random_promo)
		self.ns.set_metadata(chosen_random_promo, {"primary"})
		print(chosen_random_promo, "has been allocated as the primary")
		return chosen_random_promo

	def allocate_backup(self):
		"""
		Need to check if the server is still alive.
		if it is, do nothing
		if it isn't, choose a backup server and connect to that.
		"""

		# can't bind; can't reach!
		print("finding backup to promote to primary")
		# will need to connect to a backup server.
		b_servers = self.ns.list(metadata_all={"backup"})
		print("backs", b_servers)
		# will need to connect to a backup server.
		self.primary_server = self.randomPrimary(b_servers)

		return Pyro4.Proxy("PYRONAME:" + self.primary_server) 


# ------------------------------------
# socket functions
# ------------------------------------

def client_function(sock, frontend):
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
			# set up message for serv
			msg['request'] = 'add'
			data["game"] = resp[1]

			# add data to msg
			msg["data"] = data
			# send item to the serv
			print(msg)
			serv_resp = frontend.queryServer(msg)
			
			# print response
			print("serv response:",serv_resp['response'])
			cf.send_socket(sock, "ok")

		elif resp[0] == "2":
			print("client is asking to view items")
			# send the okay
			# set up request to serv
			msg['request'] = "get_history"
			# send request to serv
			print(msg)
			serv_resp = frontend.queryServer(msg)

			print("serv response:",serv_resp['response'])

			serv_resp = json.dumps(serv_resp['response'])
			# send serv_resp to client
			cf.send_socket(sock, serv_resp)

		elif resp[0] == "3":
			print("client is asking to remove item")
			# set up request to serv
			msg['request'] = "cancel"

			# receive the item id to remove
			item_id = resp[1]

			data["order_id"] = item_id
			msg["data"] = data

			print(msg)
			# ask serv to remove item_id from user_id
			serv_resp = frontend.queryServer(msg)

			print("serv response:",serv_resp['response'])
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

frontend = Frontend()

while 1:
	# # server waits on accept() for incoming requests
	# new socket created on return
	sock, addr = server_socket.accept()
	# commence to interact with client by creating a thread for it.
	thread = Thread(target = client_function, args=(sock,frontend))
	thread.start()