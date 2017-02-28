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

# general functions
import core_functions as cf

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
	serverSocket.shutdown(1)
	serverSocket.close()
	print("Frontend Server Terminated")
# append exit handler in the event that the front-end is closing
atexit.register(exterminate_frontend)

# # ------------------------------------
# # Methods below are for finding the primary server
# # and allocating one in the event that it doesn't
# # exist.
# # ------------------------------------

# # find the name server
# ns = Pyro4.locateNS()

# # check if no primary servers
# primary_server = None

# primary_servers = ns.list(metadata_all={"primary"})
# backup_servers = ns.list(metadata_all={"backup"})

# print("primary servers", primary_servers.keys())
# print("backup servers", backup_servers.keys())

# if len(primary_servers) is not 0:
# 	print("theres " + str(len(primary_servers)) + " primary servers")
# 	if len(primary_servers) is 1:
# 		primary_server = next (iter (primary_servers.keys()))
# else:
# 	print("theres no primary servers..")
# 	# if none, choose a primary server from one of the backup servers randomly
# 	chosen_random_promo = random.choice(list(backup_servers.keys()))
# 	print("random nominated backup:",chosen_random_promo)
# 	ns.set_metadata(chosen_random_promo, {"primary"})
# 	primary_server = chosen_random_promo
# 	print(primary_server, "has been allocated as the primary")

# # use name server object lookup uri shortcut
# server = Pyro4.Proxy("PYRONAME:" + primary_server)   



# # ------------------------------------
# # Methods below are for querying the server
# # ------------------------------------

# # uid is in the form of a md5(datetime + user_id)
# # data is in the form of {user: user_id, request:some_request, data:value}

# #req keys: "add", "get_history", "cancel", "peek_db"

# # "game" "user" "order_id"

# # def hash(msg):
# 	# return hashlib.md5(msg.encode()).hexdigest()


# def queryServer(msg):
# 	checksum = str(hash(frozenset(msg)))
# 	time_str = str(time.time())
# 	uid = hash(time_str + checksum)
# 	return server.Query(uid, msg)

# user_id = 1

# msg = {}
# data = {}
# msg["user"] = user_id
# msg['request'] = 'add'

# data["game"] = "sausages"
# data["order_id"] = 1

# msg["data"] = data

# resp = queryServer(msg)

# print("resp1:",resp['response'])
# print("msg1:",resp['message'])

# msg['request'] = "get_history"

# # resp = queryServer(msg)

# # print("resp2:",resp['response'])

# ------------------------------------
# socket functions
# ------------------------------------

def threaded_function(sock):
	# print(args)
	password = "shut up"

	# send message saying password plz?
	sock.send(cf.enc_msg("password plz"))

	# receive password
	user_entry = cf.receive_msg(sock)

	# sock.send(cf.enc_msg("dankest of memes"))

	if user_entry == password:
		print ("access granted")
		# msg = cf.enc_msg("1")


		cf.send_socket(sock, "1")

		# add socket to list of clients
		clients[sock] = 0
		# print (clients)

		while clients[sock] < 10:
			sentence = sock.recv(2048)
			capitalizedSentence = sentence.upper()
			sock.send(capitalizedSentence)
			clients[sock] += 1
			# sleep(0.5)

		msg = cf.enc_msg("You've used all your messages. Go away.")
		sock.send(msg)
		# print("kicked " + str(addr) + "; Reason: Used all Messages")
		del clients[sock];
		# print (clients)
		sock.close()
	else:
		print(user_entry)
		print (str(addr) + " is denied")
		sock.send(cf.enc_msg("9"))
		sock.close()



def danker_function(sock):
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
		resp = ["123", "123"]
		resp[0] = "-1"

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
			# server_resp = queryServer(msg)
			
			# print response
			# print("server response:",server_resp['response'])
			cf.send_socket(sock, "ok")

		elif resp[0] == "2":
			print("client is asking to view items")
			# send the okay
			# set up request to server
			msg['request'] = "get_history"
			# send request to server
			print(msg)
			# server_resp = queryServer(msg)

			# print("server response:",server_resp['response'])

			# send server_resp to client
			cf.send_socket(sock, "lool what")

		elif resp[0] == "3":
			print("client is asking to remove item")
			# set up request to server
			msg['request'] = "cancel"

			# receive the item id to remove
			item_id = resp[1]

			data["order_id"] = item_id
			msg["data"] = data
			# ask server to remove item_id from user_id
			# server_resp = queryServer(msg)
			print(msg)
			# print("server response:",server_resp['response'])
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
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 
serverSocket.bind(("", port))

# begin listening for incoming TCP requests
serverSocket.listen(1)
print ('the front end server is ready to receive goods.')

while 1:
	# # server waits on accept() for incoming requests, new socket created on return
	sock, addr = serverSocket.accept()
	# commence to send goods.. in a thread
	thread = Thread(target = danker_function, args=(sock,))
	thread.start()