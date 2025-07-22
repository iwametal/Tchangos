from mongo.collections.schemas.partners_schema import PartnersSchema


class PartnersService:
	def __init__(self, mongodb):
		self.collection = mongodb.tchangos.partners


	def get_partners(self) -> list[PartnersSchema]:
		return list(self.collection.find())


	def get_partner_from_username(self, username: str) -> PartnersSchema | None:
		return self.collection.find_one({"username": username})


	def get_partner_from_userid(self, userid: int) -> PartnersSchema | None:
		return self.collection.find_one({"userid": userid})


	def get_partner_from_twitch_user(self, username: str) -> PartnersSchema | None:
		return self.collection.find_one({"twitch_user": username})


	def create_or_update_partner(self, partners_data: dict) -> PartnersSchema | None:
		if self.get_partner_from_userid(partners_data['userid']):
			return self.collection.update_one(
				{"userid": partners_data["userid"]},
				{"$set": partners_data},
				upsert=True
			)
		
		return self.collection.insert_one(partners_data)
	

	def delete_partner(self, partner_id):
		self.collection.delete_one(
			{
				"userid": partner_id
			}
		)