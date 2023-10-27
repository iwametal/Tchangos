import os
import yt_dlp


class LiveMusic:
	@classmethod
	def get_ydl_opts(self, filename):
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
	def download_song(filename, music):
		url = ''
		with yt_dlp.YoutubeDL(LiveMusic.get_ydl_opts(filename)) as ydl:
			ydl.extract_info(music, download=True)

		return url


	@staticmethod
	def delete_song(song):
		path = 'song/' + str(song)
		if os.path.exists(path):
			os.remove(path)