"""Provide logging to the riemann client."""

import abc
import sys
import traceback
import typing as t
from io import StringIO

import discord

from . import utils

if t.TYPE_CHECKING:
    from .bot import Bot
else:
    Bot = t.Any


class Logger(abc.ABC):
    """Provide logging to the riemann client."""

    __slots__ = ()

    @abc.abstractmethod
    async def log(
        self,
        user: t.Union[discord.User, discord.Member],
        source: str,
        channel: t.Optional[
            t.Union[
                discord.DMChannel,
                discord.GroupChannel,
                discord.PartialMessageable,
                discord.Thread,
                discord.TextChannel,
                discord.VoiceChannel,
                discord.CategoryChannel,
                discord.StageChannel,
                discord.ForumChannel,
            ]
        ],
        error: Exception,
    ) -> None:
        """Log an exception.

        :param user: The user that caused the exception.
        :type user: Union[:class:`discord.User`, :class:`discord.Member`]
        :param source: The source of the exception (e.g. the command name)
        :type source: str
        :param channel: The channel that the exception occurred in.
        :type channel: Optional[Union[
            discord.abc.GuildChannel,
            discord.abc.PrivateChannel,
            discord.PartialMessageable,
            discord.Thread
            ]]
        """


class DiscordLogger(Logger):
    """Send log messages to Discord.

    Parameters
    ----------
    bot: :class:`Bot`
        The bot instance this logger is for
    log_channel: :class:`discord.TextChannel`
        The channel to send log messages to

    Attributes
    ----------
    bot: :class:`Bot`
        The bot instance.
    log_channel: :class:`discord.TextChannel`
        The channel to send log messages to.
    """

    __slots__ = ("bot", "log_channel")

    def __init__(
        self,
        bot: Bot,
        log_channel: discord.TextChannel,
    ) -> None:
        """Initialize the logger.

        :param bot: The bot instance.
        :type bot: :class:`Bot`
        :param log_channel: The channel to send log messages to.
        :type log_channel: :class:`discord.TextChannel`
        """
        self.bot = bot
        self.log_channel = log_channel

    @classmethod
    async def setup(cls, bot: Bot) -> "DiscordLogger":
        """Initialize the logger.

        :param bot: The bot instance.
        :type bot: :class:`Bot`
        :return: The logger instance.
        :rtype: :class:`DiscordLogger`
        """
        try:
            channel = await bot.fetch_channel(
                bot.config["logging"]["discord"]["channel-id"]
            )
            if not isinstance(channel, discord.TextChannel):
                raise ValueError()
        except (
            ValueError,
            discord.InvalidData,
        ):
            raise ValueError("Invalid logging channel.") from None
        except discord.NotFound:
            raise ValueError("Logging channel not found.") from None
        except discord.Forbidden:
            raise RuntimeError(
                "Missing permissions to retrieve logging channel."
            ) from None
        except discord.HTTPException:
            raise RuntimeError("Retrieving the logging channel failed.") from None

        if not channel.permissions_for(channel.guild.me).send_messages:
            raise RuntimeError("Bot cannot send messages in the logging channel.")
        return cls(bot, channel)

    async def log_file(
        self,
        user: t.Union[discord.User, discord.Member],
        title: str,
        description: str,
        formatted_traceback: str,
    ) -> None:
        """Send log messages that are too long in a file.

        :param user: The user that caused the exception.
        :type user: Union[:class:`discord.User`, :class:`discord.Member`]
        :param title: The title of the log message.
        :type title: str
        :param description: The description of the log message.
        :type description: str
        :param formatted_traceback: The traceback of the log message.
        :type formatted_traceback: str
        """
        pseudo_file = StringIO()

        pseudo_file.write(f"{title}\n")
        pseudo_file.write(f"Caused by {user} ({user.id})\n\n")
        pseudo_file.write(f"{description}\n\n")
        pseudo_file.write(formatted_traceback)
        pseudo_file.seek(0)

        await self.log_channel.send(
            file=discord.File(pseudo_file, filename="error.txt"),  # type: ignore
        )

    async def log(
        self,
        user: t.Union[discord.User, discord.Member],
        source: str,
        channel: t.Optional[
            t.Union[
                discord.DMChannel,
                discord.GroupChannel,
                discord.PartialMessageable,
                discord.Thread,
                discord.TextChannel,
                discord.VoiceChannel,
                discord.CategoryChannel,
                discord.StageChannel,
                discord.ForumChannel,
            ]
        ],
        error: Exception,
    ) -> None:
        """Log an exception.

        :param user: The user that caused the exception.
        :type user: Union[:class:`discord.User`, :class:`discord.Member`]
        :param source: The source of the exception (e.g. the command name)
        :type source: str
        :param channel: The channel that the exception occurred in.
        :type channel: Optional[Union[
            discord.abc.GuildChannel,
            discord.abc.PrivateChannel,
            discord.PartialMessageable,
            discord.Thread
            ]]
        """
        title = f"Error in {source}"

        description = f"{type(error).__name__} : {error}"

        location = utils.get_location(channel)

        description += f"\n{location}"

        formatted_traceback = "".join(traceback.format_tb(error.__traceback__))

        if len(description) + len(formatted_traceback) > 4089:
            # Discord's message limit is 4096 characters, and we add 7 characters
            await self.log_file(
                user,
                title,
                description,
                formatted_traceback,
            )
            return

        embed = discord.Embed(
            colour=0xFF0000,
            title=title,
            description=f"{description}```\n{formatted_traceback}```",
            timestamp=discord.utils.utcnow(),
        )

        embed.set_author(
            name=f"{user} ({user.id})",
            icon_url=str(user.display_avatar),
        )

        if self.bot.user is not None:
            embed.set_footer(
                text=f"{self.bot.user.name} Logging",
                icon_url=str(self.bot.user.display_avatar),
            )

        await self.log_channel.send(embed=embed)


class StdErrLogger(Logger):
    """Write log messages to stderr."""

    async def log(
        self,
        user: t.Union[discord.User, discord.Member],
        source: str,
        channel: t.Optional[
            t.Union[
                discord.DMChannel,
                discord.GroupChannel,
                discord.PartialMessageable,
                discord.Thread,
                discord.TextChannel,
                discord.VoiceChannel,
                discord.CategoryChannel,
                discord.StageChannel,
                discord.ForumChannel,
            ]
        ],
        error: Exception,
    ) -> None:
        """Log an exception.

        :param user: The user that caused the exception.
        :type user: Union[:class:`discord.User`, :class:`discord.Member`]
        :param source: The source of the exception (e.g. the command name)
        :type source: str
        :param channel: The channel that the exception occurred in.
        :type channel: Optional[Union[
            discord.abc.GuildChannel,
            discord.abc.PrivateChannel,
            discord.PartialMessageable,
            discord.Thread
            ]]
        """
        formatted_traceback = "".join(traceback.format_tb(error.__traceback__))

        error_msg = (
            f"{discord.utils.utcnow()} UTC\n"
            f"Error in {source}\n"
            f"Caused by {user} ({user.id})\n\n"
            f"{type(error).__name__} : {error}\n"
            f"{utils.get_location(channel)}\n\n"
            f"{formatted_traceback}\n\n"
        )
        print(error_msg, file=sys.stderr)


async def load(bot: Bot) -> Logger:
    """Load the logger.

    :param bot: The bot instance.
    :type bot: :class:`Bot`
    :return: The logger instance.
    :rtype: :class:`Logger`
    """
    config = bot.config["logging"]
    if config["type"] == "discord":
        return await DiscordLogger.setup(bot)

    raise ValueError(f"Unknown logger: {config['type']}")
