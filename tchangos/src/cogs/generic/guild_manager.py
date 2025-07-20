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

			try:
				await ctx.message.add_reaction('✅')
			except Exception:
				lock_msg = self.bot.ftl.extract('guild-manager-lock-channel-message', channel=channel.name)
				await ctx.send(f'{lock_msg}!')
	

	@commands.command(name="unlock", aliases=["Unlock"])
	async def unlock(self, ctx):
		channel = ctx.channel
		user_permissions = channel.permissions_for(ctx.author)
		
		if user_permissions.manage_channels:
			overwrite = discord.PermissionOverwrite()
			overwrite.send_messages = True
			# overwrite.add_reactions = True

			await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

			try:
				await ctx.message.add_reaction('✅')
			except Exception:
				unlock_msg = self.bot.ftl.extract('guild-manager-unlock-channel-message')
				await ctx.send(f'{unlock_msg}!')


async def setup(bot):
	await bot.add_cog(GuildManager(bot))