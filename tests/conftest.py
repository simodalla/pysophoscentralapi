"""Pytest configuration and shared fixtures.

This module provides common fixtures used across all tests.
"""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from pysophoscentralapi.core.auth import AuthProvider
from pysophoscentralapi.core.client import HTTPClient
from pysophoscentralapi.core.config import AuthConfig, Config
from pysophoscentralapi.core.models import PageInfo, Token, TokenResponse


@pytest.fixture
def sample_auth_config() -> AuthConfig:
    """Provide sample authentication configuration.

    Returns:
        AuthConfig instance for testing
    """
    return AuthConfig(
        client_id="test-client-id",
        client_secret="test-client-secret",
    )


@pytest.fixture
def sample_config(sample_auth_config: AuthConfig) -> Config:
    """Provide sample complete configuration.

    Args:
        sample_auth_config: Auth config fixture

    Returns:
        Config instance for testing
    """
    return Config(auth=sample_auth_config)


@pytest.fixture
def sample_token_response() -> TokenResponse:
    """Provide sample token response.

    Returns:
        TokenResponse instance
    """
    return TokenResponse(
        access_token="test-access-token",
        token_type="bearer",
        expires_in=3600,
        scope="token",
    )


@pytest.fixture
def sample_token(sample_token_response: TokenResponse) -> Token:
    """Provide sample token.

    Args:
        sample_token_response: Token response fixture

    Returns:
        Token instance
    """
    return Token.from_response(sample_token_response)


@pytest.fixture
def mock_auth_provider(sample_token: Token) -> AsyncMock:
    """Provide mock authentication provider.

    Args:
        sample_token: Token fixture

    Returns:
        Mocked AuthProvider
    """
    mock = AsyncMock(spec=AuthProvider)
    mock.get_token.return_value = sample_token
    mock.get_authorization_header.return_value = {
        "Authorization": "Bearer test-access-token"
    }
    return mock


@pytest.fixture
async def mock_http_client(mock_auth_provider: AsyncMock) -> HTTPClient:
    """Provide mock HTTP client.

    Args:
        mock_auth_provider: Auth provider fixture

    Returns:
        HTTPClient instance with mocked auth
    """
    return HTTPClient(
        base_url="https://api-test.central.sophos.com",
        auth_provider=mock_auth_provider,
        timeout=30,
    )


@pytest.fixture
def sample_page_info() -> PageInfo:
    """Provide sample pagination info.

    Returns:
        PageInfo instance
    """
    return PageInfo(
        current=1,
        size=50,
        total=1,
        maxSize=1000,
        fromKey=None,
        nextKey=None,
    )


@pytest.fixture
def sample_endpoint_response() -> dict:
    """Provide sample endpoint API response.

    Returns:
        Dictionary representing an endpoint response
    """
    return {
        "items": [
            {
                "id": "endpoint-123",
                "type": "computer",
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
                    {
                        "code": "coreAgent",
                        "version": "2.2.0",
                        "status": "installed",
                    }
                ],
                "lastSeenAt": "2025-11-14T10:00:00.000Z",
            }
        ],
        "pages": {
            "current": 1,
            "size": 1,
            "total": 1,
            "maxSize": 1000,
        },
    }


@pytest.fixture
def sample_alert_response() -> dict:
    """Provide sample alert API response.

    Returns:
        Dictionary representing an alert response
    """
    return {
        "items": [
            {
                "id": "alert-123",
                "allowedActions": ["acknowledge", "clearThreat"],
                "category": "malware",
                "description": "Malware detected",
                "groupKey": "group-key",
                "managedAgent": {
                    "id": "endpoint-id",
                    "type": "computer",
                },
                "product": "endpoint",
                "raisedAt": "2025-11-14T10:00:00.000Z",
                "severity": "high",
                "tenant": {
                    "id": "tenant-id",
                    "name": "Test Tenant",
                },
                "type": "Event::Endpoint::Threat::Detected",
            }
        ],
        "pages": {
            "current": 1,
            "size": 1,
            "total": 1,
            "maxSize": 1000,
        },
    }


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Provide temporary configuration directory.

    Args:
        tmp_path: Pytest tmp_path fixture

    Returns:
        Path to temporary config directory
    """
    config_dir = tmp_path / ".config" / "pysophos"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def temp_config_file(temp_config_dir: Path, sample_auth_config: AuthConfig) -> Path:
    """Provide temporary configuration file.

    Args:
        temp_config_dir: Temp config dir fixture
        sample_auth_config: Auth config fixture

    Returns:
        Path to temporary config file
    """
    config_file = temp_config_dir / "config.toml"
    config_file.write_text(f"""
[auth]
client_id = "{sample_auth_config.client_id}"
client_secret = "{sample_auth_config.client_secret}"

[api]
region = "us"
timeout = 30
""")
    return config_file
