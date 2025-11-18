"""Search utilities for building search queries."""

from typing import Any


class SearchBuilder:
    """Builder for search queries.

    Provides utilities for building text-based search queries
    with support for multiple fields and operators.
    """

    def __init__(self) -> None:
        """Initialize search builder."""
        self._terms: list[str] = []
        self._fields: list[str] = []
        self._operator = "AND"

    def add_term(self, term: str) -> "SearchBuilder":
        """Add a search term.

        Args:
            term: Search term

        Returns:
            Self for chaining
        """
        if term:
            self._terms.append(term.strip())
        return self

    def add_terms(self, *terms: str) -> "SearchBuilder":
        """Add multiple search terms.

        Args:
            terms: Search terms

        Returns:
            Self for chaining
        """
        for term in terms:
            self.add_term(term)
        return self

    def in_field(self, field: str) -> "SearchBuilder":
        """Add field to search in.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        if field and field not in self._fields:
            self._fields.append(field)
        return self

    def in_fields(self, *fields: str) -> "SearchBuilder":
        """Add multiple fields to search in.

        Args:
            fields: Field names

        Returns:
            Self for chaining
        """
        for field in fields:
            self.in_field(field)
        return self

    def use_and(self) -> "SearchBuilder":
        """Use AND operator for combining terms.

        Returns:
            Self for chaining
        """
        self._operator = "AND"
        return self

    def use_or(self) -> "SearchBuilder":
        """Use OR operator for combining terms.

        Returns:
            Self for chaining
        """
        self._operator = "OR"
        return self

    def clear(self) -> "SearchBuilder":
        """Clear all search criteria.

        Returns:
            Self for chaining
        """
        self._terms.clear()
        self._fields.clear()
        self._operator = "AND"
        return self

    def build_query(self) -> str:
        """Build search query string.

        Returns:
            Search query string
        """
        if not self._terms:
            return ""

        # Join terms with operator
        query = f" {self._operator} ".join(self._terms)

        # Add field specification if provided
        if self._fields:
            fields_str = ",".join(self._fields)
            query = f"fields:({fields_str}) {query}"

        return query

    def to_params(self, key: str = "search") -> dict[str, Any]:
        """Convert to API query parameters.

        Args:
            key: Parameter key name

        Returns:
            Dictionary with search parameter
        """
        query = self.build_query()
        if not query:
            return {}

        return {key: query}

    def has_terms(self) -> bool:
        """Check if any search terms exist.

        Returns:
            True if terms exist
        """
        return bool(self._terms)

    def __repr__(self) -> str:
        """String representation."""
        return f"SearchBuilder({self.build_query()})"

    def __str__(self) -> str:
        """String conversion."""
        return self.build_query()
