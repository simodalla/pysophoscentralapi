"""Pagination helper utilities."""

from typing import Any


class PaginationHelper:
    """Helper utilities for pagination handling.

    Provides utilities for calculating page numbers, offsets,
    and managing cursor-based pagination.
    """

    # Recommended page sizes for different use cases
    PAGE_SIZE_SMALL = 10
    PAGE_SIZE_MEDIUM = 50
    PAGE_SIZE_LARGE = 100
    PAGE_SIZE_MAX = 1000

    @staticmethod
    def calculate_offset(page: int, page_size: int) -> int:
        """Calculate offset for offset-based pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Offset value (0-indexed)

        Raises:
            ValueError: If page or page_size invalid
        """
        if page < 1:
            msg = "Page must be >= 1"
            raise ValueError(msg)
        if page_size < 1:
            msg = "Page size must be >= 1"
            raise ValueError(msg)

        return (page - 1) * page_size

    @staticmethod
    def calculate_page(offset: int, page_size: int) -> int:
        """Calculate page number from offset.

        Args:
            offset: Offset value (0-indexed)
            page_size: Items per page

        Returns:
            Page number (1-indexed)

        Raises:
            ValueError: If offset or page_size invalid
        """
        if offset < 0:
            msg = "Offset must be >= 0"
            raise ValueError(msg)
        if page_size < 1:
            msg = "Page size must be >= 1"
            raise ValueError(msg)

        return (offset // page_size) + 1

    @staticmethod
    def calculate_total_pages(total_items: int, page_size: int) -> int:
        """Calculate total number of pages.

        Args:
            total_items: Total number of items
            page_size: Items per page

        Returns:
            Total number of pages

        Raises:
            ValueError: If page_size invalid
        """
        if page_size < 1:
            msg = "Page size must be >= 1"
            raise ValueError(msg)

        if total_items == 0:
            return 0

        return (total_items + page_size - 1) // page_size

    @staticmethod
    def get_page_info(
        current_page: int, page_size: int, total_items: int
    ) -> dict[str, Any]:
        """Get comprehensive page information.

        Args:
            current_page: Current page number (1-indexed)
            page_size: Items per page
            total_items: Total number of items

        Returns:
            Dictionary with page information
        """
        total_pages = PaginationHelper.calculate_total_pages(total_items, page_size)
        offset = PaginationHelper.calculate_offset(current_page, page_size)

        return {
            "current_page": current_page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "offset": offset,
            "has_previous": current_page > 1,
            "has_next": current_page < total_pages,
            "is_first": current_page == 1,
            "is_last": current_page == total_pages,
        }

    @staticmethod
    def recommend_page_size(total_items: int | None = None) -> int:
        """Recommend appropriate page size based on total items.

        Args:
            total_items: Estimated total number of items

        Returns:
            Recommended page size
        """
        if total_items is None:
            return PaginationHelper.PAGE_SIZE_MEDIUM

        if total_items <= 50:
            return PaginationHelper.PAGE_SIZE_SMALL
        if total_items <= 500:
            return PaginationHelper.PAGE_SIZE_MEDIUM
        if total_items <= 5000:
            return PaginationHelper.PAGE_SIZE_LARGE

        return PaginationHelper.PAGE_SIZE_MAX

    @staticmethod
    def create_page_params(
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Create pagination parameters for API calls.

        Args:
            page: Page number (offset-based)
            page_size: Items per page
            page_token: Page token (cursor-based)

        Returns:
            Dictionary of pagination parameters
        """
        params: dict[str, Any] = {}

        if page is not None:
            if page < 1:
                msg = "Page must be >= 1"
                raise ValueError(msg)
            params["page"] = page

        if page_size is not None:
            if page_size < 1:
                msg = "Page size must be >= 1"
                raise ValueError(msg)
            params["pageSize"] = page_size

        if page_token:
            params["pageToken"] = page_token

        return params

    @staticmethod
    def validate_page_size(page_size: int, max_size: int | None = None) -> bool:
        """Validate page size.

        Args:
            page_size: Requested page size
            max_size: Maximum allowed size

        Returns:
            True if valid

        Raises:
            ValueError: If page size invalid
        """
        if page_size < 1:
            msg = "Page size must be >= 1"
            raise ValueError(msg)

        if max_size and page_size > max_size:
            msg = f"Page size {page_size} exceeds maximum {max_size}"
            raise ValueError(msg)

        return True
