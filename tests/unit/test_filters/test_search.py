"""Tests for search utilities."""

from pysophoscentralapi.filters import SearchBuilder


class TestSearchBuilder:
    """Tests for SearchBuilder."""

    def test_add_term(self):
        """Test adding a search term."""
        builder = SearchBuilder()
        builder.add_term("malware")

        query = builder.build_query()
        assert query == "malware"

    def test_add_multiple_terms(self):
        """Test adding multiple terms."""
        builder = SearchBuilder()
        builder.add_term("malware").add_term("ransomware")

        query = builder.build_query()
        assert query == "malware AND ransomware"

    def test_add_terms_batch(self):
        """Test adding terms in batch."""
        builder = SearchBuilder()
        builder.add_terms("term1", "term2", "term3")

        query = builder.build_query()
        assert query == "term1 AND term2 AND term3"

    def test_in_field(self):
        """Test searching in specific field."""
        builder = SearchBuilder()
        builder.add_term("test").in_field("name")

        query = builder.build_query()
        assert "fields:(name)" in query
        assert "test" in query

    def test_in_multiple_fields(self):
        """Test searching in multiple fields."""
        builder = SearchBuilder()
        builder.add_term("test").in_field("name").in_field("description")

        query = builder.build_query()
        assert "fields:(name,description)" in query

    def test_in_fields_batch(self):
        """Test adding fields in batch."""
        builder = SearchBuilder()
        builder.add_term("test").in_fields("name", "description", "notes")

        query = builder.build_query()
        assert "fields:(name,description,notes)" in query

    def test_use_and_operator(self):
        """Test AND operator."""
        builder = SearchBuilder()
        builder.add_terms("term1", "term2").use_and()

        query = builder.build_query()
        assert query == "term1 AND term2"

    def test_use_or_operator(self):
        """Test OR operator."""
        builder = SearchBuilder()
        builder.add_terms("term1", "term2").use_or()

        query = builder.build_query()
        assert query == "term1 OR term2"

    def test_empty_builder(self):
        """Test empty search builder."""
        builder = SearchBuilder()
        query = builder.build_query()

        assert query == ""

    def test_clear_search(self):
        """Test clearing search."""
        builder = SearchBuilder()
        builder.add_terms("term1", "term2").in_field("name")

        assert builder.has_terms()

        builder.clear()
        assert not builder.has_terms()
        assert builder.build_query() == ""

    def test_has_terms(self):
        """Test has_terms check."""
        builder = SearchBuilder()
        assert not builder.has_terms()

        builder.add_term("test")
        assert builder.has_terms()

    def test_to_params(self):
        """Test converting to parameters."""
        builder = SearchBuilder()
        builder.add_terms("malware", "ransomware")

        params = builder.to_params()
        assert "search" in params
        assert params["search"] == "malware AND ransomware"

    def test_to_params_custom_key(self):
        """Test converting to parameters with custom key."""
        builder = SearchBuilder()
        builder.add_term("test")

        params = builder.to_params(key="query")
        assert "query" in params

    def test_to_params_empty(self):
        """Test converting empty builder to parameters."""
        builder = SearchBuilder()
        params = builder.to_params()

        assert len(params) == 0

    def test_repr(self):
        """Test string representation."""
        builder = SearchBuilder()
        builder.add_terms("term1", "term2")

        repr_str = repr(builder)
        assert "SearchBuilder" in repr_str
        assert "term1 AND term2" in repr_str

    def test_str(self):
        """Test string conversion."""
        builder = SearchBuilder()
        builder.add_terms("term1", "term2")

        assert str(builder) == "term1 AND term2"

    def test_strip_whitespace(self):
        """Test that terms are stripped of whitespace."""
        builder = SearchBuilder()
        builder.add_term("  test  ")

        query = builder.build_query()
        assert query == "test"

    def test_empty_term_ignored(self):
        """Test that empty terms are ignored."""
        builder = SearchBuilder()
        builder.add_term("").add_term("test")

        query = builder.build_query()
        assert query == "test"

    def test_duplicate_fields_ignored(self):
        """Test that duplicate fields are ignored."""
        builder = SearchBuilder()
        builder.add_term("test").in_field("name").in_field("name")

        query = builder.build_query()
        # Should only appear once
        assert query.count("name") == 1

    def test_complex_search(self):
        """Test complex search with all features."""
        builder = SearchBuilder()
        builder.add_terms("malware", "virus", "trojan").in_fields(
            "name", "description"
        ).use_or()

        query = builder.build_query()
        assert "fields:(name,description)" in query
        assert "malware OR virus OR trojan" in query
