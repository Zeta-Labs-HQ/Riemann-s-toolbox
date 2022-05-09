"""Custom command tree with error handling."""


import discord
from discord import app_commands


class CommandTree(app_commands.CommandTree):
    """Custom command tree with error handling."""

    def __init__(self, client: discord.Client):
        """Initialize the command tree."""
        self.client = client
        super().__init__(client)

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Handle slash command errors."""
        if isinstance(error, app_commands.CommandInvokeError):
            pass  # Command raised an exception
            # original : original exception (Exception)
            # command : command that raised the exception (Command / ContextMenu)

        elif isinstance(error, app_commands.TransformerError):
            pass  # Failed to convert

        elif isinstance(error, app_commands.NoPrivateMessage):
            pass  # Unavailable in private messages

        elif isinstance(error, app_commands.MissingRole):
            pass  # Missing role
            # mssing_role : role that is missing (str / int), see has_role

        elif isinstance(error, app_commands.MissingAnyRole):
            pass  # Does not have any of the specified roles
            # missing_roles : roles that are missing (List[str / int]), see has_any_role

        elif isinstance(error, app_commands.MissingPermisions):
            pass  # User does not have the perms
            # missing_permissions : lacking permissions (List[str])

        elif isinstance(error, app_commands.BotMissingPermissions):
            pass  # Bot does not have the perms
            # missing_permissions : lacking permissions (List[str])

        elif isinstance(error, app_commands.CommandOnCooldown):
            pass  # Command on cooldown
            # cooldown : cooldown triggered (Cooldown)
            # retry_after : retry after (float)

        elif isinstance(error, app_commands.CommandLimitReached):
            pass  # Command use limit reached
            # type : type of command that reached the limit (AppCommandType)
            # guild_id : guild that reached the limit (None if global)
            # limit : limit that was reached (int)

        elif isinstance(error, app_commands.CommandNotFound):
            pass  # Command not found
            # name : Name of the command not found
            # parents : parent commmands that were found (List[str])
            # type : type of command that was not found (AppCommandType)
        else:
            pass  # Unkown error type
