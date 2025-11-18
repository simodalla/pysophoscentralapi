"""Base filter classes and operators."""

from enum import Enum
from typing import Any


class FilterOperator(str, Enum):
    """Filter operators for query building."""

    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class FilterBase:
    """Base class for filter construction.

    Provides methods for building type-safe filters that can be
    converted to API query parameters.
    """

    def __init__(self) -> None:
        """Initialize empty filter."""
        self._filters: dict[str, Any] = {}

    def add_filter(
        self, field: str, operator: FilterOperator, value: Any
    ) -> "FilterBase":
        """Add a filter condition.

        Args:
            field: Field name to filter on
            operator: Filter operator
            value: Value to filter by

        Returns:
            Self for method chaining
        """
        filter_key = f"{field}__{operator.value}"
        self._filters[filter_key] = value
        return self

    def equals(self, field: str, value: Any) -> "FilterBase":
        """Add equals filter.

        Args:
            field: Field name
            value: Value to match

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.EQUALS, value)

    def not_equals(self, field: str, value: Any) -> "FilterBase":
        """Add not equals filter.

        Args:
            field: Field name
            value: Value to not match

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.NOT_EQUALS, value)

    def contains(self, field: str, value: str) -> "FilterBase":
        """Add contains filter (substring match).

        Args:
            field: Field name
            value: Substring to search for

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.CONTAINS, value)

    def in_list(self, field: str, values: list[Any]) -> "FilterBase":
        """Add 'in' filter (match any value in list).

        Args:
            field: Field name
            values: List of values to match

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.IN, values)

    def between(self, field: str, min_value: Any, max_value: Any) -> "FilterBase":
        """Add between filter (inclusive range).

        Args:
            field: Field name
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.BETWEEN, (min_value, max_value))

    def is_null(self, field: str) -> "FilterBase":
        """Add is null filter.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.IS_NULL, None)

    def is_not_null(self, field: str) -> "FilterBase":
        """Add is not null filter.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.add_filter(field, FilterOperator.IS_NOT_NULL, None)

    def to_params(self) -> dict[str, Any]:
        """Convert filters to API query parameters.

        Returns:
            Dictionary of query parameters
        """
        return self._filters.copy()

    def clear(self) -> "FilterBase":
        """Clear all filters.

        Returns:
            Self for chaining
        """
        self._filters.clear()
        return self

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({self._filters})"
