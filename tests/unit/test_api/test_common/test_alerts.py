"""Tests for Alerts API client."""

from unittest.mock import AsyncMock

import pytest

from pysophoscentralapi.api.common.alerts import AlertsAPI
from pysophoscentralapi.api.common.models import Alert, AlertFilters, AlertSeverity
from pysophoscentralapi.core.models import PaginatedResponse


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    return AsyncMock()


@pytest.fixture
def alerts_api(mock_http_client):
    """Create Alerts API instance."""
    return AlertsAPI(mock_http_client)


@pytest.fixture
def sample_alert_data():
    """Sample alert data."""
    return {
        "id": "alert-123",
        "allowedActions": ["acknowledge"],
        "category": "malware",
        "description": "Malware detected",
        "groupKey": "group-123",
        "product": "endpoint",
        "raisedAt": "2025-11-15T10:00:00.000Z",
        "severity": "high",
        "tenant": {"id": "tenant-123"},
        "type": "Event::Endpoint::Threat::Detected",
    }


@pytest.fixture
def sample_paginated_response(sample_alert_data):
    """Sample paginated response."""
    return {
        "items": [sample_alert_data],
        "pages": {"current": 1, "size": 1, "total": 1, "maxSize": 1000},
    }


class TestAlertsAPI:
    """Tests for AlertsAPI class."""

    @pytest.mark.asyncio
    async def test_list_alerts(
        self, alerts_api, mock_http_client, sample_paginated_response
    ):
        """Test listing alerts."""
        mock_http_client.get.return_value = sample_paginated_response

        result = await alerts_api.list_alerts()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Alert)
        assert result.items[0].id == "alert-123"
        assert result.items[0].severity == AlertSeverity.HIGH

        mock_http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_alerts_with_filters(
        self, alerts_api, mock_http_client, sample_paginated_response
    ):
        """Test listing alerts with filters."""
        mock_http_client.get.return_value = sample_paginated_response

        filters = AlertFilters(
            severity=["high", "critical"],
            product=["endpoint"],
            page_size=100,
        )
        result = await alerts_api.list_alerts(filters)

        assert len(result.items) == 1

        call_args = mock_http_client.get.call_args
        params = (
            call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("params")
        )
        assert params["pageSize"] == "100"
        assert params["severity"] == "high,critical"
        assert params["product"] == "endpoint"

    @pytest.mark.asyncio
    async def test_get_alert(self, alerts_api, mock_http_client, sample_alert_data):
        """Test getting a specific alert."""
        mock_http_client.get.return_value = sample_alert_data

        result = await alerts_api.get_alert("alert-123")

        assert isinstance(result, Alert)
        assert result.id == "alert-123"
        assert result.severity == AlertSeverity.HIGH

        mock_http_client.get.assert_called_once_with("/common/v1/alerts/alert-123")

    @pytest.mark.asyncio
    async def test_perform_action(self, alerts_api, mock_http_client):
        """Test performing an action on an alert."""
        mock_http_client.post.return_value = {"result": "success"}

        result = await alerts_api.perform_action(
            "alert-123", "acknowledge", message="Investigating"
        )

        assert result["result"] == "success"

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert "/common/v1/alerts/alert-123/actions" in call_args[0][0]
        assert call_args[1]["json"]["action"] == "acknowledge"
        assert call_args[1]["json"]["message"] == "Investigating"

    def test_paginate_alerts(self, alerts_api):
        """Test creating a paginator for alerts."""
        filters = AlertFilters(page_size=100)
        paginator = alerts_api.paginate_alerts(filters, max_pages=5)

        assert paginator is not None
        assert paginator.page_size == 100
        assert paginator.max_pages == 5
