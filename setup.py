"""Setup options for installing the package."""

import re
from itertools import chain

from setuptools import setup

# Readme file as long description
with open("README.md", encoding="utf-8") as file:
    README = file.read()

# Version locating and assignment
with open("riemann/__init__.py", encoding="utf-8") as file:
    match = re.search(
        r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
        file.read(),
        re.MULTILINE,
    )
    VERSION = match.group(1) if match else ""

if not VERSION:
    raise RuntimeError("Version is not set")

# Dependencies configuration
extras_require = {
    "docs": ["sphinx>=4.4.0,<5", "sphinxcontrib_trio>=1.1.2,<2"],
    "voice": ["discord.py[voice]>=2.0"],
    # Database
    "sqlite": ["aiosqlite>=0.17.0"],
    "postgresql": ["psycopg[binary, pool]>=3"],
    # Caching using redis
    "caching": ["aioredis>=2.0.1"],
}
extras_require["all"] = list(chain.from_iterable(extras_require.values()))


setup(
    version=VERSION,
    long_description=README,
    long_description_content_type="text/markdown",
    # Installation data
    extras_require=extras_require,
)
