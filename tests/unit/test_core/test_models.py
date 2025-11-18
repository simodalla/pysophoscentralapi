"""Tests for data models."""

from pysophoscentralapi.core.models import (
    PageInfo,
    PaginatedResponse,
    SophosBaseModel,
    Token,
    TokenResponse,
)


class TestPageInfo:
    """Tests for PageInfo model."""

    def test_page_info_creation(self):
        """Test basic PageInfo creation."""
        page_info = PageInfo(
            current=1,
            size=50,
            total=5,
            maxSize=1000,
        )
        assert page_info.current == 1
        assert page_info.size == 50
        assert page_info.max_size == 1000

    def test_page_info_with_next_key(self):
        """Test PageInfo with next page key."""
        page_info = PageInfo(
            current=1,
            size=50,
            total=5,
            nextKey="abc123",
            maxSize=1000,
        )
        assert page_info.has_next_page() is True
        assert page_info.next_key == "abc123"

    def test_page_info_without_next_key(self):
        """Test PageInfo without next page (last page)."""
        page_info = PageInfo(
            current=5,
            size=25,
            total=5,
            maxSize=1000,
        )
        assert page_info.has_next_page() is False


class TestPaginatedResponse:
    """Tests for PaginatedResponse model."""

    def test_paginated_response(self):
        """Test PaginatedResponse with generic type."""

        class TestItem(SophosBaseModel):
            id: str
            name: str

        items = [
            TestItem(id="1", name="Item 1"),
            TestItem(id="2", name="Item 2"),
        ]

        page_info = PageInfo(
            current=1,
            size=2,
            total=1,
            maxSize=1000,
        )

        response = PaginatedResponse[TestItem](
            items=items,
            pages=page_info,
        )

        assert len(response.items) == 2
        assert response.items[0].id == "1"
        assert response.pages.size == 2


class TestTokenResponse:
    """Tests for TokenResponse model."""

    def test_token_response(self):
        """Test TokenResponse creation."""
        response = TokenResponse(
            access_token="abc123",
            token_type="bearer",
            expires_in=3600,
            scope="token",
        )
        assert response.access_token == "abc123"
        assert response.token_type == "bearer"
        assert response.expires_in == 3600


class TestToken:
    """Tests for Token class."""

    def test_token_creation(self):
        """Test Token creation from TokenResponse."""
        response = TokenResponse(
            access_token="test-token",
            token_type="bearer",
            expires_in=3600,
        )
        token = Token.from_response(response)

        assert token.access_token == "test-token"
        assert token.token_type == "bearer"
        assert token.is_expired() is False

    def test_token_expiration(self):
        """Test token expiration check."""
        # Token that expires immediately
        token = Token(
            access_token="test",
            token_type="bearer",
            expires_in=-1,  # Already expired
        )
        assert token.is_expired() is True

    def test_token_expires_soon(self):
        """Test token expires soon check."""
        # Token that expires in 60 seconds
        token = Token(
            access_token="test",
            token_type="bearer",
            expires_in=60,
        )
        # Should expire soon within 300 seconds threshold
        assert token.expires_soon(threshold_seconds=300) is True
        # Should not expire soon within 30 seconds threshold
        assert token.expires_soon(threshold_seconds=30) is False

    def test_authorization_header(self):
        """Test authorization header generation."""
        token = Token(
            access_token="test-token-123",
            token_type="bearer",
            expires_in=3600,
        )
        header = token.get_authorization_header()

        assert header == {"Authorization": "Bearer test-token-123"}
