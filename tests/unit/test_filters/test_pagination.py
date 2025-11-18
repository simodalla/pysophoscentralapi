"""Tests for pagination utilities."""

import pytest

from pysophoscentralapi.filters import PaginationHelper


class TestPaginationHelper:
    """Tests for PaginationHelper."""

    def test_calculate_offset(self):
        """Test offset calculation."""
        # Page 1, size 10 = offset 0
        assert PaginationHelper.calculate_offset(1, 10) == 0

        # Page 2, size 10 = offset 10
        assert PaginationHelper.calculate_offset(2, 10) == 10

        # Page 5, size 20 = offset 80
        assert PaginationHelper.calculate_offset(5, 20) == 80

    def test_calculate_offset_invalid_page(self):
        """Test offset calculation with invalid page."""
        with pytest.raises(ValueError, match="Page must be >= 1"):
            PaginationHelper.calculate_offset(0, 10)

        with pytest.raises(ValueError, match="Page must be >= 1"):
            PaginationHelper.calculate_offset(-1, 10)

    def test_calculate_offset_invalid_page_size(self):
        """Test offset calculation with invalid page size."""
        with pytest.raises(ValueError, match="Page size must be >= 1"):
            PaginationHelper.calculate_offset(1, 0)

    def test_calculate_page(self):
        """Test page calculation from offset."""
        # Offset 0, size 10 = page 1
        assert PaginationHelper.calculate_page(0, 10) == 1

        # Offset 10, size 10 = page 2
        assert PaginationHelper.calculate_page(10, 10) == 2

        # Offset 80, size 20 = page 5
        assert PaginationHelper.calculate_page(80, 20) == 5

    def test_calculate_page_invalid_offset(self):
        """Test page calculation with invalid offset."""
        with pytest.raises(ValueError, match="Offset must be >= 0"):
            PaginationHelper.calculate_page(-1, 10)

    def test_calculate_page_invalid_page_size(self):
        """Test page calculation with invalid page size."""
        with pytest.raises(ValueError, match="Page size must be >= 1"):
            PaginationHelper.calculate_page(0, 0)

    def test_calculate_total_pages(self):
        """Test total pages calculation."""
        # 100 items, 10 per page = 10 pages
        assert PaginationHelper.calculate_total_pages(100, 10) == 10

        # 95 items, 10 per page = 10 pages
        assert PaginationHelper.calculate_total_pages(95, 10) == 10

        # 101 items, 10 per page = 11 pages
        assert PaginationHelper.calculate_total_pages(101, 10) == 11

        # 0 items = 0 pages
        assert PaginationHelper.calculate_total_pages(0, 10) == 0

    def test_calculate_total_pages_invalid_page_size(self):
        """Test total pages with invalid page size."""
        with pytest.raises(ValueError, match="Page size must be >= 1"):
            PaginationHelper.calculate_total_pages(100, 0)

    def test_get_page_info(self):
        """Test comprehensive page information."""
        info = PaginationHelper.get_page_info(
            current_page=3, page_size=10, total_items=100
        )

        assert info["current_page"] == 3
        assert info["page_size"] == 10
        assert info["total_items"] == 100
        assert info["total_pages"] == 10
        assert info["offset"] == 20
        assert info["has_previous"] is True
        assert info["has_next"] is True
        assert info["is_first"] is False
        assert info["is_last"] is False

    def test_get_page_info_first_page(self):
        """Test page info for first page."""
        info = PaginationHelper.get_page_info(
            current_page=1, page_size=10, total_items=100
        )

        assert info["has_previous"] is False
        assert info["is_first"] is True
        assert info["is_last"] is False

    def test_get_page_info_last_page(self):
        """Test page info for last page."""
        info = PaginationHelper.get_page_info(
            current_page=10, page_size=10, total_items=100
        )

        assert info["has_next"] is False
        assert info["is_first"] is False
        assert info["is_last"] is True

    def test_recommend_page_size(self):
        """Test page size recommendations."""
        # None = medium
        assert (
            PaginationHelper.recommend_page_size() == PaginationHelper.PAGE_SIZE_MEDIUM
        )

        # Small dataset
        assert (
            PaginationHelper.recommend_page_size(30) == PaginationHelper.PAGE_SIZE_SMALL
        )

        # Medium dataset
        assert (
            PaginationHelper.recommend_page_size(200)
            == PaginationHelper.PAGE_SIZE_MEDIUM
        )

        # Large dataset
        assert (
            PaginationHelper.recommend_page_size(2000)
            == PaginationHelper.PAGE_SIZE_LARGE
        )

        # Very large dataset
        assert (
            PaginationHelper.recommend_page_size(10000)
            == PaginationHelper.PAGE_SIZE_MAX
        )

    def test_create_page_params(self):
        """Test creating pagination parameters."""
        params = PaginationHelper.create_page_params(
            page=2, page_size=50, page_token="abc123"
        )

        assert params["page"] == 2
        assert params["pageSize"] == 50
        assert params["pageToken"] == "abc123"

    def test_create_page_params_optional(self):
        """Test creating params with optional values."""
        params = PaginationHelper.create_page_params(page_size=25)

        assert "pageSize" in params
        assert "page" not in params
        assert "pageToken" not in params

    def test_create_page_params_invalid_page(self):
        """Test creating params with invalid page."""
        with pytest.raises(ValueError, match="Page must be >= 1"):
            PaginationHelper.create_page_params(page=0)

    def test_create_page_params_invalid_page_size(self):
        """Test creating params with invalid page size."""
        with pytest.raises(ValueError, match="Page size must be >= 1"):
            PaginationHelper.create_page_params(page_size=0)

    def test_validate_page_size(self):
        """Test page size validation."""
        assert PaginationHelper.validate_page_size(50) is True
        assert PaginationHelper.validate_page_size(100, max_size=1000) is True

    def test_validate_page_size_too_small(self):
        """Test validation with too small page size."""
        with pytest.raises(ValueError, match="Page size must be >= 1"):
            PaginationHelper.validate_page_size(0)

    def test_validate_page_size_too_large(self):
        """Test validation with too large page size."""
        with pytest.raises(ValueError, match="exceeds maximum"):
            PaginationHelper.validate_page_size(2000, max_size=1000)

    def test_page_size_constants(self):
        """Test page size constants."""
        assert PaginationHelper.PAGE_SIZE_SMALL == 10
        assert PaginationHelper.PAGE_SIZE_MEDIUM == 50
        assert PaginationHelper.PAGE_SIZE_LARGE == 100
        assert PaginationHelper.PAGE_SIZE_MAX == 1000
