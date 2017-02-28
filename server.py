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
	print(servername,"closed server")
# append exit handler in the event that the server is closing
atexit.register(exterminate_server)

# backup_servers
global backup_servers
backup_servers = []
# simple database store
database = {}
# store previous results
requests_history = {}
# list of items to process
requests = []

# ------------------------------------
# Server functions for access with a front-end
# ------------------------------------

@Pyro4.expose
class replica(object):
	def __init__(self):
		"""
		init()

		actions to perform when the server is being initiated
		"""
		print(servername,"Server is being poked.")

	def requestHandler(self, uid, data):
		"""
		requestHandler():

		handles request according to data.
		"""

		while len(request) > 0:
			# get the first item in the requests list.
			req = requests.pop(0)
			uid = req[0]
			data = req[1]
		return False

	def executeQuery(self, uid, data):
		# initialise ack
		ack = {}

		# execute the query
		print(servername,"this is a new request")
		# the request hasn't been dealt with before.

		# check whether the server is a primary server.
		primary = checkPrimary();

		print(servername,"interpreting data...")

		print(servername,data)
		print(servername,"------")
		print(servername,"request:", data['user'])
		print(servername,"dealing with request..")
		# deal with request

		if data['request'] == "add":
			print(servername,"request: add")
			# deal with adding
			print(servername,"creating ack. with user:", data['user'], " and game:", data['data']['game'])
			ack['response'] = self.addGame(data['user'], data['data']['game'])
			ack['message'] = "game added";
			print(servername,"created ack.")

			if primary:
				print(servername,"dealing with backups")
				ack = self.BackupsHandler(ack, uid, data)

		elif data['request'] == "get_history":
			print(servername,"request: history")
			# deal with getting history
			ack['response'] = self.getOrderHistory(data['user'])
			ack['message'] = "user is requesting history";
			# ack = BackupsHandler(ack, uid, data)

		elif data['request'] == "cancel":
			print(servername,"request: cancellation")
			# deal with cancellations
			ack['response'] = self.cancelOrder(data['user'], data['data']['order_id'])
			ack['message'] = "game is removed";
			if primary: ack = self.BackupsHandler(ack, uid, data)

		elif data['request'] == "peek_db":
			print(servername,"request: peek")
			ack['response'] = self.databasePeek()
			ack['message'] = "The database has been seent"

		else:
			print(servername,"unrecognised request, '" + data['request'] + "' is not recognised")
			# unrecognised request
			ack['response'] = False
			ack['message'] = "Error with the request";

		requests_history[uid] = ack;

		return ack;

	def Query(self, uid, data):
		"""

		Query():

		receives results from the frontend.

		uid is in the form of a md5(datetime + user_id)
		data is in the form of {user: user_id, request:some_request, data:value}
		request options: "add", "get_history", "cancel", "peek_db"

		"""
		
		print(servername,servername,"server is being queried")
		requests.append([uid, data])

		# check if the uid has been dealt with before.
		print(servername,"checking if request is new")
		resp = self.checkRequest(uid)

		if resp is False:
			return self.executeQuery(uid, data)
		else:
			print(servername,"request has been done before")
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

		# propagate list of backup servers
		print("propagating backup servers..")
		
		updateBackupServerList(backup_servers)

		print("looping through backup servers..")
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
		# returns whole database
		return database

	def addGame(self, user_id, game):
		"""
		addGame():

		adds a game to a users account.
		"""
		database[self.getUser(user_id)].append(game)
		return True

	def getOrderHistory(self, user_id):
		"""
		getOrderHistory()

		gets a users history.
		"""
		return database[self.getUser(user_id)]

	def cancelOrder(self, user_id, order_id):
		"""
		cancelOrder()

		cancels a user's order using the id.
		"""
		print("cancelling with:", order_id)
		order_id = int(order_id)
		database[self.getUser(user_id)].pop(order_id)
		return True

	def getUser(self, user_id):
		if user_id in database:
			# do nothing
			return user_id
		else:
			# add user to db
			print(servername,user_id, "is not in the db.")
			database[user_id] = []
			print(servername,"added", user_id, "to the db.")
		# else:
			# print(servername,user_id, "is in the db.")
		return user_id

	def checkRequest(self, uid):
		print(servername,"uid:", uid)
		if uid in requests_history:
			# do nothing
			print(servername,"this request has been filled before.")
			print(servername,requests_history)
			return requests_history[uid]
		else:
			print(servername,"this request has not been filled before.")
			return False

	def recoverBackup(self):
		# sends database and request_history to backup server.
		return [database, requests_history]

# ------------------------------------
# Functions to communicate with other servers
# ------------------------------------

def checkPrimary():
	"""
	checkPrimary()

	check the server's metadata to see whether
	it is a primary server.

	"""
	metadata = ns.lookup(servername, return_metadata=True)[1]
	if 'primary' in metadata:
		print(servername,"server is primary")
		return True
	else:
		print(servername,"server is backup")
		return False

def updateBackupServerList(backup_servers):

	"""
	updateBackupServerList(backup_servers)

	deal with getting the status of backup servers.
	needs to be run everytime the server is queried.
	loop through the servers in the nameserver
	if its not in the backup list, add it.
	"""

	# look at curent servers in list
	print("iterating through backup servers")
	for i in backup_servers:

		# check if you can still connect to them.
		msg = str(i).replace("Pyro4.core.Proxy at ",'').replace("for", "")

		try:
			# if you can bind, you can still connect to it.
			i._pyroBind()
		except:
			# can't bind; can't reach!
			print(msg, "is no longer reachable")
			backup_servers.remove(i)

	print("dealing with backups")
	# get new servers in list.
	fresh_list = getBackups()
	for i in backup_servers:
		if i in fresh_list:
			fresh_list.remove(i)

	for i in fresh_list:
		print(i, "is found, adding to backup list")
		backup_servers.append(i)

def getBackups():
	"""
	getBackups
	get list of objects of backup servers
	"""

	backups = []
	backup_servers_ids = ns.list(metadata_all={"backup"})

	# remove itself from the server list.
	if servername in backup_servers_ids:
		backup_servers_ids.pop(servername)

	# iterate through the backup servers.
	for i in backup_servers_ids:
		pyroname = "PYRONAME:" + i;
		# initialise the connection to the backup server
		backup_server = Pyro4.Proxy(pyroname)
		# add server connection to the list
		backups.append(backup_server)

	return backups

def checkServerSpace():
	"""
	checkServerSpace()

	checks the servers online, and gets the
	ID's of the servers.
	"""
	occupied = []

	# need to check servers online
	for i in ns.list():
		# check if numbers inside the server name
		if any(char.isdigit() for char in i):
			occupied.append(int(re.search(r'\d+', i).group()))

	return occupied

# ------------------------------------
# Methods below are for initialising the server
# ------------------------------------

def recoverData():
	# connect to primary server and retrieve database and history
	# if a primary server hasn't been delegated then retrieve data 
	# from a backup.

	# from primary server before something else happens.
	primary_servers = ns.list(metadata_all={"primary"})

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
