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
# print(server) 

def placeOrder(user_id, game):
	# add game
	server.addGame(user_id, game)
	return True

# retrieve order history
def getOrderHistory(user_id):
	return server.getOrderHistory(user_id)

# cancel an order
def cancelOrder(user_id, order_id):
	server.cancelOrder(user_id, order_id)
	return True

server.addGame(1,"Pokemans")
server.addGame(1,"BattleToads")
print(server.databasePeek())
print(server.getOrderHistory(1))
# make a loop
# check if any servers are down


