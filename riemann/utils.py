"""Various utility functions."""

import typing as t
from os import path

import discord
import toml


def get_role_name(
    guild: discord.Guild,
    identifier: t.Union[int, str],
    default: t.Optional[str] = None,
) -> t.Optional[str]:
    """Get the name of a role based on a has_role check.

    :param guild: Guild to check
    :type guild: :class:`discord.Guild`
    :param identifier: Role ID or name
    :type identifier: Union[:class:`int`, :class:`str`]
    :param default: Default value if the role is not found
    :type default: Optional[:class:`str`]
    :return: Name of the role associated with the ID or name
        If a string is passed, it is directly returned, regardless
        of if the role exists or not. If the role is not found,
        the default value is returned.
    :rtype: Optional[:class:`str`]
    """
    if isinstance(identifier, int):
        role = guild.get_role(identifier)
        if role is None:
            return default
        return role.name
    return identifier


def get_role_names(
    guild: discord.Guild,
    identifiers: t.List[t.Union[int, str]],
) -> t.List[str]:
    """Same as get_role_name, but for multiple roles.

    :param guild: Guild to check
    :type guild: :class:`discord.Guild`
    :param identifiers: Role IDs or names
    :type identifiers: List[Union[:class:`int`, :class:`str`]]
    :return: List of names of the roles associated with the IDs or names
    :rtype: List[:class:`str`]
    """
    raw_res = [get_role_name(guild, identifier) for identifier in identifiers]
    return [r for r in raw_res if r is not None]


def load_config(
    configpath: t.Optional[str],
) -> t.Dict[str, t.Any]:
    """Load the config file with defaults.

    :param configpath: Path to the config file
    :type configpath: :class:`str`
    :return: The configuration dictionnary
    :rtype: Dict[:class:`str`, Any]
    """
    if configpath is None:
        configpath = "conf.toml"

    if not path.exists(configpath):
        raise ValueError("Missing TOML configuration file.")

    with open(configpath, "r", encoding="utf-8") as file:
        config: t.Dict[str, t.Any] = toml.load(file)

    with open(
        path.join(path.dirname(__file__), "data/defaults.toml"),
        "r",
        encoding="utf-8",
    ) as file:
        defaults: t.Dict[str, t.Any] = toml.load(file)

    def add_defaults(
        key: str,
        content: t.Union[t.Any, t.Dict[str, t.Any]],
        curconf: t.Dict[str, t.Any],
    ) -> None:
        """Insert default values where necessary in the configuration.

        :param key: Configuration key to be inserted
        :type key: :class:`str`
        :param content: Default key value
        :type content: Union[Any, Dict[:class:`str`, Any]]
        :param curconf: Currently parsed configuration
        :type curconf: Dict[:class:`str`, Any]
        """
        if key not in curconf:
            curconf[key] = content
        elif isinstance(content, dict):
            for subkey, subcontent in content.items():
                add_defaults(subkey, subcontent, curconf[key])

    for key, content in defaults.items():
        add_defaults(key, content, config)

    return config


async def response_or_followup(
    interaction: discord.Interaction,
    **kwargs: t.Any,
) -> None:
    """Send a response or followup message.

    :param interaction: Interaction to send the message from
    :type interaction: :class:`discord.Interaction`
    :param kwargs: Keyword arguments to pass to the send method
    :type kwargs: Any
    """
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)


def partial_messageable_location(
    guild: t.Optional[discord.Guild],
    guild_id: t.Optional[int],
    channel_type: t.Optional[discord.ChannelType],
    channel_id: int,
) -> str:
    """Get the location associated with a partial messageable.

    :param guild: Guild to check
    :type guild: Optional[:class:`discord.Guild`]
    :param guild_id: Guild ID to check
    :type guild_id: Optional[:class:`int`]
    :param channel_type: Channel type to check
    :type channel_type: Optional[:class:`discord.ChannelType`]
    :param channel_id: Channel ID to check
    :type channel_id: :class:`int`
    :return: Location associated with the partial messageable
    :rtype: :class:`str`
    """
    loc: t.List[str] = []
    if guild is not None:
        loc.append(f"in the Guild {guild.name} ({guild.id})")
    elif guild_id is not None:
        loc.append(f"in the Guild with ID {guild_id}")

    if channel_type is not None:
        loc.append(f"In a {channel_type.name.capitalize()} Channel")
    else:
        loc.append("In a channel")

    loc[-1] += f" ({channel_id})"
    return "\n".join(loc)


def get_location(
    channel: t.Optional[
        t.Union[
            discord.PartialMessageable,
            discord.Thread,
            discord.ForumChannel,
            discord.DMChannel,
            discord.GroupChannel,
            discord.TextChannel,
            discord.VoiceChannel,
            discord.CategoryChannel,
            discord.StageChannel,
        ]
    ],
) -> str:
    """Get the location associated with a channel.

    :param channel: Channel to check
    :type channel: Optional[Union[
            discord.abc.GuildChannel,
            discord.abc.PrivateChannel,
            discord.PartialMessageable,
            discord.Thread
            ]]
    :return: Location associated with the channel
    :rtype: :class:`str`
    """
    if isinstance(channel, discord.PartialMessageable):
        return partial_messageable_location(
            channel.guild,
            channel.guild_id,
            channel.type,
            channel.id,
        )

    if isinstance(channel, discord.Thread):
        if channel.parent is not None:
            base = location(channel.parent)
        else:
            base = (
                f"in the Guild {channel.guild.name} ({channel.guild.id})"
                f"\nin a Channel with id {channel.parent_id}"
            )
        return base + f"\nin the Thread {channel.name} ({channel.id})"

    if isinstance(channel, discord.ForumChannel):
        return (
            f"in the Guild {channel.guild.name} ({channel.guild.id})"
            f"\nin the Forum Channel {channel.name} ({channel.id})"
        )

    if isinstance(channel, discord.DMChannel):
        if channel.recipient is None:
            return f"in a Private Channel ({channel.id})"
        return f"in a Private Channel with {channel.recipient.name} ({channel.id})"

    if isinstance(channel, discord.GroupChannel):
        if channel.name is None:
            return f"in a Group Channel ({channel.id})"
        return f"in a Group Channel named {channel.name} ({channel.id})"

    if isinstance(channel, discord.TextChannel):
        return (
            f"in the Guild {channel.guild.name} ({channel.guild.id})"
            f"\nin the Text Channel {channel.name} ({channel.id})"
        )

    if isinstance(channel, discord.VoiceChannel):
        return (
            f"in the Guild {channel.guild.name} ({channel.guild.id})"
            f"\nin the Voice Channel {channel.name} ({channel.id})"
        )

    if isinstance(channel, discord.CategoryChannel):
        return (
            f"in the Guild {channel.guild.name} ({channel.guild.id})"
            f"\nin the Category Channel {channel.name} ({channel.id})"
        )

    if isinstance(channel, discord.StageChannel):
        return (
            f"in the Guild {channel.guild.name} ({channel.guild.id})"
            f"\nin the Stage Channel {channel.name} ({channel.id})"
        )

    return "in an unknown place"
