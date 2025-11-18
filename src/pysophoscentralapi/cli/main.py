"""Main CLI entry point for pysophoscentralapi.

This module provides the main Click group and command structure for the CLI.
"""

import sys

import click

from pysophoscentralapi.__version__ import __version__
from pysophoscentralapi.cli.common_cmds import admins, alerts, roles, tenants
from pysophoscentralapi.cli.config import config
from pysophoscentralapi.cli.endpoint_cmds import endpoint


@click.group()
@click.version_option(version=__version__, prog_name="pysophos")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug mode with full tracebacks",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
    help="Path to configuration file (overrides default ~/.config/pysophos/config.toml)",
)
@click.pass_context
def cli(ctx: click.Context, debug: bool, config_file: str | None) -> None:
    """PySophosCentralApi - Sophos Central API Client.

    A professional Python library and CLI for interacting with
    Sophos Central APIs (Endpoint and Common APIs).

    \b
    Examples:
        pysophos config init
        pysophos endpoint list --output json
        pysophos alerts list --severity high --severity critical
        pysophos tenants list
        pysophos --config-file /path/to/config.toml endpoint list
    """
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["config_file"] = config_file


# Register command groups
cli.add_command(config)
cli.add_command(endpoint)
cli.add_command(alerts)
cli.add_command(tenants)
cli.add_command(admins)
cli.add_command(roles)


def main() -> None:
    """Main entry point for CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Fatal error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
