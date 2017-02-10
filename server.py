# server

# look for backups
# check if itself is the primary server or the backups
# interact with the frontend
# identify itself uniquely

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
atexit.register(exterminate_server)

@Pyro4.expose
class replica(object):
	def __init__(self):
		self.database = {}
	# 
	# public functions to be called by the front end
	# 
	def databasePeek(self):
		return self.database

	def addGame(self, user_id, game):
		self.database[self.getUser(user_id)].append(game)
		if checkPrimary():
			for i in getBackups():
				i.addGame(user_id, game)
			print("done")
		return True

	def getOrderHistory(self, user_id):
		return self.database[self.getUser(user_id)]

	def cancelOrder(self, user_id, order_id):
		self.database[self.getUser(user_id)].pop(order_id)
		if checkPrimary():
			for i in getBackups():
				i.cancelOrder(user_id, order_id)
		return True

	def getUser(self, user_id):
		if user_id not in self.database:
			# add user to db
			print(user_id, "is not in the db.")
			user_id = str(user_id)
			self.database[user_id] = []
			print(self.database)
			print("added", user_id, "to the db.")
		# else:
			# print(user_id, "is in the db.")
		return user_id

# ------------------------------------
# Functions to communicate with other servers

# check metadata for primary
def checkPrimary():
	metadata = ns.lookup(servername, return_metadata=True)[1]
	if 'primary' in metadata:
		return True
		# server is a primary server
		# iterate through all the servers
		# run the same command on all the servers
	else:
		return False

def printMemes(memes):
	return (memes + memes)

def getBackups():
	print("loading backups list")
	backups = []
	backup_servers_ids = ns.list(metadata_all={"backup"})
	# REMOVE THIS SERVER FROM THE LIST, YOU DON'T WANT AN INFINITE LOOP
	print("current backup list")
	print(backup_servers_ids)
	print("popping servername if it exists")
	if servername in backup_servers_ids:
		backup_servers_ids.pop(servername)
	# print(backup_servers_ids)
	for i in backup_servers_ids:
		# print(i)
		pyroname = "PYRONAME:" + i;
		# print(pyroname)
		backup_server = Pyro4.Proxy(pyroname)
		backups.append(backup_server)
		# print(backup_server.databasePeek())
		# print(backup_server)
	# print(functs)
	print("backups", backups)
	return backups
# ------------------------------------

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

serverno = 0;

# make a Pyro daemon
daemon = Pyro4.Daemon()
# find the name server
ns = Pyro4.locateNS()

# check servers online

while serverno in checkServerSpace():
	serverno += 1

# create server name
servername = "server" + str(serverno)

print("Loading up " + servername)
# register the greeting maker as a Pyro object
# (object, its id, force (boolean))
uri = daemon.register(replica, servername)
# register the object with a name in the name server
# servers name, the uri, metadata
ns.register(servername, uri, metadata={"backup"})
# if serverno is 0:
# 	ns.register(servername, uri, "backup")
# else:
# 	ns.register(servername, uri, "backup")

print(servername + " is ready.")

checkPrimary()
# print(Pyro4.core.DaemonObject(daemon).get_metadata(servername))

# start the event loop of the server to wait for calls
daemon.requestLoop()
