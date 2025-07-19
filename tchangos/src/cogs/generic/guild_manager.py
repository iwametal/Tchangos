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
			await ctx.send(f'Channel {channel.name} has been locked!')
		else:
			await ctx.send('You do not have permission to lock this channel, beesh :robot:')
	

	@commands.command(name="unlock", aliases=["Unlock"])
	async def unlock(self, ctx):
		channel = ctx.channel
		user_permissions = channel.permissions_for(ctx.author)
		
		if user_permissions.manage_channels:
			overwrite = discord.PermissionOverwrite()
			overwrite.send_messages = True
			# overwrite.add_reactions = True

			await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
			await ctx.send(f'Channel {channel.name} has been unlocked!')
		else:
			await ctx.send('You do not have permission to unlock this channel, beesh :robot:')


async def setup(bot):
	await bot.add_cog(GuildManager(bot))