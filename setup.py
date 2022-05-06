"""Setup options for installing the package."""

import re
from setuptools import setup


with open("requirements.txt", encoding="utf-8") as file:
    requirements = file.read().splitlines()


with open("riemann/__init__.py", encoding="utf-8") as file:
    match = re.search(
        r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
        file.read(),
        re.MULTILINE,
    )
    version = match.group(1) if match else ""

if not version:
    raise RuntimeError("Version is not set")


with open("README.md", encoding="utf-8") as file:
    readme = file.read()


setup(
    version=version,
    long_description=readme,
    long_description_content_type="text/markdown",
)
