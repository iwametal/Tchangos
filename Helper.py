# import os
from dotenv import dotenv_values


class Helper:

	@staticmethod
	def get_general_env():
		return dotenv_values(".env")