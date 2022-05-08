"""Various utility functions."""

import typing as t
from os import path

import toml


def load_config(
    configpath: str,
) -> t.Dict[str, t.Any]:
    """Load the config file with defaults."""
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
