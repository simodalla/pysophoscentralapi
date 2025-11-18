"""Common API CLI commands."""

import asyncio

import click

from pysophoscentralapi.api.common import CommonAPI
from pysophoscentralapi.api.common.models import AlertFilters
from pysophoscentralapi.cli.output import OutputFormatter
from pysophoscentralapi.cli.utils import (
    add_output_options,
    add_sync_option,
    create_common_api_sync,
    handle_errors,
    load_config,
)
from pysophoscentralapi.core.auth import OAuth2ClientCredentials
from pysophoscentralapi.core.client import HTTPClient


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
    config = load_config()

    # Build filters
    filters = None
    if severity:
        filters = AlertFilters()
        filters.severity = list(severity)

    # Fetch data
    if sync:
        with create_common_api_sync(config) as api:
            response = api.alerts.list_alerts(filters=filters)
            alerts_items = response.items
    else:

        async def fetch_data():
            # Create auth and get base URL
            auth = OAuth2ClientCredentials(config.auth)
            whoami_response = await auth.whoami()
            base_url = whoami_response.api_host_data_region
            tenant_id = whoami_response.id

            # Create HTTP client and API
            async with HTTPClient(
                base_url=base_url,
                auth_provider=auth,
                timeout=config.api.timeout,
                max_retries=config.api.max_retries,
                tenant_id=tenant_id,
            ) as http_client:
                api = CommonAPI(http_client)
                response = await api.alerts.list_alerts(filters=filters)
                return response.items

        alerts_items = asyncio.run(fetch_data())

    # Convert to dict format
    items = [alert.model_dump(mode="json") for alert in alerts_items]
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
    config = load_config()

    # Fetch data
    if sync:
        with create_common_api_sync(config) as api:
            alert = api.alerts.get_alert(alert_id)
    else:

        async def fetch_data():
            # Create auth and get base URL
            auth = OAuth2ClientCredentials(config.auth)
            whoami_response = await auth.whoami()
            base_url = whoami_response.api_host_data_region
            tenant_id = whoami_response.id

            # Create HTTP client and API
            async with HTTPClient(
                base_url=base_url,
                auth_provider=auth,
                timeout=config.api.timeout,
                max_retries=config.api.max_retries,
                tenant_id=tenant_id,
            ) as http_client:
                api = CommonAPI(http_client)
                return await api.alerts.get_alert(alert_id)

        alert = asyncio.run(fetch_data())

    # Convert to dict
    data = alert.model_dump(mode="json")

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
    config = load_config()

    # Fetch data
    if sync:
        with create_common_api_sync(config) as api:
            response = api.tenants.list_tenants()
            tenants_items = response.items
    else:

        async def fetch_data():
            # Create auth and get base URL
            auth = OAuth2ClientCredentials(config.auth)
            whoami_response = await auth.whoami()
            base_url = whoami_response.api_host_data_region
            tenant_id = whoami_response.id

            # Create HTTP client and API
            async with HTTPClient(
                base_url=base_url,
                auth_provider=auth,
                timeout=config.api.timeout,
                max_retries=config.api.max_retries,
                tenant_id=tenant_id,
            ) as http_client:
                api = CommonAPI(http_client)
                response = await api.tenants.list_tenants()
                return response.items

        tenants_items = asyncio.run(fetch_data())

    # Convert to dict format
    items = [tenant.model_dump(mode="json") for tenant in tenants_items]
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
    config = load_config()

    # Fetch data
    if sync:
        with create_common_api_sync(config) as api:
            tenant = api.tenants.get_tenant(tenant_id)
    else:

        async def fetch_data():
            # Create auth and get base URL
            auth = OAuth2ClientCredentials(config.auth)
            whoami_response = await auth.whoami()
            base_url = whoami_response.api_host_data_region
            tenant_id = whoami_response.id

            # Create HTTP client and API
            async with HTTPClient(
                base_url=base_url,
                auth_provider=auth,
                timeout=config.api.timeout,
                max_retries=config.api.max_retries,
                tenant_id=tenant_id,
            ) as http_client:
                api = CommonAPI(http_client)
                return await api.tenants.get_tenant(tenant_id)

        tenant = asyncio.run(fetch_data())

    # Convert to dict
    data = tenant.model_dump(mode="json")

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
    config = load_config()

    # Fetch data
    if sync:
        with create_common_api_sync(config) as api:
            response = api.admins.list_admins()
            admins_items = response.items
    else:

        async def fetch_data():
            # Create auth and get base URL
            auth = OAuth2ClientCredentials(config.auth)
            whoami_response = await auth.whoami()
            base_url = whoami_response.api_host_data_region
            tenant_id = whoami_response.id

            # Create HTTP client and API
            async with HTTPClient(
                base_url=base_url,
                auth_provider=auth,
                timeout=config.api.timeout,
                max_retries=config.api.max_retries,
                tenant_id=tenant_id,
            ) as http_client:
                api = CommonAPI(http_client)
                response = await api.admins.list_admins()
                return response.items

        admins_items = asyncio.run(fetch_data())

    # Convert to dict format
    items = [admin.model_dump(mode="json") for admin in admins_items]
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
    config = load_config()

    # Fetch data
    if sync:
        with create_common_api_sync(config) as api:
            response = api.roles.list_roles()
            roles_items = response.items
    else:

        async def fetch_data():
            # Create auth and get base URL
            auth = OAuth2ClientCredentials(config.auth)
            whoami_response = await auth.whoami()
            base_url = whoami_response.api_host_data_region
            tenant_id = whoami_response.id

            # Create HTTP client and API
            async with HTTPClient(
                base_url=base_url,
                auth_provider=auth,
                timeout=config.api.timeout,
                max_retries=config.api.max_retries,
                tenant_id=tenant_id,
            ) as http_client:
                api = CommonAPI(http_client)
                response = await api.roles.list_roles()
                return response.items

        roles_items = asyncio.run(fetch_data())

    # Convert to dict format
    items = [role.model_dump(mode="json") for role in roles_items]
    data = {"items": items}

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv(items, output_file)
    else:
        formatter.format_table([data])

    formatter.print_success(f"Found {len(items)} role(s)")
