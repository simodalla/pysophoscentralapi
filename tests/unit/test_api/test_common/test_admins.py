"""Tests for Admins API client."""

from unittest.mock import AsyncMock

import pytest

from pysophoscentralapi.api.common.admins import AdminsAPI
from pysophoscentralapi.api.common.models import Admin


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    return AsyncMock()


@pytest.fixture
def admins_api(mock_http_client):
    """Create Admins API instance."""
    return AdminsAPI(mock_http_client)


@pytest.fixture
def sample_admin_data():
    """Sample admin data."""
    return {
        "id": "admin-123",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "role": {"id": "role-123", "name": "Admin"},
        "tenants": [],
        "status": "active",
    }


class TestAdminsAPI:
    """Tests for AdminsAPI class."""

    @pytest.mark.asyncio
    async def test_list_admins(self, admins_api, mock_http_client, sample_admin_data):
        """Test listing admins."""
        mock_http_client.get.return_value = {"items": [sample_admin_data]}

        result = await admins_api.list_admins()

        assert len(result) == 1
        assert isinstance(result[0], Admin)
        assert result[0].id == "admin-123"
        assert result[0].first_name == "John"
        assert result[0].last_name == "Doe"

        mock_http_client.get.assert_called_once_with("/common/v1/admins")

    @pytest.mark.asyncio
    async def test_get_admin(self, admins_api, mock_http_client, sample_admin_data):
        """Test getting a specific admin."""
        mock_http_client.get.return_value = sample_admin_data

        result = await admins_api.get_admin("admin-123")

        assert isinstance(result, Admin)
        assert result.id == "admin-123"
        assert result.email == "john.doe@example.com"

        mock_http_client.get.assert_called_once_with("/common/v1/admins/admin-123")

    @pytest.mark.asyncio
    async def test_create_admin(self, admins_api, mock_http_client, sample_admin_data):
        """Test creating an admin."""
        mock_http_client.post.return_value = sample_admin_data

        result = await admins_api.create_admin(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            role_id="role-123",
            tenant_ids=["tenant-1"],
        )

        assert isinstance(result, Admin)
        assert result.first_name == "John"

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert "/common/v1/admins" in call_args[0][0]
        assert call_args[1]["json"]["firstName"] == "John"
        assert call_args[1]["json"]["email"] == "john.doe@example.com"

    @pytest.mark.asyncio
    async def test_update_admin(self, admins_api, mock_http_client, sample_admin_data):
        """Test updating an admin."""
        updated_data = sample_admin_data.copy()
        updated_data["firstName"] = "Jane"
        mock_http_client.patch.return_value = updated_data

        result = await admins_api.update_admin("admin-123", first_name="Jane")

        assert isinstance(result, Admin)
        assert result.first_name == "Jane"

        mock_http_client.patch.assert_called_once()
        call_args = mock_http_client.patch.call_args
        assert "/common/v1/admins/admin-123" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_delete_admin(self, admins_api, mock_http_client):
        """Test deleting an admin."""
        mock_http_client.delete.return_value = {"deleted": True}

        result = await admins_api.delete_admin("admin-123")

        assert result["deleted"] is True

        mock_http_client.delete.assert_called_once_with("/common/v1/admins/admin-123")
