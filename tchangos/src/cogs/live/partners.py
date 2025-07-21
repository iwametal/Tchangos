import discord
# import os
import requests
# import sys
import time

from discord.ext import commands, tasks
# from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
# from twitchAPI.oauth import UserAuthenticator
# from twitchAPI.type import AuthScope, ChatEvent
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
			twitch.authenticate_app([])

			self.authenticated = True
		except Exception as e:
			self.bot.logger.exception('Unable to authenticate to twitch')
	

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
			
		except Exception as e:
			pass

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

						self.bot.logger.info(f"{user} started streaming. Sending notification")
						await self.bot.get_channel(int(DISCORD_PARTNERS_CHANNEL_ID)).send(
							f":red_circle: **LIVE\n** {self.bot.ftl.extract('partners-started-streaming-message', user=f'{user.mention}')}!\n"
							f" https://www.twitch.tv/{twitch_name}",
							allowed_mentions=discord.AllowedMentions(users=False)
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
				self.bot.logger.info("twitch affiliates share stopped!")
				await ctx.message.add_reaction("✅")
			except Exception:
				await ctx.message.add_reaction("‼️")
				self.bot.logger.exception()


	@commands.command(name="tstart", aliases=["Tstart"])
	@commands.has_permissions(administrator=True)
	async def tstart(self, ctx):
		if not self.authenticated:
			await self._authenticate()

		if not self.partner_lives_notification.is_running():
			try:
				self.partner_lives_notification.start()
				self.bot.logger.info("twitch affiliates share started!")
				await ctx.message.add_reaction("✅")
			except Exception:
				self.bot.logger.exception()
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

			await ctx.send(f"{self.bot.ftl.extract('partners-partner-successfully-added', partner=partner_user.name)}")
		except Exception:
			self.bot.logger.exception()
			await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-added', parter=partner_user.name)}")


	@commands.command(name="rmparceiro", aliases=["Rmparceiro", "rmp", "Rmp"])
	@commands.has_permissions(administrator=True)
	async def rm_twitch_partner(self, ctx, partner: discord.Member):
		partner_user = ""
		try:
			partner_id = str(partner.id)
			streamers = Helper.get_json(TWITCH_PARTNERS)
			if streamers and partner.id and streamers.get(partner_id):
				if partner_id in self.streamers_online:
					self.streamers_online.remove(partner_id)
				streamers.pop(partner_id)
				Helper.set_json(TWITCH_PARTNERS, streamers)
				partner_user = self.bot.get_user(int(partner.id))

				await ctx.send(f"{self.bot.ftl.extract('partners-partner-successfully-removed', partner=partner_user.name)}")
			else:
				partner_user = self.bot.get_user(int(partner.id))

				await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-found', partner=partner_user.name)}")
		except Exception:
			self.bot.logger.exception()

			await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-removed', partner=partner_user.name)}")


async def setup(bot):
	await bot.add_cog(Partners(bot))