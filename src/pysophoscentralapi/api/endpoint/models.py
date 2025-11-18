"""Data models for Sophos Central Endpoint API.

This module contains Pydantic models for all Endpoint API entities including
endpoints, health status, OS information, and related structures.
"""

from datetime import datetime
from enum import Enum

from pydantic import Field

from pysophoscentralapi.core.models import SophosBaseModel


class HealthStatus(str, Enum):
    """Endpoint health status values."""

    GOOD = "good"
    SUSPICIOUS = "suspicious"
    BAD = "bad"
    UNKNOWN = "unknown"


class EndpointType(str, Enum):
    """Endpoint type values."""

    COMPUTER = "computer"
    SERVER = "server"
    SECURITY_VM = "securityVm"


class LockdownStatus(str, Enum):
    """Endpoint lockdown status values."""

    CREATINGWHITELIST = "creatingWhitelist"
    INSTALLING = "installing"
    LOCKED = "locked"
    NOTINSTALLED = "notInstalled"
    REGISTERING = "registering"
    STARTING = "starting"
    STOPPING = "stopping"
    UNAVAILABLE = "unavailable"
    UNINSTALLED = "uninstalled"
    UNLOCKED = "unlocked"


class OSPlatform(str, Enum):
    """Operating system platform values."""

    WINDOWS = "windows"
    MACOS = "macOS"
    LINUX = "linux"


class ThreatHealth(SophosBaseModel):
    """Threat health information.

    Attributes:
        status: Threat health status
    """

    status: HealthStatus


class ServiceDetail(SophosBaseModel):
    """Service detail information.

    Attributes:
        name: Service name
        status: Service status
    """

    name: str
    status: str


class ServicesHealth(SophosBaseModel):
    """Services health information.

    Attributes:
        status: Overall services health status
        service_details: List of individual service details
    """

    status: HealthStatus
    service_details: list[ServiceDetail] = Field(
        default_factory=list,
        alias="serviceDetails",
    )


class Health(SophosBaseModel):
    """Overall endpoint health information.

    Attributes:
        overall: Overall health status
        threats: Threat health information
        services: Services health information
    """

    overall: HealthStatus
    threats: ThreatHealth
    services: ServicesHealth


class OSInfo(SophosBaseModel):
    """Operating system information.

    Attributes:
        is_server: Whether this is a server OS
        platform: OS platform (windows, macOS, linux)
        name: Full OS name
        major_version: OS major version number
        minor_version: OS minor version number
        build: OS build number
    """

    is_server: bool = Field(alias="isServer")
    platform: OSPlatform
    name: str
    major_version: int | None = Field(None, alias="majorVersion")
    minor_version: int | None = Field(None, alias="minorVersion")
    build: int | None = None


class Tenant(SophosBaseModel):
    """Tenant reference.

    Attributes:
        id: Tenant ID
    """

    id: str


class AssociatedPerson(SophosBaseModel):
    """Person associated with endpoint.

    Attributes:
        id: Person ID
        name: Person name
        via_login: Login identifier
    """

    id: str | None = None
    name: str | None = None
    via_login: str | None = Field(None, alias="viaLogin")


class AssignedProduct(SophosBaseModel):
    """Product assigned to endpoint.

    Attributes:
        code: Product code
        version: Product version
        status: Product status
    """

    code: str
    version: str
    status: str


class Endpoint(SophosBaseModel):
    """Sophos Central endpoint representation.

    Attributes:
        id: Endpoint unique identifier
        type: Endpoint type (computer, server, securityVm)
        tenant: Tenant information
        hostname: Endpoint hostname
        health: Health status information
        os: Operating system information
        ipv4_addresses: List of IPv4 addresses
        ipv6_addresses: List of IPv6 addresses
        mac_addresses: List of MAC addresses
        associated_person: Person associated with endpoint
        tamper_protection_enabled: Whether tamper protection is enabled
        assigned_products: List of assigned products
        last_seen_at: Last seen timestamp
        lockdown_status: Lockdown status
        group: Group information
        encryption: Encryption information
    """

    id: str
    type: EndpointType
    tenant: Tenant
    hostname: str
    health: Health
    os: OSInfo
    ipv4_addresses: list[str] = Field(default_factory=list, alias="ipv4Addresses")
    ipv6_addresses: list[str] = Field(default_factory=list, alias="ipv6Addresses")
    mac_addresses: list[str] = Field(default_factory=list, alias="macAddresses")
    associated_person: AssociatedPerson | None = Field(None, alias="associatedPerson")
    tamper_protection_enabled: bool = Field(alias="tamperProtectionEnabled")
    assigned_products: list[AssignedProduct] = Field(
        default_factory=list,
        alias="assignedProducts",
    )
    last_seen_at: datetime = Field(alias="lastSeenAt")
    lockdown_status: LockdownStatus | None = Field(None, alias="lockdownStatus")
    group: dict | None = None
    encryption: dict | None = None


