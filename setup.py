"""Setup options for installing the package."""

import re
from itertools import chain
from pathlib import Path

from setuptools import find_packages, setup

# Constant variables
BASE_DIR = Path(__file__).resolve().parent

README = Path(BASE_DIR / "README.md").read_text()

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
    # Database
    "sqlite": ["aiosqlite==0.17.0"],
    "postgres": ["psycopg==3.0.12", "psycopg_pool==3.1.1"],
}
extras_require["all"] = list(
    chain.from_iterable(extras_require.values())
)  # type: ignore


setup(
    version=VERSION,
    long_description=README,
    long_description_content_type="text/markdown",
    # Package data
    packages=find_packages(exclude=["tests", "tests.*", "tools", "tools.*"]),
    package_data={"riemann": ["py.typed"]},
    # Installation data
    install_requires=[
        "requests==2.25.1",
        "aiohttp==3.7.4.post0",
    ],
    extras_require=extras_require,
)
