from dotenv import dotenv_values
import json
import os
import random


class Helper:

	@staticmethod
	def get_general_env():
		return dotenv_values(".env")


	@staticmethod
	def get_json(path, default_data=None):
		content = default_data
		with open(path, 'r') as file:
			content = json.loads(file.read())

		return content


	@staticmethod
	def create_unique_filename(path):
		filename = str(random.randint(1, 100))

		while os.path.exists(path + filename):
			filename = str(random.randint(1, 100))

		return filename


	@staticmethod
	def set_json(path, content):
		with open(path, 'w') as file:
			file.write(json.dumps(content))