"""Pagination utilities for Sophos Central APIs.

This module provides utilities for handling cursor-based pagination
in Sophos Central API responses.
"""

from collections.abc import AsyncIterator, Callable
from typing import Any, Generic, TypeVar

from pysophoscentralapi.core.exceptions import PaginationError
from pysophoscentralapi.core.models import PaginatedResponse


T = TypeVar("T")


class Paginator(Generic[T]):
    """Cursor-based paginator for Sophos APIs.

    This class handles pagination through API responses, providing
    convenient iteration over pages and items.

    Attributes:
        fetch_page: Async function to fetch a page of results
        page_size: Number of items per page
        max_pages: Maximum number of pages to fetch (None for unlimited)
    """

    def __init__(
        self,
        fetch_page: Callable[[str | None], Any],
        page_size: int = 50,
        max_pages: int | None = None,
    ) -> None:
        """Initialize the paginator.

        Args:
            fetch_page: Async function that takes a page cursor and returns a page
            page_size: Items per page (1-1000)
            max_pages: Maximum pages to fetch (None for all)

        Raises:
            ValueError: If page_size is out of range
        """
        if not 1 <= page_size <= 1000:
            msg = f"page_size must be between 1 and 1000, got {page_size}"
            raise ValueError(msg)

        self.fetch_page = fetch_page
        self.page_size = page_size
        self.max_pages = max_pages
        self._pages_fetched = 0

    async def iter_pages(self) -> AsyncIterator[PaginatedResponse[T]]:
        """Iterate over pages of results.

        Yields:
            PaginatedResponse for each page

        Raises:
            PaginationError: If pagination fails
        """
        next_key: str | None = None

        while True:
            # Check max pages limit
            if self.max_pages and self._pages_fetched >= self.max_pages:
                break

            try:
                page = await self.fetch_page(next_key)
                self._pages_fetched += 1
                yield page

                # Check if there are more pages
                if not page.pages.has_next_page():
                    break

                next_key = page.pages.next_key

            except Exception as e:
                msg = f"Pagination failed: {e}"
                raise PaginationError(msg) from e

    async def iter_items(self) -> AsyncIterator[T]:
        """Iterate over individual items across all pages.

        Yields:
            Individual items from all pages

        Raises:
            PaginationError: If pagination fails
        """
        async for page in self.iter_pages():
            for item in page.items:
                yield item

    async def get_all(self, max_items: int | None = None) -> list[T]:
        """Fetch all items as a list.

        Args:
            max_items: Maximum number of items to fetch (None for all)

        Returns:
            List of all items

        Raises:
            PaginationError: If pagination fails
        """
        items: list[T] = []

        async for item in self.iter_items():
            items.append(item)
            if max_items and len(items) >= max_items:
                break

        return items

    async def get_first_page(self) -> PaginatedResponse[T]:
        """Fetch only the first page of results.

        Returns:
            First page of results

        Raises:
            PaginationError: If fetch fails
        """
        try:
            return await self.fetch_page(None)
        except Exception as e:
            msg = f"Failed to fetch first page: {e}"
            raise PaginationError(msg) from e

    def reset(self) -> None:
        """Reset pagination state.

        Useful when reusing a paginator instance.
        """
        self._pages_fetched = 0


def create_paginator(
    fetch_fn: Callable[[str | None], Any],
    page_size: int = 50,
    max_pages: int | None = None,
) -> Paginator:
    """Create a new paginator instance.

    Helper function for creating paginators with default settings.

    Args:
        fetch_fn: Async function to fetch pages
        page_size: Items per page
        max_pages: Maximum pages to fetch

    Returns:
        Paginator instance

    Example:
        >>> async def fetch(cursor):
        ...     return await client.get(f"/endpoints?cursor={cursor}")
        >>> paginator = create_paginator(fetch, page_size=100)
        >>> async for item in paginator.iter_items():
        ...     print(item)
    """
    return Paginator(fetch_fn, page_size, max_pages)
