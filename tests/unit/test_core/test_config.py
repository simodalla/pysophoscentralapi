"""Unit tests for configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from pysophoscentralapi.core.config import (
    APIConfig,
    AuthConfig,
    Config,
    ExportConfig,
    OutputConfig,
)
from pysophoscentralapi.core.exceptions import InvalidConfigError, MissingConfigError


class TestAuthConfig:
    """Test AuthConfig class."""

    def test_valid_initialization(self):
        """Test initialization with valid credentials."""
        auth = AuthConfig(client_id="test_id", client_secret="test_secret")

        assert auth.client_id == "test_id"
        assert auth.client_secret == "test_secret"
        assert auth.credentials_file is None

    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from credentials."""
        auth = AuthConfig(
            client_id="  test_id  ",
            client_secret="  test_secret  ",
        )

        assert auth.client_id == "test_id"
        assert auth.client_secret == "test_secret"

    def test_empty_client_id(self):
        """Test that empty client_id raises error."""
        with pytest.raises(ValueError, match="Credentials cannot be empty"):
            AuthConfig(client_id="", client_secret="test_secret")

    def test_empty_client_secret(self):
        """Test that empty client_secret raises error."""
        with pytest.raises(ValueError, match="Credentials cannot be empty"):
            AuthConfig(client_id="test_id", client_secret="")

    def test_whitespace_only_client_id(self):
        """Test that whitespace-only client_id raises error."""
        with pytest.raises(ValueError, match="Credentials cannot be empty"):
            AuthConfig(client_id="   ", client_secret="test_secret")

    def test_credentials_file_path(self):
        """Test with credentials file path."""
        auth = AuthConfig(
            client_id="test_id",
            client_secret="test_secret",
            credentials_file=Path("/path/to/creds.json"),
        )

        assert auth.credentials_file == Path("/path/to/creds.json")


class TestAPIConfig:
    """Test APIConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        api = APIConfig()

        assert api.region == "us"
        assert api.tenant_id is None
        assert api.timeout == 30
        assert api.max_retries == 3
        assert api.rate_limit_retry is True
        assert api.base_url is None

    def test_custom_values(self):
        """Test custom configuration values."""
        api = APIConfig(
            region="eu",
            tenant_id="tenant123",
            timeout=60,
            max_retries=5,
            rate_limit_retry=False,
            base_url="https://api.test.com",
        )

        assert api.region == "eu"
        assert api.tenant_id == "tenant123"
        assert api.timeout == 60
        assert api.max_retries == 5
        assert api.rate_limit_retry is False
        assert api.base_url == "https://api.test.com"

    def test_timeout_validation_min(self):
        """Test timeout minimum validation."""
        with pytest.raises(ValueError, match=r"greater than or equal to 1|timeout"):
            APIConfig(timeout=0)

    def test_timeout_validation_max(self):
        """Test timeout maximum validation."""
        with pytest.raises(ValueError, match=r"less than or equal to 300|timeout"):
            APIConfig(timeout=301)

    def test_max_retries_validation_min(self):
        """Test max_retries minimum validation."""
        api = APIConfig(max_retries=0)
        assert api.max_retries == 0

    def test_max_retries_validation_max(self):
        """Test max_retries maximum validation."""
        with pytest.raises(ValueError, match=r"less than or equal to 10|max_retries"):
            APIConfig(max_retries=11)


class TestOutputConfig:
    """Test OutputConfig class."""

    def test_default_values(self):
        """Test default output configuration."""
        output = OutputConfig()

        assert output.default_format == "table"
        assert output.color_enabled is True
        assert output.page_size == 50
        assert output.table_max_width is None

    def test_custom_values(self):
        """Test custom output configuration."""
        output = OutputConfig(
            default_format="json",
            color_enabled=False,
            page_size=100,
            table_max_width=120,
        )

        assert output.default_format == "json"
        assert output.color_enabled is False
        assert output.page_size == 100
        assert output.table_max_width == 120

    def test_page_size_validation_min(self):
        """Test page_size minimum validation."""
        with pytest.raises(ValueError, match=r"greater than or equal to 1|page_size"):
            OutputConfig(page_size=0)

    def test_page_size_validation_max(self):
        """Test page_size maximum validation."""
        with pytest.raises(ValueError, match=r"less than or equal to 1000|page_size"):
            OutputConfig(page_size=1001)

    def test_format_literal_values(self):
        """Test that format accepts only valid values."""
        # Valid formats
        output1 = OutputConfig(default_format="table")
        output2 = OutputConfig(default_format="json")
        output3 = OutputConfig(default_format="csv")

        assert output1.default_format == "table"
        assert output2.default_format == "json"
        assert output3.default_format == "csv"


class TestExportConfig:
    """Test ExportConfig class."""

    def test_default_values(self):
        """Test default export configuration."""
        export = ExportConfig()

        assert export.default_directory == Path.home() / "sophos-exports"
        assert export.json_indent == 2
        assert export.csv_delimiter == ","
        assert export.csv_flatten is True

    def test_custom_values(self):
        """Test custom export configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir) / "custom-exports"

            export = ExportConfig(
                default_directory=custom_dir,
                json_indent=4,
                csv_delimiter=";",
                csv_flatten=False,
            )

            assert export.default_directory == custom_dir
            assert export.json_indent == 4
            assert export.csv_delimiter == ";"
            assert export.csv_flatten is False
            # Directory should be created
            assert custom_dir.exists()

    def test_directory_creation(self):
        """Test that default_directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new" / "nested" / "dir"

            export = ExportConfig(default_directory=new_dir)

            assert export.default_directory == new_dir
            assert new_dir.exists()

    def test_json_indent_validation_min(self):
        """Test json_indent minimum validation."""
        export = ExportConfig(json_indent=0)
        assert export.json_indent == 0

    def test_json_indent_validation_max(self):
        """Test json_indent maximum validation."""
        with pytest.raises(ValueError, match=r"less than or equal to 8|json_indent"):
            ExportConfig(json_indent=9)


class TestConfig:
    """Test main Config class."""

    def test_initialization(self):
        """Test Config initialization."""
        auth = AuthConfig(client_id="test_id", client_secret="test_secret")
        config = Config(auth=auth)

        assert config.auth == auth
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.output, OutputConfig)
        assert isinstance(config.export, ExportConfig)

    def test_initialization_with_all_sections(self):
        """Test Config initialization with all sections."""
        auth = AuthConfig(client_id="test_id", client_secret="test_secret")
        api = APIConfig(region="eu", timeout=60)
        output = OutputConfig(default_format="json")
        export = ExportConfig(json_indent=4)

        config = Config(auth=auth, api=api, output=output, export=export)

        assert config.auth == auth
        assert config.api == api
        assert config.output == output
        assert config.export == export

    def test_from_file_success(self):
        """Test loading config from valid TOML file."""
        toml_content = """
