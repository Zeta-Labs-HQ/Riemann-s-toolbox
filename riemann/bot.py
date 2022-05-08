"""Custom bot subclass."""

import discord

from . import database, utils


class Bot(discord.Client):
    """Custom bot subclass."""

    def __init__(self, config_path: str) -> None:
        """Initialize the bot."""
        self.config = utils.load_config(config_path)
        self.database: database.Database = None  # type: ignore

        if "token" not in self.config:
            raise ValueError("Missing token in configuration.")
        super().__init__()

    async def setup_hook(self) -> None:
        """Setup the bot."""
        self.database = await database.load(self.config["database"])
