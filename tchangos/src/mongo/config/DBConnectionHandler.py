from pymongo import MongoClient


class MongoConnectionHandler:
	def __init__(self, connection_string):
		self.connection_string = connection_string
	
	
	def get_conn(self, user, passw):
		connection_string = self.connection_string.format(user, passw)

		return MongoClient(connection_string)
