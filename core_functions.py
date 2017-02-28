import random
import hashlib as hash
import time

def enc_msg(msg):
	return msg.encode()

def receive_msg(socket):
	k = socket.recv(2048).decode()
	return k

def send_socket(socket, message):
	socket.send(enc_msg(message))

def generateID():
	msg = "hi"
	msg = msg.encode('utf-8')
	m = hash.md5()
	m.update(msg)
	k = m.hexdigest()
	return k

def split_req(message):
	vals = message.split(":")
	return vals

# ------------------------------------
# Front End Functions
# ------------------------------------

def hash_msg(msg):
	msg = msg.encode('utf-8')
	msg = hash.md5(msg)
	msg = msg.hexdigest()
	return msg

# ------------------------------------
# Game Shop Functions
# ------------------------------------

def printBlanks():
	# printing blanks
	print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

def WelcomeScreen(user_id):
	print("Welcome, you are user", user_id)
	print("what do you wanna do?")

