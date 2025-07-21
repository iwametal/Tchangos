import discord

from discord.ext import commands


class GambleGeneral(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	

	async def rand_roll(self, ctx, roll: int, num: int):
		stat = [6, 7, 9]

		if roll in stat:
			self.bot.rand_stats['selected_stats'][ctx.channel.id] = num - 1

			embed = discord.Embed(title="Stat Rolled", description=f"Stat rolled was **{self.bot.rand_stats['stat_list'][num-1]}!**")
			await ctx.channel.send(embed=embed)

		elif roll ==1025:
			gamble_helper_cog = self.bot.get_cog('GambleHelper')

			if gamble_helper_cog:
				await gamble_helper_cog.show_pokemon(ctx, num)
			else:
				self.bot.logger.error("Gamble Helper Cog not found!")
	
	
	async def ft1_roll(self, ctx, num: int):
		if num == 1:
			embed = discord.Embed(title="FT1 WINNER!", description=f"**Congrats {ctx.author.mention}!** You won the gamble!")
			await ctx.channel.send(embed=embed)
	

	@DeprecationWarning
	async def event_roll(self, ctx, roll: int, num: int):
		if roll == self.bot.EVENT_ROLL.get("roll_number") and num == self.bot.EVENT_ROLL.get("roll_max"):
			embed = discord.Embed(
				title="Event Roll Winner!",
				description=f"Congratulations **{ctx.author.mention}**!! You have won the event!!",
				color = discord.Color.purple()
			)
			await ctx.send(embed=embed)

			self.bot.EVENT_ROLL["event_active"] = False
			self.bot.EVENT_ROLL.pop("roll_number", None)
			self.bot.EVENT_ROLL.pop("roll_max", None)

			channel = ctx.channel
			
			overwrite = discord.PermissionOverwrite()
			overwrite.send_messages = False
			overwrite.add_reactions = False

			await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
			await ctx.send(f'Channel {channel.name} has been locked!')


	""" ROLL COMMAND
	"""
	@commands.command(name='roll', aliases=["Roll"], help='Roll a number between 1 and a specified number.')
	async def roll(self, ctx, roll: int = 100):
		import random

		num = random.randint(1, roll)
		embed = discord.Embed(
			title="",
			description=f"{ctx.author.mention} rolled a **{num}**!",
			color=discord.Color.blue()
		)
		await ctx.send(embed=embed)

		if ctx.channel.id in self.bot.channels['gamble']['rand']:
			await self.rand_roll(ctx, roll, num)
		
		elif ctx.channel.id in self.bot.channels['gamble']['ft1']:
			await self.ft1_roll(ctx, num)

		# elif self.bot.EVENT_ROLL["event_active"] and ctx.channel.id in self.bot.EVENT_ROLL["event_channels"]:
		# 	await self.event_roll(ctx, num, roll)


	""" COINFLIP COMMAND
	"""
	@commands.command(name='coinflip', aliases=['Coinflip', 'Cf', 'cf'])
	async def coinflip(self, ctx, timer: int = 1):
		import random
		import time

		coin_flip = {
			'heads': 'https://i.imgur.com/h1Os447.png',
			'tails': 'https://i.imgur.com/EiBLhPX.png'
		}

		res = random.choice(list(coin_flip.keys()))

		""" Flips a coin """
		flipping = discord.Embed(title="A coin has been flipped...", description="The coin is flying...",
		colour=0x00b8f5)
		flipping.set_image(url="https://i.imgur.com/nULLx1x.gif")
		msg = await ctx.send(embed=flipping)

		time.sleep(timer)

		embed = discord.Embed(title="A coin has been flipped...", description=f"The coin landed on **{res}**!",
						colour=0x00b8f5)
		embed.set_image(url=coin_flip[res])
		await msg.edit(embed=embed)


async def setup(bot):
	await bot.add_cog(GambleGeneral(bot))