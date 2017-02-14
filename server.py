# server

import Pyro4
import atexit
from Pyro4 import naming
from Pyro4 import core
from random import randint
import re


def exterminate_server():
	"""
	Exit Handler
	gracefully removes itself from server.
	"""
	ns.remove(servername)
	daemon.close()
	print("closed server")
# append exit handler in the event that the server is closing
atexit.register(exterminate_server)

# simple database store
database = {}
requests_history = {}
requests = []

# ------------------------------------
# Server functions for access with a front-end
# ------------------------------------

@Pyro4.expose
class replica(object):
	def __init__(self):
		print("Server is being poked.")
		# load data from file
		# check data integrity with other files

	def requestHandler(self, uid, data):
		while len(request) > 0:
			# do something
			sausage = 1
		return False

	def Query(self, uid, data):
		print("server is being queried")
		requests.append(uid)
		# uid is in the form of a md5(datetime + user_id)
		# data is in the form of {user: user_id, request:some_request, data:value}
		
		# request options: "add", "get_history", "cancel", "peek_db"
		ack = {}

		# check if the uid has been dealt with before.
		print("checking if request is new")
		resp = self.checkRequest(uid)

		if resp is False:
			print("this is a new request")
			# the request hasn't been dealt with before.

			# check whether the server is a primary server.
			primary = checkPrimary();

			print("interpreting data...")

			print(data)
			print("------")

			print("request:", data['user'])
			

			print("dealing with request..")
			# deal with request

			if data['request'] == "add":
				print("request: add")
				# deal with adding
				print("creating ack. with user:", data['user'], " and game:", data['data']['game'])
				ack['response'] = self.addGame(data['user'], data['data']['game'])
				ack['message'] = "game added";
				print("created ack.")

				if primary:
					print("dealing with backups")
					ack = self.BackupsHandler(ack, uid, data)


			elif data['request'] == "get_history":
				print("request: history")
				# deal with getting history
				ack['response'] = self.getOrderHistory(data['user'])
				ack['message'] = "user is requesting history";
				# ack = BackupsHandler(ack, uid, data)

			elif data['request'] == "cancel":
				print("request: cancellation")
				# deal with cancellations
				ack['response'] = self.cancelOrder(data['user'], data[data['order_id']])
				ack['message'] = "game is removed";
				if primary: ack = self.BackupsHandler(ack, uid, data)

			elif data['request'] == "peek_db":
				print("request: peek")
				ack['response'] = self.databasePeek()
				ack['message'] = "The database has been seent"

			else:
				print("unrecognised request, '" + data['request'] + "' is not recognised")
				# unrecognised request
				ack['response'] = False
				ack['message'] = "Error with the request";

			requests_history[uid] = ack;

			return ack;

		else:
			print("request has been done before")
			return requests_history[uid]

	def BackupsHandler(self, primary_ack, uid, data):
		checksums = [];
		checksum_dictionary = {}

		# create checksum of server's ack
		prim_checksum = hash(frozenset(primary_ack));
		# add ack to dictionary with key being checksum
		checksum_dictionary[prim_checksum] = primary_ack;
		# add checksum to list
		checksums.append(hash(frozenset(primary_ack)))

		for backup in backup_servers:
			# execute query on backup_servers
			backup_ack = backup.Query(uid, data)
			# compute a checksum of the response
			checksum = hash(frozenset(backup_ack))
			# add to list
			checksums.append(checksum)
			# add to dictionary if it doesn't exist
			if checksum not in checksum_dictionary:
				checksum_dictionary[checksum] = backup_ack
		
		# return most popular checksum.
		most_popular = max(set(checksums), key=checksums.count)
		return checksum_dictionary[most_popular]

	def databasePeek(self):
		return database

	def addGame(self, user_id, game):
		# print("request to add ", game, "to", user_id)
		database[self.getUser(user_id)].append(game)
		# print(game,"-",user_id, "successful")
		# print(database[self.getUser(user_id)])
		return True

	def getOrderHistory(self, user_id):
		# print("frontend is requesting server history")
		return database[self.getUser(user_id)]

	def cancelOrder(self, user_id, order_id):
		# print("request to remove order", order_id, "from", user_id)
		# print("before",database[self.getUser(user_id)] )
		database[self.getUser(user_id)].pop(order_id)
		# print("after", database[self.getUser(user_id)])
		# print(order_id, "from", user_id, "removed successfully")
		# if checkPrimary():
		# 	for i in backup_servers:
		# 		i.cancelOrder(user_id, order_id)
		return True

	def getUser(self, user_id):
		if user_id in database:
			# do nothing
			return user_id
		else:
			# add user to db
			print(user_id, "is not in the db.")
			database[user_id] = []
			print("added", user_id, "to the db.")
		# else:
			# print(user_id, "is in the db.")
		return user_id

	def checkRequest(self, uid):
		print("uid:", uid)
		if uid in requests_history:
			# do nothing
			print("this request has been filled before.")
			print(requests_history)
			return requests_history[uid]
		else:
			print("this request has not been filled before.")
			return False

# ------------------------------------
# Functions to communicate with other servers
# ------------------------------------

# check the server's metadata to see whether it is a primary server
def checkPrimary():
	metadata = ns.lookup(servername, return_metadata=True)[1]
	if 'primary' in metadata:
		print("server is primary")
		return True
	else:
		print("server is backup")
		return False

def checkServerStatus(server):
	return False

# update the status of all backup servers
def getBackupServerStatus():
	# deal with getting the status of backup servers.
	# needs to be run everytime the server is queried.
	# loop through the servers in the nameserver
	# if its not in the backup list, add it.

	# look at curent servers in list
	# polled?
	return False

# get list of objects of backup servers
def getBackups():
	# print("loading backups list")
	backups = []
	backup_servers_ids = ns.list(metadata_all={"backup"})
	# remove itself from the server list.
	if servername in backup_servers_ids:
		backup_servers_ids.pop(servername)

	for i in backup_servers_ids:
		pyroname = "PYRONAME:" + i;
		backup_server = Pyro4.Proxy(pyroname)
		backups.append(backup_server)
	# print(functs)
	# print("backups", backups)
	return backups

# return list of occupied servers
def checkServerSpace():
	occupied = []
	# need to check servers online
	for i in ns.list():
		# check if numbers inside the server name
		if any(char.isdigit() for char in i):
			occupied.append(int(re.search(r'\d+', i).group()))
	# print("occupied servers:",occupied)
	return occupied

# ------------------------------------
# Methods below are for initialising the server
# ------------------------------------

# initialise server #
serverno = 0;

# make Pyro daemon
daemon = Pyro4.Daemon()

# find the name server
ns = Pyro4.locateNS()

# check other servers in order to allocate server number
while serverno in checkServerSpace() : serverno += 1

# create server name
servername = "server" + str(serverno)
print("Loading up " + servername)

# register the server as a Pyro object
uri = daemon.register(replica, servername)

# register the object with a name in the name server
ns.register(servername, uri, metadata={"backup"})

# find backup servers
backup_servers = getBackups()

# start the event loop of the server to wait for calls
print(servername + " is ready.")
daemon.requestLoop()