[auth]
client_id = "test_id"
client_secret = "test_secret"

[api]
region = "eu"
timeout = 60

[output]
default_format = "json"

[export]
json_indent = 4
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            temp_path = Path(f.name)

        try:
            config = Config.from_file(temp_path)

            assert config.auth.client_id == "test_id"
            assert config.auth.client_secret == "test_secret"
            assert config.api.region == "eu"
            assert config.api.timeout == 60
            assert config.output.default_format == "json"
            assert config.export.json_indent == 4
        finally:
            temp_path.unlink()

    def test_from_file_missing(self):
        """Test loading from non-existent file."""
        with pytest.raises(MissingConfigError, match="Config file not found"):
            Config.from_file(Path("/nonexistent/config.toml"))

    def test_from_file_invalid_toml(self):
        """Test loading from invalid TOML file."""
        invalid_content = "this is not valid TOML [["

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(invalid_content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(InvalidConfigError, match="Failed to parse config file"):
                Config.from_file(temp_path)
        finally:
            temp_path.unlink()

    def test_from_file_invalid_config(self):
        """Test loading from TOML with invalid config data."""
        # Invalid TOML syntax
        invalid_config = """
[auth
client_id = "test"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(invalid_config)
            temp_path = Path(f.name)

        try:
            with pytest.raises(InvalidConfigError, match="Failed to parse config file"):
                Config.from_file(temp_path)
        finally:
            temp_path.unlink()

    @patch.dict(
        os.environ,
        {
            "SOPHOS_CLIENT_ID": "env_id",
            "SOPHOS_CLIENT_SECRET": "env_secret",
        },
    )
    def test_from_env_success(self):
        """Test loading config from environment variables."""
        config = Config.from_env()

        assert config.auth.client_id == "env_id"
        assert config.auth.client_secret == "env_secret"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_vars(self):
        """Test loading from env when required vars are missing."""
        with pytest.raises(InvalidConfigError):
            Config.from_env()

    @patch.dict(os.environ, {"SOPHOS_CONFIG_FILE": "/test/config.toml"})
    @patch("pathlib.Path.exists")
    def test_find_config_file_from_env(self, mock_exists):
        """Test finding config file from environment variable."""
        mock_exists.return_value = True

        config_path = Config._find_config_file()

        assert config_path == Path("/test/config.toml")

    def test_find_config_file_with_temp_file(self):
        """Test finding config file in current directory with real temp file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a config file in temp dir
            config_file = Path(tmpdir) / "config.toml"
            config_file.write_text("[auth]\nclient_id='test'\nclient_secret='test'")

            # Patch cwd to return temp dir
            with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                config_path = Config._find_config_file()
                assert config_path == config_file

    @patch("pathlib.Path.exists", return_value=False)
    def test_find_config_file_not_found(self, mock_exists):
        """Test when config file is not found anywhere."""
        config_path = Config._find_config_file()

        assert config_path is None

    def test_get_config_dir(self):
        """Test getting config directory."""
        auth = AuthConfig(client_id="test", client_secret="test")
        config = Config(auth=auth)

        config_dir = config.get_config_dir()

        assert config_dir == Path.home() / ".config" / "pysophos"
        assert config_dir.exists()  # Should be created

    def test_config_dir_creation_nested(self):
        """Test that config dir is created with parents."""
        auth = AuthConfig(client_id="test", client_secret="test")
        config = Config(auth=auth)

        # This should not raise even if intermediate dirs don't exist
        config_dir = config.get_config_dir()
        assert config_dir.exists()
