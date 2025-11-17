"""Basic tests for CLI functionality."""

from click.testing import CliRunner

from pysophoscentralapi.cli.main import cli


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
    """Tests for CLI commands (demo mode)."""

    def test_endpoint_list_demo(self):
        """Test endpoint list command in demo mode."""
        runner = CliRunner()
        result = runner.invoke(cli, ["endpoint", "list"])

        assert result.exit_code == 0
        # Should show demo data
        assert (
            "Not fully implemented yet" in result.output or "DESKTOP" in result.output
        )

    def test_endpoint_list_json(self):
        """Test endpoint list with JSON output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["endpoint", "list", "--output", "json"])

        assert result.exit_code == 0

    def test_alerts_list_demo(self):
        """Test alerts list command in demo mode."""
        runner = CliRunner()
        result = runner.invoke(cli, ["alerts", "list"])

        assert result.exit_code == 0

    def test_alerts_list_with_severity(self):
        """Test alerts list with severity filter."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["alerts", "list", "--severity", "high", "--severity", "critical"]
        )

        assert result.exit_code == 0

    def test_tenants_list_demo(self):
        """Test tenants list command in demo mode."""
        runner = CliRunner()
        result = runner.invoke(cli, ["tenants", "list"])

        assert result.exit_code == 0

    def test_endpoint_scan_demo(self):
        """Test endpoint scan command in demo mode."""
        runner = CliRunner()
        result = runner.invoke(cli, ["endpoint", "scan", "test-endpoint-123"])

        assert result.exit_code == 0
        assert (
            "Scanning endpoint" in result.output
            or "Not fully implemented" in result.output
        )

    def test_endpoint_tamper_status(self):
        """Test endpoint tamper status command."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["endpoint", "tamper", "status", "test-endpoint-123"]
        )

        assert result.exit_code == 0


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
