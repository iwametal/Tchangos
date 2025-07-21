import discord

from discord.ext import commands


class Ft1(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	"""ON MESSAGE EVENT LISTENER
	"""
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		if message.channel.id in self.bot.channels['gamble']['ft1']:
			gamble_helper_cog = self.bot.get_cog('GambleHelper')

			if gamble_helper_cog:
				roll_number = (await gamble_helper_cog.check_roll(message, 'ft1'))[0]
			else:
				roll_number = None
				self.bot.logger.error("Gamble Helper Cog not found!")

			if roll_number and roll_number == 1:
				embed = discord.Embed(title="FT1 WINNER!", description=f"**Congrats {message.author.mention}!** You won the gamble!")
				await message.channel.send(embed=embed)


async def setup(bot):
	await bot.add_cog(Ft1(bot))