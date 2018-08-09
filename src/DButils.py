from pymongo import MongoClient

class DBtraces():
	"""docstring for DB"""
	def __init__(self):
		client = MongoClient("127.0.0.1", 27017)
		self.db = client.Traces
		self.TimeCollection = self.db.timedomain
		self.FreqCollection = self.db.freqdomain
		# print dir(self.TimeCollection)
		# print type(self.db)
		

	def insertTime(self, event, trace, dt, sta, network, channel, fun, location=None):

		if self.CheckIfExist(event, sta, network, channel, "TimeCollection"):
			self.TimeCollection.insert_one(
				{"event": event, 
				"trace": trace,
				"delta": dt,
				"sta": sta,
				"network": network,
				"channel": channel,
				"function": fun,
				"location": location})
		else:
			print "STA alredy exist", sta
		return

	def insertFreq(self, event, trace, dt, sta, network, channel, fun, location=None):
		
		if self.CheckIfExist(event, sta, network, channel, "FreqCollection"):
			self.FreqCollection.insert_one(
				{"event": event, 
				"trace": trace,
				"delta": dt,
				"sta": sta,
				"network": network,
				"channel": channel,
				"function": fun,
				"location": location})
		else:
			print "STA alredy exist"
		return

	def CheckIfExist(self, event, sta, net, chan, collection):
		print event, sta, net, chan
		ex = self.db[collection].find_one({ "$and:" [{"event":event}, {"sta":sta},
										 {"network":net}, {"channel":chan}]})
		print ex

		if ex:
			return False
		else:
			return True # not exsist

	def remove(self, event, sta_name):
		pass

	def find(self, event, sta_name, id=None):
		pass


class DBevents():
	"""docstring for DBmeta"""
	def __init__(self):
		client = MongoClient("127.0.0.1:9666")
		self.db = client.events

	def insert(self, event, nsta, location, magnituda, depth, id):
		pass

	def CheckIfExist(self, id):
		pass

	def remove(self, id):
		pass

	def find(self, event, nsta, location, magnituda, depth, id):
		pass
		
DBtraces()
