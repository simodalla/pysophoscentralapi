"""Configuration management for pysophoscentralapi.

This module handles loading and validating configuration from multiple sources:
files, environment variables, and defaults.
"""

import os
import sys
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from pysophoscentralapi.core.exceptions import InvalidConfigError, MissingConfigError


class AuthConfig(BaseSettings):
    """Authentication configuration.

    Attributes:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        credentials_file: Path to credentials file (alternative to direct credentials)
    """

    model_config = SettingsConfigDict(
        env_prefix="SOPHOS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    credentials_file: Path | None = Field(
        None,
        description="Path to credentials file",
    )

    @field_validator("client_id", "client_secret")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that credential fields are not empty.

        Args:
            v: Value to validate

        Returns:
            Validated value

        Raises:
            ValueError: If value is empty
        """
        if not v or not v.strip():
            msg = "Credentials cannot be empty"
            raise ValueError(msg)
        return v.strip()


class APIConfig(BaseSettings):
    """API configuration.

    Attributes:
        region: Data region (us, eu, ap, etc.)
        tenant_id: Tenant ID (if applicable)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        rate_limit_retry: Whether to retry on rate limits
        base_url: Base URL override (for testing)
    """

    model_config = SettingsConfigDict(
        env_prefix="SOPHOS_",
        extra="ignore",
    )

    region: str = Field(default="us", description="Data region")
    tenant_id: str | None = Field(None, description="Tenant ID")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout")
    max_retries: int = Field(default=3, ge=0, le=10, description="Max retry attempts")
    rate_limit_retry: bool = Field(
        default=True,
        description="Retry on rate limits",
    )
    base_url: str | None = Field(None, description="Base URL override")


class OutputConfig(BaseSettings):
    """Output configuration for CLI.

    Attributes:
        default_format: Default output format
        color_enabled: Enable colored output
        page_size: Default page size
        table_max_width: Maximum table width (None for auto)
    """

    model_config = SettingsConfigDict(
        env_prefix="SOPHOS_OUTPUT_",
        extra="ignore",
    )

    default_format: Literal["table", "json", "csv"] = Field(
        default="table",
        description="Default output format",
    )
    color_enabled: bool = Field(default=True, description="Enable colors")
    page_size: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Default page size",
    )
    table_max_width: int | None = Field(
        None,
        description="Max table width",
    )


class ExportConfig(BaseSettings):
    """Export configuration.

    Attributes:
        default_directory: Default export directory
        json_indent: JSON indentation spaces
        csv_delimiter: CSV delimiter character
        csv_flatten: Flatten nested objects in CSV
    """

    model_config = SettingsConfigDict(
        env_prefix="SOPHOS_EXPORT_",
        extra="ignore",
    )

    default_directory: Path = Field(
        default_factory=lambda: Path.home() / "sophos-exports",
        description="Default export directory",
    )
    json_indent: int = Field(default=2, ge=0, le=8, description="JSON indent")
    csv_delimiter: str = Field(default=",", description="CSV delimiter")
    csv_flatten: bool = Field(
        default=True,
        description="Flatten nested objects",
    )

    @field_validator("default_directory")
    @classmethod
    def create_directory(cls, v: Path) -> Path:
        """Create directory if it doesn't exist.

        Args:
            v: Directory path

        Returns:
            Validated path
        """
        v.mkdir(parents=True, exist_ok=True)
        return v


class Config(BaseSettings):
    """Main configuration container.

    This class aggregates all configuration sections and provides
    methods to load from files and environment variables.

    Attributes:
        auth: Authentication configuration
        api: API configuration
        output: Output configuration
        export: Export configuration
    """

    auth: AuthConfig
    api: APIConfig = Field(default_factory=APIConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)

    @classmethod
    def from_file(cls, config_path: Path | None = None) -> "Config":
        """Load configuration from TOML file.

        Args:
            config_path: Path to config file. If None, uses default locations.

        Returns:
            Config instance

        Raises:
            MissingConfigError: If config file not found
            InvalidConfigError: If config file is invalid

        Example:
            >>> config = Config.from_file(Path("config.toml"))
            >>> config.auth.client_id
            'your-client-id'
        """
        if config_path is None:
            config_path = cls._find_config_file()

        if not config_path or not config_path.exists():
            msg = f"Config file not found: {config_path}"
            raise MissingConfigError(msg)

        try:
            with config_path.open("rb") as f:
                config_data = tomllib.load(f)
        except Exception as e:
            msg = f"Failed to parse config file: {e}"
            raise InvalidConfigError(msg) from e

        try:
            return cls(**config_data)
        except Exception as e:
            msg = f"Invalid configuration: {e}"
            raise InvalidConfigError(msg) from e

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables only.

        Returns:
            Config instance

        Raises:
            InvalidConfigError: If required env vars missing

        Example:
            >>> os.environ["SOPHOS_CLIENT_ID"] = "test"
            >>> os.environ["SOPHOS_CLIENT_SECRET"] = "secret"
            >>> config = Config.from_env()
        """
        try:
            auth = AuthConfig()
            return cls(auth=auth)
        except Exception as e:
            msg = f"Failed to load config from environment: {e}"
            raise InvalidConfigError(msg) from e

    @staticmethod
    def _find_config_file() -> Path | None:
        """Find config file in standard locations.

        Checks in order:
        1. SOPHOS_CONFIG_FILE environment variable
        2. ./config.toml (current directory)
        3. ~/.config/pysophos/config.toml
        4. ~/.pysophos/config.toml

        Returns:
            Path to config file if found, None otherwise
        """
        # Check environment variable
        if env_path := os.getenv("SOPHOS_CONFIG_FILE"):
            path = Path(env_path)
            if path.exists():
                return path

        # Check standard locations
        locations = [
            Path.cwd() / "config.toml",
            Path.home() / ".config" / "pysophos" / "config.toml",
            Path.home() / ".pysophos" / "config.toml",
        ]

        for location in locations:
            if location.exists():
                return location

        return None

    def get_config_dir(self) -> Path:
        """Get configuration directory path.

        Creates directory if it doesn't exist.

        Returns:
            Path to config directory
        """
        config_dir = Path.home() / ".config" / "pysophos"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
