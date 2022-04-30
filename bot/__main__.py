from discord import Game, Intents

from .config import VERSION, Config
from .core.bot import Bot

# Intents
intents = Intents.default()

# Bot
bot = Bot(
    version=VERSION,
    command_prefix=Config.PREFIX,
    intents=intents,
    activity=Game(name=f"Call me with {Config.PREFIX}help"),
    case_insensitive=True,
    owner_ids=Config.ADMINS,
)

# Run the bot
bot.run(Config.TOKEN)
