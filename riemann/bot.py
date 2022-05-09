"""Custom bot subclass."""

import typing as t
from os import path

import discord

from . import database, logging, utils


class Bot(discord.Client):
    """Custom bot class for riemann.

    Attributes
    ----------
    config: Dict[:class:`str`, Any]
        Dictionnary representing the configuration of the bot
    database: :class:`database.Database`
        Database instance of the bot.
    logger: :class:`logging.Logger`
        Logger instance of the bot.
    """

    def __init__(self, config_path: str) -> None:
        """Initialize the bot.

        :param config_path: Path to the configuration file
        :type config_path: :class:`str`
        """
        self._config_path = config_path
        self.config = utils.load_config(config_path)
        self.database: database.Database = None  # type: ignore
        self.logger: logging.Logger = None  # type: ignore

        if "token" not in self.config:
            raise ValueError("Missing token in configuration.")
        super().__init__()

    async def setup_hook(self) -> None:
        """Load the necessay dependencies."""
        self.database = await database.load(self)
        self.logger = await logging.load(self)

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
