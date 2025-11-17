"""Sophos Central Admins API client.

This module provides the AdminsAPI class for managing administrators.
"""

from typing import Any

from pysophoscentralapi.api.common.models import (
    Admin,
    AdminCreateRequest,
    AdminUpdateRequest,
)
from pysophoscentralapi.core.client import HTTPClient


class AdminsAPI:
    """Sophos Central Admins API client.

    Provides methods for managing administrators including CRUD operations.

    Attributes:
        http_client: HTTP client for making API requests
        base_path: Base URL path for admins API

    Example:
        >>> async with HTTPClient(base_url, auth) as client:
        ...     admins_api = AdminsAPI(client)
        ...     admins = await admins_api.list_admins()
        ...     for admin in admins:
        ...         print(f"{admin.first_name} {admin.last_name}")
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the Admins API client.

        Args:
            http_client: HTTP client for API requests
        """
        self.http_client = http_client
        self.base_path = "/common/v1"

    async def list_admins(self) -> list[Admin]:
        """List all admins.

        Returns:
            List of admins

        Raises:
            APIError: If API returns an error

        Example:
            >>> admins = await api.list_admins()
            >>> for admin in admins:
            ...     print(f"{admin.email}: {admin.role.name if admin.role else 'No role'}")
        """
        response = await self.http_client.get(f"{self.base_path}/admins")
        items = response.get("items", [])
        return [Admin(**item) for item in items]

    async def get_admin(self, admin_id: str) -> Admin:
        """Get a specific admin by ID.

        Args:
            admin_id: The admin ID

        Returns:
            Admin information

        Raises:
            ResourceNotFoundError: If admin not found
            APIError: If API returns an error

        Example:
            >>> admin = await api.get_admin("admin-123")
            >>> print(f"{admin.first_name} {admin.last_name}")
        """
        response = await self.http_client.get(f"{self.base_path}/admins/{admin_id}")
        return Admin(**response)

    async def create_admin(
        self,
        first_name: str,
        last_name: str,
        email: str,
        role_id: str,
        tenant_ids: list[str] | None = None,
    ) -> Admin:
        """Create a new admin.

        Args:
            first_name: Admin's first name
            last_name: Admin's last name
            email: Admin's email address
            role_id: Role ID to assign
            tenant_ids: List of tenant IDs the admin can access

        Returns:
            Created admin

        Raises:
            ValidationError: If data is invalid
            APIError: If API returns an error

        Example:
            >>> admin = await api.create_admin(
            ...     first_name="John",
            ...     last_name="Doe",
            ...     email="john.doe@example.com",
            ...     role_id="role-123",
            ...     tenant_ids=["tenant-1", "tenant-2"]
            ... )
        """
        request = AdminCreateRequest(
            firstName=first_name,
            lastName=last_name,
            email=email,
            roleId=role_id,
            tenantIds=tenant_ids or [],
        )
        response = await self.http_client.post(
            f"{self.base_path}/admins",
            json=request.model_dump(by_alias=True),
        )
        return Admin(**response)

    async def update_admin(
        self,
        admin_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        role_id: str | None = None,
        tenant_ids: list[str] | None = None,
    ) -> Admin:
        """Update an admin.

        Args:
            admin_id: The admin ID
            first_name: New first name
            last_name: New last name
            email: New email address
            role_id: New role ID
            tenant_ids: New list of tenant IDs

        Returns:
            Updated admin

        Raises:
            ValidationError: If data is invalid
            ResourceNotFoundError: If admin not found
            APIError: If API returns an error

        Example:
            >>> admin = await api.update_admin(
            ...     "admin-123",
            ...     role_id="new-role-id"
            ... )
        """
        request = AdminUpdateRequest(
            firstName=first_name,
            lastName=last_name,
            email=email,
            roleId=role_id,
            tenantIds=tenant_ids,
        )
        response = await self.http_client.patch(
            f"{self.base_path}/admins/{admin_id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Admin(**response)

    async def delete_admin(self, admin_id: str) -> dict[str, Any]:
        """Delete an admin.

        Args:
            admin_id: The admin ID

        Returns:
            Deletion confirmation

        Raises:
            ResourceNotFoundError: If admin not found
            APIError: If API returns an error

        Example:
            >>> result = await api.delete_admin("admin-123")
        """
        return await self.http_client.delete(f"{self.base_path}/admins/{admin_id}")
