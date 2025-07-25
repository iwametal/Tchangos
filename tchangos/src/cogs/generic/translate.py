from constants import TRANSLATE_FLAGS
from discord.ext import commands
from googletrans import Translator


class Translate(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
	

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if user.bot:
			return
		
		message = reaction.message

		if not message.content.strip():
			return

		if reaction.emoji in TRANSLATE_FLAGS:
			try:
				translator = Translator()
				trans_msg = await translator.translate(message.content, dest=TRANSLATE_FLAGS[reaction.emoji])
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


async def setup(bot):
	await bot.add_cog(Translate(bot))