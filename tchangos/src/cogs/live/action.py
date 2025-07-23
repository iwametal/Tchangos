from discord.ext import commands


class LiveInteraction(commands.Cog):
	def __init__(self, bot):
		super().__init__()

		self.bot = bot
	

	"""TODO
	"""
	# @commands.command(name="action", aliases=['Action'])
	# @commands.cooldown(1, 300, commands.BucketType.guild)
	# async def action(self, ctx, _action):
	# 	await ctx.send(f"{_action} logo")


async def setup(bot):
	await bot.add_cog(LiveInteraction(bot))
