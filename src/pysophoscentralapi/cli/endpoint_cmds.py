"""Endpoint API CLI commands."""

import asyncio
from datetime import datetime

import click

from pysophoscentralapi.api.endpoint import EndpointAPI
from pysophoscentralapi.api.endpoint.models import (
    EndpointFilters,
    EndpointType,
    HealthStatus,
    LockdownStatus,
)
from pysophoscentralapi.cli.output import OutputFormatter
from pysophoscentralapi.cli.utils import (
    add_output_options,
    add_sync_option,
    create_endpoint_api_sync,
    handle_errors,
    load_config,
)
from pysophoscentralapi.core.auth import OAuth2ClientCredentials
from pysophoscentralapi.core.client import HTTPClient


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
    "--lockdown-status",
    type=click.Choice(
        [
            "creatingWhitelist",
            "installing",
            "locked",
            "notInstalled",
            "registering",
            "starting",
            "stopping",
            "unavailable",
            "uninstalled",
            "unlocked",
        ]
    ),
    help="Filter by lockdown status",
)
@click.option(
    "--tamper-protection/--no-tamper-protection",
    default=None,
    help="Filter by tamper protection status",
)
@click.option(
    "--hostname-contains",
    type=str,
    help="Filter by hostname substring",
)
@click.option(
    "--last-seen-before",
    type=str,
    help="Filter endpoints last seen before (ISO 8601: YYYY-MM-DDTHH:MM:SS, assumed UTC)",
)
@click.option(
    "--last-seen-after",
    type=str,
    help="Filter endpoints last seen after (ISO 8601: YYYY-MM-DDTHH:MM:SS, assumed UTC)",
)
@click.option(
    "--ids",
    type=str,
    help="Filter by endpoint IDs (comma-separated)",
)
@click.option(
    "--ip-addresses",
    type=str,
    help="Filter by IP addresses (comma-separated)",
)
@click.option(
    "--mac-addresses",
    type=str,
    help="Filter by MAC addresses (comma-separated)",
)
@click.option(
    "--search",
    type=str,
    help="Search query across endpoint fields",
)
@click.option(
    "--view",
    type=click.Choice(["basic", "summary", "full"]),
    default="summary",
    help="Detail level for results (default: summary)",
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
def endpoint_list(  # noqa: PLR0912, PLR0915
    output: str,
    output_file: str | None,
    no_color: bool,
    sync: bool,
    health_status: str | None,
    endpoint_type: str | None,
    lockdown_status: str | None,
    tamper_protection: bool | None,
    hostname_contains: str | None,
    last_seen_before: str | None,
    last_seen_after: str | None,
    ids: str | None,
    ip_addresses: str | None,
    mac_addresses: str | None,
    search: str | None,
    view: str,
    page_size: int,
    all_pages: bool,
) -> None:
    """List endpoints with optional filtering.

    \b
    Examples:
        # Basic listing
        pysophos endpoint list

        # Filter by health status
        pysophos endpoint list --health-status bad

        # Filter by endpoint type and tamper protection
        pysophos endpoint list --endpoint-type server --tamper-protection

        # Search by hostname
        pysophos endpoint list --hostname-contains "web-server"

        # Filter by last seen date
        pysophos endpoint list --last-seen-after 2024-01-01T00:00:00

        # Multiple filters with full detail view
        pysophos endpoint list --health-status bad --view full --output json

        # Export all pages to CSV
        pysophos endpoint list --all-pages --output csv -f endpoints.csv
    """
    formatter = OutputFormatter(color_enabled=not no_color)

    # Load configuration
    config = load_config()

    # Build filters - create if any filter is specified
    filters = None
    if any(
        [
            health_status,
            endpoint_type,
            lockdown_status,
            tamper_protection is not None,
            hostname_contains,
            last_seen_before,
            last_seen_after,
            ids,
            ip_addresses,
            mac_addresses,
            search,
        ]
    ):
        filters = EndpointFilters()
        filters.view = view
        filters.page_size = page_size

        # Enum filters
        if health_status:
            filters.health_status = HealthStatus(health_status)
        if endpoint_type:
            filters.type = EndpointType(endpoint_type)
        if lockdown_status:
            filters.lockdown_status = LockdownStatus(lockdown_status)

        # Boolean filter
        if tamper_protection is not None:
            filters.tamper_protection_enabled = tamper_protection

        # String filters
        if hostname_contains:
            filters.hostname_contains = hostname_contains
        if search:
            filters.search = search

        # Date filters
        if last_seen_before:
            filters.last_seen_before = datetime.fromisoformat(last_seen_before)
        if last_seen_after:
            filters.last_seen_after = datetime.fromisoformat(last_seen_after)

        # List filters (comma-separated strings)
        if ids:
            filters.ids = [id.strip() for id in ids.split(",")]
        if ip_addresses:
            filters.ip_addresses = [ip.strip() for ip in ip_addresses.split(",")]
        if mac_addresses:
            filters.mac_addresses = [mac.strip() for mac in mac_addresses.split(",")]
    else:
        # No filters specified, but still set view and page_size
        filters = EndpointFilters()
        filters.view = view
        filters.page_size = page_size

    # Fetch data
    if sync:
        with create_endpoint_api_sync(config) as api:
            if all_pages:
                endpoints = []
                for endpoint in api.paginate(filters=filters):
                    endpoints.append(endpoint)
            else:
                response = api.list_endpoints(filters=filters)
                endpoints = response.items
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
                api = EndpointAPI(http_client)
                if all_pages:
                    endpoints = []
                    async for endpoint in api.paginate(filters=filters):
                        endpoints.append(endpoint)
                    return endpoints
                response = await api.list_endpoints(filters=filters)
                return response.items

        endpoints = asyncio.run(fetch_data())

    # Convert to dict format for output
    items = [endpoint.model_dump(mode="json") for endpoint in endpoints]
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
    config = load_config()

    # Fetch data
    if sync:
        with create_endpoint_api_sync(config) as api:
            endpoint = api.get_endpoint(endpoint_id)
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
                api = EndpointAPI(http_client)
                return await api.get_endpoint(endpoint_id)

        endpoint = asyncio.run(fetch_data())

    # Convert to dict
    data = endpoint.model_dump(mode="json")

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
    config = load_config()

    # Trigger scan
    if sync:
        with create_endpoint_api_sync(config) as api:
            api.scan_endpoint(endpoint_id, comment=comment)
    else:

        async def trigger_scan():
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
                api = EndpointAPI(http_client)
                await api.scan_endpoint(endpoint_id, comment=comment)

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
    config = load_config()

    # Isolate endpoint
    if sync:
        with create_endpoint_api_sync(config) as api:
            api.isolate_endpoint(endpoint_id, comment=comment)
    else:

        async def isolate_endpoint_async():
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
                api = EndpointAPI(http_client)
                await api.isolate_endpoint(endpoint_id, comment=comment)

        asyncio.run(isolate_endpoint_async())

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
    config = load_config()

    # Unisolate endpoint
    if sync:
        with create_endpoint_api_sync(config) as api:
            api.unisolate_endpoint(endpoint_id, comment=comment)
    else:

        async def unisolate_endpoint_async():
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
                api = EndpointAPI(http_client)
                await api.unisolate_endpoint(endpoint_id, comment=comment)

        asyncio.run(unisolate_endpoint_async())

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
    config = load_config()

    # Get tamper protection status
    if sync:
        with create_endpoint_api_sync(config) as api:
            tamper_status = api.get_tamper_protection(endpoint_id)
    else:

        async def get_status():
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
                api = EndpointAPI(http_client)
                return await api.get_tamper_protection(endpoint_id)

        tamper_status = asyncio.run(get_status())

    # Convert to dict
    data = tamper_status.model_dump(mode="json")

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
    config = load_config()

    # Update tamper protection
    if sync:
        with create_endpoint_api_sync(config) as api:
            api.update_tamper_protection(
                endpoint_id, enabled=enable, regenerate_password=regenerate_password
            )
    else:

        async def update_tamper():
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
                api = EndpointAPI(http_client)
                await api.update_tamper_protection(
                    endpoint_id, enabled=enable, regenerate_password=regenerate_password
                )

        asyncio.run(update_tamper())

    formatter.print_info(f"Updating tamper protection for: {endpoint_id}")
    formatter.print_info(f"Action: {'Enable' if enable else 'Disable'}")

    if regenerate_password:
        formatter.print_info("Regenerating password: Yes")

    formatter.print_success("Tamper protection updated successfully")
