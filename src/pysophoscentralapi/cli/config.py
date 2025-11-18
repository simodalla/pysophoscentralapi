"""Configuration commands for CLI."""

import asyncio
from pathlib import Path

import click

from pysophoscentralapi.cli.output import OutputFormatter
from pysophoscentralapi.cli.utils import handle_errors, load_config
from pysophoscentralapi.core.auth import OAuth2ClientCredentials
from pysophoscentralapi.core.config import Config


@click.group()
def config() -> None:
    """Configuration management commands."""


@config.command()
@click.option(
    "--client-id",
    prompt=True,
    help="Sophos Central API client ID",
)
@click.option(
    "--client-secret",
    prompt=True,
    hide_input=True,
    help="Sophos Central API client secret",
)
@click.option(
    "--region",
    type=click.Choice(["us", "eu", "ap", "de", "ie"]),
    default="us",
    help="Data region (default: us)",
)
@click.option(
    "--config-file",
    type=click.Path(),
    default=None,
    help="Config file path (default: ~/.config/pysophos/config.toml)",
)
def init(
    client_id: str,
    client_secret: str,
    region: str,
    config_file: str | None,
) -> None:
    """Initialize configuration interactively.

    \b
    Example:
        pysophos config init
        pysophos config init --region eu
    """
    formatter = OutputFormatter()

    # Determine config file path
    if config_file:
        config_path = Path(config_file)
    else:
        config_path = Path.home() / ".config" / "pysophos" / "config.toml"

    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Create config content
    config_content = f"""# PySophosCentralApi Configuration

[auth]
client_id = "{client_id}"
client_secret = "{client_secret}"

[api]
region = "{region}"
timeout = 30
max_retries = 3

[output]
default_format = "table"
color_enabled = true
page_size = 50

[export]
default_directory = "~/sophos-exports"
json_indent = 2
csv_delimiter = ","
"""

    # Write config file
    config_path.write_text(config_content)

    formatter.print_success(f"Configuration saved to {config_path}")
    formatter.print_info(f"Region: {region}")
    formatter.print_warning(
        "Keep your credentials secure! Consider using environment variables."
    )


@config.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    default=None,
    help="Config file path",
)
def show(config_file: str | None) -> None:
    """Show current configuration.

    \b
    Example:
        pysophos config show
    """
    formatter = OutputFormatter()

    # Determine config file path
    if config_file:
        config_path = Path(config_file)
    else:
        config_path = Path.home() / ".config" / "pysophos" / "config.toml"

    if not config_path.exists():
        formatter.print_error(f"Configuration file not found: {config_path}")
        formatter.print_info("Run 'pysophos config init' to create one")
        return

    # Read and display config (masking sensitive data)
    content = config_path.read_text()
    lines = content.split("\n")

    masked_lines = []
    for line in lines:
        if "client_secret" in line and "=" in line:
            key, _ = line.split("=", 1)
            masked_lines.append(f'{key}= "********"')
        else:
            masked_lines.append(line)

    click.echo("\n".join(masked_lines))
    formatter.print_info(f"Config file: {config_path}")


@config.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    default=None,
    help="Config file path (overrides global --config-file)",
)
@click.pass_context
@handle_errors
def test(ctx: click.Context, config_file: str | None) -> None:
    """Test API connection with current configuration.

    \b
    Example:
        pysophos config test
        pysophos config test --config-file /path/to/config.toml
    """
    formatter = OutputFormatter()
    formatter.print_info("Testing API connection...")

    # Load configuration
    # Local --config-file takes precedence over global one
    config_obj = (
        Config.from_file(Path(config_file)) if config_file else load_config()
    )

    # Test authentication
    formatter.print_info("Step 1: Testing authentication...")
    auth = OAuth2ClientCredentials(config_obj.auth)

    try:
        token = asyncio.run(auth.get_token())
        formatter.print_success("✓ Authentication successful")
        formatter.print_info(f"  Token type: {token.token_type}")
        formatter.print_info(f"  Expires at: {token.expires_at}")
    except Exception as e:
        formatter.print_error(f"✗ Authentication failed: {e}")
        return

    # Test whoami endpoint
    formatter.print_info("Step 2: Testing whoami endpoint...")
    try:
        whoami = asyncio.run(auth.whoami())
        formatter.print_success("✓ Whoami request successful")
        formatter.print_info(f"  Organization ID: {whoami.id}")
        formatter.print_info(f"  ID Type: {whoami.id_type}")
        formatter.print_info(f"  Global API: {whoami.api_host_global}")
        formatter.print_info(f"  Data Region API: {whoami.api_host_data_region}")
    except Exception as e:
        formatter.print_error(f"✗ Whoami request failed: {e}")
        return

    formatter.print_success("\n✓ All tests passed! Configuration is valid.")
