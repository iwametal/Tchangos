from discord.ext import commands
from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions, Content, Part

class Chat(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		self.client = genai.Client(api_key=self.bot.genai_key, http_options=HttpOptions(api_version="v1beta"))
		self.model = "gemini-2.5-flash"
		self.personality = "Você é um mineiro. Pode falar português, inglês e espanhol. Seu inglês possui falhas visíveis, apesar de ser entendível. Seu espanhol é bom, mas também possui algumas falhas. Seu português é fluente, mas você fala com sotaque mineiro. Caso você receber como prompt qualquer outra lingua que não seja uma dessas, sua resposta deverá ser 'Que porra é essa, sei falar isso não carai' ou algo similar a isso."
		self.MAX_RESPONSE_TEXT_LEN = 2000


	@commands.command(name="chat", aliases=["Chat"])
	@commands.guild_only()
	async def chat(self, ctx, *, prompt: str):
		if not prompt:
			await ctx.send(self.bot.ftl.extract('ai-missing-prompt'))
			return
		
		if not (len(prompt) > 5 and (any(char.isalpha() for char in prompt))):
			await ctx.send(self.bot.ftl.extract('ai-prompt-too-short-or-no-text'))
			return

		try:
			response = self.client.models.generate_content(
				model=self.model,
				contents=f"{prompt}",
				config=GenerateContentConfig(
					system_instruction=Content(
						role="system",
						parts=[
							Part(text=f"{self.personality}"),
						],
					)
				),
			)
			response_size = len(response.text)

			if response_size > self.MAX_RESPONSE_TEXT_LEN:
				loop = response_size // self.MAX_RESPONSE_TEXT_LEN

				for i in range(0, loop):
					await ctx.send(response.text[i*self.MAX_RESPONSE_TEXT_LEN:self.MAX_RESPONSE_TEXT_LEN*(i+1)])

				await ctx.send(response.text[loop*self.MAX_RESPONSE_TEXT_LEN:])
			else:
				await ctx.send(response.text)
		except Exception:
			await ctx.send(self.bot.ftl.extract('ai-fail-to-generate-response'))
			self.bot.logger.exception('Error giving chat response')


async def setup(bot):
	await bot.add_cog(Chat(bot))