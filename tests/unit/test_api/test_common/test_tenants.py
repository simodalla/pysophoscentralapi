"""Tests for Tenants API client."""

from unittest.mock import AsyncMock

import pytest

from pysophoscentralapi.api.common.models import Tenant, TenantFilters
from pysophoscentralapi.api.common.tenants import TenantsAPI
from pysophoscentralapi.core.models import PaginatedResponse


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    return AsyncMock()


@pytest.fixture
def tenants_api(mock_http_client):
    """Create Tenants API instance."""
    return TenantsAPI(mock_http_client)


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data."""
    return {
        "id": "tenant-123",
        "name": "Test Company",
        "dataRegion": "us",
        "apiHost": "https://api-us.central.sophos.com",
    }


@pytest.fixture
def sample_paginated_response(sample_tenant_data):
    """Sample paginated response."""
    return {
        "items": [sample_tenant_data],
        "pages": {"current": 1, "size": 1, "total": 1, "maxSize": 1000},
    }


class TestTenantsAPI:
    """Tests for TenantsAPI class."""

    @pytest.mark.asyncio
    async def test_list_tenants(
        self, tenants_api, mock_http_client, sample_paginated_response
    ):
        """Test listing tenants."""
        mock_http_client.get.return_value = sample_paginated_response

        result = await tenants_api.list_tenants()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Tenant)
        assert result.items[0].id == "tenant-123"
        assert result.items[0].name == "Test Company"

        mock_http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tenants_with_filters(
        self, tenants_api, mock_http_client, sample_paginated_response
    ):
        """Test listing tenants with filters."""
        mock_http_client.get.return_value = sample_paginated_response

        filters = TenantFilters(data_region="us", show_counts=True, page_size=50)
        result = await tenants_api.list_tenants(filters)

        assert len(result.items) == 1

        call_args = mock_http_client.get.call_args
        params = (
            call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("params")
        )
        assert params["dataRegion"] == "us"
        assert params["showCounts"] == "true"

    @pytest.mark.asyncio
    async def test_get_tenant(self, tenants_api, mock_http_client, sample_tenant_data):
        """Test getting a specific tenant."""
        mock_http_client.get.return_value = sample_tenant_data

        result = await tenants_api.get_tenant("tenant-123")

        assert isinstance(result, Tenant)
        assert result.id == "tenant-123"
        assert result.name == "Test Company"

        mock_http_client.get.assert_called_once_with("/common/v1/tenants/tenant-123")

    def test_paginate_tenants(self, tenants_api):
        """Test creating a paginator for tenants."""
        filters = TenantFilters(page_size=50)
        paginator = tenants_api.paginate_tenants(filters, max_pages=10)

        assert paginator is not None
        assert paginator.page_size == 50
        assert paginator.max_pages == 10
