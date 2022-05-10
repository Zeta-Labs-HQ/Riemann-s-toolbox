"""Custom bot subclass."""

import typing as t
from os import path

import discord

from . import utils
from .database import Database
from .database import load as load_database
from .logging import Logger
from .logging import load as load_logger


class Bot(discord.Client):
    """Custom bot class for riemann.

    Parameters
    ----------
    config_path : Optional[:class:`str`]
        Path to the configuration file.

        If you do not give a path, the bot will try finding a
        ``conf.toml`` file in the working directory

    Attributes
    ----------
    config: Dict[:class:`str`, Any]
        Dictionnary representing the configuration of the bot
    database: :class:`database.Database`
        Database instance of the bot.
    logger: :class:`logging.Logger`
        Logger instance of the bot.
    """

    def __init__(self, config_path: t.Optional[str] = None) -> None:
        """Initialize the bot."""
        self._config_path = config_path
        self.config = utils.load_config(config_path)
        self.database: Database = None  # type: ignore
        self.logger: Logger = None  # type: ignore

        if "token" not in self.config["bot"] or self.config["bot"]["token"] == "":
            raise ValueError("Missing token in configuration.")
        super().__init__()

    async def setup_hook(self) -> None:
        """Load the necessay dependencies."""
        self.database = await load_database(self)
        self.logger = await load_logger(self)

    async def interaction_error(
        self,
        interaction: discord.Interaction,
        code: int,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
    ) -> None:
        """Send an error message to the user.

        :param interaction: Interaction that caused the error
        :type interaction: :class:`discord.Interaction`
        :param code: HTTP error code associated with the error
        :type code: int
        :param title: Title of the error embed
        :type title: Optional[:class:`str`]
        :param description: Description of the error embed
        :type description: Optional[:class:`str`]
        """
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
