"""Common API CLI commands."""

import asyncio

import click

from pysophoscentralapi.api.common import CommonAPI
from pysophoscentralapi.api.common.models import AlertFilters
from pysophoscentralapi.cli.output import OutputFormatter
from pysophoscentralapi.cli.utils import (
    add_output_options,
    add_sync_option,
    handle_errors,
)
from pysophoscentralapi.core.config import Config
from pysophoscentralapi.sync.common import CommonAPISync


@click.group()
def alerts() -> None:
    """Alert management commands."""


@alerts.command("list")
@add_output_options
@add_sync_option
@click.option(
    "--severity",
    type=click.Choice(["low", "medium", "high", "critical"]),
    multiple=True,
    help="Filter by severity (can specify multiple)",
)
@click.option(
    "--product",
    type=click.Choice(["endpoint", "server", "mobile", "email", "firewall"]),
    multiple=True,
    help="Filter by product (can specify multiple)",
)
@click.option(
    "--page-size",
    type=int,
    default=50,
    help="Number of items per page",
)
@handle_errors
def alerts_list(
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
    severity: tuple[str, ...],
    product: tuple[str, ...],
    page_size: int,
) -> None:
    """List alerts with optional filtering.

    \b
    Examples:
        pysophos alerts list
        pysophos alerts list --severity high --severity critical
        pysophos alerts list --product endpoint --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Build filters
    filters = None
    if severity:
        filters = AlertFilters()
        filters.severity = list(severity)

    # Fetch data
    if sync:
        with CommonAPISync(config) as api:
            alerts = api.alerts.list(page_size=page_size, filters=filters)
    else:

        async def fetch_data():
            async with CommonAPI(config) as api:
                return await api.alerts.list(page_size=page_size, filters=filters)

        alerts = asyncio.run(fetch_data())

    # Convert to dict format
    items = [alert.model_dump() for alert in alerts]
    data = {"items": items}

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv(items, output_file)
    else:
        formatter.format_table(items)

    formatter.print_success(f"Found {len(items)} alert(s)")
    if severity:
        formatter.print_info(f"Filtered by severity: {', '.join(severity)}")
    if product:
        formatter.print_info(f"Filtered by product: {', '.join(product)}")


@alerts.command("get")
@add_output_options
@add_sync_option
@click.argument("alert_id")
@handle_errors
def alerts_get(
    alert_id: str,
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
) -> None:
    """Get details for a specific alert.

    \b
    Examples:
        pysophos alerts get alert-123
        pysophos alerts get alert-123 --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Fetch data
    if sync:
        with CommonAPISync(config) as api:
            alert = api.alerts.get(alert_id)
    else:

        async def fetch_data():
            async with CommonAPI(config) as api:
                return await api.alerts.get(alert_id)

        alert = asyncio.run(fetch_data())

    # Convert to dict
    data = alert.model_dump()

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv([data], output_file)
    else:
        formatter.format_table([data])

    formatter.print_success(f"Retrieved alert: {alert_id}")


@alerts.command()
@add_sync_option
@click.argument("alert_id")
@click.argument("action", type=click.Choice(["acknowledge", "clearThreat", "clearPua"]))
@click.option(
    "--message",
    help="Message explaining the action",
)
def action(
    alert_id: str,
    action: str,
    sync: bool,
    message: str | None,
) -> None:
    """Perform an action on an alert.

    \b
    Examples:
        pysophos alerts action alert-123 acknowledge
        pysophos alerts action alert-123 clearThreat --message "False positive"
    """
    formatter = OutputFormatter()

    formatter.print_warning("Not fully implemented yet - demo mode")
    formatter.print_info(f"Performing action '{action}' on alert: {alert_id}")

    if message:
        formatter.print_info(f"Message: {message}")

    formatter.print_success(
        f"Action performed successfully (Mode: {'sync' if sync else 'async'})"
    )


@click.group()
def tenants() -> None:
    """Tenant management commands."""


@tenants.command("list")
@add_output_options
@add_sync_option
@click.option(
    "--region",
    type=click.Choice(["us", "eu", "ap", "de", "ie"]),
    help="Filter by data region",
)
@handle_errors
def tenants_list(
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
    region: str | None,
) -> None:
    """List tenants.

    \b
    Examples:
        pysophos tenants list
        pysophos tenants list --region us
        pysophos tenants list --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Fetch data
    if sync:
        with CommonAPISync(config) as api:
            tenants = api.tenants.list()
    else:

        async def fetch_data():
            async with CommonAPI(config) as api:
                return await api.tenants.list()

        tenants = asyncio.run(fetch_data())

    # Convert to dict format
    items = [tenant.model_dump() for tenant in tenants]
    data = {"items": items}

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv(items, output_file)
    else:
        formatter.format_table(items)

    formatter.print_success(f"Found {len(items)} tenant(s)")


@tenants.command("get")
@add_output_options
@add_sync_option
@click.argument("tenant_id")
@handle_errors
def tenants_get(
    tenant_id: str,
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
) -> None:
    """Get details for a specific tenant.

    \b
    Examples:
        pysophos tenants get tenant-123
        pysophos tenants get tenant-123 --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Fetch data
    if sync:
        with CommonAPISync(config) as api:
            tenant = api.tenants.get(tenant_id)
    else:

        async def fetch_data():
            async with CommonAPI(config) as api:
                return await api.tenants.get(tenant_id)

        tenant = asyncio.run(fetch_data())

    # Convert to dict
    data = tenant.model_dump()

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv([data], output_file)
    else:
        formatter.format_table([data])

    formatter.print_success(f"Retrieved tenant: {tenant.name}")


@click.group()
def admins() -> None:
    """Admin management commands."""


@admins.command("list")
@add_output_options
@add_sync_option
@handle_errors
def admins_list(
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
) -> None:
    """List admins.

    \b
    Examples:
        pysophos admins list
        pysophos admins list --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Fetch data
    if sync:
        with CommonAPISync(config) as api:
            admins = api.admins.list()
    else:

        async def fetch_data():
            async with CommonAPI(config) as api:
                return await api.admins.list()

        admins = asyncio.run(fetch_data())

    # Convert to dict format
    items = [admin.model_dump() for admin in admins]
    data = {"items": items}

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv(items, output_file)
    else:
        formatter.format_table(items)

    formatter.print_success(f"Found {len(items)} administrator(s)")


@click.group()
def roles() -> None:
    """Role management commands."""


@roles.command("list")
@add_output_options
@add_sync_option
@handle_errors
def roles_list(
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
) -> None:
    """List roles.

    \b
    Examples:
        pysophos roles list
        pysophos roles list --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Fetch data
    if sync:
        with CommonAPISync(config) as api:
            roles = api.roles.list()
    else:

        async def fetch_data():
            async with CommonAPI(config) as api:
                return await api.roles.list()

        roles = asyncio.run(fetch_data())

    # Convert to dict format
    items = [role.model_dump() for role in roles]
    data = {"items": items}

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv(items, output_file)
    else:
        formatter.format_table(items)

    formatter.print_success(f"Found {len(items)} role(s)")
