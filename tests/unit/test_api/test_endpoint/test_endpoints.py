"""Tests for Endpoint API client."""

from unittest.mock import AsyncMock

import pytest

from pysophoscentralapi.api.endpoint.endpoints import EndpointAPI
from pysophoscentralapi.api.endpoint.models import (
    Endpoint,
    EndpointFilters,
    HealthStatus,
)
from pysophoscentralapi.core.models import PaginatedResponse


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    return AsyncMock()


@pytest.fixture
def endpoint_api(mock_http_client):
    """Create Endpoint API instance."""
    return EndpointAPI(mock_http_client)


@pytest.fixture
def sample_endpoint_data():
    """Sample endpoint data."""
    return {
        "id": "endpoint-123",
        "type": "computer",
        "tenant": {"id": "tenant-123"},
        "hostname": "DESKTOP-TEST",
        "health": {
            "overall": "good",
            "threats": {"status": "good"},
            "services": {"status": "good", "serviceDetails": []},
        },
        "os": {
            "isServer": False,
            "platform": "windows",
            "name": "Windows 10 Pro",
            "majorVersion": 10,
            "minorVersion": 0,
            "build": 19045,
        },
        "ipv4Addresses": ["192.168.1.100"],
        "ipv6Addresses": [],
        "macAddresses": ["00:11:22:33:44:55"],
        "tamperProtectionEnabled": True,
        "assignedProducts": [],
        "lastSeenAt": "2025-11-15T10:00:00.000Z",
    }


@pytest.fixture
def sample_paginated_response(sample_endpoint_data):
    """Sample paginated response."""
    return {
        "items": [sample_endpoint_data],
        "pages": {"current": 1, "size": 1, "total": 1, "maxSize": 1000},
    }


