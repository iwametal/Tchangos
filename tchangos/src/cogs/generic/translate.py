from constants import DATA_PATH
from discord.ext import commands
from googletrans import Translator

from helper import Helper


class Translate(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.flags = Helper.get_json(f"{DATA_PATH}/flags.json", {})
	

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if user.bot:
			return
		
		message = reaction.message

		if not message.content.strip():
			return

		if reaction.emoji in self.flags:
			try:
				translator = Translator()
				trans_msg = await translator.translate(message.content, dest=self.flags[reaction.emoji])
				await message.channel.send(f"-# {message.content}\n> {trans_msg.text}")
			except Exception:
				self.bot.logger.exception('Unable to translate message')
				translate_error_msg = self.bot.ftl.extract('translate-unnable-to-translate-message')
				await message.channel.send(f"❌ | {translate_error_msg}")
	

	@commands.command(name="translate", aliases=["Translate"])
	@commands.has_permissions(administrator=True)
	async def translate(self, ctx, *, message: str):
		try:
			translator = Translator()
			trans_msg = await translator.translate(message, dest='pt')
			await ctx.send(f"-# {message}\n> {trans_msg.text}")
		except Exception:
			self.bot.logger.exception('Unable to translate message')
			translate_error_msg = self.bot.ftl.extract('translate-unnable-to-translate-message')
			await message.channel.send(f"❌ | {translate_error_msg}")


	@commands.command(name="addflag", aliases=["Addflag"])
	@commands.has_permissions(administrator=True)
	async def add_translation_flag(self, ctx, *, message: str):
		try:
			split_msg = message.split(" ")
			flag = split_msg[0].strip()
			translation_alias = split_msg[-1].strip()

			if flag in self.flags:
				await ctx.send(self.bot.ftl.extract('translate-flag-already-in-map', flag=flag, alias=translation_alias))
				return

			self.flags[flag] = translation_alias
			Helper.set_json(f"{DATA_PATH}/flags.json", self.flags)
			await ctx.send(self.bot.ftl.extract('translate-flag-successfully-added-in-map', flag=flag, alias=translation_alias))
		except Exception:
			await ctx.send(self.bot.ftl.extract('translate-flag-error-adding-in-map', flag=flag, alias=translation_alias))
			self.bot.logger.exception('Unable to add flag')


	@commands.command(name="rmflag", aliases=["Rmflag"])
	@commands.has_permissions(administrator=True)
	async def remove_translation_flag(self, ctx, *, flag: str):
		try:
			if flag in self.flags:
				del self.flags[flag]
				Helper.set_json(f"{DATA_PATH}/flags.json", self.flags)
				await ctx.send(self.bot.ftl.extract('translate-flag-successfully-deleted-from-map', flag=flag))
			else:
				await ctx.send(self.bot.ftl.extract('translate-flag-not-in-map', flag=flag))
		except Exception:
			await ctx.send(self.bot.ftl.extract('translate-flag-not-in-map', flag=flag))
			self.bot.logger.exception('Unable to add flag')


async def setup(bot):
	await bot.add_cog(Translate(bot))