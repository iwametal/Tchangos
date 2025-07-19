import asyncio
import discord
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from constants import POKETWO_USER, trade_messages
from discord.ext import commands


class GambleTrades(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	

	def is_sending_trade(self, content):
		ret = False
		try:
			poketwo = f"<@{POKETWO_USER}>"
			if content.startswith(poketwo):
				msg_part = content.split(poketwo)[1].split(' ')
				msg_part = [msg.strip().lower() for msg in msg_part if msg and msg != ' ']

				ret = len(msg_part) > 2\
					and msg_part[0] in trade_messages['command']
		except Exception as e:
			print(f"Error checking trade: {e}")
			ret = False
		
		return ret
	

	async def get_requested_user(self, message):
		try:
			poketwo = f"<@{POKETWO_USER}>"
			if message.content.startswith(poketwo):
				msg_part = message.content.split(poketwo)[1].split(' ')
				msg_part = [msg.strip().lower() for msg in msg_part if msg and msg != ' ']
				guild = message.guild

				return await guild.fetch_member(int(msg_part[1][2:-1]))
		except Exception as e:
			return None


	async def create_trade_embed(self, message, trade_msg, requested_user):
		send_user = message.author
		send_user_nick = send_user.nick if send_user.nick else send_user.name
		requested_user_nick = requested_user.nick if requested_user.nick else requested_user.name

		message.channel.send(f"{send_user.name} t {requested_user.name}")

		embed = discord.Embed()
		embed.title = f"{trade_messages['completed']}{send_user_nick} and {requested_user_nick}."
		embed.color = discord.Color.pink()

		if trade_msg.embeds:
			embed = trade_msg.embeds[0]

			msg_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
			embed.add_field(name="Message Link", value=msg_link, inline=False)

		return embed


	@commands.Cog.listener()
	async def on_message(self, message):
		if any(message.channel.id in channels for channels in self.bot.channels['gamble'].values())\
			and self.is_sending_trade(message.content):

			def check(m):
				return m.author.id == POKETWO_USER\
					and m.channel == message.channel\
						and m.embeds and m.embeds[0].title and m.embeds[0].title.startswith(trade_messages['send'])

			try:
				requested_user = await self.get_requested_user(message)
				trade_msg = await self.bot.wait_for('message', check=check, timeout=90.0)

				def check_trade(m):
					return m.author.id == POKETWO_USER\
						and m.channel == message.channel\
							and m.embeds and m.embeds[0].fields and len(m.embeds[0].fields) > 1\
								and m.embeds[0].fields[0].name.startswith(trade_messages['completed'])\
									and m.embeds[0].fields[1].name.startswith(trade_messages['completed'])

				trade_msg = await self.bot.wait_for('message', check=check_trade, timeout=300.0)

				embed = await self.create_trade_embed(message, trade_msg, requested_user)

				if embed.fields:
					log_channel = self.bot.get_channel(self.bot.channels['gamble_extra']['log'])
					await log_channel.send(embed=embed)

			except asyncio.TimeoutError as e:
				print(f"Could not track a completed trade {e}")
	

	@commands.command(name="ttt")
	async def ttt(self, ctx):
		print(ctx.mentions[0])
		if any(ctx.channel.id in channels for channels in self.bot.channels['gamble'].values())\
			and len(ctx.mentions) == 2 and ctx.mentions[0] == POKETWO_USER:
			await ctx.channel.send(f"{ctx.mentions[0]} - {ctx.mentions[1]}")
			await ctx.add_reaction('🔁')


async def setup(bot):
	await bot.add_cog(GambleTrades(bot))