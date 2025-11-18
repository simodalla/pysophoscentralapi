"""Unit tests for pagination module."""

import pytest

from pysophoscentralapi.core.exceptions import PaginationError
from pysophoscentralapi.core.models import PageInfo, PaginatedResponse
from pysophoscentralapi.core.pagination import Paginator, create_paginator


@pytest.fixture
def mock_page_data():
    """Create mock page data for testing."""

    def create_page(items: list[str], next_key: str | None = None):
        return PaginatedResponse[str](
            items=items,
            pages=PageInfo(
                current=None,
                size=len(items),
                total=None,
                from_key=None,
                next_key=next_key,
                max_size=100,
            ),
        )

    return create_page


@pytest.fixture
def multi_page_fetcher(mock_page_data):
    """Create a fetcher that returns multiple pages."""

    async def fetch_page(cursor: str | None):
        if cursor is None:
            # First page
            return mock_page_data(["item1", "item2", "item3"], next_key="page2")
        if cursor == "page2":
            # Second page
            return mock_page_data(["item4", "item5"], next_key="page3")
        if cursor == "page3":
            # Third page (last)
            return mock_page_data(["item6"], next_key=None)
        msg = f"Invalid cursor: {cursor}"
        raise ValueError(msg)

    return fetch_page


@pytest.fixture
def single_page_fetcher(mock_page_data):
    """Create a fetcher that returns a single page."""

    async def fetch_page(cursor: str | None):
        return mock_page_data(["item1", "item2", "item3"], next_key=None)

    return fetch_page


@pytest.fixture
def error_fetcher():
    """Create a fetcher that raises an error."""

    async def fetch_page(cursor: str | None):
        msg = "API error"
        raise RuntimeError(msg)

    return fetch_page


class TestPaginatorInitialization:
    """Test paginator initialization."""

    def test_valid_page_size(self, single_page_fetcher):
        """Test paginator with valid page size."""
        paginator = Paginator(single_page_fetcher, page_size=50)
        assert paginator.page_size == 50
        assert paginator.max_pages is None
        assert paginator._pages_fetched == 0

    def test_min_page_size(self, single_page_fetcher):
        """Test paginator with minimum page size."""
        paginator = Paginator(single_page_fetcher, page_size=1)
        assert paginator.page_size == 1

    def test_max_page_size(self, single_page_fetcher):
        """Test paginator with maximum page size."""
        paginator = Paginator(single_page_fetcher, page_size=1000)
        assert paginator.page_size == 1000

    def test_invalid_page_size_too_small(self, single_page_fetcher):
        """Test paginator with page size too small."""
        with pytest.raises(ValueError, match="page_size must be between 1 and 1000"):
            Paginator(single_page_fetcher, page_size=0)

    def test_invalid_page_size_too_large(self, single_page_fetcher):
        """Test paginator with page size too large."""
        with pytest.raises(ValueError, match="page_size must be between 1 and 1000"):
            Paginator(single_page_fetcher, page_size=1001)

    def test_max_pages_parameter(self, single_page_fetcher):
        """Test paginator with max_pages parameter."""
        paginator = Paginator(single_page_fetcher, page_size=50, max_pages=5)
        assert paginator.max_pages == 5


class TestPaginatorIterPages:
    """Test paginator iter_pages method."""

    @pytest.mark.asyncio
    async def test_single_page(self, single_page_fetcher):
        """Test iterating over a single page."""
        paginator = Paginator(single_page_fetcher)
        pages = []

        async for page in paginator.iter_pages():
            pages.append(page)

        assert len(pages) == 1
        assert len(pages[0].items) == 3
        assert pages[0].items == ["item1", "item2", "item3"]
        assert paginator._pages_fetched == 1

    @pytest.mark.asyncio
    async def test_multiple_pages(self, multi_page_fetcher):
        """Test iterating over multiple pages."""
        paginator = Paginator(multi_page_fetcher)
        pages = []

        async for page in paginator.iter_pages():
            pages.append(page)

        assert len(pages) == 3
        assert pages[0].items == ["item1", "item2", "item3"]
        assert pages[1].items == ["item4", "item5"]
        assert pages[2].items == ["item6"]
        assert paginator._pages_fetched == 3

    @pytest.mark.asyncio
    async def test_max_pages_limit(self, multi_page_fetcher):
        """Test max_pages limit."""
        paginator = Paginator(multi_page_fetcher, max_pages=2)
        pages = []

        async for page in paginator.iter_pages():
            pages.append(page)

        assert len(pages) == 2
        assert paginator._pages_fetched == 2

    @pytest.mark.asyncio
    async def test_pagination_error(self, error_fetcher):
        """Test pagination error handling."""
        paginator = Paginator(error_fetcher)

        with pytest.raises(PaginationError, match="Pagination failed"):
            async for _ in paginator.iter_pages():
                pass


