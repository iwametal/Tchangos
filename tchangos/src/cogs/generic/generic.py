import discord

from discord.ext import commands


class Generic(commands.Cog):

	def __init__(self, bot):
		self.bot = bot


	@commands.command(name="ping", aliases=["Ping"], brief="Check the bot's latency.")
	async def ping(self, ctx):
		await ctx.send(f"**:ping_pong: | Pong!** 「`{int(self.bot.latency * 1000)} ms`」")


	"""BAN COMMAND
	"""
	@commands.command(name="ban", aliases=["Ban"])
	@commands.guild_only()
	# @commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		# Check if the author of the command has permission to ban members
		if not ctx.author.guild_permissions.ban_members:
			await ctx.send(f":point_up::nerd: {self.bot.ftl.extract('missing-permissions')}")
			
		else:
			ban_msg  = self.bot.ftl.extract('generic-member-banned-message', member=member.name)
			ban = discord.Embed(title=f"<:aham:978415635203756132> | {ban_msg}!", description=f"Reason: {reason}\nBy: {ctx.author.mention}")
			await ctx.message.delete()
			await ctx.channel.send(embed=ban)

			bandm = ""
			try:
				await member.ban(reason=reason)

			except Exception as e:
				self.bot.logger.error(e)

			try:
				ban_msg = self.bot.ftl.extractor('generic-member-banned-dm-message')
				bandm = discord.Embed(title=f"<:aham:978415635203756132> | {ban_msg}!", description=f"Reason: {reason}\nBy: {ctx.author.mention}")
				await member.send(embed=bandm)
			except Exception as e:
				self.bot.logger.error(e)

		# ban_embed = discord.Embed(
		# 	title=f"<:1257147175649935361:> <:1257147441732390933:> | Banned {member.name} from Shroom Room!", 
		# 	description=f"Reason: {reason}\nBy: {ctx.author.mention}", 
		# 	color=discord.Color.green())
		# already_banned_embed = discord.Embed(title=f"<:1257146986071720006:> | {member.name} is already Banned!", color=discord.Color.teal())


	"""UNBAN CMD
	"""
	@commands.command(name="unban", aliases=["Unban", "Unb", "unb"])
	@commands.guild_only()
	# @commands.has_permissions(ban_members=True)
	async def unban(self, ctx, user: discord.User, *, reason="***No reason provided.***"):
		# Check if the author of the command has permission to ban members
		if not ctx.author.guild_permissions.ban_members:
			await ctx.send(f":point_up::nerd: {self.bot.ftl.extract('missing-permissions')}")
		
		else:
			unban_msg = self.bot.ftl.extract('generic-member-unbanned-message', member=user.name)
			not_banned_msg = self.bot.ftl.extract('generic-member-is-not-banned-message', member=user.name) 
			unban_embed = discord.Embed(title=f"<:aham:978415635203756132> | {unban_msg}!", description=f"Reason: {reason}\nBy: {ctx.author.mention}", color=discord.Color.green())
			not_banned_embed = discord.Embed(title=f"<:aham:978415635203756132> | {not_banned_msg}!", color=discord.Color.teal())
			
			try:
				# Attempt to fetch the ban entry
				await ctx.guild.fetch_ban(user)
			except discord.errors.NotFound:
				await ctx.send(embed=not_banned_embed)
				return
			
			# Unban the user
			await ctx.guild.unban(user, reason=reason)
			await ctx.send(embed=unban_embed)
			await ctx.message.delete()


	"""KICK COMMAND
	"""
	@commands.command(name="kick", aliases=["Kick"])
	@commands.guild_only()
	# @commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		if not ctx.author.guild_permissions.kick_members:
			await ctx.send(f":point_up::nerd: {self.bot.ftl.extract('missing-permissions')}")
		else:
			kick_msg = self.bot.ftl.extract('generic-member-kicked-message', member=member.name)
			kick = discord.Embed(title=f"<:hammer:> | {kick_msg}!", description=f"Reason: {reason}\nBy: {ctx.author.mention}")
			await ctx.message.delete()
			await ctx.channel.send(embed=kick)

			try:
				await member.kick(reason=reason)
			except Exception as e:
				self.bot.logger.error(e)

			try:
				kickdm_msg = self.bot.ftl.extract('generic-member-kicked-dm-message')
				kickdm = discord.Embed(title=f"<:hammer:> | {kickdm_msg}!", description=f"Reason: {reason}\nBy: {ctx.author.mention}")
				await member.send(embed=kickdm)
			except Exception as e:
				self.bot.logger.error(e)


	"""PURGE COMMAND
	"""
	@commands.command(name="clear", aliases=["Clear", "Purge", "purge"])
	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, amount: int = 5):
		message = await ctx.send(f"**:put_litter_in_its_place: | {self.bot.ftl.extract('generic-purge-message', amount=amount, channel_id=ctx.channel.id)}!**")
		await ctx.channel.purge(limit=amount+2)
		await message.delete(delay=5)


async def setup(bot):
	await bot.add_cog(Generic(bot))