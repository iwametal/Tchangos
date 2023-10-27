import os


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
	def delete_song(song):
		path = 'song/' + str(song)
		if os.path.exists(path):
			os.remove(path)