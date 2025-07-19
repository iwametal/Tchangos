import discord

from discord.ext import commands


class GuildManager(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="lock", aliases=["Lock"])
	async def lock(self, ctx):
		channel = ctx.channel
		user_permissions = channel.permissions_for(ctx.author)
		
		if user_permissions.manage_channels:
			overwrite = discord.PermissionOverwrite()
			overwrite.send_messages = False
			# overwrite.add_reactions = False

			await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
			await ctx.send(f'Canal {channel.name} lockeado!')
	

	@commands.command(name="unlock", aliases=["Unlock"])
	async def unlock(self, ctx):
		channel = ctx.channel
		user_permissions = channel.permissions_for(ctx.author)
		
		if user_permissions.manage_channels:
			overwrite = discord.PermissionOverwrite()
			overwrite.send_messages = True
			# overwrite.add_reactions = True

			await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
			await ctx.send(f'Canal {channel.name} liberado!')


async def setup(bot):
	await bot.add_cog(GuildManager(bot))