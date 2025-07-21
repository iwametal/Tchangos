import discord
import logging

# from constants import channels, pokemon_data, rand_stats
from constants import LOGGING_PATH
from discord.ext import commands
from helper import Helper, FTLExtractor


### ENV VARIABLES ###
gen_data = Helper.get_general_config('config.ini')


def get_prefix(bot, message):
    prefixes = ['b.']
    # You can add more complex logic here to determine the prefix
    return commands.when_mentioned_or(*prefixes)(bot, message)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.reactions = True


class TchangosBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        self.ftl = FTLExtractor(locale='pt', fallback_locale='pt')

        # GENAI KEY
        self.genai_key = gen_data['GENAI']['KEY']

        # TWITCH KEYS
        self.twitch_client = gen_data['TWITCH']['CLIENT_ID']
        self.twitch_secret = gen_data['TWITCH']['CLIENT_SECRET']
        self.twitch_token = None
        self.expires_at = 0

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


    # ON BOT START
    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user}\n------')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Tchangos"))
        self.logger.info("Tchangos bot is up")
    

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"🚫 | {self.ftl.extract('missing-permissions', error=str(error))}")
            self.logger.warning(f"🚫 | {self.ftl.extract('missing-permissions', error=str(error))}")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"❌ | {self.ftl.extract('check-failure', error=str(error))}")
            self.logger.warning(f"❌ | {self.ftl.extract('check-failure', error=str(error))}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ | {self.ftl.extract('missing-required-argument')}. {error}")
            self.logger.warning(f"⚠️ | {self.ftl.extract('missing-required-argument')} -> {error}")
        else:
            # await ctx.send(f"️️❌ | {self.ftl.extract('unexpected-error', error=str(error))}")
            logging.exception(f"❌ | <Unexpected error>")


    # # SYNC SLASH COMMANDS WITH ?sync
    # from typing import Literal, Optional
    # @bot.command()
    # @commands.guild_only()
    # @commands.is_owner()
    # async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    #     if not guilds:
    #         if spec == "~":
    #             synced = await ctx.bot.tree.sync(guild=ctx.guild)
    #         elif spec == "*":
    #             ctx.bot.tree.copy_global_to(guild=ctx.guild)
    #             synced = await ctx.bot.tree.sync(guild=ctx.guild)
    #         elif spec == "^":
    #             ctx.bot.tree.clear_commands(guild=ctx.guild)
    #             await ctx.bot.tree.sync(guild=ctx.guild)
    #             synced = []
    #         else:
    #             synced = await ctx.bot.tree.sync()

    #         await ctx.send(
    #             f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
    #         )
    #         return

    #     ret = 0
    #     for guild in guilds:
    #         try:
    #             await ctx.bot.tree.sync(guild=guild)
    #         except discord.HTTPException:
    #             pass
    #         else:
    #             ret += 1

    #     await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    async def setup_hook(self):
        import glob
        import os

        await bot.load_extension('jishaku')

        cog_folders = ['ai', 'generic', 'live']

        for folder in cog_folders:
            cog_files = glob.glob(os.path.join(f"tchangos/src/cogs/{folder}", "*.py"))
            # cog_files = glob.glob(os.path.join("cogs", "*.py"))

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

    bot.run(gen_data['TCHANGOS']['TOKEN'])