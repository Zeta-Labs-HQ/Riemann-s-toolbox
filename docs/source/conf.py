# type: ignore
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import pathlib
import re
import sys

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("extensions"))
sys.path.insert(0, pathlib.Path(__file__).parents[3].resolve().as_posix())


# -- Project information -----------------------------------------------------

project = "riemann"
copyright = "2022, Zeta labs"
author = "Zeta labs"

# The full version, including alpha/beta/rc tags

version = ""
with open("../../riemann/__init__.py", encoding="utf-8") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

release = version

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

extlinks = {
    "issue": ("https://github.com/Zeta-Labs-HQ/Riemann-s-toolbox/issues/%s", "issue %s"),
}


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "builder",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinxcontrib_trio",
    "details",
    "exception_hierarchy",
    "attributetable",
    "resourcelinks",
    "nitpick_file_ignorer",
]

# Links used for cross-referencing stuff
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "asqlite": ("https://aiosqlite.omnilib.dev/en/stable/", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "pg": ("https://www.psycopg.org/psycopg3/docs", None),
    "dpy": ("https://discordpy.readthedocs.io/en/latest/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]

master_doc = "index"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "basic"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_experimental_html5_writer = True

html_context = {
    "discord_invite": "https://discord.gg/eFfjdyZ"
}

resource_links = {
    "discord": "https://discord.gg/eFfjdyZ",
    "issues": "https://github.com/Zeta-Labs-HQ/Riemann-s-toolbox/issues",
}

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

html_favicon = "./images/favicon.ico"
html_logo = "./images/logo.png"

html_js_files = ["custom.js", "settings.js", "copy.js", "sidebar.js"]

html_copy_source = False

# Autodoc options
autodoc_member_order = "bysource"
autodoc_typehints = "none"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}

autodoc_mock_imports = ["discord"]
# TODO: Remove when discord.py 2.0 is released & fix .readthedocs.yml

nitpick_ignore_files = []
