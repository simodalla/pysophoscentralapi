"""Tests for filter and query builders."""

from datetime import datetime, timezone

import pytest

from pysophoscentralapi.filters import FilterBuilder, FilterOperator, QueryBuilder


class TestFilterBuilder:
    """Tests for FilterBuilder."""

    def test_equals_filter(self):
        """Test equals filter."""
        builder = FilterBuilder()
        builder.equals("status", "active")

        params = builder.to_params()
        assert "status__eq" in params
        assert params["status__eq"] == "active"

    def test_not_equals_filter(self):
        """Test not equals filter."""
        builder = FilterBuilder()
        builder.not_equals("type", "inactive")

        params = builder.to_params()
        assert "type__ne" in params

    def test_contains_filter(self):
        """Test contains filter."""
        builder = FilterBuilder()
        builder.contains("name", "test")

        params = builder.to_params()
        assert "name__contains" in params
        assert params["name__contains"] == "test"

    def test_in_list_filter(self):
        """Test in list filter."""
        builder = FilterBuilder()
        builder.in_list("status", ["active", "pending"])

        params = builder.to_params()
        assert "status__in" in params
        assert params["status__in"] == ["active", "pending"]

    def test_between_filter(self):
        """Test between filter."""
        builder = FilterBuilder()
        builder.between("count", 10, 100)

        params = builder.to_params()
        assert "count__between" in params
        assert params["count__between"] == (10, 100)

    def test_is_null_filter(self):
        """Test is null filter."""
        builder = FilterBuilder()
        builder.is_null("deleted_at")

        params = builder.to_params()
        assert "deleted_at__is_null" in params

    def test_is_not_null_filter(self):
        """Test is not null filter."""
        builder = FilterBuilder()
        builder.is_not_null("created_at")

        params = builder.to_params()
        assert "created_at__is_not_null" in params

    def test_chaining_filters(self):
        """Test chaining multiple filters."""
        builder = FilterBuilder()
        builder.equals("status", "active").contains("name", "test").greater_than(
            "count", 5
        )

        params = builder.to_params()
        assert len(params) == 3

    def test_date_range_filter(self):
        """Test date range filter."""
        builder = FilterBuilder()
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end = datetime(2025, 12, 31, tzinfo=timezone.utc)

        builder.date_range("created_at", start, end)

        params = builder.to_params()
        assert "created_at__gte" in params
        assert "created_at__lte" in params

    def test_date_range_start_only(self):
        """Test date range with start only."""
        builder = FilterBuilder()
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)

        builder.date_range("created_at", start=start)

        params = builder.to_params()
        assert "created_at__gte" in params
        assert "created_at__lte" not in params

    def test_search_alias(self):
        """Test search (alias for contains)."""
        builder = FilterBuilder()
        builder.search("name", "test query")

        params = builder.to_params()
        assert "name__contains" in params

    def test_match_any_alias(self):
        """Test match_any (alias for in_list)."""
        builder = FilterBuilder()
        builder.match_any("status", ["active", "pending"])

        params = builder.to_params()
        assert "status__in" in params

    def test_greater_than_filter(self):
        """Test greater than filter."""
        builder = FilterBuilder()
        builder.greater_than("count", 10)

        params = builder.to_params()
        assert "count__gt" in params

    def test_less_than_filter(self):
        """Test less than filter."""
        builder = FilterBuilder()
        builder.less_than("count", 100)

        params = builder.to_params()
        assert "count__lt" in params

    def test_logic_operators(self):
        """Test OR/AND logic operators."""
        builder = FilterBuilder()
        assert builder.get_logic() == "AND"

        builder.use_or_logic()
        assert builder.get_logic() == "OR"

        builder.use_and_logic()
        assert builder.get_logic() == "AND"

    def test_has_filters(self):
        """Test has_filters check."""
        builder = FilterBuilder()
        assert not builder.has_filters()

        builder.equals("status", "active")
        assert builder.has_filters()

    def test_count_filters(self):
        """Test filter count."""
        builder = FilterBuilder()
        assert builder.count() == 0

        builder.equals("status", "active")
        assert builder.count() == 1

        builder.contains("name", "test")
        assert builder.count() == 2

    def test_clear_filters(self):
        """Test clearing all filters."""
        builder = FilterBuilder()
        builder.equals("status", "active").contains("name", "test")

        assert builder.count() == 2

        builder.clear()
        assert builder.count() == 0
        assert not builder.has_filters()

    def test_add_filter_with_operator(self):
        """Test add_filter with custom operator."""
        builder = FilterBuilder()
        builder.add_filter("field", FilterOperator.STARTS_WITH, "prefix")

        params = builder.to_params()
        assert "field__starts_with" in params