class TestEndpointAPI:
    """Tests for EndpointAPI class."""

    @pytest.mark.asyncio
    async def test_list_endpoints(
        self, endpoint_api, mock_http_client, sample_paginated_response
    ):
        """Test listing endpoints."""
        mock_http_client.get.return_value = sample_paginated_response

        result = await endpoint_api.list_endpoints()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Endpoint)
        assert result.items[0].id == "endpoint-123"
        assert result.items[0].hostname == "DESKTOP-TEST"

        mock_http_client.get.assert_called_once()
        call_args = mock_http_client.get.call_args
        assert "/endpoint/v1/endpoints" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_list_endpoints_with_filters(
        self, endpoint_api, mock_http_client, sample_paginated_response
    ):
        """Test listing endpoints with filters."""
        mock_http_client.get.return_value = sample_paginated_response

        filters = EndpointFilters(
            health_status=HealthStatus.GOOD,
            page_size=100,
            hostname_contains="DESKTOP",
        )
        result = await endpoint_api.list_endpoints(filters)

        assert len(result.items) == 1

        # Check that filters were passed
        call_args = mock_http_client.get.call_args
        # Parameters are passed as second positional argument
        params = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("params")
        assert params["healthStatus"] == "good"
        assert params["pageSize"] == "100"
        assert params["hostnameContains"] == "DESKTOP"

    @pytest.mark.asyncio
    async def test_get_endpoint(
        self, endpoint_api, mock_http_client, sample_endpoint_data
    ):
        """Test getting a specific endpoint."""
        mock_http_client.get.return_value = sample_endpoint_data

        result = await endpoint_api.get_endpoint("endpoint-123")

        assert isinstance(result, Endpoint)
        assert result.id == "endpoint-123"
        assert result.hostname == "DESKTOP-TEST"

        mock_http_client.get.assert_called_once_with(
            "/endpoint/v1/endpoints/endpoint-123"
        )

    @pytest.mark.asyncio
    async def test_update_endpoint(
        self, endpoint_api, mock_http_client, sample_endpoint_data
    ):
        """Test updating an endpoint."""
        mock_http_client.patch.return_value = sample_endpoint_data

        update_data = {"hostname": "NEW-HOSTNAME"}
        result = await endpoint_api.update_endpoint("endpoint-123", update_data)

        assert isinstance(result, Endpoint)

        mock_http_client.patch.assert_called_once()
        call_args = mock_http_client.patch.call_args
        assert "/endpoint/v1/endpoints/endpoint-123" in call_args[0][0]
        assert call_args[1]["json"] == update_data

    @pytest.mark.asyncio
    async def test_delete_endpoint(self, endpoint_api, mock_http_client):
        """Test deleting an endpoint."""
        mock_http_client.delete.return_value = {"deleted": True}

        result = await endpoint_api.delete_endpoint("endpoint-123")

        assert result["deleted"] is True

        mock_http_client.delete.assert_called_once_with(
            "/endpoint/v1/endpoints/endpoint-123"
        )

    @pytest.mark.asyncio
    async def test_scan_endpoint(self, endpoint_api, mock_http_client):
        """Test scanning an endpoint."""
        mock_http_client.post.return_value = {"id": "scan-123", "status": "requested"}

        result = await endpoint_api.scan_endpoint("endpoint-123")

        assert result.id == "scan-123"
        assert result.status == "requested"

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert "/endpoint/v1/endpoints/endpoint-123/scans" in call_args[0][0]
        assert call_args[1]["json"]["enabled"] is True

    @pytest.mark.asyncio
    async def test_isolate_endpoint(self, endpoint_api, mock_http_client):
        """Test isolating an endpoint."""
        mock_http_client.post.return_value = {
            "id": "isolation-123",
            "status": "requested",
        }

        result = await endpoint_api.isolate_endpoint(
            "endpoint-123", comment="Suspected malware"
        )

        assert result.id == "isolation-123"
        assert result.status == "requested"

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert "/endpoint/v1/endpoints/endpoint-123/isolation" in call_args[0][0]
        assert call_args[1]["json"]["comment"] == "Suspected malware"

    @pytest.mark.asyncio
    async def test_unisolate_endpoint(self, endpoint_api, mock_http_client):
        """Test removing isolation from an endpoint."""
        mock_http_client.delete.return_value = {"status": "unisolated"}

        result = await endpoint_api.unisolate_endpoint(
            "endpoint-123", comment="Threat remediated"
        )

        assert result["status"] == "unisolated"

        mock_http_client.delete.assert_called_once_with(
            "/endpoint/v1/endpoints/endpoint-123/isolation"
        )

    @pytest.mark.asyncio
    async def test_get_tamper_protection(self, endpoint_api, mock_http_client):
        """Test getting tamper protection status."""
        mock_http_client.get.return_value = {
            "enabled": True,
            "globallyEnabled": True,
            "previouslyEnabled": False,
        }

        result = await endpoint_api.get_tamper_protection("endpoint-123")

        assert result.enabled is True
        assert result.globally_enabled is True

        mock_http_client.get.assert_called_once_with(
            "/endpoint/v1/endpoints/endpoint-123/tamper-protection"
        )

    @pytest.mark.asyncio
    async def test_update_tamper_protection(self, endpoint_api, mock_http_client):
        """Test updating tamper protection."""
        mock_http_client.post.return_value = {
            "enabled": True,
            "globallyEnabled": True,
        }

        result = await endpoint_api.update_tamper_protection(
            "endpoint-123", enabled=True, regenerate_password=True
        )

        assert result.enabled is True

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert (
            "/endpoint/v1/endpoints/endpoint-123/tamper-protection" in call_args[0][0]
        )
        assert call_args[1]["json"]["enabled"] is True
        assert call_args[1]["json"]["regeneratePassword"] is True

    @pytest.mark.asyncio
    async def test_get_tamper_protection_password(self, endpoint_api, mock_http_client):
        """Test getting tamper protection password."""
        mock_http_client.get.return_value = {"password": "test-password-123"}

        result = await endpoint_api.get_tamper_protection_password("endpoint-123")

        assert result == "test-password-123"

        mock_http_client.get.assert_called_once_with(
            "/endpoint/v1/endpoints/endpoint-123/tamper-protection/password"
        )

    def test_paginate_endpoints(self, endpoint_api):
        """Test creating a paginator."""
        filters = EndpointFilters(page_size=100)
        paginator = endpoint_api.paginate_endpoints(filters, max_pages=5)

        assert paginator is not None
        assert paginator.page_size == 100
        assert paginator.max_pages == 5
