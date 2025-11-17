"""Synchronous pagination wrapper.

This module provides synchronous wrappers for pagination utilities.
"""

from collections.abc import Iterator
from typing import Generic, TypeVar

from pysophoscentralapi.core.pagination import Paginator
from pysophoscentralapi.sync.utils import run_async


T = TypeVar("T")


class PaginatorSync(Generic[T]):
    """Synchronous paginator wrapper.

    This is a synchronous wrapper around the async Paginator. It provides
    blocking iteration over paginated results.

    Attributes:
        _async_paginator: The underlying async Paginator instance

    Example:
        >>> # Assuming endpoint_api is a sync API client
        >>> paginator = endpoint_api.paginate_endpoints()
        >>> for endpoint in paginator.iter_items():
        ...     print(endpoint.hostname)
    """

    def __init__(self, async_paginator: Paginator[T]) -> None:
        """Initialize the synchronous paginator.

        Args:
            async_paginator: The async paginator to wrap
        """
        self._async_paginator = async_paginator

    @property
    def page_size(self) -> int:
        """Get the page size."""
        return self._async_paginator.page_size

    @property
    def max_pages(self) -> int | None:
        """Get the maximum number of pages."""
        return self._async_paginator.max_pages

    @property
    def pages_fetched(self) -> int:
        """Get the number of pages fetched so far."""
        return self._async_paginator.pages_fetched

    @property
    def items_fetched(self) -> int:
        """Get the number of items fetched so far."""
        return self._async_paginator.items_fetched

    def iter_pages(self) -> Iterator:
        """Iterate through pages synchronously.

        Yields:
            PaginatedResponse objects

        Example:
            >>> paginator = api.paginate_endpoints()
            >>> for page in paginator.iter_pages():
            ...     print(f"Page with {len(page.items)} items")
        """

        async def async_iter():
            results = []
            async for page in self._async_paginator.iter_pages():
                results.append(page)
            return results

        pages = run_async(async_iter())
        yield from pages

    def iter_items(self) -> Iterator[T]:
        """Iterate through individual items synchronously.

        Yields:
            Individual items from all pages

        Example:
            >>> paginator = api.paginate_endpoints()
            >>> for endpoint in paginator.iter_items():
            ...     print(endpoint.hostname)
        """

        async def async_iter():
            results = []
            async for item in self._async_paginator.iter_items():
                results.append(item)
            return results

        items = run_async(async_iter())
        yield from items
