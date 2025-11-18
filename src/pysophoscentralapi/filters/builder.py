"""Query and filter builder utilities."""

from datetime import datetime
from typing import Any

from pysophoscentralapi.filters.base import FilterBase, FilterOperator


class FilterBuilder(FilterBase):
    """Enhanced filter builder with additional utilities.

    Provides a fluent interface for building complex filter queries
    with validation and type safety.
    """

    def __init__(self, validate: bool = True) -> None:
        """Initialize filter builder.

        Args:
            validate: Whether to validate filter values
        """
        super().__init__()
        self.validate = validate
        self._logic = "AND"  # Default logic operator

    def date_range(
        self, field: str, start: datetime | None = None, end: datetime | None = None
    ) -> "FilterBuilder":
        """Add date range filter.

        Args:
            field: Field name (e.g., 'created_at')
            start: Start datetime (inclusive)
            end: End datetime (inclusive)

        Returns:
            Self for chaining
        """
        if start:
            self.add_filter(field, FilterOperator.GREATER_THAN_OR_EQUAL, start)
        if end:
            self.add_filter(field, FilterOperator.LESS_THAN_OR_EQUAL, end)
        return self

    def search(self, field: str, query: str) -> "FilterBuilder":
        """Add search filter (alias for contains).

        Args:
            field: Field name
            query: Search query

        Returns:
            Self for chaining
        """
        return self.contains(field, query)

    def match_any(self, field: str, values: list[Any]) -> "FilterBuilder":
        """Match any value in list (alias for in_list).

        Args:
            field: Field name
            values: List of values

        Returns:
            Self for chaining
        """
        return self.in_list(field, values)

    def greater_than(self, field: str, value: Any) -> "FilterBuilder":
        """Add greater than filter.

        Args:
            field: Field name
            value: Minimum value (exclusive)

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.GREATER_THAN, value)

    def less_than(self, field: str, value: Any) -> "FilterBuilder":
        """Add less than filter.

        Args:
            field: Field name
            value: Maximum value (exclusive)

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.LESS_THAN, value)

    def use_or_logic(self) -> "FilterBuilder":
        """Use OR logic for combining filters.

        Returns:
            Self for chaining
        """
        self._logic = "OR"
        return self

    def use_and_logic(self) -> "FilterBuilder":
        """Use AND logic for combining filters (default).

        Returns:
            Self for chaining
        """
        self._logic = "AND"
        return self

    def get_logic(self) -> str:
        """Get current logic operator.

        Returns:
            Logic operator ('AND' or 'OR')
        """
        return self._logic

    def has_filters(self) -> bool:
        """Check if any filters are set.

        Returns:
            True if filters exist
        """
        return bool(self._filters)

    def count(self) -> int:
        """Count number of filters.

        Returns:
            Number of filters
        """
        return len(self._filters)


class QueryBuilder:
    """Complete query builder with filters, sorting, and pagination.

    Provides a unified interface for building complex API queries.
    """

    def __init__(self) -> None:
        """Initialize query builder."""
        self.filters = FilterBuilder()
        self._sort_fields: list[tuple[str, str]] = []
        self._page_size: int | None = None
        self._page_token: str | None = None
        self._fields: list[str] | None = None
        self._limit: int | None = None

    def filter(self) -> FilterBuilder:
        """Get filter builder for adding filters.

        Returns:
            FilterBuilder instance
        """
        return self.filters

    def sort_by(self, field: str, direction: str = "asc") -> "QueryBuilder":
        """Add sort field.

        Args:
            field: Field name to sort by
            direction: Sort direction ('asc' or 'desc')

        Returns:
            Self for chaining
        """
        if direction not in ("asc", "desc"):
            msg = f"Invalid sort direction: {direction}"
            raise ValueError(msg)

        self._sort_fields.append((field, direction))
        return self

    def sort_ascending(self, field: str) -> "QueryBuilder":
        """Sort by field ascending.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.sort_by(field, "asc")

    def sort_descending(self, field: str) -> "QueryBuilder":
        """Sort by field descending.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.sort_by(field, "desc")

    def page_size(self, size: int) -> "QueryBuilder":
        """Set page size for pagination.

        Args:
            size: Number of items per page

        Returns:
            Self for chaining
        """
        if size < 1:
            msg = "Page size must be positive"
            raise ValueError(msg)

        self._page_size = size
        return self

    def page_token(self, token: str) -> "QueryBuilder":
        """Set page token for cursor-based pagination.

        Args:
            token: Page token from previous response

        Returns:
            Self for chaining
        """
        self._page_token = token
        return self

    def fields(self, *field_names: str) -> "QueryBuilder":
        """Select specific fields to return.

        Args:
            field_names: Field names to include

        Returns:
            Self for chaining
        """
        self._fields = list(field_names)
        return self

    def limit(self, max_items: int) -> "QueryBuilder":
        """Limit total number of items returned.

        Args:
            max_items: Maximum items to return

        Returns:
            Self for chaining
        """
        if max_items < 1:
            msg = "Limit must be positive"
            raise ValueError(msg)

        self._limit = max_items
        return self

    def build(self) -> dict[str, Any]:
        """Build final query parameters.

        Returns:
            Dictionary of query parameters
        """
        params: dict[str, Any] = {}

        # Add filters
        if self.filters.has_filters():
            params.update(self.filters.to_params())

        # Add sorting
        if self._sort_fields:
            sort_strings = [
                f"{field}:{direction}" for field, direction in self._sort_fields
            ]
            params["sort"] = ",".join(sort_strings)

        # Add pagination
        if self._page_size:
            params["pageSize"] = self._page_size
        if self._page_token:
            params["pageToken"] = self._page_token

        # Add field selection
        if self._fields:
            params["fields"] = ",".join(self._fields)

        # Add limit
        if self._limit:
            params["limit"] = self._limit

        return params

    def clear(self) -> "QueryBuilder":
        """Clear all query parameters.

        Returns:
            Self for chaining
        """
        self.filters.clear()
        self._sort_fields.clear()
        self._page_size = None
        self._page_token = None
        self._fields = None
        self._limit = None
        return self

    def __repr__(self) -> str:
        """String representation."""
        return f"QueryBuilder(filters={self.filters.count()}, sorts={len(self._sort_fields)})"
