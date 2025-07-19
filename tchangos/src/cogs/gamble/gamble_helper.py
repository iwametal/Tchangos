import asyncio
import discord

from discord.ext import commands


class GambleHelper(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.extract_methods = {
			'n!': {
				'bot_id': 854233015475109888,
				'method': self.extract_p2a
			},
			'!': {
				'bot_id': 235148962103951360,
				'method': self.extract_carl
			},
			'>': {
				'bot_id': 204255221017214977,
				'method': self.extract_yag
			}
			# '+': {
			# 	'bot_id': 1233876149931737220,
			# 	'method': self.extract_shroom
			# }
		}


	async def show_pokemon(self, ctx, dex_number: int):
		index = -1
		bold_stat = [''] * 9
		stat_list = self.bot.rand_stats['stat_list'].copy()
		data_list = []

		if ctx.channel.id in self.bot.rand_stats['selected_stats']:
			index = self.bot.rand_stats['selected_stats'][ctx.channel.id]
		
		if index != -1:
			bold_stat[index] = "**"
			# stat_list[index] = stat_list[index].upper()

		data = next((p for p in self.bot.pokemon_data if p['dex_number'] == dex_number), None)
		if not data:
			await ctx.channel.send(f"Pokémon with Dex number {dex_number} not found.")
			return

		# embed = discord.Embed(title=f"#{data['dex_number']} — {data['name'].capitalize()}", description=data['description'].replace("\n", " ").replace("\f", " "), color=discord.Color.blue())
		embed = discord.Embed(title=f"#{data['dex_number']} — {data['name'].capitalize()}", color=discord.Color.blue())
		
		# if 'evolution_chain' in data:
		# 	embed.add_field(name="Evolution", value=" -> ".join(data['evolution_chain']).capitalize(), inline=False)
		
		# if 'types' in data:
		# 	types = ", ".join(data['types']).capitalize()
		# 	embed.add_field(name="Types", value=types, inline=True)
		
		# if 'region' in data:
		# 	embed.add_field(name="Region", value=data['region'].capitalize(), inline=True)
		
		# embed.add_field(name="Catchable", value="Yes", inline=True)
		
		stats = ''
		if 'base_stats' in data:
			base_stats = data['base_stats']
			for i in range(0, 6):
				data_list.append(base_stats.get(self.bot.rand_stats['stat_data'][i], 'N/A'))
				stats += f"{bold_stat[i]}{stat_list[i]}: {data_list[-1]}{bold_stat[i]}\n"
			
			data_list.append(sum(base_stats.values()))
			stats += f"{bold_stat[6]}{stat_list[6]}: {data_list[-1]}{bold_stat[6]}\n"
			# stats = (
			# 	f"**HP**: {base_stats.get('hp', 'N/A')}\n"
			# 	f"**Attack**: {base_stats.get('attack', 'N/A')}\n"
			# 	f"**Defense**: {base_stats.get('defense', 'N/A')}\n"
			# 	f"**Sp. Atk**: {base_stats.get('special-attack', 'N/A')}\n"
			# 	f"**Sp. Def**: {base_stats.get('special-defense', 'N/A')}\n"
			# 	f"**Speed**: {base_stats.get('speed', 'N/A')}\n"
			# 	f"**Total**: {sum(base_stats.values())}"
			# )
			# embed.add_field(name="Base Stats", value=stats, inline=True)
		
		# if 'other_lang_names' in data:
		# 	names = data['other_lang_names']
		# 	names_str = (
		# 		f":flag_jp: {names.get('ja-Hrkt', 'N/A')}\n"
		# 		f":flag_jp: {names.get('roomaji', 'N/A')}\n"
		# 		f":flag_kr: {names.get('ko', 'N/A')}\n"
		# 		f":flag_cn: {names.get('zh-Hant', 'N/A')}\n"
		# 		f":flag_fr: {names.get('fr', 'N/A')}\n"
		# 		f":flag_de: {names.get('de', 'N/A')}\n"
		# 		f":flag_es: {names.get('es', 'N/A')}\n"
		# 		f":flag_it: {names.get('it', 'N/A')}\n"
		# 		f":flag_us: {names.get('en', 'N/A')}"
		# 	)
		# 	embed.add_field(name="Names", value=names_str, inline=True)
		
		appearance_str = ''
		if 'appearance_info' in data:
			appearance = data['appearance_info']
			data_list.append(appearance.get(self.bot.rand_stats['stat_data'][7], 0) / 10)
			data_list.append(appearance.get(self.bot.rand_stats['stat_data'][8], 0) / 10)
			appearance_str = "{}{}: {} m{}\n{}{}: {} kg{}".format(
				bold_stat[7],
				stat_list[7],
				data_list[-2],
				bold_stat[7],
				bold_stat[8],
				stat_list[8],
				data_list[-1],
				bold_stat[8],
			)
			# appearance_str = f"**Height**: {appearance.get('height', 0) / 10} m\n**Weight**: {appearance.get('weight', 0) / 10} kg"
			# embed.add_field(name="Appearance", value=appearance_str, inline=True)
		
		embed.add_field(name="Stats", value=f"{stats}\n{appearance_str}", inline=True)
		# if 'gender_ratio' in data:
		# 	gender_ratio = data['gender_ratio']
		# 	gender_ratio_str = f"Male: {gender_ratio.get('male', 0) / 8 * 100}%\nFemale: {gender_ratio.get('female', 0) / 8 * 100}%"
		# 	embed.add_field(name="Gender Ratio", value=gender_ratio_str, inline=True)
		
		if 'official_artwork_url' in data:
			# embed.set_image(url=data['official_artwork_url'])
			embed.set_thumbnail(url=data['official_artwork_url'])
		
		await ctx.channel.send(embed=embed)
		if index > -1:
			stat_embed = discord.Embed(title=f"{ctx.author.name} got {data_list[index]}", color=0x000000)
			await ctx.channel.send(embed=stat_embed)


	@DeprecationWarning
	async def check_bot_roll(self, message):
		import time

		next_message = None
		time_limit = 10
		start_time = time.time()

		while ((time.time() - start_time) < time_limit and not next_message):
			channel = message.channel
			
			async for msg in channel.history(limit=3):
				if msg.author == self.bot.user:
					if msg.embeds and msg.embeds[0].description and ' rolled a ' in msg.embeds[0].description:
						next_message = msg
					break
			time.sleep(0.1)

		return next_message
	

	def part_message(self, content):
		message_part = content.lower().strip().split('roll')

		for index in range (0, len(message_part)):
			message_part[index] = message_part[index].strip()

		if len(message_part) == 1:
			message_part.append(None)
		else:
			try:
				message_part[1] = message_part[1].strip().split(' ')[0]
				if 'd' in message_part[1]:
					message_part[1] = message_part[1].split('d')[1].strip()
			except:
				message_part = None
		
		return message_part
	

	""" Extract Roll From P2Assistant
	"""
	def extract_p2a(self, message):
		try:
			embed = message.embeds[0]
			description = embed.description
			if description:
				roll_number = description.split(' rolled a ')[1].split('**')[1]
				roll = int(roll_number)
				return roll
		except (ValueError, IndexError, AttributeError) as e:
			print(f'[debug] Failed to extract Dex number for n!roll: {e}')
			return None
	

	""" Extract Roll From CarlBot
	"""
	def extract_carl(self, message):
		try:
			embed = message.embeds[0]
			title = embed.title
			if title:
				roll_number = title.split('rolls')[1].split('**')[1]
				roll = int(roll_number)
				return roll
		except (ValueError, IndexError, AttributeError) as e:
			print(f'[debug] Failed to extract Dex number for !roll: {e}')
			return None
	

	""" Extract Roll From YAGPDB
	"""
	def extract_yag(self, message):
		try:
			roll_number = message.content.split()[1]
			roll = int(roll_number)
			return roll
		except (ValueError, IndexError) as e:
			print(f'[debug] Failed to extract Dex number for >roll: {e}')
			return None
	

	""" Extract Roll From ShroomBot
	"""
	@DeprecationWarning
	def extract_shroom(self, message):
		try:
			embed = message.embeds[0]
			description = embed.description
			if description:
				roll_number = description.split(' rolled a ')[1].split('**')[1]
				roll = int(roll_number)
				return roll
		except (ValueError, IndexError, AttributeError) as e:
			print(f'[debug] Failed to extract Dex number for +roll: {e}')
			return None
	

	""" Extract Roll Number
	"""
	def extract(self, prefix, message):
		print(message)
		if prefix not in self.extract_methods:
			print(f'[debug] Failed to extract Dex number: Unknown prefix {prefix}')
			return None

		return self.extract_methods[prefix]['method'](message)
	

	"""Check roll type for command
	"""
	async def check_roll(self, message, gamble_type):
		# Dictionary to map commands to bot IDs

		message_part = self.part_message(message.content)
		if not message_part:
			return None, None

		prefix = next((p for p in self.extract_methods if message_part[0] == p), None)

		if prefix:
			bot_id = self.extract_methods[prefix]['bot_id']

			def check(m):
				return m.author.id == bot_id and m.channel == message.channel and (prefix != '>roll 1024' or m.content)

			try:
				# next_message = await self.bot.wait_for('message', check=check, timeout=10.0) if not prefix == '+' else await self.check_bot_roll(message)
				next_message = await self.bot.wait_for('message', check=check, timeout=10.0)

				roll_number = self.extract(prefix, next_message)

				if gamble_type == 'rand':
					if message_part[1] == '1025':
						return roll_number, 'rand'
					
					elif message_part[1] in ['6', '7', '9']:
						return roll_number, 'stat'

				elif gamble_type == 'ft1':
					return roll_number, 'ft1'

			except asyncio.TimeoutError:
				print("[debug] Timed out waiting for the next message.")
				return None, None

		return None, None


async def setup(bot):
	await bot.add_cog(GambleHelper(bot))