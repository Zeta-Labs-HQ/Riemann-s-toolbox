import sys

from loguru import logger

from .config import LogConfig

# Configure logging
logger.configure(
    handlers=[
        dict(sink=sys.stdout, format=LogConfig.LOG_FORMAT, level=LogConfig.LOG_LEVEL),
        dict(
            sink=LogConfig.LOG_FILE,
            format=LogConfig.LOG_FORMAT,
            level=LogConfig.LOG_LEVEL,
            rotation=LogConfig.LOG_FILE_SIZE,
        ),
    ]
)
