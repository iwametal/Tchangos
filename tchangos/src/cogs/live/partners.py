import discord
import requests
import time

from constants import DISCORD_PARTNERS_CHANNEL_ID, REACTION
from discord.ext import commands, tasks
from mongo.collections.services.partners_service import PartnersService
from twitchAPI.twitch import Twitch


class Partners(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.TWITCH_STREAM_API_ENDPOINT_V5 = 'https://api.twitch.tv/helix/streams?user_login={}'
		self.authenticated = False

		self.__partners = PartnersService(self.bot._mongodb)
		self.partners_list = self.__partners.get_partners(sort_field='twitch_user', sort_order='ascending')
		self.streamers_online = []
		self.__send_notify = True


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

						if self.__send_notify is True:
							self.bot.logger.info(f"{user} started streaming. Sending notification")
							await self.bot.get_channel(int(DISCORD_PARTNERS_CHANNEL_ID)).send(
								f":red_circle: **LIVE\n** {self.bot.ftl.extract('partners-started-streaming-message', user=f'{user.mention}')}!\n"
								f" https://www.twitch.tv/{partner['twitch_user']}",
								allowed_mentions=discord.AllowedMentions(users=False)
							)
				else:
					if userid in self.streamers_online:
						self.streamers_online.remove(userid)


	@commands.command(name="partnersnotify", aliases=["Partnersnotify", "Notify", "notify"])
	@commands.has_permissions(administrator=True)
	async def partners_notify(self, ctx, notify: str="true"):
		notify = notify.lower()
		if notify in ["true", "t"]:
			self.__send_notify = True
		elif notify in ["false", "f"]:
			self.__send_notify = False
		else:
			await ctx.message.add_reaction(REACTION['fail'])
			return

		await ctx.message.add_reaction(REACTION['success'])

	
	@commands.command(name="tstop", aliases=["Tstop"])
	@commands.has_permissions(administrator=True)
	async def tstop(self, ctx):
		if self.partner_live_notification.is_running():
			try:
				self.partner_live_notification.stop()
				self.bot.logger.info("twitch affiliates share stopped!")
				await ctx.message.add_reaction(REACTION['success'])
			except Exception:
				await ctx.message.add_reaction(REACTION['fail'])
				self.bot.logger.exception()


	@commands.command(name="tstart", aliases=["Tstart"])
	@commands.has_permissions(administrator=True)
	async def tstart(self, ctx, notify: str="true"):
		if not self.authenticated:
			await self.__authenticate()

		if not self.partner_live_notification.is_running():
			options = ['true', 't', 'false', 'f']
			self.__send_notify = notify.lower() in options[:2] if notify.lower() in options else self.__send_notify

			try:
				self.partner_live_notification.start()
				self.bot.logger.info("twitch affiliates share started!")
				await ctx.message.add_reaction(REACTION['success'])
			except Exception:
				self.bot.logger.exception('Could not start affiliates sharing -> ')
				await ctx.message.add_reaction(REACTION['fail'])


	@commands.command(name="listparceiros", aliases=["Listparceiros", "Lsparceiros", "lsparceiros", "Lsp", "lsp"])
	async def list_twitch_partners(self, ctx):
		if self.partners_list:
			online = "-# 🟢 online\n" if len(self.streamers_online) > 0 else ""
			offline = "-# 🔴 offline\n" if len(self.streamers_online) < len(self.partners_list) else ""

			for partner in self.partners_list:
				if partner['userid'] in self.streamers_online:
					online = f"{online}- **{partner['twitch_user']}** - <https://twitch.tv/{partner['twitch_user']}>\n"
				else:
					offline = f"{offline}> {partner['twitch_user']}\n"
			
			await ctx.send(f"{online}\n{offline}")
		
		else:
			await ctx.send(self.bot.ftl.extract('partners-no-partners-found'))


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
			partner_obj = self.__partners.get_partner_from_userid(partner.id)
			if partner_obj:
				if partner.id in self.streamers_online:
					self.streamers_online.remove(partner.id)
				
				self.partners_list.remove(partner_obj)
				self.__partners.delete_partner(partner.id)

				await ctx.send(f"{self.bot.ftl.extract('partners-partner-successfully-removed', partner=partner.name)}")
			else:
				await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-found', partner=partner.name)}")
		except Exception:
			self.bot.logger.exception(f"{self.bot.ftl.extract('partners-partner-could-not-be-removed', partner=partner.name)}")

			await ctx.send(f"{self.bot.ftl.extract('partners-partner-could-not-be-removed', partner=partner.name)}")


async def setup(bot):
	await bot.add_cog(Partners(bot))
