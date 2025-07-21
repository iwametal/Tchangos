import discord
import requests
import time

from constants import DISCORD_PARTNERS_CHANNEL_ID, TWITCH_PARTNERS
from discord.ext import commands, tasks
from helper import Helper
from mongo.collections.services.partners_service import PartnersService
from twitchAPI.twitch import Twitch


class Partners(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.TWITCH_STREAM_API_ENDPOINT_V5 = 'https://api.twitch.tv/helix/streams?user_login={}'
		self.authenticated = False

		self.__partners = PartnersService(self.bot._mongodb)
		self.partners_list = self.__partners.get_partners()
		self.streamers_online = []


	async def __authenticate(self):
		try:
			twitch = await Twitch(self.bot.twitch_client, self.bot.twitch_secret)
			await twitch.authenticate_app([])

			self.authenticated = True
		except Exception:
			self.bot.logger.exception('Unable to authenticate to twitch')
	

	def __get_token(self):
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


	def __check_user(self, user):
		req = requests.Session()
		url = self.TWITCH_STREAM_API_ENDPOINT_V5.format(user)
		try:

			if not self.bot.twitch_token or time.time() >= self.expires_at:
				self.__get_token()

			headers = {
				'Client-ID': self.bot.twitch_client,
				'Authorization': 'Bearer ' + self.bot.twitch_token
			}
			
			resp = req.get(url, headers=headers)
			jsondata = resp.json()

			if jsondata.get('data')[0].get('user_login') == user:
				return True
			
		except Exception:
			pass

		return False


	@tasks.loop(seconds=10)
	async def partner_live_notification(self):
		if self.partners_list is not None:
			for partner in self.partners_list:
				status = self.__check_user(partner['twitch_user'])
				userid = partner['userid']
				user = self.bot.get_user(userid)
			
				if status is True:
					if userid not in self.streamers_online:
						self.streamers_online.append(userid)

						self.bot.logger.info(f"{user} started streaming. Sending notification")
						await self.bot.get_channel(int(DISCORD_PARTNERS_CHANNEL_ID)).send(
							f":red_circle: **LIVE\n** {self.bot.ftl.extract('partners-started-streaming-message', user=f'{user.mention}')}!\n"
							f" https://www.twitch.tv/{partner['twitch_user']}",
							allowed_mentions=discord.AllowedMentions(users=False)
						)
				else:
					if userid in self.streamers_online:
						self.streamers_online.remove(userid)

	
	@commands.command(name="tsopt", aliases=["Tstop"])
	@commands.has_permissions(administrator=True)
	async def tstop(self, ctx):
		if self.partner_live_notification.is_running():
			try:
				self.partner_live_notification.stop()
				self.bot.logger.info("twitch affiliates share stopped!")
				await ctx.message.add_reaction("✅")
			except Exception:
				await ctx.message.add_reaction("‼️")
				self.bot.logger.exception()


	@commands.command(name="tstart", aliases=["Tstart"])
	@commands.has_permissions(administrator=True)
	async def tstart(self, ctx):
		if not self.authenticated:
			await self.__authenticate()

		if not self.partner_live_notification.is_running():
			try:
				self.partner_live_notification.start()
				self.bot.logger.info("twitch affiliates share started!")
				await ctx.message.add_reaction("✅")
			except Exception:
				self.bot.logger.exception()
				await ctx.message.add_reaction("‼️")


	@commands.command(name="addparceiro", aliases=["Addparceiro", "addp", "Addp"])
	@commands.has_permissions(administrator=True)
	async def add_twitch_partner(self, ctx, partner: discord.Member, twitch_name: str):
		try:
			self.__partners.create_or_update_partner(
				{
					'username': partner.name,
					'userid': partner.id,
					'twitch_user': twitch_name
				}
			)
			_partner = self.__partners.get_partner_from_userid(partner.id)
			if _partner not in self.partners_list:
				self.partners_list.append(_partner)

			await ctx.send(f"{self.bot.ftl.extract('partners-partner-successfully-added', partner=partner.name)}")
		except Exception:
			self.bot.logger.exception()
			await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-added', parter=partner.name)}")


	@commands.command(name="rmparceiro", aliases=["Rmparceiro", "rmp", "Rmp"])
	@commands.has_permissions(administrator=True)
	async def rm_twitch_partner(self, ctx, partner: discord.Member):
		try:
			partner_id = partner.id

			if self.__partners.get_partner_from_userid(partner_id):
				if partner_id in self.streamers_online:
					self.streamers_online.remove(partner_id)
				
				self.__partners.delete_partner(partner_id)

				await ctx.send(f"{self.bot.ftl.extract('partners-partner-successfully-removed', partner=partner.name)}")
			else:
				await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-found', partner=partner.name)}")
		except Exception:
			self.bot.logger.exception()

			await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-removed', partner=partner.name)}")


async def setup(bot):
	await bot.add_cog(Partners(bot))
