"""Sophos Central Common API v1 client.

This package provides access to all Common API endpoints including:
- Alert management
- Tenant operations
- Admin management
- Role management
"""

from pysophoscentralapi.api.common.admins import AdminsAPI
from pysophoscentralapi.api.common.alerts import AlertsAPI
from pysophoscentralapi.api.common.models import (
    Admin,
    Alert,
    AlertFilters,
    AlertSeverity,
    Role,
    Tenant,
    TenantFilters,
)
from pysophoscentralapi.api.common.roles import RolesAPI
from pysophoscentralapi.api.common.tenants import TenantsAPI
from pysophoscentralapi.core.client import HTTPClient


class CommonAPI:
    """Sophos Central Common API aggregator.

    Provides a unified interface to all Common API endpoints through
    specialized sub-clients.

    Attributes:
        http_client: HTTP client for making API requests
        alerts: Alerts API client
        tenants: Tenants API client
        admins: Admins API client
        roles: Roles API client

    Example:
        >>> from pysophoscentralapi.core.client import HTTPClient
        >>> from pysophoscentralapi.api.common import CommonAPI
        >>>
        >>> async with HTTPClient(base_url, auth) as client:
        ...     common_api = CommonAPI(client)
        ...
        ...     # Access alerts
        ...     alerts = await common_api.alerts.list_alerts()
        ...
        ...     # Access tenants
        ...     tenants = await common_api.tenants.list_tenants()
        ...
        ...     # Access admins
        ...     admins = await common_api.admins.list_admins()
        ...
        ...     # Access roles
        ...     roles = await common_api.roles.list_roles()
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the Common API client.

        Args:
            http_client: HTTP client for API requests
        """
        self.http_client = http_client
        self.alerts = AlertsAPI(http_client)
        self.tenants = TenantsAPI(http_client)
        self.admins = AdminsAPI(http_client)
        self.roles = RolesAPI(http_client)


__all__ = [
    "Admin",
    "AdminsAPI",
    "Alert",
    "AlertFilters",
    "AlertSeverity",
    "AlertsAPI",
    "CommonAPI",
    "Role",
    "RolesAPI",
    "Tenant",
    "TenantFilters",
    "TenantsAPI",
]
