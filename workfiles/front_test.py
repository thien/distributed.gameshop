# Front End

# Make Replication Transparent
# Interact with Duplicates
# Maintain the Duplicates
# Send/Receive to Replicas
# Collate Responses
# Make sure client doesnt mess up replicas

# saved as greeting-client.py
import Pyro4
from Pyro4 import naming
import random
import hashlib
import time




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
