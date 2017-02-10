# Client

# Interact with the Front End
# Send requests to system
# read/update requests


# 1. interact with the front end

import hashlib as hash


def generateID():
	msg = "hi"
	msg = msg.encode('utf-8')
	m = hash.md5()
	m.update(msg)
	k = m.hexdigest()
	return k


you = generateID()

# place an order
frontend.placeOrder(you, ["Battle Toads", "Chicken Run", "Pokemoans"])

# get an order's history
frontend.getOrderHistory(you)

# cancel an order
frontend.cancelOrder(you, order_id)