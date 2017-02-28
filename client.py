# Client

# Interact with the Front End using sockets
# Send requests to system
# read/update requests

# general functions
import core_functions as cf

from socket import *
import atexit

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

# server_message = soc.recv(1024).decode() + ": "
# password = input(server_message).encode()

# print ("sending to server")

# soc.send(password)


# resp = cf.receive_msg(soc)
# print(resp)
# if resp == "1":
# 	for i in range(1,15):
# 		try:
# 			sentence = "yo mama so fat that that small things orbit her"
# 			# no need to attach the server name or the port anymore
# 			# soc.send(cf.enc_msg(sentence))
# 			cf.send_socket(soc, sentence)
# 			modifiedSentence = cf.receive_msg(soc)
# 			# print(modifiedSentence)
# 			if modifiedSentence == "You've used all your messages. Go away.":
# 				# print ('shut up')
# 				raise
# 			else:
# 				print ('from Server: ' + modifiedSentence)
# 		except:
# 			print ("You've been kicked out.")
# 			break
# else:
# 	print ("you've been denied, go away")


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
	print("what do you wanna add?")
	req = input(">")
	
	# send request to front end
	cf.send_socket(soc, "1:" + req)

	# # get response to send
	resp = cf.receive_msg(soc)
	print("received an:" + resp)
	# check resp if it's the ok
	if resp == "ok":
		# send item name
		print(req + " has been added your basket.")
	else:
		print("theres an error in adding " + req + " to the basket.")

def viewItems():
	# user requesting to view items
	print("you viewing yo items")

	# send request to front end
	cf.send_socket(soc, "2")

	# get response of items
	resp = cf.receive_msg(soc)
	print(resp)

def cancel():
	# user requesting to cancel items
	print("What do you want to cancel?")
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