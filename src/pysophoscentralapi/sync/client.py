"""Synchronous HTTP client wrapper.

This module provides a synchronous wrapper around the async HTTPClient.
"""

from typing import Any

from pysophoscentralapi.core.auth import OAuth2ClientCredentials
from pysophoscentralapi.core.client import HTTPClient
from pysophoscentralapi.sync.utils import run_async


class HTTPClientSync:
    """Synchronous HTTP client for Sophos Central APIs.

    This is a synchronous wrapper around the async HTTPClient. It uses
    asyncio.run() internally to execute async operations in a blocking manner.

    Attributes:
        base_url: Base URL for API requests
        auth: Authentication provider
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        _async_client: The underlying async HTTPClient instance

    Example:
        >>> from pysophoscentralapi.core.auth import OAuth2ClientCredentials
        >>> auth = OAuth2ClientCredentials(client_id="...", client_secret="...")
        >>> with HTTPClientSync("https://api.central.sophos.com", auth) as client:
        ...     response = client.get("/endpoint/v1/endpoints")
        ...     print(response)
    """

    def __init__(
        self,
        base_url: str,
        auth: OAuth2ClientCredentials,
        timeout: int = 30,
        max_retries: int = 3,
        tenant_id: str | None = None,
    ) -> None:
        """Initialize the synchronous HTTP client.

        Args:
            base_url: Base URL for API requests
            auth: Authentication provider
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            tenant_id: Optional tenant ID for regional endpoints
        """
        self.base_url = base_url
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        self.tenant_id = tenant_id
        self._async_client: HTTPClient | None = None

    def __enter__(self) -> "HTTPClientSync":
        """Context manager entry.

        Returns:
            Self for use in with statement
        """
        self._async_client = HTTPClient(
            base_url=self.base_url,
            auth_provider=self.auth,
            timeout=self.timeout,
            max_retries=self.max_retries,
            tenant_id=self.tenant_id,
        )

        async def async_enter():
            return await self._async_client.__aenter__()

        run_async(async_enter())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if self._async_client:

            async def async_exit():
                return await self._async_client.__aexit__(exc_type, exc_val, exc_tb)

            run_async(async_exit())
            self._async_client = None

    def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        """Perform a synchronous GET request.

        Args:
            path: Request path (relative to base URL)
            params: Optional query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        if not self._async_client:
            msg = "Client not initialized. Use within a context manager."
            raise RuntimeError(msg)

        return run_async(self._async_client.get(path, params))

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Perform a synchronous POST request.

        Args:
            path: Request path (relative to base URL)
            json: Optional JSON body
            params: Optional query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        if not self._async_client:
            msg = "Client not initialized. Use within a context manager."
            raise RuntimeError(msg)

        return run_async(self._async_client.post(path, json, params))

    def patch(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Perform a synchronous PATCH request.

        Args:
            path: Request path (relative to base URL)
            json: Optional JSON body
            params: Optional query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        if not self._async_client:
            msg = "Client not initialized. Use within a context manager."
            raise RuntimeError(msg)

        return run_async(self._async_client.patch(path, json, params))

    def delete(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Perform a synchronous DELETE request.

        Args:
            path: Request path (relative to base URL)
            params: Optional query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        if not self._async_client:
            msg = "Client not initialized. Use within a context manager."
            raise RuntimeError(msg)

        return run_async(self._async_client.delete(path, params))
