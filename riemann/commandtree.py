"""Custom command tree with error handling."""

import typing as t

import discord
from discord import app_commands

from . import utils

if t.TYPE_CHECKING:
    from .bot import Bot
else:
    Bot = t.Any


# pylint: disable=too-few-public-methods
class CommandTree(app_commands.CommandTree):
    """Custom command tree with error handling.

    Parameters
    ----------
    bot: :class:`Bot`
        Bot instance this CommandTree is built for

    Attributes
    ----------
    bot: :class:`Bot`
        Bot instance associated with this command tree
    """

    def __init__(self, bot: Bot) -> None:
        """Initialize the command tree."""
        self.bot = bot
        super().__init__(bot)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Handle slash command errors.

        :param interaction: Interaction that caused the error
        :type interaction: :class:`discord.Interaction`
        :param error: Error that occurred
        :type error: :class:`discord.app_commands.AppCommandError`
        """
        error_description: t.Optional[str] = None

        if isinstance(error, app_commands.TransformerError):
            error_code = 415
            error_title = "Failed to convert argument"  # TODO : be more descriptive

        elif isinstance(error, app_commands.NoPrivateMessage):
            error_code = 403
            error_title = "This command cannot be used in private messages."

        elif isinstance(error, app_commands.MissingRole):
            error_code = 403
            error_title = "You do not have the required role to use this command"
            if interaction.guild is not None:
                error_title += ": " + utils.get_role_name(
                    interaction.guild, error.missing_role, "Unknown role"
                )

        elif isinstance(error, app_commands.MissingAnyRole):
            error_code = 403
            error_title = (
                "You do not have any of the required roles to use this command"
            )
            if interaction.guild is not None:
                role_names = utils.get_role_names(
                    interaction.guild, error.missing_roles
                )
                if role_names:
                    error_title += ":\n - " + "\n - ".join(role_names)

        elif isinstance(error, app_commands.MissingPermissions):
            error_code = 403
            error_title = (
                "You do not have the required permissions to use this command :\n - "
                + "\n - ".join(
                    error.missing_permissions,
                )
            )

        elif isinstance(error, app_commands.BotMissingPermissions):
            error_code = 403
            error_title = (
                "I do not have the required permissions for you to use this command :\n - "
                + "\n - ".join(
                    error.missing_permissions,
                )
            )

        elif isinstance(error, app_commands.CommandOnCooldown):
            error_code = 429
            error_title = f"Command on cooldown ! Retry in {error.retry_after} seconds"

        elif isinstance(error, app_commands.CommandLimitReached):
            error_code = 429
            error_title = "The execution limit for this command has been reached"
            if error.guild_id is not None:
                error_title += " in your guild"
            error_title += f" ({error.limit})"

        elif isinstance(error, app_commands.CommandNotFound):
            error_code = 404
            error_title = f"Slash command {error.name} not found"
        elif isinstance(error, app_commands.CommandInvokeError):
            error_code = 500
            error_title = "An error occured while executing the command"

            if isinstance(error.command, app_commands.Command):
                source = f"Slash Command {error.command.qualified_name}"
            else:
                source = f"Context Menu {error.command.qualified_name}"

            await self.bot.logger.log(
                interaction.user,
                source,
                interaction.channel,
                error.original,
            )
        else:
            # Unknown AppCommandError !
            # THIS SHOULD NOT HAPPEN
            error_code = 521
            error_title = "A fatal error occured"

            if interaction.command is None:
                source = "Unknown interaction"
            elif isinstance(interaction.command, app_commands.Command):
                source = f"Slash Command {error.command.qualified_name}"
            else:
                source = f"Context Menu {error.command.qualified_name}"

            await self.bot.logger.log(
                interaction.user,
                source,
                interaction.channel,
                error,
            )

        await self.bot.interaction_error(
            interaction, error_code, error_title, error_description
        )
