import discord
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from discord.ext import commands
from constants import CHANNELS_JSON
from helper import Helper


class GambleManager(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(name="addchannel", aliases=["Addchannel", "Addc", "addc"], help="Add a channel to the roll list.")
	@commands.has_permissions(administrator=True)
	async def add_channel(self, ctx, channel_type):
		if ctx.channel.id not in self.bot.channels['gamble'][channel_type]:
			self.bot.channels['gamble'][channel_type].append(ctx.channel.id)
			Helper.set_json(CHANNELS_JSON, self.bot.channels)
			await ctx.send(f"Channel **{ctx.channel.name}** has been added to the **{channel_type}** roll list!")
		else:
			await ctx.send(f"Channel **{ctx.channel.name}** is already in the **{channel_type}** roll list!")
	

	@commands.command(name="removechannel", aliases=["Removechannel", "Removec", "removec", "Rmc", "rmc"], help="Remove a channel from the roll list.")
	@commands.has_permissions(administrator=True)
	async def remove_channel(self, ctx, channel_type):
		if ctx.channel.id in self.bot.channels['gamble'][channel_type]:
			self.bot.channels['gamble'][channel_type].remove(ctx.channel.id)
			Helper.set_json(CHANNELS_JSON, self.bot.channels)
			await ctx.send(f"Channel **{ctx.channel.name}** has been removed from the **{channel_type}** roll list!")
		else:
			await ctx.send(f"Channel **{ctx.channel.name}** is not in the **{channel_type}** roll list!")


	@commands.command(name="addrandchannel", aliases=["Addrandchannel", "Addrandc", "addrandc"], help="Add a channel to the rand roll list.")
	@commands.has_permissions(administrator=True)
	async def add_rand_channel(self, ctx):
		await self.add_channel(ctx, 'rand')
	

	@commands.command(name="removerandchannel", aliases=["Removerandchannel", "Removerc", "removerc", "Rmrandc", "rmrandc"], help="Remove a channel from the rand roll list.")
	@commands.has_permissions(administrator=True)
	async def remove_rand_channel(self, ctx):
		await self.remove_channel(ctx, 'rand')
	

	@commands.command(name="addft1channel", aliases=["Addft1channel", "Addft1c", "addft1c"], help="Add a channel to the FT1 roll list.")
	@commands.has_permissions(administrator=True)
	async def add_ft1_channel(self, ctx):
		await self.add_channel(ctx, 'ft1')


	@commands.command(name="removeft1channel", aliases=["Removeft1channel", "Removeft1c", "removeft1c", "Rmft1c", "rmft1c"], help="Remove a channel from the FT1 roll list.")
	@commands.has_permissions(administrator=True)
	async def remove_ft1_channel(self, ctx):
		await self.remove_channel(ctx, 'ft1')
	

	@commands.command(name="addhighchannel", aliases=["Addhighchannel", "Addhighc", "addhighc"], help="Add a channel to the high roll list.")
	@commands.has_permissions(administrator=True)
	async def add_high_channel(self, ctx):
		await self.add_channel(ctx, 'high')
	

	@commands.command(name="removehighchannel", aliases=["Removehighchannel", "Removehighc", "removehighc", "Rmhighc", "rmhighc"], help="Remove a channel from the high roll list.")
	@commands.has_permissions(administrator=True)
	async def remove_high_channel(self, ctx):
		await self.remove_channel(ctx, 'high')
	

	@commands.command(name="addlowchannel", aliases=["Addlowchannel", "Addlowc", "addlowc"], help="Add a channel to the low roll list.")
	@commands.has_permissions(administrator=True)
	async def add_low_channel(self, ctx):
		await self.add_channel(ctx, 'low')
	

	@commands.command(name="removelowchannel", aliases=["Removelowchannel", "Removelowc", "removelowc", "Rmlowc", "rmlowc"], help="Remove a channel from the low roll list.")
	@commands.has_permissions(administrator=True)
	async def remove_low_channel(self, ctx):
		await self.remove_channel(ctx, 'low')
	

	@commands.command(name="addcoinflipchannel", aliases=["Addcoinflipchannel", "Addcoinflipc", "addcoinflipc", "Addcfc", "addcfc"], help="Add a channel to the coinflip list.")
	@commands.has_permissions(administrator=True)
	async def add_coinflip_channel(self, ctx):
		await self.add_channel(ctx, 'coin_flip')
	

	@commands.command(name="removecoinflipchannel", aliases=["Removecoinflipchannel", "Removecoinflipc", "removecoinflipc", "Rmcfc", "rmcfc"], help="Remove a channel from the coinflip list.")
	@commands.has_permissions(administrator=True)
	async def remove_coinflip_channel(self, ctx):
		await self.remove_channel(ctx, 'coin_flip')
	

	@commands.command(name="addtournamentchannel", aliases=["Addtournamentchannel", "Addtournamentc", "addtournamentc", "Addtc", "addtc"], help="Add a channel to the tournament list.")
	@commands.has_permissions(administrator=True)
	async def add_tournament_channel(self, ctx):
		await self.add_channel(ctx, 'tournament')
	

	@commands.command(name="removetournamentchannel", aliases=["Removetournamentchannel", "Removetournamentc", "removetournamentc", "Rmtc", "rmtc"], help="Remove a channel from the tournament list.")
	@commands.has_permissions(administrator=True)
	async def remove_tournament_channel(self, ctx):
		await self.remove_channel(ctx, 'tournament')
	

	@commands.command(name="listgamblechannels", aliases=["Listgamblechannels", "Listgc", "listgc"], help="List all gamble channels.")
	@commands.has_permissions(administrator=True)
	async def list_gamble_channels(self, ctx, channel_type=None):
		embed = discord.Embed(title="Gamble Channels", color=discord.Color.pink())
		if channel_type:
			if channel_type in self.bot.channels['gamble']:
				embed.add_field(name=channel_type, value="\n".join([f"<#{channel_id}>" for channel_id in self.bot.channels['gamble'][channel_type]]), inline=True)
				await ctx.send(embed=embed)
			else:
				await ctx.send(f"**{channel_type}** is not a valid channel type!")
		else:
			for channel_type in self.bot.channels['gamble']:
				embed.add_field(name=channel_type, value="\n".join([f"<#{channel_id}>" for channel_id in self.bot.channels['gamble'][channel_type]]), inline=True)
			await ctx.send(embed=embed)
	

async def setup(bot):
	await bot.add_cog(GambleManager(bot))