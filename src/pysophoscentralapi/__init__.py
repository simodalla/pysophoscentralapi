"""PySophosCentralApi - Python library and CLI for Sophos Central APIs.

This library provides comprehensive access to Sophos Central Endpoint API and
Common API, with both a programmatic interface and a command-line tool.

Example:
    Basic usage::

        from pysophoscentralapi import SophosClient
        from pysophoscentralapi.core.config import Config

        config = Config.from_file("config.toml")
        async with SophosClient(config) as client:
            endpoints = await client.endpoint.list_endpoints()
"""

from pysophoscentralapi.__version__ import __version__


__all__ = ["__version__"]
