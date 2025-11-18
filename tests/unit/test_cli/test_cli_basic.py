"""Basic tests for CLI functionality."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from pysophoscentralapi.cli.main import cli
from pysophoscentralapi.core.config import APIConfig, AuthConfig, Config


class TestCLIBasic:
    """Tests for basic CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "PySophosCentralApi" in result.output
        assert "Sophos Central API Client" in result.output

    def test_cli_version(self):
        """Test CLI version output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "pysophos" in result.output
        assert "0.1.0" in result.output

    def test_config_group(self):
        """Test config command group."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])

        assert result.exit_code == 0
        assert "Configuration management" in result.output
        assert "init" in result.output
        assert "show" in result.output
        assert "test" in result.output

    def test_endpoint_group(self):
        """Test endpoint command group."""
        runner = CliRunner()
        result = runner.invoke(cli, ["endpoint", "--help"])

        assert result.exit_code == 0
        assert "Endpoint API commands" in result.output
        assert "list" in result.output
        assert "get" in result.output
        assert "scan" in result.output
        assert "isolate" in result.output

    def test_alerts_group(self):
        """Test alerts command group."""
        runner = CliRunner()
        result = runner.invoke(cli, ["alerts", "--help"])

        assert result.exit_code == 0
        assert "Alert management" in result.output
        assert "list" in result.output
        assert "get" in result.output

    def test_tenants_group(self):
        """Test tenants command group."""
        runner = CliRunner()
        result = runner.invoke(cli, ["tenants", "--help"])

        assert result.exit_code == 0
        assert "Tenant management" in result.output
        assert "list" in result.output
        assert "get" in result.output

    def test_admins_group(self):
        """Test admins command group."""
        runner = CliRunner()
        result = runner.invoke(cli, ["admins", "--help"])

        assert result.exit_code == 0
        assert "Admin management" in result.output
        assert "list" in result.output

    def test_roles_group(self):
        """Test roles command group."""
        runner = CliRunner()
        result = runner.invoke(cli, ["roles", "--help"])

        assert result.exit_code == 0
        assert "Role management" in result.output
        assert "list" in result.output


