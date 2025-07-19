import discord
# import os
import requests
# import sys
import time

from discord.ext import commands, tasks
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.twitch import Twitch

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from constants import DISCORD_PARTNERS_CHANNEL_ID, TWITCH_PARTNERS
from helper import Helper


class Partners(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.TWITCH_STREAM_API_ENDPOINT_V5 = 'https://api.twitch.tv/helix/streams?user_login={}'
		self.streamers_online = []
		self.authenticated = False


	async def _authenticate(self):
		try:
			twitch = await Twitch(self.bot.twitch_client, self.bot.twitch_secret)
			twitch.authenticate_app()

			self.authenticated = True
		except Exception as e:
			print(e)
	

	def get_token(self):
		params = {
			'client_id': self.bot.twitch_client,
            'client_secret': self.bot.twitch_secret,
            'grant_type': 'client_credentials'
		}

		url = 'https://id.twitch.tv/oauth2/token'
		response = requests.post(url, params=params)
		data = response.json()

		self.bot.twitch_token = data['access_token']
		self.expires_at = time.time() + data['expires_in'] - 60


	def _check_user(self, user):
		req = requests.Session()
		try:
			url = self.TWITCH_STREAM_API_ENDPOINT_V5.format(user)
			try:

				if not self.bot.twitch_token or time.time() >= self.expires_at:
					self.get_token()

				headers = {
					'Client-ID': self.bot.twitch_client,
					'Authorization': 'Bearer ' + self.bot.twitch_token
				}
				
				resp = req.get(url, headers=headers)
				jsondata = resp.json()

				if jsondata.get('data')[0].get('user_login') == user:
					return True
				
				return False
			except Exception as e:
				return False
		except Exception as e:
			print(f'2-Error checking user {user}: {e}')
			return False


	@tasks.loop(seconds=10)
	async def partner_lives_notification(self):
		streamers = Helper.get_json(TWITCH_PARTNERS)
		if streamers is not None:
			for user_id, twitch_name in streamers.items():
				status = self._check_user(twitch_name)
				user = self.bot.get_user(int(user_id))
			
				if status is True:
					if user_id not in self.streamers_online:
						self.streamers_online.append(user_id)

						print(f"{user} started streaming. Sending notification")
						await self.bot.get_channel(int(DISCORD_PARTNERS_CHANNEL_ID)).send(
							f":red_circle: **LIVE\n**{user} tá on na Roxinha!\n"
							f"\nhttps://www.twitch.tv/{twitch_name}"
						)
				else:
					if user_id in self.streamers_online:
						self.streamers_online.remove(user_id)

	
	@commands.command(name="tsopt", aliases=["Tstop"])
	@commands.has_permissions(administrator=True)
	async def tstop(self, ctx):
		if self.partner_lives_notification.is_running():
			try:
				self.partner_lives_notification.stop()
				print("twitch affiliates share stopped!")
				await ctx.message.add_reaction("✅")
			except Exception as e:
				await ctx.message.add_reaction("‼️")
				print(e)


	@commands.command(name="tstart", aliases=["Tstart"])
	@commands.has_permissions(administrator=True)
	async def tstart(self, ctx):
		if not self.authenticated:
			await self._authenticate()

		if not self.partner_lives_notification.is_running():
			try:
				self.partner_lives_notification.start()
				print("twitch affiliates share started!")
				await ctx.message.add_reaction("✅")
			except Exception as e:
				print(e)
				await ctx.message.add_reaction("‼️")


	@commands.command(name="addparceiro", aliases=["Addparceiro", "addp", "Addp"])
	@commands.has_permissions(administrator=True)
	async def add_twitch_partner(self, ctx, partner: discord.Member, twitch_name: str):
		partner_user = ""
		try:
			streamers = Helper.get_json(TWITCH_PARTNERS)
			streamers[str(partner.id)] = twitch_name
			Helper.set_json(TWITCH_PARTNERS, streamers)
			partner_user = self.bot.get_user(int(partner.id))

			await ctx.send(f"{partner_user} adicionado a lista de parceiros com sucesso.")
		except Exception as e:
			print(e)

			await ctx.send(f"Não foi possível adicionar {partner_user} à lista de parceiros.")


	@commands.command(name="rmparceiro", aliases=["Rmparceiro", "rmp", "Rmp"])
	@commands.has_permissions(administrator=True)
	async def rm_twitch_partner(self, ctx, partner: discord.Member):
		partner_user = ""
		try:
			streamers = Helper.get_json(TWITCH_PARTNERS)
			if streamers and partner.id and streamers.get(str(partner.id)):
				streamers.pop(str(partner.id))
				Helper.set_json(TWITCH_PARTNERS, streamers)
				partner_user = self.bot.get_user(int(partner.id))

				await ctx.send(f"{partner_user} removido com sucesso da lista de streamers parceiros.")
			else:
				partner_user = self.bot.get_user(int(partner.id))

				await ctx.send(f"{partner_user} não foi encontrado na lista de streamers parceiros.")
		except Exception as e:
			print(e)

			await ctx.send(f"Não foi possível remover {partner_user} da lista de parceiros.")
			await ctx.send(f"{e}")


async def setup(bot):
	await bot.add_cog(Partners(bot))