class EndpointFilters(SophosBaseModel):
    """Filters for endpoint listing.

    Attributes:
        page_size: Number of items per page (1-1000)
        page_from_key: Pagination cursor
        view: Detail level (basic/summary/full)
        health_status: Filter by health status
        type: Filter by endpoint type
        tamper_protection_enabled: Filter by tamper protection status
        lockdown_status: Filter by lockdown status
        last_seen_before: Filter endpoints last seen before this time
        last_seen_after: Filter endpoints last seen after this time
        ids: Filter by specific endpoint IDs
        hostname_contains: Filter by hostname substring
        ip_addresses: Filter by IP addresses
        mac_addresses: Filter by MAC addresses
        search: Search query
        search_fields: Fields to search in
    """

    page_size: int = Field(50, ge=1, le=1000)
    page_from_key: str | None = None
    view: str = "summary"  # basic, summary, full
    health_status: HealthStatus | None = None
    type: EndpointType | None = None
    tamper_protection_enabled: bool | None = None
    lockdown_status: LockdownStatus | None = None
    last_seen_before: datetime | None = None
    last_seen_after: datetime | None = None
    ids: list[str] | None = None
    hostname_contains: str | None = None
    ip_addresses: list[str] | None = None
    mac_addresses: list[str] | None = None
    search: str | None = None
    search_fields: list[str] | None = None

    def to_params(self) -> dict[str, str]:
        """Convert filters to API query parameters.

        Returns:
            Dictionary of query parameters
        """
        params: dict[str, str] = {}

        # Simple fields
        params["pageSize"] = str(self.page_size)
        if self.page_from_key:
            params["pageFromKey"] = self.page_from_key
        if self.view:
            params["view"] = self.view
        if self.health_status:
            # Enum already converted to string by Pydantic use_enum_values
            params["healthStatus"] = str(self.health_status)
        if self.type:
            params["type"] = str(self.type)
        if self.tamper_protection_enabled is not None:
            params["tamperProtectionEnabled"] = str(
                self.tamper_protection_enabled
            ).lower()
        if self.lockdown_status:
            params["lockdownStatus"] = str(self.lockdown_status)
        if self.last_seen_before:
            params["lastSeenBefore"] = self.last_seen_before.isoformat()
        if self.last_seen_after:
            params["lastSeenAfter"] = self.last_seen_after.isoformat()
        if self.hostname_contains:
            params["hostnameContains"] = self.hostname_contains
        if self.search:
            params["search"] = self.search

        # List fields
        if self.ids:
            params["ids"] = ",".join(self.ids)
        if self.ip_addresses:
            params["ipAddresses"] = ",".join(self.ip_addresses)
        if self.mac_addresses:
            params["macAddresses"] = ",".join(self.mac_addresses)
        if self.search_fields:
            params["searchFields"] = ",".join(self.search_fields)

        return params


class ScanRequest(SophosBaseModel):
    """Request to scan an endpoint.

    Attributes:
        enabled: Whether to enable scanning
    """

    enabled: bool = True


class ScanResponse(SophosBaseModel):
    """Response from scan request.

    Attributes:
        id: Scan job ID
        status: Scan status
    """

    id: str
    status: str


class IsolationRequest(SophosBaseModel):
    """Request to isolate an endpoint.

    Attributes:
        enabled: Whether to enable isolation
        comment: Optional comment explaining the isolation
    """

    enabled: bool = True
    comment: str | None = None


class IsolationResponse(SophosBaseModel):
    """Response from isolation request.

    Attributes:
        id: Isolation job ID
        status: Isolation status
    """

    id: str
    status: str


class TamperProtectionStatus(SophosBaseModel):
    """Tamper protection status.

    Attributes:
        enabled: Whether tamper protection is currently enabled
        globally_enabled: Whether tamper protection is globally enabled
        previously_enabled: Whether tamper protection was previously enabled
    """

    enabled: bool
    globally_enabled: bool = Field(alias="globallyEnabled")
    previously_enabled: bool | None = Field(None, alias="previouslyEnabled")


class TamperProtectionUpdate(SophosBaseModel):
    """Request to update tamper protection.

    Attributes:
        enabled: Whether to enable tamper protection
        regenerate_password: Whether to regenerate the tamper protection password
    """

    enabled: bool
    regenerate_password: bool = Field(False, alias="regeneratePassword")


class TamperProtectionPassword(SophosBaseModel):
    """Tamper protection password.

    Attributes:
        password: The tamper protection password
    """

    password: str
