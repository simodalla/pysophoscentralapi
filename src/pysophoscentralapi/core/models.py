"""Shared data models and base classes for pysophoscentralapi.

This module contains base models and common data structures used throughout
the library, built on Pydantic for validation and serialization.
"""

from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class SophosBaseModel(BaseModel):
    """Base model for all Pydantic models in the library.

    Provides common configuration and utilities for all data models.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",  # Ignore extra fields from API
    )


class PageInfo(SophosBaseModel):
    """Pagination information from API responses.

    Attributes:
        current: Current page number
        size: Number of items in current page
        total: Total number of pages
        from_key: Cursor key for current page
        next_key: Cursor key for next page (None if last page)
        max_size: Maximum allowed page size
    """

    current: int | None = None
    size: int
    total: int | None = None
    from_key: str | None = Field(None, alias="fromKey")
    next_key: str | None = Field(None, alias="nextKey")
    max_size: int = Field(alias="maxSize")

    def has_next_page(self) -> bool:
        """Check if there are more pages available.

        Returns:
            True if there are more pages, False otherwise
        """
        return self.next_key is not None


T = TypeVar("T")


class PaginatedResponse(SophosBaseModel, Generic[T]):
    """Generic paginated response from Sophos APIs.

    This model wraps paginated API responses with type safety for items.

    Attributes:
        items: List of items in the current page
        pages: Pagination information

    Example:
        >>> from pydantic import BaseModel
        >>> class Endpoint(BaseModel):
        ...     id: str
        ...     hostname: str
        >>> response = PaginatedResponse[Endpoint](
        ...     items=[Endpoint(id="1", hostname="test")],
        ...     pages=PageInfo(current=1, size=1, total=1, maxSize=100)
        ... )
        >>> response.items[0].hostname
        'test'
    """

    items: list[T]
    pages: PageInfo


class WhoAmIResponse(SophosBaseModel):
    """Response from the whoami endpoint.

    Attributes:
        id: Organization or partner ID
        id_type: Type of ID (tenant, partner, organization)
        api_host_global: Global API host URL
        api_host_data_region: Data region-specific API host URL
    """

    id: str
    id_type: str = Field(alias="idType")
    api_host_global: str = Field(alias="apiHosts.global")
    api_host_data_region: str = Field(alias="apiHosts.dataRegion")


class TokenResponse(SophosBaseModel):
    """OAuth2 token response.

    Attributes:
        access_token: The access token
        token_type: Type of token (typically "bearer")
        expires_in: Token lifetime in seconds
        refresh_token: Refresh token if provided
        scope: Token scope
    """

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None


class Token:
    """Token container with expiration tracking.

    This class wraps an access token and tracks its expiration time.

    Attributes:
        access_token: The access token string
        token_type: Type of token
        expires_at: When the token expires
        refresh_token: Optional refresh token
    """

    def __init__(
        self,
        access_token: str,
        token_type: str,
        expires_in: int,
        refresh_token: str | None = None,
    ) -> None:
        """Initialize token with expiration calculation.

        Args:
            access_token: The access token
            token_type: Token type (e.g., "bearer")
            expires_in: Token lifetime in seconds
            refresh_token: Optional refresh token
        """
        self.access_token = access_token
        self.token_type = token_type
        self.expires_at = datetime.now(timezone.utc).timestamp() + expires_in
        self.refresh_token = refresh_token

    def is_expired(self) -> bool:
        """Check if token is expired.

        Returns:
            True if token is expired, False otherwise
        """
        return datetime.now(timezone.utc).timestamp() >= self.expires_at

    def expires_soon(self, threshold_seconds: int = 300) -> bool:
        """Check if token expires within threshold.

        Args:
            threshold_seconds: Time in seconds to consider "soon"

        Returns:
            True if token expires within threshold, False otherwise
        """
        return datetime.now(timezone.utc).timestamp() >= (
            self.expires_at - threshold_seconds
        )

    def get_authorization_header(self) -> dict[str, str]:
        """Get authorization header dict.

        Returns:
            Dictionary with Authorization header

        Example:
            >>> token = Token("abc123", "bearer", 3600)
            >>> token.get_authorization_header()
            {'Authorization': 'Bearer abc123'}
        """
        return {"Authorization": f"{self.token_type.capitalize()} {self.access_token}"}

    @classmethod
    def from_response(cls, response: TokenResponse) -> "Token":
        """Create Token from API response.

        Args:
            response: Token response from API

        Returns:
            Token instance
        """
        return cls(
            access_token=response.access_token,
            token_type=response.token_type,
            expires_in=response.expires_in,
            refresh_token=response.refresh_token,
        )


class ErrorResponse(SophosBaseModel):
    """Standard error response from Sophos APIs.

    Attributes:
        error: Error code
        message: Human-readable error message
        correlation_id: Correlation ID for tracking
        request_id: Request ID for tracking
    """

    error: str
    message: str
    correlation_id: str | None = Field(None, alias="correlationId")
    request_id: str | None = Field(None, alias="requestId")