class TestPaginatorIterItems:
    """Test paginator iter_items method."""

    @pytest.mark.asyncio
    async def test_single_page_items(self, single_page_fetcher):
        """Test iterating over items in a single page."""
        paginator = Paginator(single_page_fetcher)
        items = []

        async for item in paginator.iter_items():
            items.append(item)

        assert items == ["item1", "item2", "item3"]

    @pytest.mark.asyncio
    async def test_multiple_pages_items(self, multi_page_fetcher):
        """Test iterating over items across multiple pages."""
        paginator = Paginator(multi_page_fetcher)
        items = []

        async for item in paginator.iter_items():
            items.append(item)

        assert items == ["item1", "item2", "item3", "item4", "item5", "item6"]

    @pytest.mark.asyncio
    async def test_iter_items_with_max_pages(self, multi_page_fetcher):
        """Test iter_items respects max_pages."""
        paginator = Paginator(multi_page_fetcher, max_pages=2)
        items = []

        async for item in paginator.iter_items():
            items.append(item)

        # First 2 pages: 3 + 2 = 5 items
        assert len(items) == 5
        assert items == ["item1", "item2", "item3", "item4", "item5"]


class TestPaginatorGetAll:
    """Test paginator get_all method."""

    @pytest.mark.asyncio
    async def test_get_all_items(self, multi_page_fetcher):
        """Test fetching all items."""
        paginator = Paginator(multi_page_fetcher)
        items = await paginator.get_all()

        assert len(items) == 6
        assert items == ["item1", "item2", "item3", "item4", "item5", "item6"]

    @pytest.mark.asyncio
    async def test_get_all_with_max_items(self, multi_page_fetcher):
        """Test get_all with max_items limit."""
        paginator = Paginator(multi_page_fetcher)
        items = await paginator.get_all(max_items=4)

        assert len(items) == 4
        assert items == ["item1", "item2", "item3", "item4"]

    @pytest.mark.asyncio
    async def test_get_all_with_max_items_exceeding_total(self, single_page_fetcher):
        """Test get_all with max_items exceeding total items."""
        paginator = Paginator(single_page_fetcher)
        items = await paginator.get_all(max_items=100)

        assert len(items) == 3
        assert items == ["item1", "item2", "item3"]

    @pytest.mark.asyncio
    async def test_get_all_empty_page(self):
        """Test get_all with empty results."""

        async def fetch_empty(cursor: str | None):
            return PaginatedResponse[str](
                items=[],
                pages=PageInfo(
                    current=None,
                    size=0,
                    total=None,
                    from_key=None,
                    next_key=None,
                    max_size=100,
                ),
            )

        paginator = Paginator(fetch_empty)
        items = await paginator.get_all()

        assert items == []


class TestPaginatorGetFirstPage:
    """Test paginator get_first_page method."""

    @pytest.mark.asyncio
    async def test_get_first_page(self, multi_page_fetcher):
        """Test fetching only the first page."""
        paginator = Paginator(multi_page_fetcher)
        page = await paginator.get_first_page()

        assert len(page.items) == 3
        assert page.items == ["item1", "item2", "item3"]
        assert page.pages.next_key == "page2"

    @pytest.mark.asyncio
    async def test_get_first_page_error(self, error_fetcher):
        """Test get_first_page error handling."""
        paginator = Paginator(error_fetcher)

        with pytest.raises(PaginationError, match="Failed to fetch first page"):
            await paginator.get_first_page()


class TestPaginatorReset:
    """Test paginator reset method."""

    @pytest.mark.asyncio
    async def test_reset(self, multi_page_fetcher):
        """Test resetting paginator state."""
        paginator = Paginator(multi_page_fetcher, max_pages=2)

        # Fetch some pages
        pages = []
        async for page in paginator.iter_pages():
            pages.append(page)

        assert paginator._pages_fetched == 2

        # Reset
        paginator.reset()
        assert paginator._pages_fetched == 0

        # Fetch again
        pages = []
        async for page in paginator.iter_pages():
            pages.append(page)

        assert paginator._pages_fetched == 2


class TestCreatePaginator:
    """Test create_paginator helper function."""

    def test_create_paginator_default(self, single_page_fetcher):
        """Test creating paginator with defaults."""
        paginator = create_paginator(single_page_fetcher)

        assert isinstance(paginator, Paginator)
        assert paginator.page_size == 50
        assert paginator.max_pages is None

    def test_create_paginator_custom(self, single_page_fetcher):
        """Test creating paginator with custom parameters."""
        paginator = create_paginator(single_page_fetcher, page_size=100, max_pages=5)

        assert isinstance(paginator, Paginator)
        assert paginator.page_size == 100
        assert paginator.max_pages == 5

    @pytest.mark.asyncio
    async def test_create_paginator_functional(self, multi_page_fetcher):
        """Test that created paginator works correctly."""
        paginator = create_paginator(multi_page_fetcher)
        items = await paginator.get_all()

        assert len(items) == 6
        assert items == ["item1", "item2", "item3", "item4", "item5", "item6"]
