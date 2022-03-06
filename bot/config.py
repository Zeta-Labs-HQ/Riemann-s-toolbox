import typing as t

from decouple import config


class Config:
    # Debug mode
    DEBUG: bool = t.cast(bool, config("DEBUG", default=False, cast=bool))

    # Bot token
    TOKEN: str = t.cast(str, config("TOKEN"))

    # Command prefix
    PREFIX: str = t.cast(str, config("PREFIX", default="!"))

    # List of admin developers.
    ADMINS: t.List[int] = t.cast(
        t.List[int],
        config("ADMINS", default=[], cast=lambda x: [int(i) for i in x.split(",")]),
    )


class LogConfig:
    # Location and max size
    LOG_FILE = "logs/bot.log"
    LOG_FILE_SIZE = "400 MB"

    # Level
    LOG_LEVEL = "TRACE" if Config.DEBUG else "INFO"

    # Format
    LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD hh:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name: <18}</cyan> | <level>{message}</level>"
    )
