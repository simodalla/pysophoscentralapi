"""Utilities for synchronous wrappers.

This module provides utility functions for wrapping async code in synchronous interfaces.
"""

import asyncio
from collections.abc import Coroutine
from typing import TypeVar


T = TypeVar("T")


def run_async(coro: Coroutine[None, None, T]) -> T:
    """Run an async coroutine synchronously.

    This function uses asyncio.run() to execute an async coroutine in a
    blocking manner. It handles the event loop creation and cleanup.

    Args:
        coro: The coroutine to execute

    Returns:
        The result of the coroutine

    Example:
        >>> async def fetch_data():
        ...     return {"data": "value"}
        >>> result = run_async(fetch_data())
        >>> print(result)
        {'data': 'value'}
    """
    return asyncio.run(coro)


def sync_wrapper(async_method):
    """Decorator to create a synchronous wrapper for an async method.

    This decorator wraps an async method to make it callable synchronously.
    It uses asyncio.run() internally.

    Args:
        async_method: The async method to wrap

    Returns:
        A synchronous wrapper function

    Example:
        >>> class AsyncClass:
        ...     async def fetch(self):
        ...         return "data"
        >>>
        >>> class SyncClass:
        ...     def __init__(self, async_instance):
        ...         self._async = async_instance
        ...
        ...     @sync_wrapper
        ...     async def fetch(self):
        ...         return await self._async.fetch()
    """

    def wrapper(*args, **kwargs):
        return run_async(async_method(*args, **kwargs))

    return wrapper
