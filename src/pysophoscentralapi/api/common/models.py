"""Data models for Sophos Central Common API.

This module contains Pydantic models for Common API entities including
alerts, tenants, admins, roles, and related structures.
"""

from datetime import datetime
from enum import Enum

from pydantic import Field

from pysophoscentralapi.core.models import SophosBaseModel


# Alert Models


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertCategory(str, Enum):
    """Alert categories."""

    MALWARE = "malware"
    PUA = "pua"
    RANSOMWARE = "ransomware"
    EXPLOIT = "exploit"
    RUNTIME_DETECTION = "runtimeDetection"
    POLICY_VIOLATION = "policyViolation"
    SUSPICIOUS_BEHAVIOR = "suspiciousBehavior"
    THREAT_CASE = "threatCase"


class AlertProduct(str, Enum):
    """Product types for alerts."""

    ENDPOINT = "endpoint"
    SERVER = "server"
    MOBILE = "mobile"
    EMAIL = "email"
    WIRELESS = "wireless"
    FIREWALL = "firewall"
    OTHER = "other"


class AlertAction(str, Enum):
    """Available alert actions."""

    ACKNOWLEDGE = "acknowledge"
    CLEAR_THREAT = "clearThreat"
    CLEAR_PUA = "clearPua"
    CLEAR_HMPA = "clearHmpa"
    CLEAR_BEHAVIOR = "clearBehavior"
    AUTH_PUA = "authPua"
    CLEAN_PUA = "cleanPua"
    CLEAN_BEHAVIOR = "cleanBehavior"


class ManagedAgent(SophosBaseModel):
    """Managed agent information in alert.

    Attributes:
        id: Agent ID
        type: Agent type
    """

    id: str
    type: str


class Person(SophosBaseModel):
    """Person information in alert.

    Attributes:
        id: Person ID
        name: Person name
    """

    id: str
    name: str | None = None


class TenantInfo(SophosBaseModel):
    """Tenant information.

    Attributes:
        id: Tenant ID
        name: Tenant name
    """

    id: str
    name: str | None = None


class Alert(SophosBaseModel):
    """Sophos Central alert representation.

    Attributes:
        id: Alert unique identifier
        allowed_actions: List of actions that can be performed
        category: Alert category
        description: Alert description
        group_key: Group key for related alerts
        managed_agent: Managed agent associated with alert
        person: Person associated with alert
        product: Product that generated the alert
        raised_at: When alert was raised
        severity: Alert severity level
        tenant: Tenant information
        type: Alert type
        data: Additional alert data
    """

    id: str
    allowed_actions: list[str] = Field(default_factory=list, alias="allowedActions")
    category: AlertCategory
    description: str
    group_key: str = Field(alias="groupKey")
    managed_agent: ManagedAgent | None = Field(None, alias="managedAgent")
    person: Person | None = None
    product: AlertProduct
    raised_at: datetime = Field(alias="raisedAt")
    severity: AlertSeverity
    tenant: TenantInfo
    type: str
    data: dict | None = None


class AlertFilters(SophosBaseModel):
    """Filters for alert listing.

    Attributes:
        page_size: Number of items per page (1-1000)
        page_from_key: Pagination cursor
        product: Filter by product types
        category: Filter by categories
        group_key: Filter by group key
        severity: Filter by severity levels
        ids: Filter by specific alert IDs
        fields: Fields to return
        from_date: Alerts raised after this time
        to_date: Alerts raised before this time
    """

    page_size: int = Field(50, ge=1, le=1000)
    page_from_key: str | None = None
    product: list[str] | None = None
    category: list[str] | None = None
    group_key: str | None = None
    severity: list[str] | None = None
    ids: list[str] | None = None
    fields: list[str] | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None

    def to_params(self) -> dict[str, str]:
        """Convert filters to API query parameters.

        Returns:
            Dictionary of query parameters
        """
        params: dict[str, str] = {}

        params["pageSize"] = str(self.page_size)
        if self.page_from_key:
            params["pageFromKey"] = self.page_from_key
        if self.group_key:
            params["groupKey"] = self.group_key

        # List fields
        if self.product:
            params["product"] = ",".join(self.product)
        if self.category:
            params["category"] = ",".join(self.category)
        if self.severity:
            params["severity"] = ",".join(self.severity)
        if self.ids:
            params["ids"] = ",".join(self.ids)
        if self.fields:
            params["fields"] = ",".join(self.fields)

        # Date fields
        if self.from_date:
            params["from"] = self.from_date.isoformat()
        if self.to_date:
            params["to"] = self.to_date.isoformat()

        return params


class AlertActionRequest(SophosBaseModel):
    """Request to perform an alert action.

    Attributes:
        action: Action to perform
        message: Optional message
    """

    action: str
    message: str | None = None


