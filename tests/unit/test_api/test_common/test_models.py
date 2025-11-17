"""Tests for Common API data models."""

from datetime import datetime, timezone

from pysophoscentralapi.api.common.models import (
    Admin,
    AdminCreateRequest,
    Alert,
    AlertFilters,
    AlertSeverity,
    Role,
    RoleCreateRequest,
    Tenant,
    TenantFilters,
)


class TestAlertModels:
    """Tests for Alert models."""

    def test_alert_severity_values(self):
        """Test alert severity enum values."""
        assert AlertSeverity.LOW == "low"
        assert AlertSeverity.MEDIUM == "medium"
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.CRITICAL == "critical"

    def test_alert_creation(self):
        """Test creating alert object from API response."""
        data = {
            "id": "alert-123",
            "allowedActions": ["acknowledge", "clearThreat"],
            "category": "malware",
            "description": "Malware detected",
            "groupKey": "group-123",
            "product": "endpoint",
            "raisedAt": "2025-11-15T10:00:00.000Z",
            "severity": "high",
            "tenant": {"id": "tenant-123", "name": "Test Tenant"},
            "type": "Event::Endpoint::Threat::Detected",
        }

        alert = Alert(**data)

        assert alert.id == "alert-123"
        assert len(alert.allowed_actions) == 2
        assert str(alert.category) == "malware"
        assert alert.description == "Malware detected"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.tenant.id == "tenant-123"

    def test_alert_filters_to_params(self):
        """Test converting alert filters to params."""
        dt = datetime(2025, 11, 15, 10, 0, 0, tzinfo=timezone.utc)
        filters = AlertFilters(
            page_size=100,
            severity=["high", "critical"],
            product=["endpoint", "server"],
            from_date=dt,
        )

        params = filters.to_params()

        assert params["pageSize"] == "100"
        assert params["severity"] == "high,critical"
        assert params["product"] == "endpoint,server"
        assert "2025-11-15" in params["from"]


class TestTenantModels:
    """Tests for Tenant models."""

    def test_tenant_creation(self):
        """Test creating tenant object."""
        data = {
            "id": "tenant-123",
            "name": "Test Company",
            "dataRegion": "us",
            "billingType": "usage",
            "apiHost": "https://api-us.central.sophos.com",
        }

        tenant = Tenant(**data)

        assert tenant.id == "tenant-123"
        assert tenant.name == "Test Company"
        assert tenant.data_region == "us"
        assert tenant.api_host == "https://api-us.central.sophos.com"

    def test_tenant_filters_to_params(self):
        """Test converting tenant filters to params."""
        filters = TenantFilters(
            page_size=50,
            data_region="us",
            show_counts=True,
        )

        params = filters.to_params()

        assert params["pageSize"] == "50"
        assert params["dataRegion"] == "us"
        assert params["showCounts"] == "true"


class TestAdminModels:
    """Tests for Admin models."""

    def test_admin_creation(self):
        """Test creating admin object."""
        data = {
            "id": "admin-123",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "role": {"id": "role-123", "name": "Admin"},
            "tenants": [{"id": "tenant-1", "name": "Tenant 1"}],
            "status": "active",
        }

        admin = Admin(**data)

        assert admin.id == "admin-123"
        assert admin.first_name == "John"
        assert admin.last_name == "Doe"
        assert admin.email == "john.doe@example.com"
        assert admin.role.name == "Admin"
        assert len(admin.tenants) == 1

    def test_admin_create_request(self):
        """Test admin create request serialization."""
        request = AdminCreateRequest(
            firstName="Jane",
            lastName="Smith",
            email="jane.smith@example.com",
            roleId="role-456",
            tenantIds=["tenant-1", "tenant-2"],
        )

        data = request.model_dump(by_alias=True)

        assert data["firstName"] == "Jane"
        assert data["lastName"] == "Smith"
        assert data["email"] == "jane.smith@example.com"
        assert data["roleId"] == "role-456"
        assert len(data["tenantIds"]) == 2


class TestRoleModels:
    """Tests for Role models."""

    def test_role_creation(self):
        """Test creating role object."""
        data = {
            "id": "role-123",
            "name": "Custom Admin",
            "description": "Custom admin role",
            "permissions": [
                {"scope": "tenant", "actions": ["read", "write"]},
                {"scope": "endpoint", "actions": ["read"]},
            ],
            "builtin": False,
        }

        role = Role(**data)

        assert role.id == "role-123"
        assert role.name == "Custom Admin"
        assert role.description == "Custom admin role"
        assert len(role.permissions) == 2
        assert role.builtin is False

    def test_role_create_request(self):
        """Test role create request serialization."""
        request = RoleCreateRequest(
            name="Test Role",
            description="Test role description",
            permissions=[
                {"scope": "alert", "actions": ["read"]},
            ],
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data["name"] == "Test Role"
        assert data["description"] == "Test role description"
        assert len(data["permissions"]) == 1
