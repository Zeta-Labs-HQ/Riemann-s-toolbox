:orphan:

Configuring Riemann
====================

Riemann is a library to help you create a Discord server.
As such, it needs to be configured. For that, the library will
parse a TOML configuration file, making it available to you as
the *conf* attribute of the :ref:`Bot instance <bot-instance>`.

The complete set of defaults for the current version of Riemann is:

.. literalinclude:: ../../riemann/data/defaults.toml
    :language: toml
