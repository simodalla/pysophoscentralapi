"""Synchronous wrappers for PySophosCentralApi.

This module provides synchronous interfaces that wrap the async implementations.
The sync wrappers use asyncio.run() to execute async methods in a blocking manner,
making the library accessible to synchronous codebases.

Example:
    >>> from pysophoscentralapi.sync import SophosClientSync
    >>> from pysophoscentralapi.core.config import Config
    >>>
    >>> # Synchronous usage
    >>> config = Config(client_id="...", client_secret="...")
    >>> with SophosClientSync(config) as client:
    ...     endpoints = client.endpoint.list_endpoints()
    ...     for endpoint in endpoints.items:
    ...         print(endpoint.hostname)
"""

from pysophoscentralapi.sync.client import HTTPClientSync
from pysophoscentralapi.sync.common import (
    AdminsAPISync,
    AlertsAPISync,
    CommonAPISync,
    RolesAPISync,
    TenantsAPISync,
)
from pysophoscentralapi.sync.endpoint import EndpointAPISync
from pysophoscentralapi.sync.pagination import PaginatorSync


__all__ = [
    "AdminsAPISync",
    "AlertsAPISync",
    "CommonAPISync",
    "EndpointAPISync",
    "HTTPClientSync",
    "PaginatorSync",
    "RolesAPISync",
    "TenantsAPISync",
]
