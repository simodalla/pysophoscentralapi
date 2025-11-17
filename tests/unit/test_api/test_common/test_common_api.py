"""Tests for CommonAPI aggregator."""

from unittest.mock import AsyncMock

import pytest

from pysophoscentralapi.api.common import CommonAPI
from pysophoscentralapi.api.common.admins import AdminsAPI
from pysophoscentralapi.api.common.alerts import AlertsAPI
from pysophoscentralapi.api.common.roles import RolesAPI
from pysophoscentralapi.api.common.tenants import TenantsAPI


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    return AsyncMock()


@pytest.fixture
def common_api(mock_http_client):
    """Create CommonAPI instance."""
    return CommonAPI(mock_http_client)


class TestCommonAPI:
    """Tests for CommonAPI aggregator class."""

    def test_initialization(self, common_api, mock_http_client):
        """Test CommonAPI initialization."""
        assert common_api.http_client is mock_http_client
        assert isinstance(common_api.alerts, AlertsAPI)
        assert isinstance(common_api.tenants, TenantsAPI)
        assert isinstance(common_api.admins, AdminsAPI)
        assert isinstance(common_api.roles, RolesAPI)

    def test_sub_clients_share_http_client(self, common_api, mock_http_client):
        """Test that all sub-clients share the same HTTP client."""
        assert common_api.alerts.http_client is mock_http_client
        assert common_api.tenants.http_client is mock_http_client
        assert common_api.admins.http_client is mock_http_client
        assert common_api.roles.http_client is mock_http_client
