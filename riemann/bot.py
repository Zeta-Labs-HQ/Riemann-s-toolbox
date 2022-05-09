"""Custom bot subclass."""

import typing as t
from os import path

import discord

from . import database, logging, utils


class Bot(discord.Client):
    """Custom bot subclass."""

    def __init__(self, config_path: str) -> None:
        """Initialize the bot."""
        self.config = utils.load_config(config_path)
        self.database: database.Database = None  # type: ignore
        self.logger: logging.Logger = None  # type: ignore

        if "token" not in self.config:
            raise ValueError("Missing token in configuration.")
        super().__init__()

    async def setup_hook(self) -> None:
        """Setup the bot."""
        self.database = await database.load(self)
        self.logger = await logging.load(self)

    async def interaction_error(
        self,
        interaction: discord.Interaction,
        code: int,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
    ) -> None:
        """Send an error message to the user."""
        if (
            title is None
            and description is None
            and not self.config["error"]["http-cat"]
        ):
            return  # TODO : log error

        embed = discord.Embed(
            title=title,
            description=description,
        )

        if self.config["error"]["http-cat"]:
            file = discord.File(
                path.join(path.dirname(__file__), f"data/cats/{code}.jpg"), "cat.jpg"
            )
            embed.set_image(url="attachment://cat.png")
            await utils.response_or_followup(interaction, file=file, embed=embed)
        else:
            await utils.response_or_followup(interaction, embed=embed)
