import discord

from discord.ext import commands

class Event(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	

	@DeprecationWarning
	@commands.command(name="seteventroll", aliases=["Seteventroll", "Ser", "ser"])
	@commands.has_permissions(administrator=True)
	async def set_event_roll(self, ctx, roll_number, roll_max):
		if True:
			await ctx.send("This command is deprecated.")
		
		else:
			roll_number = int(roll_number)
			roll_max = int(roll_max)

			self.bot.EVENT_ROLL['event_active'] = True
			self.bot.EVENT_ROLL['roll_number'] = roll_number
			self.bot.EVENT_ROLL['roll_max'] = roll_max

			embed = discord.Embed(
				title="New Event Roll Set",
				description=f"Get Number **{roll_number}** out of `+roll {roll_max}` to win the event!",
			)

			await ctx.send(embed=embed)


async def setup(bot):
	await bot.add_cog(Event(bot))