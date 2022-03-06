from datetime import datetime
from typing import Optional

import aiohttp
from discord import User
from discord.ext.commands import AutoShardedBot
from loguru import logger

from ..config import Config
from .autoload import COGS


class Bot(AutoShardedBot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Startup time
        self.startup_time = datetime.utcnow()

        # Fresh startup
        self.initial_call = True

        # Aiohttp session
        self.session: Optional[aiohttp.ClientSession] = None

    # Is owner function
    async def is_owner(self, user: User) -> bool:
        if user.id in Config.ADMINS:
            return True

        return await super().is_owner(user)

    async def load_extensions(self) -> None:
        for extension in COGS:
            try:
                self.load_extension(extension)
                logger.info(f"Extension loaded: {extension}.")
            except Exception as exc:
                logger.error(f"Cog {extension} failed to load with {type(exc)}: {exc!r}")
                raise exc

    async def on_ready(self) -> None:
        if self.initial_call:
            self.initial_call = False
            await self.load_extensions()

            logger.info("Bot is ready.")
        else:
            logger.info("Bot connection reinitialized.")

    def run(self, token: Optional[str]) -> None:
        if not token:
            logger.critical("Missing Bot Token!")
        else:
            super().run(token)

    async def start(self, *args, **kwargs) -> None:
        self.session = aiohttp.ClientSession()

        await super().start(*args, **kwargs)
        logger.info("Successfully connected to discord.")

    async def close(self) -> None:
        logger.info("Closing bot connection")

        if self.session:
            await self.session.close()

        await super().close()
        logger.info("Bot successfully closed.")
