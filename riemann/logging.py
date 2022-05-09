"""Provide logging to the riemann client."""

import abc
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
        """Log an exception."""


class DiscordLogger(Logger):
    """Send log messages to Discord."""

    def __init__(
        self,
        bot: Bot,
        log_channel: discord.TextChannel,
    ) -> None:
        """Initialize the logger."""
        self.bot = bot
        self.log_channel = log_channel

    @classmethod
    async def setup(cls, bot: Bot) -> "DiscordLogger":
        """Initialize the logger."""
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
        """Send log messages that are too long in a file."""
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
        """Log an error."""
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

        await self.log_channel.send(embed=embed)


async def load(bot: Bot) -> Logger:
    """Load the logger."""
    config = bot.config["logging"]
    if config["type"] == "discord":
        return await DiscordLogger.setup(bot)

    raise ValueError(f"Unknown logger: {config['type']}")