class TestQueryBuilder:
    """Tests for QueryBuilder."""

    def test_query_builder_filters(self):
        """Test adding filters via query builder."""
        query = QueryBuilder()
        query.filter().equals("status", "active")

        params = query.build()
        assert "status__eq" in params

    def test_sort_by(self):
        """Test sorting."""
        query = QueryBuilder()
        query.sort_by("name", "asc")

        params = query.build()
        assert "sort" in params
        assert params["sort"] == "name:asc"

    def test_sort_ascending(self):
        """Test sort ascending helper."""
        query = QueryBuilder()
        query.sort_ascending("name")

        params = query.build()
        assert params["sort"] == "name:asc"

    def test_sort_descending(self):
        """Test sort descending helper."""
        query = QueryBuilder()
        query.sort_descending("date")

        params = query.build()
        assert params["sort"] == "date:desc"

    def test_multiple_sorts(self):
        """Test multiple sort fields."""
        query = QueryBuilder()
        query.sort_by("name", "asc").sort_by("date", "desc")

        params = query.build()
        assert params["sort"] == "name:asc,date:desc"

    def test_invalid_sort_direction(self):
        """Test invalid sort direction raises error."""
        query = QueryBuilder()

        with pytest.raises(ValueError, match="Invalid sort direction"):
            query.sort_by("name", "invalid")

    def test_page_size(self):
        """Test page size setting."""
        query = QueryBuilder()
        query.page_size(50)

        params = query.build()
        assert params["pageSize"] == 50

    def test_page_size_validation(self):
        """Test page size validation."""
        query = QueryBuilder()

        with pytest.raises(ValueError, match="must be positive"):
            query.page_size(0)

    def test_page_token(self):
        """Test page token."""
        query = QueryBuilder()
        query.page_token("abc123")

        params = query.build()
        assert params["pageToken"] == "abc123"

    def test_fields_selection(self):
        """Test field selection."""
        query = QueryBuilder()
        query.fields("id", "name", "status")

        params = query.build()
        assert params["fields"] == "id,name,status"

    def test_limit(self):
        """Test result limit."""
        query = QueryBuilder()
        query.limit(100)

        params = query.build()
        assert params["limit"] == 100

    def test_limit_validation(self):
        """Test limit validation."""
        query = QueryBuilder()

        with pytest.raises(ValueError, match="must be positive"):
            query.limit(0)

    def test_complete_query(self):
        """Test building complete query with all features."""
        query = QueryBuilder()
        query.filter().equals("status", "active").contains("name", "test")
        query.sort_ascending("name").sort_descending("date")
        query.page_size(50).fields("id", "name").limit(500)

        params = query.build()

        assert "status__eq" in params
        assert "name__contains" in params
        assert params["sort"] == "name:asc,date:desc"
        assert params["pageSize"] == 50
        assert params["fields"] == "id,name"
        assert params["limit"] == 500

    def test_clear_query(self):
        """Test clearing all query parameters."""
        query = QueryBuilder()
        query.filter().equals("status", "active")
        query.sort_by("name", "asc")
        query.page_size(50)

        query.clear()

        params = query.build()
        assert len(params) == 0

    def test_repr(self):
        """Test string representation."""
        query = QueryBuilder()
        query.filter().equals("status", "active")
        query.sort_by("name", "asc")

        repr_str = repr(query)
        assert "QueryBuilder" in repr_str
        assert "filters=1" in repr_str
        assert "sorts=1" in repr_str
