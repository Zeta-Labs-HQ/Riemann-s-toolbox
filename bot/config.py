from decouple import config


class Config:
    # Debug mode
    DEBUG = config('DEBUG', default=False, cast=bool)

    # Bot token
    TOKEN = str, config('TOKEN')

    # Command prefix
    PREFIX = config('PREFIX', default='!')

    # List of admin developers.
    ADMINS = config('ADMINS', default='', cast=lambda x: x.split(','))


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
