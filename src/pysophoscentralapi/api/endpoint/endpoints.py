"""Sophos Central Endpoint API client.

This module provides the EndpointAPI class for managing endpoints including
listing, filtering, actions (scan, isolate), and tamper protection operations.
"""

from typing import Any

from pysophoscentralapi.api.endpoint.models import (
    Endpoint,
    EndpointFilters,
    IsolationRequest,
    IsolationResponse,
    ScanRequest,
    ScanResponse,
    TamperProtectionPassword,
    TamperProtectionStatus,
    TamperProtectionUpdate,
)
from pysophoscentralapi.core.client import HTTPClient
from pysophoscentralapi.core.models import PaginatedResponse
from pysophoscentralapi.core.pagination import Paginator, create_paginator


class EndpointAPI:
    """Sophos Central Endpoint API client.

    Provides methods for managing endpoints including listing, scanning,
    isolation, and tamper protection operations.

    Attributes:
        http_client: HTTP client for making API requests
        base_path: Base URL path for endpoint API

    Example:
        >>> async with HTTPClient(base_url, auth) as client:
        ...     endpoint_api = EndpointAPI(client)
        ...     endpoints = await endpoint_api.list_endpoints()
        ...     for endpoint in endpoints.items:
        ...         print(f"{endpoint.hostname}: {endpoint.health.overall}")
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the Endpoint API client.

        Args:
            http_client: HTTP client for API requests
        """
        self.http_client = http_client
        self.base_path = "/endpoint/v1"

    async def list_endpoints(
        self,
        filters: EndpointFilters | None = None,
    ) -> PaginatedResponse[Endpoint]:
        """List endpoints with optional filtering.

        Args:
            filters: Optional filters to apply to the listing

        Returns:
            Paginated response containing endpoints

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API returns an error

        Example:
            >>> filters = EndpointFilters(
            ...     health_status=HealthStatus.GOOD,
            ...     page_size=100
            ... )
            >>> result = await api.list_endpoints(filters)
            >>> print(f"Found {len(result.items)} endpoints")
        """
        if filters is None:
            filters = EndpointFilters()

        params = filters.to_params()
        response = await self.http_client.get(f"{self.base_path}/endpoints", params)

        # Parse items as Endpoint models
        items = [Endpoint(**item) for item in response.get("items", [])]

        return PaginatedResponse[Endpoint](
            items=items,
            pages=response["pages"],
        )

    async def get_endpoint(self, endpoint_id: str) -> Endpoint:
        """Get a specific endpoint by ID.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Endpoint information

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> endpoint = await api.get_endpoint("abc-123")
            >>> print(endpoint.hostname)
        """
        response = await self.http_client.get(
            f"{self.base_path}/endpoints/{endpoint_id}"
        )
        return Endpoint(**response)

    async def update_endpoint(
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

        Raises:
            ValidationError: If data is invalid
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> endpoint = await api.update_endpoint(
            ...     "abc-123",
            ...     {"hostname": "new-hostname"}
            ... )
        """
        response = await self.http_client.patch(
            f"{self.base_path}/endpoints/{endpoint_id}",
            json=data,
        )
        return Endpoint(**response)

    async def delete_endpoint(self, endpoint_id: str) -> dict[str, Any]:
        """Delete an endpoint.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Deletion confirmation

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> result = await api.delete_endpoint("abc-123")
        """
        return await self.http_client.delete(
            f"{self.base_path}/endpoints/{endpoint_id}"
        )

    def paginate_endpoints(
        self,
        filters: EndpointFilters | None = None,
        max_pages: int | None = None,
    ) -> Paginator[Endpoint]:
        """Create a paginator for endpoints.

        This allows iterating through all endpoints across multiple pages.

        Args:
            filters: Optional filters to apply
            max_pages: Maximum number of pages to fetch

        Returns:
            Paginator instance for iterating through endpoints

        Example:
            >>> paginator = api.paginate_endpoints(
            ...     filters=EndpointFilters(page_size=100)
            ... )
            >>> async for endpoint in paginator.iter_items():
            ...     print(endpoint.hostname)
        """
        if filters is None:
            filters = EndpointFilters()

        async def fetch_page(
            page_key: str | None,
        ) -> PaginatedResponse[Endpoint]:
            if page_key:
                filters.page_from_key = page_key
            return await self.list_endpoints(filters)

        return create_paginator(
            fetch_page,
            page_size=filters.page_size,
            max_pages=max_pages,
        )

    # Endpoint Actions

    async def scan_endpoint(
        self,
        endpoint_id: str,
        enabled: bool = True,
    ) -> ScanResponse:
        """Start a scan on an endpoint.

        Args:
            endpoint_id: The endpoint ID
            enabled: Whether to enable scanning (default: True)

        Returns:
            Scan response with job ID and status

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> scan = await api.scan_endpoint("abc-123")
            >>> print(f"Scan {scan.id}: {scan.status}")
        """
        request = ScanRequest(enabled=enabled)
        response = await self.http_client.post(
            f"{self.base_path}/endpoints/{endpoint_id}/scans",
            json=request.model_dump(by_alias=True),
        )
        return ScanResponse(**response)

    async def isolate_endpoint(
        self,
        endpoint_id: str,
        comment: str | None = None,
    ) -> IsolationResponse:
        """Isolate an endpoint from the network.

        Args:
            endpoint_id: The endpoint ID
            comment: Optional comment explaining the isolation

        Returns:
            Isolation response with job ID and status

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> isolation = await api.isolate_endpoint(
            ...     "abc-123",
            ...     comment="Suspected malware"
            ... )
            >>> print(f"Isolation {isolation.id}: {isolation.status}")
        """
        request = IsolationRequest(enabled=True, comment=comment)
        response = await self.http_client.post(
            f"{self.base_path}/endpoints/{endpoint_id}/isolation",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return IsolationResponse(**response)

    async def unisolate_endpoint(
        self,
        endpoint_id: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """Remove isolation from an endpoint.

        Args:
            endpoint_id: The endpoint ID
            comment: Optional comment explaining the unisolation

        Returns:
            Unisolation confirmation

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> result = await api.unisolate_endpoint(
            ...     "abc-123",
            ...     comment="Threat remediated"
            ... )
        """
        data = {}
        if comment:
            data["comment"] = comment

        return await self.http_client.delete(
            f"{self.base_path}/endpoints/{endpoint_id}/isolation"
        )

    # Tamper Protection

    async def get_tamper_protection(
        self,
        endpoint_id: str,
    ) -> TamperProtectionStatus:
        """Get tamper protection status for an endpoint.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Tamper protection status

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> status = await api.get_tamper_protection("abc-123")
            >>> print(f"Tamper protection: {status.enabled}")
        """
        response = await self.http_client.get(
            f"{self.base_path}/endpoints/{endpoint_id}/tamper-protection"
        )
        return TamperProtectionStatus(**response)

    async def update_tamper_protection(
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

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> status = await api.update_tamper_protection(
            ...     "abc-123",
            ...     enabled=True,
            ...     regenerate_password=True
            ... )
        """
        request = TamperProtectionUpdate(
            enabled=enabled,
            regenerate_password=regenerate_password,
        )
        response = await self.http_client.post(
            f"{self.base_path}/endpoints/{endpoint_id}/tamper-protection",
            json=request.model_dump(by_alias=True),
        )
        return TamperProtectionStatus(**response)

    async def get_tamper_protection_password(
        self,
        endpoint_id: str,
    ) -> str:
        """Get the tamper protection password for an endpoint.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Tamper protection password

        Raises:
            ResourceNotFoundError: If endpoint not found
            APIError: If API returns an error

        Example:
            >>> password = await api.get_tamper_protection_password("abc-123")
            >>> print(f"Password: {password}")
        """
        response = await self.http_client.get(
            f"{self.base_path}/endpoints/{endpoint_id}/tamper-protection/password"
        )
        return TamperProtectionPassword(**response).password
