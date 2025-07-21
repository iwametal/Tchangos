from helper import Helper
from mongo.config.DBConnectionHandler import MongoConnectionHandler
from mongo.collections.services.partners_service import PartnersService


data = Helper.get_general_config('config.ini')
mongo = MongoConnectionHandler(data['mongodb']['connection_string'])

mongodb = mongo.get_conn(data['mongodb']['user'], data['mongodb']['pass'])

__partners = PartnersService(mongodb)

partners = __partners.get_partners()

print(partners)