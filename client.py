# Client

# Interact with the Front End using sockets
# Send requests to system
# read/update requests

import hashlib as hash
from socket import *

servername = "localhost"
port = 12036

soc = socket(AF_INET, SOCK_STREAM)
soc.connect((servername, port))


server_message = soc.recv(1024) + ": "
password = raw_input(server_message)
print ("sending to server")
soc.send(password)
if soc.recv(1024) == "1":
	for i in range(1,15):
		try:
			sentence = "you shouldn't be looking at this commit."
			# no need to attach the server name or the port anymore
			soc.send(sentence)
			modifiedSentence = soc.recv(1024)
			if modifiedSentence == "You've used all your messages. Go away.":
				# print ('shut up')
				raise
			else:
				print ('from Server: ' + modifiedSentence)
		# except Kick as e:
		# 	print e
		# 	break
		except:
			print ("You've been kicked out.")
			break
	soc.close()
else:
	print ("you've been denied, go away")
	soc.close()

# ------------------------------------
# Game Shop Functions
# ------------------------------------

def generateID():
	msg = "hi"
	msg = msg.encode('utf-8')
	m = hash.md5()
	m.update(msg)
	k = m.hexdigest()
	return k

def printBlanks():
	# printing blanks
	print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

def WelcomeScreen():
	print("Welcome, you are user", you)
	print("what do you wanna do?")

def addItem():
	print("what do you wanna add?")
	resp = input(">")
	# do function to add thing
	print(resp, "has been added to the game bro.")

def viewItems():
	# user requesting to view items
	print("you viewing yo items")

def cancel():
	# user requesting to cancel items
	print("you cancellin")

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
			printBlanks()
			print("you wot?")
			print("--------")
			WelcomeScreen()
	else:
		check = True

	return check

# ------------------------------------
# Initialise Client Program
# ------------------------------------

you = generateID()
quit = False

printBlanks()
WelcomeScreen()

while not quit:
	resp = input(">")
	# get input
	quit = interpretUserInput(resp)
	print("---------")
	print("what do you wanna do?")
