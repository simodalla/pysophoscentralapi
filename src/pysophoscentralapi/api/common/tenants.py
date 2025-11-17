"""Sophos Central Tenants API client.

This module provides the TenantsAPI class for managing tenants.
"""

from pysophoscentralapi.api.common.models import Tenant, TenantFilters
from pysophoscentralapi.core.client import HTTPClient
from pysophoscentralapi.core.models import PaginatedResponse
from pysophoscentralapi.core.pagination import Paginator, create_paginator


class TenantsAPI:
    """Sophos Central Tenants API client.

    Provides methods for listing and retrieving tenant information.

    Attributes:
        http_client: HTTP client for making API requests
        base_path: Base URL path for tenants API

    Example:
        >>> async with HTTPClient(base_url, auth) as client:
        ...     tenants_api = TenantsAPI(client)
        ...     tenants = await tenants_api.list_tenants()
        ...     for tenant in tenants.items:
        ...         print(f"{tenant.name} ({tenant.data_region})")
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the Tenants API client.

        Args:
            http_client: HTTP client for API requests
        """
        self.http_client = http_client
        self.base_path = "/common/v1"

    async def list_tenants(
        self,
        filters: TenantFilters | None = None,
    ) -> PaginatedResponse[Tenant]:
        """List tenants with optional filtering.

        Args:
            filters: Optional filters to apply to the listing

        Returns:
            Paginated response containing tenants

        Raises:
            APIError: If API returns an error

        Example:
            >>> filters = TenantFilters(data_region="us", show_counts=True)
            >>> result = await api.list_tenants(filters)
            >>> print(f"Found {len(result.items)} tenants")
        """
        if filters is None:
            filters = TenantFilters()

        params = filters.to_params()
        response = await self.http_client.get(f"{self.base_path}/tenants", params)

        items = [Tenant(**item) for item in response.get("items", [])]

        return PaginatedResponse[Tenant](
            items=items,
            pages=response["pages"],
        )

    async def get_tenant(self, tenant_id: str) -> Tenant:
        """Get a specific tenant by ID.

        Args:
            tenant_id: The tenant ID

        Returns:
            Tenant information

        Raises:
            ResourceNotFoundError: If tenant not found
            APIError: If API returns an error

        Example:
            >>> tenant = await api.get_tenant("tenant-123")
            >>> print(f"{tenant.name} in {tenant.data_region}")
        """
        response = await self.http_client.get(f"{self.base_path}/tenants/{tenant_id}")
        return Tenant(**response)

    def paginate_tenants(
        self,
        filters: TenantFilters | None = None,
        max_pages: int | None = None,
    ) -> Paginator[Tenant]:
        """Create a paginator for tenants.

        Args:
            filters: Optional filters to apply
            max_pages: Maximum number of pages to fetch

        Returns:
            Paginator instance for iterating through tenants

        Example:
            >>> paginator = api.paginate_tenants()
            >>> async for tenant in paginator.iter_items():
            ...     print(tenant.name)
        """
        if filters is None:
            filters = TenantFilters()

        async def fetch_page(page_key: str | None) -> PaginatedResponse[Tenant]:
            if page_key:
                filters.page_from_key = page_key
            return await self.list_tenants(filters)

        return create_paginator(
            fetch_page,
            page_size=filters.page_size,
            max_pages=max_pages,
        )
