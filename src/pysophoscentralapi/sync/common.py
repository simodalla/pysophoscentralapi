"""Synchronous wrappers for Common API.

This module provides synchronous wrappers for all Common API clients.
"""

from typing import Any

from pysophoscentralapi.api.common.admins import AdminsAPI
from pysophoscentralapi.api.common.alerts import AlertsAPI
from pysophoscentralapi.api.common.models import (
    Admin,
    Alert,
    AlertFilters,
    Role,
    Tenant,
    TenantFilters,
)
from pysophoscentralapi.api.common.roles import RolesAPI
from pysophoscentralapi.api.common.tenants import TenantsAPI
from pysophoscentralapi.core.models import PaginatedResponse
from pysophoscentralapi.sync.client import HTTPClientSync
from pysophoscentralapi.sync.pagination import PaginatorSync
from pysophoscentralapi.sync.utils import run_async


class AlertsAPISync:
    """Synchronous Alerts API client."""

    def __init__(self, http_client_sync: HTTPClientSync) -> None:
        """Initialize the synchronous Alerts API client."""
        if not http_client_sync._async_client:
            msg = "HTTP client not initialized"
            raise RuntimeError(msg)

        self._async_api = AlertsAPI(http_client_sync._async_client)

    def list_alerts(
        self,
        filters: AlertFilters | None = None,
    ) -> PaginatedResponse[Alert]:
        """List alerts with optional filtering."""
        return run_async(self._async_api.list_alerts(filters))

    def get_alert(self, alert_id: str) -> Alert:
        """Get a specific alert by ID."""
        return run_async(self._async_api.get_alert(alert_id))

    def perform_action(
        self,
        alert_id: str,
        action: str,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Perform an action on an alert."""
        return run_async(self._async_api.perform_action(alert_id, action, message))

    def paginate_alerts(
        self,
        filters: AlertFilters | None = None,
        max_pages: int | None = None,
    ) -> PaginatorSync[Alert]:
        """Create a paginator for alerts."""
        async_paginator = self._async_api.paginate_alerts(filters, max_pages)
        return PaginatorSync(async_paginator)


class TenantsAPISync:
    """Synchronous Tenants API client."""

    def __init__(self, http_client_sync: HTTPClientSync) -> None:
        """Initialize the synchronous Tenants API client."""
        if not http_client_sync._async_client:
            msg = "HTTP client not initialized"
            raise RuntimeError(msg)

        self._async_api = TenantsAPI(http_client_sync._async_client)

    def list_tenants(
        self,
        filters: TenantFilters | None = None,
    ) -> PaginatedResponse[Tenant]:
        """List tenants with optional filtering."""
        return run_async(self._async_api.list_tenants(filters))

    def get_tenant(self, tenant_id: str) -> Tenant:
        """Get a specific tenant by ID."""
        return run_async(self._async_api.get_tenant(tenant_id))

    def paginate_tenants(
        self,
        filters: TenantFilters | None = None,
        max_pages: int | None = None,
    ) -> PaginatorSync[Tenant]:
        """Create a paginator for tenants."""
        async_paginator = self._async_api.paginate_tenants(filters, max_pages)
        return PaginatorSync(async_paginator)


class AdminsAPISync:
    """Synchronous Admins API client."""

    def __init__(self, http_client_sync: HTTPClientSync) -> None:
        """Initialize the synchronous Admins API client."""
        if not http_client_sync._async_client:
            msg = "HTTP client not initialized"
            raise RuntimeError(msg)

        self._async_api = AdminsAPI(http_client_sync._async_client)

    def list_admins(self) -> list[Admin]:
        """List all admins."""
        return run_async(self._async_api.list_admins())

    def get_admin(self, admin_id: str) -> Admin:
        """Get a specific admin by ID."""
        return run_async(self._async_api.get_admin(admin_id))

    def create_admin(
        self,
        first_name: str,
        last_name: str,
        email: str,
        role_id: str,
        tenant_ids: list[str] | None = None,
    ) -> Admin:
        """Create a new admin."""
        return run_async(
            self._async_api.create_admin(
                first_name, last_name, email, role_id, tenant_ids
            )
        )

    def update_admin(
        self,
        admin_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        role_id: str | None = None,
        tenant_ids: list[str] | None = None,
    ) -> Admin:
        """Update an admin."""
        return run_async(
            self._async_api.update_admin(
                admin_id, first_name, last_name, email, role_id, tenant_ids
            )
        )

    def delete_admin(self, admin_id: str) -> dict[str, Any]:
        """Delete an admin."""
        return run_async(self._async_api.delete_admin(admin_id))


class RolesAPISync:
    """Synchronous Roles API client."""

    def __init__(self, http_client_sync: HTTPClientSync) -> None:
        """Initialize the synchronous Roles API client."""
        if not http_client_sync._async_client:
            msg = "HTTP client not initialized"
            raise RuntimeError(msg)

        self._async_api = RolesAPI(http_client_sync._async_client)

    def list_roles(self) -> list[Role]:
        """List all roles."""
        return run_async(self._async_api.list_roles())

    def get_role(self, role_id: str) -> Role:
        """Get a specific role by ID."""
        return run_async(self._async_api.get_role(role_id))

    def create_role(
        self,
        name: str,
        description: str | None = None,
        permissions: list[dict[str, Any]] | None = None,
    ) -> Role:
        """Create a new role."""
        return run_async(self._async_api.create_role(name, description, permissions))

    def update_role(
        self,
        role_id: str,
        name: str | None = None,
        description: str | None = None,
        permissions: list[dict[str, Any]] | None = None,
    ) -> Role:
        """Update a role."""
        return run_async(
            self._async_api.update_role(role_id, name, description, permissions)
        )

    def delete_role(self, role_id: str) -> dict[str, Any]:
        """Delete a role."""
        return run_async(self._async_api.delete_role(role_id))


class CommonAPISync:
    """Synchronous Common API aggregator.

    Provides a unified synchronous interface to all Common API endpoints.

    Attributes:
        alerts: Alerts API client
        tenants: Tenants API client
        admins: Admins API client
        roles: Roles API client

    Example:
        >>> with HTTPClientSync(base_url, auth) as client:
        ...     common_api = CommonAPISync(client)
        ...     alerts = common_api.alerts.list_alerts()
        ...     tenants = common_api.tenants.list_tenants()
    """

    def __init__(self, http_client_sync: HTTPClientSync) -> None:
        """Initialize the synchronous Common API client.

        Args:
            http_client_sync: Synchronous HTTP client
        """
        self.alerts = AlertsAPISync(http_client_sync)
        self.tenants = TenantsAPISync(http_client_sync)
        self.admins = AdminsAPISync(http_client_sync)
        self.roles = RolesAPISync(http_client_sync)
