"""Endpoint API CLI commands."""

import asyncio

import click

from pysophoscentralapi.api.endpoint import EndpointAPI
from pysophoscentralapi.api.endpoint.models import EndpointFilters, HealthStatus
from pysophoscentralapi.cli.output import OutputFormatter
from pysophoscentralapi.cli.utils import (
    add_output_options,
    add_sync_option,
    handle_errors,
)
from pysophoscentralapi.core.config import Config
from pysophoscentralapi.sync.endpoint import EndpointAPISync


@click.group()
def endpoint() -> None:
    """Endpoint API commands."""


@endpoint.command("list")
@add_output_options
@add_sync_option
@click.option(
    "--health-status",
    type=click.Choice(["good", "suspicious", "bad", "unknown"]),
    help="Filter by health status",
)
@click.option(
    "--endpoint-type",
    type=click.Choice(["computer", "server", "securityVm"]),
    help="Filter by endpoint type",
)
@click.option(
    "--page-size",
    type=int,
    default=50,
    help="Number of items per page (1-1000)",
)
@click.option(
    "--all-pages",
    is_flag=True,
    default=False,
    help="Fetch all pages",
)
@handle_errors
def endpoint_list(
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
    health_status: str | None,
    endpoint_type: str | None,
    page_size: int,
    all_pages: bool,
) -> None:
    """List endpoints with optional filtering.

    \b
    Examples:
        pysophos endpoint list
        pysophos endpoint list --health-status bad
        pysophos endpoint list --endpoint-type server --output json
        pysophos endpoint list --all-pages --output csv -f endpoints.csv
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Build filters
    filters = None
    if health_status or endpoint_type:
        filters = EndpointFilters()
        if health_status:
            filters.health_status = [HealthStatus(health_status)]
        if endpoint_type:
            filters.type = endpoint_type

    # Fetch data
    if sync:
        with EndpointAPISync(config) as api:
            if all_pages:
                endpoints = []
                for endpoint in api.paginate(page_size=page_size, filters=filters):
                    endpoints.append(endpoint)
            else:
                endpoints = api.list(page_size=page_size, filters=filters)
    else:

        async def fetch_data():
            async with EndpointAPI(config) as api:
                if all_pages:
                    endpoints = []
                    async for endpoint in api.paginate(
                        page_size=page_size, filters=filters
                    ):
                        endpoints.append(endpoint)
                    return endpoints
                return await api.list(page_size=page_size, filters=filters)

        endpoints = asyncio.run(fetch_data())

    # Convert to dict format for output
    items = [endpoint.model_dump() for endpoint in endpoints]
    data = {"items": items}

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv(items, output_file)
    else:
        formatter.format_table(items)

    formatter.print_success(f"Found {len(items)} endpoint(s)")


@endpoint.command("get")
@add_output_options
@add_sync_option
@click.argument("endpoint_id")
@handle_errors
def endpoint_get(
    endpoint_id: str,
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
) -> None:
    """Get details for a specific endpoint.

    \b
    Examples:
        pysophos endpoint get abc-123
        pysophos endpoint get abc-123 --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Fetch data
    if sync:
        with EndpointAPISync(config) as api:
            endpoint = api.get(endpoint_id)
    else:

        async def fetch_data():
            async with EndpointAPI(config) as api:
                return await api.get(endpoint_id)

        endpoint = asyncio.run(fetch_data())

    # Convert to dict
    data = endpoint.model_dump()

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv([data], output_file)
    else:
        formatter.format_table([data])

    formatter.print_success(f"Retrieved endpoint: {endpoint.hostname}")


@endpoint.command()
@add_sync_option
@click.argument("endpoint_id")
@click.option(
    "--comment",
    help="Comment explaining the scan",
)
@handle_errors
def scan(
    endpoint_id: str,
    sync: bool,
    comment: str | None,
) -> None:
    """Trigger a scan on an endpoint.

    \b
    Examples:
        pysophos endpoint scan abc-123
        pysophos endpoint scan abc-123 --comment "Routine scan"
    """
    formatter = OutputFormatter()

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Trigger scan
    if sync:
        with EndpointAPISync(config) as api:
            api.scan(endpoint_id, comment=comment)
    else:

        async def trigger_scan():
            async with EndpointAPI(config) as api:
                await api.scan(endpoint_id, comment=comment)

        asyncio.run(trigger_scan())

    formatter.print_success(f"Scan triggered for endpoint: {endpoint_id}")
    if comment:
        formatter.print_info(f"Comment: {comment}")