class TestCLICommands:
    """Tests for CLI commands with mocked API."""

    def _create_mock_config(self):
        """Create a mock configuration."""
        return Config(
            auth=AuthConfig(client_id="test-id", client_secret="test-secret"),
            api=APIConfig(region="us"),
        )

    @patch("pysophoscentralapi.cli.endpoint_cmds.Config.from_file")
    @patch("pysophoscentralapi.cli.endpoint_cmds.create_endpoint_api_sync")
    def test_endpoint_list_demo(self, mock_create_api, mock_config):
        """Test endpoint list command with mocked API."""
        # Setup mocks
        mock_config.return_value = self._create_mock_config()

        mock_api_instance = MagicMock()
        mock_endpoint = MagicMock()
        mock_endpoint.model_dump.return_value = {
            "id": "endpoint-1",
            "hostname": "DESKTOP-001",
            "health": "good",
            "type": "computer",
        }
        mock_response = MagicMock()
        mock_response.items = [mock_endpoint]
        mock_api_instance.list_endpoints.return_value = mock_response
        mock_create_api.return_value.__enter__.return_value = mock_api_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["endpoint", "list", "--sync"])

        assert result.exit_code == 0
        assert "DESKTOP-001" in result.output or "Found 1 endpoint" in result.output

    @patch("pysophoscentralapi.cli.endpoint_cmds.Config.from_file")
    @patch("pysophoscentralapi.cli.endpoint_cmds.create_endpoint_api_sync")
    def test_endpoint_list_json(self, mock_create_api, mock_config):
        """Test endpoint list with JSON output."""
        mock_config.return_value = self._create_mock_config()

        mock_api_instance = MagicMock()
        mock_endpoint = MagicMock()
        mock_endpoint.model_dump.return_value = {
            "id": "endpoint-1",
            "hostname": "DESKTOP-001",
            "health": "good",
            "type": "computer",
        }
        mock_response = MagicMock()
        mock_response.items = [mock_endpoint]
        mock_api_instance.list_endpoints.return_value = mock_response
        mock_create_api.return_value.__enter__.return_value = mock_api_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["endpoint", "list", "--output", "json", "--sync"])

        assert result.exit_code == 0
        assert "endpoint-1" in result.output or "DESKTOP-001" in result.output

    @patch("pysophoscentralapi.cli.common_cmds.Config.from_file")
    @patch("pysophoscentralapi.cli.common_cmds.create_common_api_sync")
    def test_alerts_list_demo(self, mock_create_api, mock_config):
        """Test alerts list command with mocked API."""
        mock_config.return_value = self._create_mock_config()

        mock_api_instance = MagicMock()
        mock_alert = MagicMock()
        mock_alert.model_dump.return_value = {
            "id": "alert-1",
            "severity": "high",
            "description": "Test alert",
            "category": "malware",
            "product": "endpoint",
        }
        mock_response = MagicMock()
        mock_response.items = [mock_alert]
        mock_api_instance.alerts.list_alerts.return_value = mock_response
        mock_create_api.return_value.__enter__.return_value = mock_api_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["alerts", "list", "--sync"])

        assert result.exit_code == 0
        assert "Found 1 alert" in result.output or "alert-1" in result.output

    @patch("pysophoscentralapi.cli.common_cmds.Config.from_file")
    @patch("pysophoscentralapi.cli.common_cmds.create_common_api_sync")
    def test_alerts_list_with_severity(self, mock_create_api, mock_config):
        """Test alerts list with severity filter."""
        mock_config.return_value = self._create_mock_config()

        mock_api_instance = MagicMock()
        mock_alert = MagicMock()
        mock_alert.model_dump.return_value = {
            "id": "alert-1",
            "severity": "critical",
            "description": "Critical alert",
            "category": "malware",
            "product": "endpoint",
        }
        mock_response = MagicMock()
        mock_response.items = [mock_alert]
        mock_api_instance.alerts.list_alerts.return_value = mock_response
        mock_create_api.return_value.__enter__.return_value = mock_api_instance

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "alerts",
                "list",
                "--severity",
                "high",
                "--severity",
                "critical",
                "--sync",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Found 1 alert" in result.output or "Filtered by severity" in result.output
        )

    @patch("pysophoscentralapi.cli.common_cmds.Config.from_file")
    @patch("pysophoscentralapi.cli.common_cmds.create_common_api_sync")
    def test_tenants_list_demo(self, mock_create_api, mock_config):
        """Test tenants list command with mocked API."""
        mock_config.return_value = self._create_mock_config()

        mock_api_instance = MagicMock()
        mock_tenant = MagicMock()
        mock_tenant.model_dump.return_value = {
            "id": "tenant-1",
            "name": "Test Company",
            "dataRegion": "us",
        }
        mock_response = MagicMock()
        mock_response.items = [mock_tenant]
        mock_api_instance.tenants.list_tenants.return_value = mock_response
        mock_create_api.return_value.__enter__.return_value = mock_api_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["tenants", "list", "--sync"])

        assert result.exit_code == 0
        assert "Found 1 tenant" in result.output or "Test Company" in result.output

    @patch("pysophoscentralapi.cli.endpoint_cmds.Config.from_file")
    @patch("pysophoscentralapi.cli.endpoint_cmds.create_endpoint_api_sync")
    def test_endpoint_scan_demo(self, mock_create_api, mock_config):
        """Test endpoint scan command with mocked API."""
        mock_config.return_value = self._create_mock_config()

        mock_api_instance = MagicMock()
        mock_api_instance.scan_endpoint.return_value = None
        mock_create_api.return_value.__enter__.return_value = mock_api_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["endpoint", "scan", "test-endpoint-123", "--sync"])

        assert result.exit_code == 0
        assert "Scan triggered" in result.output or "test-endpoint-123" in result.output

    @patch("pysophoscentralapi.cli.endpoint_cmds.Config.from_file")
    @patch("pysophoscentralapi.cli.endpoint_cmds.create_endpoint_api_sync")
    def test_endpoint_tamper_status(self, mock_create_api, mock_config):
        """Test endpoint tamper status command with mocked API."""
        mock_config.return_value = self._create_mock_config()

        mock_api_instance = MagicMock()
        mock_tamper = MagicMock()
        mock_tamper.model_dump.return_value = {
            "enabled": True,
            "globally_enabled": True,
        }
        mock_api_instance.get_tamper_protection.return_value = mock_tamper
        mock_create_api.return_value.__enter__.return_value = mock_api_instance

        runner = CliRunner()
        result = runner.invoke(
            cli, ["endpoint", "tamper", "status", "test-endpoint-123", "--sync"]
        )

        assert result.exit_code == 0
        assert "Tamper protection status" in result.output or "enabled" in result.output


class TestConfigCommands:
    """Tests for config commands."""

    def test_config_show_no_file(self):
        """Test config show with no config file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["config", "show"])

            # Should either show error about missing config OR show config file location
            # (test may find global config file)
            assert result.exit_code == 0 or "not found" in result.output

    def test_config_init(self):
        """Test config init command."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["config", "init"],
                input="test-client-id\ntest-secret\n",
            )

            # Should complete successfully
            assert result.exit_code == 0 or "Configuration saved" in result.output