# Tenant Models


class DataRegion(str, Enum):
    """Data region codes."""

    US = "us"
    EU = "eu"
    DE = "de"
    IE = "ie"
    AP = "ap"


class BillingType(str, Enum):
    """Tenant billing types."""

    TRIAL = "trial"
    USAGE = "usage"
    USER = "user"


class PartnerInfo(SophosBaseModel):
    """Partner information.

    Attributes:
        id: Partner ID
    """

    id: str


class Tenant(SophosBaseModel):
    """Sophos Central tenant representation.

    Attributes:
        id: Tenant unique identifier
        name: Tenant name
        data_region: Data region code
        data_geography: Data geography
        billing_type: Billing type
        partner: Partner information
        api_host: API host URL
        status: Tenant status
        show_counts: Whether to show entity counts
    """

    id: str
    name: str
    data_region: str = Field(alias="dataRegion")
    data_geography: str | None = Field(None, alias="dataGeography")
    billing_type: str | None = Field(None, alias="billingType")
    partner: PartnerInfo | None = None
    api_host: str = Field(alias="apiHost")
    status: str | None = None
    show_counts: bool | None = Field(None, alias="showCounts")


class TenantFilters(SophosBaseModel):
    """Filters for tenant listing.

    Attributes:
        page_size: Number of items per page
        page_from_key: Pagination cursor
        data_region: Filter by data region
        ids: Filter by specific tenant IDs
        show_counts: Include entity counts
    """

    page_size: int = Field(50, ge=1, le=1000)
    page_from_key: str | None = None
    data_region: str | None = None
    ids: list[str] | None = None
    show_counts: bool | None = None

    def to_params(self) -> dict[str, str]:
        """Convert filters to API query parameters."""
        params: dict[str, str] = {}

        params["pageSize"] = str(self.page_size)
        if self.page_from_key:
            params["pageFromKey"] = self.page_from_key
        if self.data_region:
            params["dataRegion"] = self.data_region
        if self.ids:
            params["ids"] = ",".join(self.ids)
        if self.show_counts is not None:
            params["showCounts"] = str(self.show_counts).lower()

        return params


# Admin Models


class RoleReference(SophosBaseModel):
    """Role reference.

    Attributes:
        id: Role ID
        name: Role name
    """

    id: str
    name: str


class TenantReference(SophosBaseModel):
    """Tenant reference.

    Attributes:
        id: Tenant ID
        name: Tenant name
    """

    id: str
    name: str


class Admin(SophosBaseModel):
    """Sophos Central admin representation.

    Attributes:
        id: Admin unique identifier
        first_name: First name
        last_name: Last name
        email: Email address
        role: Admin role
        tenants: List of accessible tenants
        status: Admin status
    """

    id: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: str
    role: RoleReference | None = None
    tenants: list[TenantReference] = Field(default_factory=list)
    status: str | None = None


class AdminCreateRequest(SophosBaseModel):
    """Request to create an admin.

    Attributes:
        first_name: First name
        last_name: Last name
        email: Email address
        role_id: Role ID
        tenant_ids: List of tenant IDs
    """

    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: str
    role_id: str = Field(alias="roleId")
    tenant_ids: list[str] = Field(default_factory=list, alias="tenantIds")


class AdminUpdateRequest(SophosBaseModel):
    """Request to update an admin.

    Attributes:
        first_name: First name
        last_name: Last name
        email: Email address
        role_id: Role ID
        tenant_ids: List of tenant IDs
    """

    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    email: str | None = None
    role_id: str | None = Field(None, alias="roleId")
    tenant_ids: list[str] | None = Field(None, alias="tenantIds")


# Role Models


class Permission(SophosBaseModel):
    """Permission definition.

    Attributes:
        scope: Permission scope
        actions: List of allowed actions
    """

    scope: str
    actions: list[str] = Field(default_factory=list)


class Role(SophosBaseModel):
    """Sophos Central role representation.

    Attributes:
        id: Role unique identifier
        name: Role name
        description: Role description
        permissions: List of permissions
        builtin: Whether this is a built-in role
    """

    id: str
    name: str
    description: str | None = None
    permissions: list[Permission] = Field(default_factory=list)
    builtin: bool | None = None


class RoleCreateRequest(SophosBaseModel):
    """Request to create a role.

    Attributes:
        name: Role name
        description: Role description
        permissions: List of permissions
    """

    name: str
    description: str | None = None
    permissions: list[Permission] = Field(default_factory=list)


class RoleUpdateRequest(SophosBaseModel):
    """Request to update a role.

    Attributes:
        name: Role name
        description: Role description
        permissions: List of permissions
    """

    name: str | None = None
    description: str | None = None
    permissions: list[Permission] | None = None
