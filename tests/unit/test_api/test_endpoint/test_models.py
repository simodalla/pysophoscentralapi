"""Tests for Endpoint API data models."""

from datetime import datetime, timezone

from pysophoscentralapi.api.endpoint.models import (
    Endpoint,
    EndpointFilters,
    EndpointType,
    Health,
    HealthStatus,
    IsolationRequest,
    OSInfo,
    OSPlatform,
    ScanRequest,
    ServicesHealth,
    TamperProtectionUpdate,
    ThreatHealth,
)


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self):
        """Test all health status values."""
        assert HealthStatus.GOOD == "good"
        assert HealthStatus.SUSPICIOUS == "suspicious"
        assert HealthStatus.BAD == "bad"
        assert HealthStatus.UNKNOWN == "unknown"


class TestEndpointType:
    """Tests for EndpointType enum."""

    def test_endpoint_type_values(self):
        """Test all endpoint type values."""
        assert EndpointType.COMPUTER == "computer"
        assert EndpointType.SERVER == "server"
        assert EndpointType.SECURITY_VM == "securityVm"


class TestHealth:
    """Tests for Health model."""

    def test_health_creation(self):
        """Test creating health object."""
        health = Health(
            overall=HealthStatus.GOOD,
            threats=ThreatHealth(status=HealthStatus.GOOD),
            services=ServicesHealth(status=HealthStatus.GOOD, serviceDetails=[]),
        )

        assert health.overall == HealthStatus.GOOD
        assert health.threats.status == HealthStatus.GOOD
        assert health.services.status == HealthStatus.GOOD


class TestOSInfo:
    """Tests for OSInfo model."""

    def test_os_info_creation(self):
        """Test creating OS info object."""
        os_info = OSInfo(
            isServer=False,
            platform=OSPlatform.WINDOWS,
            name="Windows 10 Pro",
            majorVersion=10,
            minorVersion=0,
            build=19045,
        )

        assert os_info.is_server is False
        assert os_info.platform == OSPlatform.WINDOWS
        assert os_info.name == "Windows 10 Pro"
        assert os_info.major_version == 10
        assert os_info.minor_version == 0
        assert os_info.build == 19045


class TestEndpoint:
    """Tests for Endpoint model."""

    def test_endpoint_creation(self):
        """Test creating endpoint object from API response."""
        data = {
            "id": "endpoint-123",
            "type": "computer",
            "tenant": {"id": "tenant-123"},
            "hostname": "DESKTOP-TEST",
            "health": {
                "overall": "good",
                "threats": {"status": "good"},
                "services": {"status": "good", "serviceDetails": []},
            },
            "os": {
                "isServer": False,
                "platform": "windows",
                "name": "Windows 10 Pro",
                "majorVersion": 10,
                "minorVersion": 0,
                "build": 19045,
            },
            "ipv4Addresses": ["192.168.1.100"],
            "ipv6Addresses": [],
            "macAddresses": ["00:11:22:33:44:55"],
            "tamperProtectionEnabled": True,
            "assignedProducts": [
                {"code": "coreAgent", "version": "2.2.0", "status": "installed"}
            ],
            "lastSeenAt": "2025-11-15T10:00:00.000Z",
        }

        endpoint = Endpoint(**data)

        assert endpoint.id == "endpoint-123"
        assert endpoint.type == EndpointType.COMPUTER
        assert endpoint.tenant.id == "tenant-123"
        assert endpoint.hostname == "DESKTOP-TEST"
        assert endpoint.health.overall == HealthStatus.GOOD
        assert endpoint.os.platform == OSPlatform.WINDOWS
        assert "192.168.1.100" in endpoint.ipv4_addresses
        assert endpoint.tamper_protection_enabled is True
        assert len(endpoint.assigned_products) == 1


class TestEndpointFilters:
    """Tests for EndpointFilters model."""

    def test_default_filters(self):
        """Test default filter values."""
        filters = EndpointFilters()

        assert filters.page_size == 50
        assert filters.view == "summary"
        assert filters.health_status is None

    def test_filters_to_params_basic(self):
        """Test converting basic filters to params."""
        filters = EndpointFilters(
            page_size=100,
            health_status=HealthStatus.GOOD,
        )

        params = filters.to_params()

        assert params["pageSize"] == "100"
        assert params["healthStatus"] == "good"
        assert params["view"] == "summary"

    def test_filters_to_params_with_lists(self):
        """Test converting filters with lists."""
        filters = EndpointFilters(
            ids=["id-1", "id-2"],
            ip_addresses=["192.168.1.1", "192.168.1.2"],
            search_fields=["hostname", "ipAddress"],
        )

        params = filters.to_params()

        assert params["ids"] == "id-1,id-2"
        assert params["ipAddresses"] == "192.168.1.1,192.168.1.2"
        assert params["searchFields"] == "hostname,ipAddress"

    def test_filters_to_params_with_datetime(self):
        """Test converting filters with datetime."""
        dt = datetime(2025, 11, 15, 10, 0, 0, tzinfo=timezone.utc)
        filters = EndpointFilters(last_seen_after=dt)

        params = filters.to_params()

        assert "lastSeenAfter" in params
        assert "2025-11-15" in params["lastSeenAfter"]

    def test_filters_to_params_with_boolean(self):
        """Test converting filters with boolean."""
        filters = EndpointFilters(tamper_protection_enabled=True)

        params = filters.to_params()

        assert params["tamperProtectionEnabled"] == "true"


class TestScanRequest:
    """Tests for ScanRequest model."""

    def test_scan_request_default(self):
        """Test default scan request."""
        request = ScanRequest()
        assert request.enabled is True

    def test_scan_request_custom(self):
        """Test custom scan request."""
        request = ScanRequest(enabled=False)
        assert request.enabled is False


class TestIsolationRequest:
    """Tests for IsolationRequest model."""

    def test_isolation_request_with_comment(self):
        """Test isolation request with comment."""
        request = IsolationRequest(
            enabled=True,
            comment="Suspected malware",
        )

        assert request.enabled is True
        assert request.comment == "Suspected malware"

        # Test serialization
        data = request.model_dump(by_alias=True, exclude_none=True)
        assert "enabled" in data
        assert "comment" in data


class TestTamperProtectionUpdate:
    """Tests for TamperProtectionUpdate model."""

    def test_tamper_protection_update(self):
        """Test tamper protection update request."""
        update = TamperProtectionUpdate(
            enabled=True,
            regenerate_password=True,
        )

        assert update.enabled is True
        assert update.regenerate_password is True

        # Test alias
        data = update.model_dump(by_alias=True)
        assert "regeneratePassword" in data
