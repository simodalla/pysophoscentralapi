"""Tests for Roles API client."""

from unittest.mock import AsyncMock

import pytest

from pysophoscentralapi.api.common.models import Role
from pysophoscentralapi.api.common.roles import RolesAPI


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    return AsyncMock()


@pytest.fixture
def roles_api(mock_http_client):
    """Create Roles API instance."""
    return RolesAPI(mock_http_client)


@pytest.fixture
def sample_role_data():
    """Sample role data."""
    return {
        "id": "role-123",
        "name": "Admin",
        "description": "Administrator role",
        "permissions": [{"scope": "tenant", "actions": ["read", "write"]}],
        "builtin": True,
    }


class TestRolesAPI:
    """Tests for RolesAPI class."""

    @pytest.mark.asyncio
    async def test_list_roles(self, roles_api, mock_http_client, sample_role_data):
        """Test listing roles."""
        mock_http_client.get.return_value = {"items": [sample_role_data]}

        result = await roles_api.list_roles()

        assert len(result) == 1
        assert isinstance(result[0], Role)
        assert result[0].id == "role-123"
        assert result[0].name == "Admin"
        assert len(result[0].permissions) == 1

        mock_http_client.get.assert_called_once_with("/common/v1/roles")

    @pytest.mark.asyncio
    async def test_get_role(self, roles_api, mock_http_client, sample_role_data):
        """Test getting a specific role."""
        mock_http_client.get.return_value = sample_role_data

        result = await roles_api.get_role("role-123")

        assert isinstance(result, Role)
        assert result.id == "role-123"
        assert result.name == "Admin"

        mock_http_client.get.assert_called_once_with("/common/v1/roles/role-123")

    @pytest.mark.asyncio
    async def test_create_role(self, roles_api, mock_http_client, sample_role_data):
        """Test creating a role."""
        mock_http_client.post.return_value = sample_role_data

        result = await roles_api.create_role(
            name="Custom Role",
            description="Custom admin role",
            permissions=[{"scope": "alert", "actions": ["read"]}],
        )

        assert isinstance(result, Role)
        assert result.name == "Admin"  # From mock response

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert "/common/v1/roles" in call_args[0][0]
        assert call_args[1]["json"]["name"] == "Custom Role"

    @pytest.mark.asyncio
    async def test_update_role(self, roles_api, mock_http_client, sample_role_data):
        """Test updating a role."""
        updated_data = sample_role_data.copy()
        updated_data["description"] = "Updated description"
        mock_http_client.patch.return_value = updated_data

        result = await roles_api.update_role(
            "role-123", description="Updated description"
        )

        assert isinstance(result, Role)
        assert result.description == "Updated description"

        mock_http_client.patch.assert_called_once()
        call_args = mock_http_client.patch.call_args
        assert "/common/v1/roles/role-123" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_delete_role(self, roles_api, mock_http_client):
        """Test deleting a role."""
        mock_http_client.delete.return_value = {"deleted": True}

        result = await roles_api.delete_role("role-123")

        assert result["deleted"] is True

        mock_http_client.delete.assert_called_once_with("/common/v1/roles/role-123")
