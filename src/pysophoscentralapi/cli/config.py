"""Configuration commands for CLI."""

from pathlib import Path

import click

from pysophoscentralapi.cli.output import OutputFormatter


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
def test() -> None:
    """Test API connection with current configuration.

    \b
    Example:
        pysophos config test
    """
    formatter = OutputFormatter()
    formatter.print_info("Testing API connection...")
    formatter.print_warning("Not implemented yet - coming soon!")
    # TODO: Implement actual API connection test
