import discord
import logging

# from constants import channels, pokemon_data, rand_stats
from constants import LOGGING_PATH
from discord.ext import commands
from helper import Helper, FTLExtractor
from mongo.config.DBConnectionHandler import MongoConnectionHandler


### ENV VARIABLES ###
gen_data = Helper.get_general_config('config.ini')


def get_prefix(bot, message):
    return commands.when_mentioned_or('.')(bot, message)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.reactions = True


class TchangosBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ### MONGO SETTINGS ###
        mongodb = MongoConnectionHandler(gen_data['mongodb']['connection_string'])
        self._mongodb = mongodb.get_conn(gen_data['mongodb']['user'], gen_data['mongodb']['pass'])
        ###

        ### SETTING LOGGER ###
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")

        file_handler = logging.FileHandler(f'{LOGGING_PATH}/bot.log')
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        ###

        ### FLUENT ###
        self.ftl = FTLExtractor(locale='pt', fallback_locale='pt')
        ###

        ### KEYS ###
        self.genai_key = gen_data['genai']['key']
        self.twitch_client = gen_data['twitch']['client_id']
        self.twitch_secret = gen_data['twitch']['client_secret']
        self.twitch_token = None
        self.expires_at = 0
        ###

        # POKEMON_DATA
        # self.pokemon_data = pokemon_data
        # self.rand_stats = rand_stats

        # GAMBLE CHANNELS
        # self.channels = channels

        # self.EVENT_ROLL = {
        #     'event_active': False,
        #     'event_channels': event_channel_list,
        #     'roll_number': 0,
        #     'roll_max': 0
        # }
    

    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user}\n------')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Tchangos"))
        self.logger.info("Tchangos bot is up")
    

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

        from error_list import command_error_list
        for key, value in command_error_list.items():
            if isinstance(error, value['error']):
                await ctx.send(f"{value['prefix']}{self.ftl.extract(key)} -> {error}")
                return

        self.logger.exception(f"❌ | <Unexpected error>\n{error}")


    async def setup_hook(self):
        import glob
        import os

        await bot.load_extension('jishaku')

        cog_folders = ['ai', 'generic', 'live']

        for folder in cog_folders:
            cog_files = glob.glob(os.path.join(f"tchangos/src/cogs/{folder}", "*.py"))

            for cog_f in cog_files:
                if cog_f.endswith(".py") and not cog_f.endswith("__init__.py"):
                    cog = os.path.splitext(os.path.basename(cog_f))[0]
                    cog_path = f"cogs.{folder}.{cog}"
                    try:
                        await self.load_extension(cog_path)
                        self.logger.info(f"Loaded {cog_path}")
                    except Exception as e:
                        self.logger.exception(f"<Failed to load {cog_path}>")


if __name__ == '__main__':
    bot = TchangosBot(command_prefix=get_prefix, intents=intents)

    bot.run(gen_data['tchangos']['token'])