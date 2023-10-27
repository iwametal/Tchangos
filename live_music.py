import json
import os

### DATA FILES ###
CURRENT_SONG = 'data/current_song.json'

class LiveMusic:
	@staticmethod
	def get_ydl_opts(filename):
		return {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
			'outtmpl': f'song/{filename}.%(ext)s',
		}


	@staticmethod
	def get_song_json():
		current_song = ''
		with open(CURRENT_SONG, 'r') as file:
			current_song = json.loads(file.read())

		return current_song


	@staticmethod
	def set_song_json(song):
		with open(CURRENT_SONG, 'w') as file:
			file.write(json.dumps(song))
	

	@staticmethod
	def delete_song(song):
		path = 'song/' + str(song)
		if os.path.exists(path):
			os.remove(path)