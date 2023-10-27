import asyncio
import discord
from discord.ext import commands, tasks
from Helper import Helper
import json
from live_music import LiveMusic
import random
from twitch_helper import TwitchHelper
from twitchAPI.twitch import Twitch
import yt_dlp

### ENV VARIABLES ###
gen_data = Helper.get_general_env()

CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"
TWITCH_TOKEN = "TWITCH_TOKEN"
COFFEE_GUILD_ID = "COFFEE_GUILD_ID"
GUILD_ID = "GUILD_ID"
CHANNEL_ID = "CHANNEL_ID"
BOT_TOKEN = 'BOT_TOKEN'
MUSIC_CHANNEL_ID="MUSIC_CHANNEL_ID"
VOICE_ID="VOICE_ID"

### DATA FILES ###
TWITCH_PARTNERS = 'data/streamers.json'
USER_WARNINGS = 'data/warnings.json'

voice_client = None
counter = 0

twitch = Twitch(gen_data[CLIENT_ID], gen_data[CLIENT_SECRET])
twitch.authenticate_app([])
TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/helix/streams?user_login={}"

API_HEADERS = {
	'Client-ID': gen_data[CLIENT_ID],
	'Authorization': 'Bearer ' + gen_data[TWITCH_TOKEN],
}

streamers_online = []

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=">", bot=True, intents=intents)


