from pydantic import BaseModel


class PartnersSchema(BaseModel):
	username: str
	userid: int
	twitch_user: str

	class config:
		extra = 'ignore'