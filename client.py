# Client

# Interact with the Front End using sockets
# Send requests to system
# read/update requests

# general functions
import core_functions as cf

from socket import *
import atexit
import json

# ------------------------------------
# exit handler in the event that the 
# client needs to be closed (not a force)
# ------------------------------------

def exterminate_frontend():
	"""
	Exit Handler
	gracefully removes itself from server.
	"""
	soc.close()
# append exit handler in the event that the front-end is closing
atexit.register(exterminate_frontend)

# ------------------------------------
# socket initiation code
# ------------------------------------

servername = "localhost"
port = 12042

soc = socket(AF_INET, SOCK_STREAM)
soc.connect((servername, port))

# ------------------------------------
# Game Shop Functions
# ------------------------------------

def initialiseShop():
	quit = False
	cf.printBlanks()
	cf.WelcomeScreen(you)

	while not quit:
		resp = input(">")
		# get input
		quit = interpretUserInput(resp)
		print("---------")
		print("what do you wanna do?")

def addItem():
	# print("what do you wanna add?")
	order = getItems()
	if len(order) == 0:
		# do nothing
		print("You didn't add anything.")
	else:
		# convert result into string
		order = str(order)
	
		# send request to front end
		cf.send_socket(soc, "1:" + order)

		# # get response to send
		resp = cf.receive_msg(soc)

		# check resp if it's the ok
		if resp == "ok":
			# send item name
			print("Your orders have been processed successfully.")
		elif resp == "too_much":
			print("You can only have at most 3 items. Please remove some.")
		else:
			print("theres an error in adding your order to the basket.")

def viewItems():

	# send request to front end
	cf.send_socket(soc, "2")

	# get response of items
	resp = cf.receive_msg(soc)

	resp = json.loads(resp)

	for i in range(0, len(resp)):
		print(str(i) + ": " + resp[i])

def cancel():
	# user requesting to cancel items
	print("What do you want to cancel? (type in the ID of the item)")

	viewItems()

	cancel_id = input(">")
	# process it

	string = "3:" + str(cancel_id)
	# send request to front end
	cf.send_socket(soc, string)

	# get response of items
	resp = cf.receive_msg(soc)

	# check resp if it's the ok
	if resp == "ok":
		print("item", cancel_id, "has been removed from your basket.");
	else:
		print("something bad happened")

def interpretUserInput(resp):
	check = False
	if resp != "quit":
		if resp == "add":
			addItem()
		elif resp == "view":
			viewItems()
		elif resp == "cancel":
			cancel()
		else:
			cf.printBlanks()
			print("you wot?")
			print("--------")
			cf.WelcomeScreen(you)
	else:
		check = True

	return check

def getItems():
	check = False
	items = []
	while check is False:
		item_count = len(items)
		print("What would you like to add? (Or type 'done' to finish)")
		item = input(str(item_count+1) + "/3 >")
		if item == 'done':
			check = True
		else:
			items.append(item)
		if len(items) == 3:
			check = True
	return items

# ------------------------------------
# Initialise Client Program
# ------------------------------------

you = cf.generateID()
# send user_id to front_end
cf.send_socket(soc, you)
# get response from front_end
resp = cf.receive_msg(soc)

if resp == "ok":
	initialiseShop()
else:
	print("The Front End is down.. :(")