def run_discord_bot():

	# executes as soon as the bot is up
	@bot.event
	async def on_ready():
		print("Tchangos up!")
	

	"""
	Task live_notifs_loop:
	- When a partner streamer goes online on twitch, it shares the stream in the registared channel
	"""
	@tasks.loop(seconds=10)
	async def live_notifs_loop():
		with open(TWITCH_PARTNERS, 'r') as file:
			streamers = json.loads(file.read())
		if streamers is not None:
			for user_id, twitch_name in streamers.items():

				status = TwitchHelper.check_user(twitch_name, API_HEADERS)
				user = bot.get_user(int(user_id))

				if status is True:
					if user_id not in streamers_online:
						streamers_online.append(user_id)
						
						await bot.get_channel(int(gen_data[CHANNEL_ID])).send(
							f":red_circle:  **LIVE**\n**{user}** tá on na Roxinha!"
							f"\nhttps://www.twitch.tv/{twitch_name}")
						print(f"{user} started streaming. Sending a notification.")
				
				else:
					if user_id in streamers_online:
						streamers_online.remove(user_id)


	"""
	Task check_nightbot_music:
	- Check which music is currently playing on twitch live stream
	- Reproduces the same music on discord server
	"""
	@tasks.loop(seconds=9)
	async def check_nightbot_music():
		guild = bot.get_guild(int(gen_data[GUILD_ID]))
		channel = guild.get_channel(int(gen_data[MUSIC_CHANNEL_ID]))

		music = ''

		current_song = LiveMusic.get_song_json()

		await channel.send("!tocando")

		await asyncio.sleep(1)

		content = []
		author = ''
		async for msg in channel.history(limit=1):
			author = msg.author.name
			if 'https:' in msg.content:
				content = msg.content.split(" ")

		if len(content) > 0:
			music = content[-1]

		await channel.purge(limit=(2 if author == "Nightbot" else 1))

		voice = bot.get_channel(int(gen_data[VOICE_ID]))
		global voice_client
		global counter

		if not music and len(current_song['song']) > 0:
			counter = 0
			try:
				if voice_client and not voice_client.is_playing():
					LiveMusic.delete_song(current_song['id'])

					current_song = {'song': '', 'id': ''}
					LiveMusic.set_song_json(current_song)
			except Exception as e:
				print(e)
				if voice_client and voice_client.is_connected():
					voice_client.disconnect()
				voice_client = None

				LiveMusic.delete_song(current_song['id'])

				current_song = {'song': '', 'id': ''}
				LiveMusic.set_song_json(current_song)


		elif music != current_song['song']:
			counter = 0
			try:
				if not voice_client or not voice_client.is_connected():
					voice_client = await voice.connect()
			except Exception as e:
				print(e)
				if voice_client and voice_client.is_connected():
					voice_client.disconnect()
				voice_client = None

			current_song['song'] = music

			filename = str(random.randint(1, 100))

			ps = current_song['id']
			current_song['id'] = filename + '.mp3'

			print(current_song)
			print(ps)

			LiveMusic.set_song_json(current_song)

			ydl_opts = LiveMusic.get_ydl_opts(filename)

			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				ydl.extract_info(music, download=True)
				url = 'song/' + str(current_song['id'])

			print(music)
			print(url)

			if voice_client.is_playing():
				voice_client.stop()

			LiveMusic.delete_song(ps)

			print("PLAYING MUSIC")
			voice_client.play(discord.FFmpegPCMAudio(url))

		elif (not music or music == current_song['song']) and voice_client and not voice_client.is_playing():
			counter += 1

			if counter > 6:
				counter = 0
				try:
					await voice_client.disconnect()
					voice_client = None
					print("Innactivity")
				except Exception as e:
					print(e)
					voice_client = None


	@bot.command()
	@commands.has_permissions(administrator=True)
	async def play(ctx):
		
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			if not check_nightbot_music.is_running():
				check_nightbot_music.start()
				print("Task started")


	@bot.command()
	@commands.has_permissions(administrator=True)
	async def stop(ctx):
		
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			if check_nightbot_music.is_running():
				print("Task stopped")
				check_nightbot_music.stop()

				global voice_client
				if voice_client and voice_client.is_connected():
					voice_client.disconnect()
					voice_client = None


	@bot.command()
	@commands.has_permissions(administrator=True)
	async def tstop(ctx):
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			if live_notifs_loop.is_running():
				live_notifs_loop.stop()
				print("Twitch affiliates share stopped!")


	@bot.command()
	@commands.has_permissions(administrator=True)
	async def tstart(ctx):
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			if not live_notifs_loop.is_running():
				live_notifs_loop.start()
				print("Twitch affiliates share started!")


	@bot.event
	async def on_voice_state_update(member, before, after):
		if after.channel is None and member==bot.user:
			print('Bot disconnected from voice channel')
			global voice_client
			voice_client = None


	@bot.command(name='addparceiro', pass_context=True)
	@commands.has_permissions(administrator=True)
	async def add_twitch(ctx, partner: discord.Member, twitch_name):
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			try:
				with open(TWITCH_PARTNERS, 'r') as file:
					streamers = json.loads(file.read())
				
				streamers[str(partner.id)] = twitch_name
				
				with open(TWITCH_PARTNERS, 'w') as file:
					file.write(json.dumps(streamers))
				
				partner_user = bot.get_user(int(partner.id))

				embed = discord.Embed(color=discord.Colour.purple(), title="", description="")
				embed.add_field(name="STREAM:", value=f"""
	**{partner_user}** foi adicionardo a lista de parceria com sucesso!

	O server será notificado sempre que o streamer estiver em live pelo canal de divulgação: **<#{int(gen_data[CHANNEL_ID])}>**
				""", inline=True)

			except Exception as e:
				print(e)

				embed = discord.Embed(color=discord.Colour.red(), title="", description="")
				embed.add_field(name="ERRO:", value=f"""
	Não foi possível adicionar o usuário a lista de Streamers parceiros :c
				""", inline=True)
			
			finally:
				await ctx.send(embed=embed)

		elif ctx.guild.id == int(gen_data[COFFEE_GUILD_ID]):
			print("由結ちゃん大好き！")


	@bot.command(name='rmparceiro', pass_context=True)
	@commands.has_permissions(administrator=True)
	async def rm_twitch(ctx, partner: discord.Member):
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			try:
				with open(TWITCH_PARTNERS, 'r') as file:
					streamers = json.loads(file.read())
				
				if streamers and partner.id and streamers.get(str(partner.id)):
					streamers.pop(str(partner.id))
				
					with open(TWITCH_PARTNERS, 'w') as file:
						file.write(json.dumps(streamers))
					
					partner_user = bot.get_user(int(partner.id))

					embed = discord.Embed(color=discord.Colour.red(), title="", description="")
					embed.add_field(name="STREAM:", value=f"""
		**{partner_user}** foi retirado da lista de parceria com sucesso!
					""", inline=True)

				else:
					partner_user = bot.get_user(int(partner.id))

					embed = discord.Embed(color=discord.Colour.red(), title="", description="")
					embed.add_field(name="STREAM:", value=f"""
		**{partner_user}** não foi encontrado na lista de parceiros!
					""", inline=True)

			except Exception as e:
				print(e)

				embed = discord.Embed(color=discord.Colour.red(), title="", description="")
				embed.add_field(name="ERRO:", value=f"""
	Não foi possível retirar o usuário a lista de Streamers parceiros :c
				""", inline=True)
			
			finally:
				await ctx.send(embed=embed)

		elif ctx.guild.id == int(gen_data[COFFEE_GUILD_ID]):
			print("由結ちゃん大好き！")


	@bot.command(pass_context=True)
	@commands.has_permissions(kick_members=True)
	async def warn(ctx, member: discord.Member, reason="Nenhuma razão foi providenciada"):
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			try:
				str_id = str(member.id)
				with open(USER_WARNINGS, 'r') as file:
					warnings = json.loads(file.read())
				
				if str_id in warnings:
					warnings[str_id].append(reason)
				else:
					warnings[str_id] = [reason]

				with open(USER_WARNINGS, 'w') as file:
					file.write(json.dumps(warnings))
				
				embed = discord.Embed(color=discord.Colour.orange(), title="", description="")
				embed.add_field(name="WARN:", value=f"""
	Você recebeu um 'warning' no server do **{bot.get_guild(int(gen_data[GUILD_ID])).name}**

	**Razão:**
	> {reason}
				""", inline=True)

				await member.send(embed=embed)

			except Exception as e:
				print(e)

				embed = discord.Embed(color=discord.Colour.red(), title="", description="")
				embed.add_field(name="ERRO:", value=f"""
	Não foi possível realizar o warning para o usuário
				""", inline=True)
				await ctx.reply(embed=embed)

		elif ctx.guild.id == int(gen_data[COFFEE_GUILD_ID]):
			print("由結ちゃん大好き！")

	
	@bot.command(pass_context=True)
	@commands.has_permissions(kick_members=True)
	async def warnings(ctx, member: discord.Member):
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			try:
				str_id = str(member.id)

				with open(USER_WARNINGS, 'r') as file:
					warnings = json.loads(file.read())

				if str_id in warnings:
					warning_list = ''

					for id, warn in enumerate(warnings[str_id]):
						warning_list += '\n\n**' + str(id + 1) + ')** ' + warn
					
					embed = discord.Embed(color=discord.Colour.yellow(), title="", description="")
					embed.add_field(name="WARNINGS:", value=f"""
	> {warning_list}
					""")

				else:
					embed = discord.Embed(color=discord.Colour.yellow(), title="", description="")
					embed.add_field(name="WARNINGS:", value=f"""
	> O usuário não possui nenhum 'warning'
					""")
			except Exception as e:
				print(e)
				embed = discord.Embed(color=discord.Colour.red(), title="", description="")
				embed.add_field(name="ERRO:", value=f"""
	> Não foi listar os warnings para o usuário
				""", inline=True)

			finally:
				await ctx.reply(embed=embed)

		elif ctx.guild.id == int(gen_data[COFFEE_GUILD_ID]):
			print("由結ちゃん大好き！")

	@bot.command(pass_context=True)
	@commands.has_permissions(kick_members=True)
	async def unwarn(ctx, member: discord.Member, id):
		if ctx.guild.id == int(gen_data[GUILD_ID]):
			try:
				str_id = str(member.id)
				with open(USER_WARNINGS, 'r') as file:
					warnings = json.loads(file.read())

				if str_id in warnings:
					warn = warnings[str_id][int(id)-1]
					warnings[str_id].remove(warn)

					if len(warnings[str_id]) == 0:
						warnings.pop(str_id)

					with open(USER_WARNINGS, 'w') as file:
						file.write(json.dumps(warnings))

					embed = discord.Embed(color=discord.Colour.dark_blue(), title="", description="")
					embed.add_field(name="UNWARN:", value=f"""
	Warn *'{warn}'* removido para o usuário **{member}**
					""")
				
				else:
					embed = discord.Embed(color=discord.Colour.dark_blue(), title="", description="")
					embed.add_field(name="UNWARN:", value=f"""
	O usuário **{member}** não possui nenhum warning!
					""")
			
			except Exception as e:
				print(e)
				embed = discord.Embed(color=discord.Colour.red(), title="", description="")
				embed.add_field(name="ERRO:", value=f"""
Não foi possível remover o warning para o usuário
				""")
			
			finally:
				await ctx.send(embed=embed)

		elif ctx.guild.id == int(gen_data[GUILD_ID]):
			print("由結ちゃん大好き")


	bot.run(gen_data[BOT_TOKEN])
