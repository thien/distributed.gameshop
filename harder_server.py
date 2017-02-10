# saved as greeting-server.py
import Pyro4

@Pyro4.expose
class biggerMaths(object):
	def get_fortune(self, name):
		return "Hello, {0}. Here is your fortune message:\n" \
			   "Tomorrow's lucky number is 12345678.".format(name)
	def do_avg(self, x,y,z):
		result = (x + y + z)/3
		return result
	def do_max(self, x,y,z):
		result =[x,y,z]
		return max(result)

daemon = Pyro4.Daemon()				# make a Pyro daemon
ns = Pyro4.locateNS()				  # find the name server
uri = daemon.register(biggerMaths)   # register the greeting maker as a Pyro object
ns.register("hard.maths", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()				   # start the event loop of the server to wait for calls