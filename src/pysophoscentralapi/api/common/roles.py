"""Sophos Central Roles API client.

This module provides the RolesAPI class for managing roles and permissions.
"""

from typing import Any

from pysophoscentralapi.api.common.models import (
    Role,
    RoleCreateRequest,
    RoleUpdateRequest,
)
from pysophoscentralapi.core.client import HTTPClient


class RolesAPI:
    """Sophos Central Roles API client.

    Provides methods for managing roles including CRUD operations.

    Attributes:
        http_client: HTTP client for making API requests
        base_path: Base URL path for roles API

    Example:
        >>> async with HTTPClient(base_url, auth) as client:
        ...     roles_api = RolesAPI(client)
        ...     roles = await roles_api.list_roles()
        ...     for role in roles:
        ...         print(f"{role.name}: {role.description}")
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the Roles API client.

        Args:
            http_client: HTTP client for API requests
        """
        self.http_client = http_client
        self.base_path = "/common/v1"

    async def list_roles(self) -> list[Role]:
        """List all roles.

        Returns:
            List of roles

        Raises:
            APIError: If API returns an error

        Example:
            >>> roles = await api.list_roles()
            >>> for role in roles:
            ...     print(f"{role.name}: {len(role.permissions)} permissions")
        """
        response = await self.http_client.get(f"{self.base_path}/roles")
        items = response.get("items", [])
        return [Role(**item) for item in items]

    async def get_role(self, role_id: str) -> Role:
        """Get a specific role by ID.

        Args:
            role_id: The role ID

        Returns:
            Role information

        Raises:
            ResourceNotFoundError: If role not found
            APIError: If API returns an error

        Example:
            >>> role = await api.get_role("role-123")
            >>> print(f"{role.name}: {role.description}")
        """
        response = await self.http_client.get(f"{self.base_path}/roles/{role_id}")
        return Role(**response)

    async def create_role(
        self,
        name: str,
        description: str | None = None,
        permissions: list[dict[str, Any]] | None = None,
    ) -> Role:
        """Create a new role.

        Args:
            name: Role name
            description: Role description
            permissions: List of permission dictionaries

        Returns:
            Created role

        Raises:
            ValidationError: If data is invalid
            APIError: If API returns an error

        Example:
            >>> from pysophoscentralapi.api.common.models import Permission
            >>> role = await api.create_role(
            ...     name="Custom Role",
            ...     description="Custom admin role",
            ...     permissions=[
            ...         Permission(scope="tenant", actions=["read"]).model_dump()
            ...     ]
            ... )
        """
        request = RoleCreateRequest(
            name=name,
            description=description,
            permissions=permissions or [],
        )
        response = await self.http_client.post(
            f"{self.base_path}/roles",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Role(**response)

    async def update_role(
        self,
        role_id: str,
        name: str | None = None,
        description: str | None = None,
        permissions: list[dict[str, Any]] | None = None,
    ) -> Role:
        """Update a role.

        Args:
            role_id: The role ID
            name: New role name
            description: New role description
            permissions: New list of permissions

        Returns:
            Updated role

        Raises:
            ValidationError: If data is invalid
            ResourceNotFoundError: If role not found
            APIError: If API returns an error

        Example:
            >>> role = await api.update_role(
            ...     "role-123",
            ...     description="Updated description"
            ... )
        """
        request = RoleUpdateRequest(
            name=name,
            description=description,
            permissions=permissions,
        )
        response = await self.http_client.patch(
            f"{self.base_path}/roles/{role_id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Role(**response)

    async def delete_role(self, role_id: str) -> dict[str, Any]:
        """Delete a role.

        Args:
            role_id: The role ID

        Returns:
            Deletion confirmation

        Raises:
            ResourceNotFoundError: If role not found
            APIError: If API returns an error

        Example:
            >>> result = await api.delete_role("role-123")
        """
        return await self.http_client.delete(f"{self.base_path}/roles/{role_id}")
