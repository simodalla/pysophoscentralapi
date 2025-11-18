"""Sorting utilities for API queries."""

from enum import Enum
from typing import Any


class SortDirection(str, Enum):
    """Sort direction enumeration."""

    ASCENDING = "asc"
    DESCENDING = "desc"


class SortBuilder:
    """Builder for complex sorting specifications.

    Provides utilities for building multi-field sort orders
    with type safety and validation.
    """

    def __init__(self) -> None:
        """Initialize sort builder."""
        self._sorts: list[tuple[str, SortDirection]] = []

    def add(
        self, field: str, direction: SortDirection | str = SortDirection.ASCENDING
    ) -> "SortBuilder":
        """Add a sort field.

        Args:
            field: Field name to sort by
            direction: Sort direction

        Returns:
            Self for chaining
        """
        if isinstance(direction, str):
            direction = SortDirection(direction)

        self._sorts.append((field, direction))
        return self

    def ascending(self, field: str) -> "SortBuilder":
        """Add ascending sort.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.add(field, SortDirection.ASCENDING)

    def descending(self, field: str) -> "SortBuilder":
        """Add descending sort.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.add(field, SortDirection.DESCENDING)

    def asc(self, field: str) -> "SortBuilder":
        """Add ascending sort (alias).

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.ascending(field)

    def desc(self, field: str) -> "SortBuilder":
        """Add descending sort (alias).

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        return self.descending(field)

    def reverse(self) -> "SortBuilder":
        """Reverse all sort directions.

        Returns:
            Self for chaining
        """
        self._sorts = [
            (
                field,
                SortDirection.DESCENDING
                if direction == SortDirection.ASCENDING
                else SortDirection.ASCENDING,
            )
            for field, direction in self._sorts
        ]
        return self

    def clear(self) -> "SortBuilder":
        """Clear all sorts.

        Returns:
            Self for chaining
        """
        self._sorts.clear()
        return self

    def to_string(self, separator: str = ",") -> str:
        """Convert to sort string.

        Args:
            separator: Separator between sort fields

        Returns:
            Sort string (e.g., "name:asc,date:desc")
        """
        return separator.join(
            [f"{field}:{direction.value}" for field, direction in self._sorts]
        )

    def to_params(self, key: str = "sort") -> dict[str, Any]:
        """Convert to API query parameters.

        Args:
            key: Parameter key name

        Returns:
            Dictionary with sort parameter
        """
        if not self._sorts:
            return {}

        return {key: self.to_string()}

    def has_sorts(self) -> bool:
        """Check if any sorts are defined.

        Returns:
            True if sorts exist
        """
        return bool(self._sorts)

    def count(self) -> int:
        """Count number of sort fields.

        Returns:
            Number of sort fields
        """
        return len(self._sorts)

    def __repr__(self) -> str:
        """String representation."""
        return f"SortBuilder({self.to_string()})"

    def __str__(self) -> str:
        """String conversion."""
        return self.to_string()
