"""HTTP client with retry logic and error handling.

This module provides a robust HTTP client for interacting with Sophos APIs,
with automatic retry, rate limiting handling, and proper error conversion.
"""

import asyncio
import logging
from typing import Any

import httpx

from pysophoscentralapi.core.auth import AuthProvider
from pysophoscentralapi.core.exceptions import (
    ConnectionError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    create_exception_from_response,
)


logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client for Sophos Central APIs.

    This client handles all HTTP communication with Sophos APIs, including:
    - Automatic authentication header injection
    - Retry logic with exponential backoff
    - Rate limit handling
    - Error response conversion to exceptions
    - Request/response logging

    Attributes:
        base_url: Base URL for API requests
        auth_provider: Authentication provider
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        rate_limit_retry: Whether to retry on rate limits
    """

    def __init__(
        self,
        base_url: str,
        auth_provider: AuthProvider,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_retry: bool = True,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: Base URL for API requests
            auth_provider: Authentication provider
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit_retry: Enable rate limit retries
        """
        self.base_url = base_url.rstrip("/")
        self.auth_provider = auth_provider
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_retry = rate_limit_retry
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HTTPClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client.

        Returns:
            AsyncClient instance
        """
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                ),
            )
        return self._client

    async def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON request body
            headers: Additional headers
            retry_count: Current retry attempt

        Returns:
            Response data as dictionary

        Raises:
            Various SophosAPIException subclasses based on error type
        """
        # Build full URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Get authorization header
        auth_headers = await self.auth_provider.get_authorization_header()

        # Merge headers
        request_headers = {**auth_headers}
        if headers:
            request_headers.update(headers)

        logger.debug(f"{method} {url}")
        if params:
            logger.debug(f"Params: {params}")

        client = self._get_client()

        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=request_headers,
            )

            # Handle different status codes
            if response.status_code in {200, 201}:
                # Successful response
                if response.text:
                    return response.json()
                return {}

            if response.status_code == 204:
                # No content
                return {}

            if response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(response.headers.get("Retry-After", 60))

                if self.rate_limit_retry and retry_count < self.max_retries:
                    logger.warning(
                        f"Rate limit exceeded, retrying after {retry_after}s"
                    )
                    await asyncio.sleep(retry_after)
                    return await self.request(
                        method,
                        endpoint,
                        params,
                        json,
                        headers,
                        retry_count + 1,
                    )

                msg = "Rate limit exceeded"
                raise RateLimitError(
                    msg,
                    retry_after=retry_after,
                    status_code=429,
                )

            # Error response - convert to exception
            error_data = None
            if response.text:
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"message": response.text}

            raise create_exception_from_response(response.status_code, error_data)

        except httpx.TimeoutException as e:
            if retry_count < self.max_retries:
                wait_time = 2**retry_count  # Exponential backoff
                logger.warning(f"Request timeout, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
                return await self.request(
                    method,
                    endpoint,
                    params,
                    json,
                    headers,
                    retry_count + 1,
                )
            msg = f"Request timed out after {self.timeout}s"
            raise TimeoutError(msg) from e

        except httpx.ConnectError as e:
            if retry_count < self.max_retries:
                wait_time = 2**retry_count
                logger.warning(f"Connection error, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
                return await self.request(
                    method,
                    endpoint,
                    params,
                    json,
                    headers,
                    retry_count + 1,
                )
            msg = f"Failed to connect to {url}"
            raise ConnectionError(msg) from e

        except httpx.HTTPError as e:
            msg = f"HTTP error occurred: {e}"
            raise NetworkError(msg) from e

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self.request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request.

        Args:
            endpoint: API endpoint path
            json: JSON request body
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self.request("POST", endpoint, json=json, headers=headers)

    async def patch(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a PATCH request.

        Args:
            endpoint: API endpoint path
            json: JSON request body
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self.request("PATCH", endpoint, json=json, headers=headers)

    async def delete(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a DELETE request.

        Args:
            endpoint: API endpoint path
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self.request("DELETE", endpoint, headers=headers)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
