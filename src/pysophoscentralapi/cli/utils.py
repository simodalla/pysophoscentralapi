"""CLI utilities and helper functions."""

import asyncio
import sys
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any

import click

from pysophoscentralapi.cli.output import OutputFormatter
from pysophoscentralapi.core.auth import OAuth2ClientCredentials
from pysophoscentralapi.core.config import Config
from pysophoscentralapi.core.exceptions import (
    AuthenticationError,
    SophosAPIException,
)
from pysophoscentralapi.sync.client import HTTPClientSync
from pysophoscentralapi.sync.common import CommonAPISync
from pysophoscentralapi.sync.endpoint import EndpointAPISync


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle CLI errors gracefully.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError as e:
            formatter = OutputFormatter()
            formatter.print_error(f"Authentication failed: {e}")
            sys.exit(1)
        except SophosAPIException as e:
            formatter = OutputFormatter()
            formatter.print_error(f"API error: {e}")
            if hasattr(e, "status_code"):
                formatter.print_info(f"Status code: {e.status_code}")
            sys.exit(1)
        except Exception as e:
            formatter = OutputFormatter()
            formatter.print_error(f"Unexpected error: {e}")
            if "--debug" in sys.argv or "-d" in sys.argv:
                raise
            sys.exit(1)

    return wrapper


def _extract_items(data: Any) -> list:
    """Extract items from various data formats."""
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    if isinstance(data, list):
        return data
    return [data]


def _convert_to_dicts(items: list) -> list[dict]:
    """Convert items to dictionaries."""
    dict_items = []
    for item in items:
        if hasattr(item, "model_dump"):
            dict_items.append(item.model_dump())
        elif isinstance(item, dict):
            dict_items.append(item)
        else:
            dict_items.append({"value": str(item)})
    return dict_items


def format_output(
    data: Any,
    output_format: str,
    output_file: str | None = None,
    color: bool = True,
) -> None:
    """Format and output data according to specified format.

    Args:
        data: Data to output
        output_format: Output format (table, json, csv)
        output_file: Optional output file for CSV
        color: Whether to enable colored output
    """
    formatter = OutputFormatter(color_enabled=color)

    if output_format == "json":
        formatter.format_json(data)
    elif output_format == "csv":
        items = _extract_items(data)
        dict_items = _convert_to_dicts(items)
        formatter.format_csv(dict_items, output_file)
    elif output_format == "table":
        items = _extract_items(data)
        dict_items = _convert_to_dicts(items)
        formatter.format_table(dict_items)
    else:
        click.echo(f"Unknown output format: {output_format}", err=True)
        sys.exit(1)


# Common CLI options
def add_output_options(func: Callable) -> Callable:
    """Add common output options to a command.

    Args:
        func: Command function to decorate

    Returns:
        Decorated function with output options
    """
    func = click.option(
        "--no-color",
        is_flag=True,
        default=False,
        help="Disable colored output",
    )(func)
    func = click.option(
        "--output-file",
        "-f",
        type=click.Path(),
        default=None,
        help="Output file (CSV only)",
    )(func)
    return click.option(
        "--output",
        "-o",
        type=click.Choice(["table", "json", "csv"]),
        default="table",
        help="Output format",
    )(func)


def add_sync_option(func: Callable) -> Callable:
    """Add --sync option to a command.

    Args:
        func: Command function to decorate

    Returns:
        Decorated function with sync option
    """
    return click.option(
        "--sync",
        is_flag=True,
        default=False,
        help="Use synchronous mode",
    )(func)


@contextmanager
def create_endpoint_api_sync(config: Config):
    """Create a sync Endpoint API client from config.

    Args:
        config: Configuration object

    Yields:
        EndpointAPISync: Configured sync endpoint API client
    """
    # Create auth provider
    auth = OAuth2ClientCredentials(config.auth)

    # Get whoami to determine base URL
    whoami_response = asyncio.run(auth.whoami())
    base_url = whoami_response.api_hosts.dataRegion

    # Create HTTP client and API
    with HTTPClientSync(
        base_url=base_url,
        auth_provider=auth,
        timeout=config.api.timeout,
        max_retries=config.api.max_retries,
    ) as http_client:
        yield EndpointAPISync(http_client)


@contextmanager
def create_common_api_sync(config: Config):
    """Create a sync Common API client from config.

    Args:
        config: Configuration object

    Yields:
        CommonAPISync: Configured sync common API client
    """
    # Create auth provider
    auth = OAuth2ClientCredentials(config.auth)

    # Get whoami to determine base URL
    whoami_response = asyncio.run(auth.whoami())
    base_url = whoami_response.api_hosts.dataRegion

    # Create HTTP client and API
    with HTTPClientSync(
        base_url=base_url,
        auth_provider=auth,
        timeout=config.api.timeout,
        max_retries=config.api.max_retries,
    ) as http_client:
        yield CommonAPISync(http_client)