@endpoint.command()
@add_sync_option
@click.argument("endpoint_id")
@click.option(
    "--comment",
    required=True,
    prompt=True,
    help="Comment explaining the isolation (required)",
)
@handle_errors
def isolate(
    endpoint_id: str,
    sync: bool,
    comment: str,
) -> None:
    """Isolate an endpoint from the network.

    \b
    Examples:
        pysophos endpoint isolate abc-123 --comment "Security incident"
        pysophos endpoint isolate abc-123
    """
    formatter = OutputFormatter()

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Isolate endpoint
    if sync:
        with EndpointAPISync(config) as api:
            api.isolate(endpoint_id, comment=comment)
    else:

        async def isolate_endpoint():
            async with EndpointAPI(config) as api:
                await api.isolate(endpoint_id, comment=comment)

        asyncio.run(isolate_endpoint())

    formatter.print_info(f"Isolating endpoint: {endpoint_id}")
    formatter.print_info(f"Comment: {comment}")

    formatter.print_success(
        f"Endpoint isolated successfully (Mode: {'sync' if sync else 'async'})"
    )


@endpoint.command()
@add_sync_option
@click.argument("endpoint_id")
@click.option(
    "--comment",
    help="Comment explaining the unisolation",
)
@handle_errors
def unisolate(
    endpoint_id: str,
    sync: bool,
    comment: str | None,
) -> None:
    """Remove isolation from an endpoint.

    \b
    Examples:
        pysophos endpoint unisolate abc-123
        pysophos endpoint unisolate abc-123 --comment "Threat remediated"
    """
    formatter = OutputFormatter()

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Unisolate endpoint
    if sync:
        with EndpointAPISync(config) as api:
            api.unisolate(endpoint_id, comment=comment)
    else:

        async def unisolate_endpoint():
            async with EndpointAPI(config) as api:
                await api.unisolate(endpoint_id, comment=comment)

        asyncio.run(unisolate_endpoint())

    formatter.print_info(f"Removing isolation from endpoint: {endpoint_id}")

    if comment:
        formatter.print_info(f"Comment: {comment}")

    formatter.print_success("Isolation removed successfully")


@endpoint.group()
def tamper() -> None:
    """Tamper protection commands."""


@tamper.command()
@add_output_options
@add_sync_option
@click.argument("endpoint_id")
@handle_errors
def status(
    endpoint_id: str,
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
) -> None:
    """Get tamper protection status for an endpoint.

    \b
    Examples:
        pysophos endpoint tamper status abc-123
        pysophos endpoint tamper status abc-123 --output json
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Get tamper protection status
    if sync:
        with EndpointAPISync(config) as api:
            tamper_status = api.get_tamper_protection(endpoint_id)
    else:

        async def get_status():
            async with EndpointAPI(config) as api:
                return await api.get_tamper_protection(endpoint_id)

        tamper_status = asyncio.run(get_status())

    # Convert to dict
    data = tamper_status.model_dump()

    # Output
    if output == "json":
        formatter.format_json(data, output_file)
    elif output == "csv":
        formatter.format_csv([data], output_file)
    else:
        formatter.format_table([data])

    formatter.print_success("Tamper protection status retrieved")


@tamper.command()
@add_sync_option
@click.argument("endpoint_id")
@click.option(
    "--enable/--disable",
    default=True,
    help="Enable or disable tamper protection",
)
@click.option(
    "--regenerate-password",
    is_flag=True,
    default=False,
    help="Regenerate tamper protection password",
)
@handle_errors
def update(
    endpoint_id: str,
    sync: bool,
    enable: bool,
    regenerate_password: bool,
) -> None:
    """Update tamper protection for an endpoint.

    \b
    Examples:
        pysophos endpoint tamper update abc-123 --enable
        pysophos endpoint tamper update abc-123 --disable
        pysophos endpoint tamper update abc-123 --enable --regenerate-password
    """
    formatter = OutputFormatter()

    # Load configuration
    try:
        config = Config.from_file()
    except FileNotFoundError:
        config = Config.from_env()

    # Update tamper protection
    if sync:
        with EndpointAPISync(config) as api:
            api.update_tamper_protection(
                endpoint_id, enabled=enable, regenerate_password=regenerate_password
            )
    else:

        async def update_tamper():
            async with EndpointAPI(config) as api:
                await api.update_tamper_protection(
                    endpoint_id, enabled=enable, regenerate_password=regenerate_password
                )

        asyncio.run(update_tamper())

    formatter.print_info(f"Updating tamper protection for: {endpoint_id}")
    formatter.print_info(f"Action: {'Enable' if enable else 'Disable'}")

    if regenerate_password:
        formatter.print_info("Regenerating password: Yes")

    formatter.print_success("Tamper protection updated successfully")
