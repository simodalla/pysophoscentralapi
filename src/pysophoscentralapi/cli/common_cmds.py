"""Common API CLI commands."""

import click

from pysophoscentralapi.cli.output import OutputFormatter
from pysophoscentralapi.cli.utils import add_output_options, add_sync_option


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

    formatter.print_warning("Not fully implemented yet - demo mode")

    # Demo data
    demo_data = {
        "items": [
            {
                "id": "alert-1",
                "severity": "high",
                "description": "Malware detected",
                "product": "endpoint",
                "raised_at": "2025-11-17T10:00:00Z",
            },
            {
                "id": "alert-2",
                "severity": "critical",
                "description": "Ransomware activity",
                "product": "server",
                "raised_at": "2025-11-17T09:30:00Z",
            },
        ]
    }

    if output == "json":
        formatter.format_json(demo_data)
    elif output == "csv":
        formatter.format_csv(demo_data["items"], output_file)
    else:
        formatter.format_table(demo_data["items"])

    if severity:
        formatter.print_info(f"Filtered by severity: {', '.join(severity)}")
    if product:
        formatter.print_info(f"Filtered by product: {', '.join(product)}")


@alerts.command("get")
@add_output_options
@add_sync_option
@click.argument("alert_id")
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

    formatter.print_warning("Not fully implemented yet - demo mode")

    # Demo data
    demo_data = {
        "id": alert_id,
        "severity": "high",
        "description": "Malware detected on endpoint",
        "category": "malware",
        "product": "endpoint",
        "raised_at": "2025-11-17T10:00:00Z",
        "allowed_actions": ["acknowledge", "clearThreat"],
    }

    if output == "json":
        formatter.format_json(demo_data)
    else:
        formatter.format_table([demo_data])


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

    formatter.print_warning("Not fully implemented yet - demo mode")

    # Demo data
    demo_data = {
        "items": [
            {
                "id": "tenant-1",
                "name": "Company A",
                "data_region": "us",
                "billing_type": "usage",
            },
            {
                "id": "tenant-2",
                "name": "Company B",
                "data_region": "eu",
                "billing_type": "user",
            },
        ]
    }

    if output == "json":
        formatter.format_json(demo_data)
    elif output == "csv":
        formatter.format_csv(demo_data["items"], output_file)
    else:
        formatter.format_table(demo_data["items"])


@tenants.command("get")
@add_output_options
@add_sync_option
@click.argument("tenant_id")
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

    formatter.print_warning("Not fully implemented yet - demo mode")

    # Demo data
    demo_data = {
        "id": tenant_id,
        "name": "Company A",
        "data_region": "us",
        "billing_type": "usage",
        "api_host": "https://api-us.central.sophos.com",
    }

    if output == "json":
        formatter.format_json(demo_data)
    else:
        formatter.format_table([demo_data])


@click.group()
def admins() -> None:
    """Admin management commands."""


@admins.command("list")
@add_output_options
@add_sync_option
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

    formatter.print_warning("Not fully implemented yet - demo mode")

    # Demo data
    demo_data = [
        {
            "id": "admin-1",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "role": "Admin",
        },
        {
            "id": "admin-2",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "role": "SuperAdmin",
        },
    ]

    if output == "json":
        formatter.format_json(demo_data)
    elif output == "csv":
        formatter.format_csv(demo_data, output_file)
    else:
        formatter.format_table(demo_data)


@click.group()
def roles() -> None:
    """Role management commands."""


@roles.command("list")
@add_output_options
@add_sync_option
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

    formatter.print_warning("Not fully implemented yet - demo mode")

    # Demo data
    demo_data = [
        {
            "id": "role-1",
            "name": "Admin",
            "description": "Administrator role",
            "builtin": True,
        },
        {
            "id": "role-2",
            "name": "SuperAdmin",
            "description": "Super administrator role",
            "builtin": True,
        },
    ]

    if output == "json":
        formatter.format_json(demo_data)
    elif output == "csv":
        formatter.format_csv(demo_data, output_file)
    else:
        formatter.format_table(demo_data)
