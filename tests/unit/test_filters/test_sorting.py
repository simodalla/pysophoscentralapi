"""Tests for sorting utilities."""

from pysophoscentralapi.filters import SortBuilder, SortDirection


class TestSortBuilder:
    """Tests for SortBuilder."""

    def test_add_sort(self):
        """Test adding a sort field."""
        builder = SortBuilder()
        builder.add("name", SortDirection.ASCENDING)

        assert builder.count() == 1
        assert builder.to_string() == "name:asc"

    def test_ascending_sort(self):
        """Test ascending sort."""
        builder = SortBuilder()
        builder.ascending("name")

        assert builder.to_string() == "name:asc"

    def test_descending_sort(self):
        """Test descending sort."""
        builder = SortBuilder()
        builder.descending("date")

        assert builder.to_string() == "date:desc"

    def test_asc_alias(self):
        """Test asc() alias."""
        builder = SortBuilder()
        builder.asc("field")

        assert builder.to_string() == "field:asc"

    def test_desc_alias(self):
        """Test desc() alias."""
        builder = SortBuilder()
        builder.desc("field")

        assert builder.to_string() == "field:desc"

    def test_multiple_sorts(self):
        """Test multiple sort fields."""
        builder = SortBuilder()
        builder.asc("name").desc("date").asc("id")

        result = builder.to_string()
        assert result == "name:asc,date:desc,id:asc"

    def test_custom_separator(self):
        """Test custom separator."""
        builder = SortBuilder()
        builder.asc("name").desc("date")

        result = builder.to_string(separator=";")
        assert result == "name:asc;date:desc"

    def test_reverse_sorts(self):
        """Test reversing all sort directions."""
        builder = SortBuilder()
        builder.asc("name").desc("date")

        assert builder.to_string() == "name:asc,date:desc"

        builder.reverse()
        assert builder.to_string() == "name:desc,date:asc"

    def test_clear_sorts(self):
        """Test clearing all sorts."""
        builder = SortBuilder()
        builder.asc("name").desc("date")

        assert builder.count() == 2

        builder.clear()
        assert builder.count() == 0
        assert not builder.has_sorts()

    def test_has_sorts(self):
        """Test has_sorts check."""
        builder = SortBuilder()
        assert not builder.has_sorts()

        builder.asc("name")
        assert builder.has_sorts()

    def test_count(self):
        """Test sort count."""
        builder = SortBuilder()
        assert builder.count() == 0

        builder.asc("name")
        assert builder.count() == 1

        builder.desc("date")
        assert builder.count() == 2

    def test_to_params(self):
        """Test converting to parameters."""
        builder = SortBuilder()
        builder.asc("name").desc("date")

        params = builder.to_params()
        assert "sort" in params
        assert params["sort"] == "name:asc,date:desc"

    def test_to_params_custom_key(self):
        """Test converting to parameters with custom key."""
        builder = SortBuilder()
        builder.asc("name")

        params = builder.to_params(key="orderBy")
        assert "orderBy" in params

    def test_to_params_empty(self):
        """Test converting empty builder to parameters."""
        builder = SortBuilder()
        params = builder.to_params()

        assert len(params) == 0

    def test_repr(self):
        """Test string representation."""
        builder = SortBuilder()
        builder.asc("name").desc("date")

        repr_str = repr(builder)
        assert "SortBuilder" in repr_str
        assert "name:asc,date:desc" in repr_str

    def test_str(self):
        """Test string conversion."""
        builder = SortBuilder()
        builder.asc("name").desc("date")

        assert str(builder) == "name:asc,date:desc"

    def test_string_direction(self):
        """Test adding sort with string direction."""
        builder = SortBuilder()
        builder.add("name", "asc")

        assert builder.to_string() == "name:asc"
