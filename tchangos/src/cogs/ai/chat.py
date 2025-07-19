from discord.ext import commands
import google.generativeai as genai

class Chat(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		genai.configure(api_key=self.bot.genai_key)
		model = genai.GenerativeModel("gemini-1.5-flash")
		self._chat = model.start_chat(history=[])
		self.MAX_HISTORY_LENGTH = 100


	@commands.command(name="chat", aliases=["Chat"])
	@commands.guild_only()
	async def chat(self, ctx, *, prompt: str):
		if not prompt:
			await ctx.send("Preciso de um prompt para gerar uma resposta.")
			return
		
		if not (len(prompt) > 5 and (any(char.isalpha() for char in prompt))):
			await ctx.send("O prompt passado é muito curto ou não contém um texto lógico.")
			return

		if len(self._chat.history) > self.MAX_HISTORY_LENGTH:
			self._chat.history = self._chat.history[-(self.MAX_HISTORY_LENGTH - 2):]

		try:
			response = self._chat.send_message(prompt)
			response_size = len(response.text)

			if response_size > 2000:
				loop = int(response_size / 2000)

				for i in range(0, loop):
					await ctx.send(response.text[i*2000:2000*(i+1)])

				await ctx.send(response.text[loop*2000:])
			else:
				await ctx.send(response.text)
		except Exception as e:
			await print(e)


async def setup(bot):
	await bot.add_cog(Chat(bot))