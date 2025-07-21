import discord

from discord.ext import commands


class Rand(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	"""ON MESSAGE EVENT LISTENER
	"""
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		if message.channel.id in self.bot.channels['gamble']['rand']:
			gamble_helper_cog = self.bot.get_cog('GambleHelper')

			if gamble_helper_cog:
				roll_number, gamble_type = await gamble_helper_cog.check_roll(message, 'rand')
			else:
				roll_number, gamble_type = None, None
				self.bot.logger.error("Gamble Helper Cog not found!")

			if roll_number and gamble_type:
				if gamble_type == 'rand':
					await gamble_helper_cog.show_pokemon(message, roll_number)

				elif gamble_type == 'stat':

					self.bot.rand_stats['selected_stats'][message.channel.id] = roll_number - 1

					embed = discord.Embed(title="Stat Rolled", description=f"Stat rolled was **{self.bot.rand_stats['stat_list'][roll_number-1]}!**")
					await message.channel.send(embed=embed)
	

	@commands.command(name='setrandstat', aliases=['Setrandstat', 'Setrs', 'setrs'], help='Set the stats for the random stats command.')
	async def set_rand_stat(self, ctx, *stat):
		if ctx.channel.id in self.bot.channels['gamble']['rand']:
			errors = False
			v_stats = ''
			for index in range(0, len(self.bot.rand_stats['stat_list'])):
				v_stats += f"- **{index+1} ・ {self.bot.rand_stats['stat_list'][index]}**\n"

			err_embed = discord.Embed(
				title="Invalid Stat Provided",
				description=f"**Please enter a valid stat. (either number or name):**\n\n{v_stats}",
			)
			err_embed.set_footer(text="Want a random stat for you? Roll a number of 6, 7, or 9!")

			try:
				stat = int(''.join(stat))

				if stat < 1 or stat > len(self.bot.rand_stats['stat_list']):
					errors = True

					await ctx.send(embed=err_embed)
			except:
				stat = ''.join(stat)
				valid_stat = False

				for index in range(0, len(self.bot.rand_stats['stat_list'])):
					rs = ''.join(s.strip() for s in self.bot.rand_stats['stat_list'][index].lower().split(' '))

					if stat == rs:
						valid_stat = True
						stat = index + 1
						break
				
				if not valid_stat:
					errors = True
					await ctx.send(embed=err_embed)
				
			if not errors:
				self.bot.rand_stats['selected_stats'][ctx.channel.id] = stat-1

				embed = discord.Embed(title="Rand Stat Set", description=f"Status set to **{self.bot.rand_stats['stat_list'][stat-1]}!**")
				await ctx.send(embed=embed)

	
	@commands.command(name='randtest', aliases=['Randtest', 'Randt', 'randt'], help='Check stats of specific pokémon')
	@commands.has_permissions(administrator=True)
	async def rand_test(self, ctx, num):
		try:
			num = int(num)
			gamble_helper_cog = self.bot.get_cog('GambleHelper')

			if gamble_helper_cog:
				await gamble_helper_cog.show_pokemon(ctx, num)
			else:
				self.bot.logger.error("Gamble Helper Cog not found!")

		except ValueError:
			await ctx.send(f"Please enter a valid number between 1 and {len(self.pokemon_data)}")
			return


async def setup(bot):
	await bot.add_cog(Rand(bot))