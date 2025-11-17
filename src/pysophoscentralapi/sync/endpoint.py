"""Synchronous wrapper for Endpoint API.

This module provides synchronous wrappers for the Endpoint API.
"""

from typing import Any

from pysophoscentralapi.api.endpoint.endpoints import EndpointAPI
from pysophoscentralapi.api.endpoint.models import (
    Endpoint,
    EndpointFilters,
    IsolationResponse,
    ScanResponse,
    TamperProtectionStatus,
)
from pysophoscentralapi.core.models import PaginatedResponse
from pysophoscentralapi.sync.client import HTTPClientSync
from pysophoscentralapi.sync.pagination import PaginatorSync
from pysophoscentralapi.sync.utils import run_async


class EndpointAPISync:
    """Synchronous Endpoint API client.

    This is a synchronous wrapper around the async EndpointAPI.

    Attributes:
        _async_api: The underlying async EndpointAPI instance

    Example:
        >>> with HTTPClientSync(base_url, auth) as client:
        ...     endpoint_api = EndpointAPISync(client)
        ...     endpoints = endpoint_api.list_endpoints()
        ...     for endpoint in endpoints.items:
        ...         print(endpoint.hostname)
    """

    def __init__(self, http_client_sync: HTTPClientSync) -> None:
        """Initialize the synchronous Endpoint API client.

        Args:
            http_client_sync: Synchronous HTTP client
        """
        if not http_client_sync._async_client:
            msg = "HTTP client not initialized"
            raise RuntimeError(msg)

        self._async_api = EndpointAPI(http_client_sync._async_client)

    def list_endpoints(
        self,
        filters: EndpointFilters | None = None,
    ) -> PaginatedResponse[Endpoint]:
        """List endpoints with optional filtering.

        Args:
            filters: Optional filters to apply

        Returns:
            Paginated response containing endpoints
        """
        return run_async(self._async_api.list_endpoints(filters))

    def get_endpoint(self, endpoint_id: str) -> Endpoint:
        """Get a specific endpoint by ID.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Endpoint information
        """
        return run_async(self._async_api.get_endpoint(endpoint_id))

    def update_endpoint(
        self,
        endpoint_id: str,
        data: dict[str, Any],
    ) -> Endpoint:
        """Update an endpoint.

        Args:
            endpoint_id: The endpoint ID
            data: Update data

        Returns:
            Updated endpoint information
        """
        return run_async(self._async_api.update_endpoint(endpoint_id, data))

    def delete_endpoint(self, endpoint_id: str) -> dict[str, Any]:
        """Delete an endpoint.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Deletion confirmation
        """
        return run_async(self._async_api.delete_endpoint(endpoint_id))

    def paginate_endpoints(
        self,
        filters: EndpointFilters | None = None,
        max_pages: int | None = None,
    ) -> PaginatorSync[Endpoint]:
        """Create a paginator for endpoints.

        Args:
            filters: Optional filters to apply
            max_pages: Maximum number of pages to fetch

        Returns:
            Synchronous paginator for endpoints
        """
        async_paginator = self._async_api.paginate_endpoints(filters, max_pages)
        return PaginatorSync(async_paginator)

    def scan_endpoint(
        self,
        endpoint_id: str,
        enabled: bool = True,
    ) -> ScanResponse:
        """Start a scan on an endpoint.

        Args:
            endpoint_id: The endpoint ID
            enabled: Whether to enable scanning

        Returns:
            Scan response
        """
        return run_async(self._async_api.scan_endpoint(endpoint_id, enabled))

    def isolate_endpoint(
        self,
        endpoint_id: str,
        comment: str | None = None,
    ) -> IsolationResponse:
        """Isolate an endpoint from the network.

        Args:
            endpoint_id: The endpoint ID
            comment: Optional comment

        Returns:
            Isolation response
        """
        return run_async(self._async_api.isolate_endpoint(endpoint_id, comment))

    def unisolate_endpoint(
        self,
        endpoint_id: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """Remove isolation from an endpoint.

        Args:
            endpoint_id: The endpoint ID
            comment: Optional comment

        Returns:
            Unisolation confirmation
        """
        return run_async(self._async_api.unisolate_endpoint(endpoint_id, comment))

    def get_tamper_protection(
        self,
        endpoint_id: str,
    ) -> TamperProtectionStatus:
        """Get tamper protection status for an endpoint.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Tamper protection status
        """
        return run_async(self._async_api.get_tamper_protection(endpoint_id))

    def update_tamper_protection(
        self,
        endpoint_id: str,
        enabled: bool,
        regenerate_password: bool = False,
    ) -> TamperProtectionStatus:
        """Update tamper protection for an endpoint.

        Args:
            endpoint_id: The endpoint ID
            enabled: Whether to enable tamper protection
            regenerate_password: Whether to regenerate the password

        Returns:
            Updated tamper protection status
        """
        return run_async(
            self._async_api.update_tamper_protection(
                endpoint_id, enabled, regenerate_password
            )
        )

    def get_tamper_protection_password(
        self,
        endpoint_id: str,
    ) -> str:
        """Get the tamper protection password for an endpoint.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Tamper protection password
        """
        return run_async(self._async_api.get_tamper_protection_password(endpoint_id))
