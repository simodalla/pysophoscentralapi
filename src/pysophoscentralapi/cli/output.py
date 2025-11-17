"""Output formatting for CLI.

This module provides output formatters for different formats (table, JSON, CSV).
"""

import csv
import json
import sys
from io import StringIO
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


class OutputFormatter:
    """Base output formatter."""

    def __init__(self, color_enabled: bool = True) -> None:
        """Initialize the output formatter.

        Args:
            color_enabled: Whether to enable colored output
        """
        self.color_enabled = color_enabled
        self.console = Console(highlight=False, force_terminal=color_enabled)

    def format_table(
        self, data: list[dict[str, Any]], title: str | None = None
    ) -> None:
        """Format data as a table.

        Args:
            data: List of dictionaries to display
            title: Optional table title
        """
        if not data:
            self.console.print("[yellow]No data to display[/yellow]")
            return

        # Create table
        table = Table(title=title, show_header=True, header_style="bold magenta")

        # Add columns from first item
        for key in data[0]:
            table.add_column(str(key).title(), style="cyan")

        # Add rows
        for item in data:
            row = []
            for value in item.values():
                if value is None:
                    row.append("[dim]None[/dim]")
                elif isinstance(value, bool):
                    row.append("[green]True[/green]" if value else "[red]False[/red]")
                else:
                    row.append(str(value))
            table.add_row(*row)

        self.console.print(table)

    def format_json(self, data: Any, indent: int = 2, compact: bool = False) -> None:
        """Format data as JSON.

        Args:
            data: Data to format as JSON
            indent: Indentation level (ignored if compact)
            compact: Whether to use compact format
        """
        if compact:
            output = json.dumps(data, separators=(",", ":"))
        else:
            output = json.dumps(data, indent=indent)

        if self.color_enabled:
            self.console.print_json(output)
        else:
            print(output)

    def format_csv(
        self,
        data: list[dict[str, Any]],
        output_file: str | None = None,
        delimiter: str = ",",
    ) -> None:
        """Format data as CSV.

        Args:
            data: List of dictionaries to format
            output_file: Optional output file path (stdout if None)
            delimiter: CSV delimiter (default: comma)
        """
        if not data:
            self.console.print("[yellow]No data to export[/yellow]")
            return

        # Get fieldnames from first item
        fieldnames = list(data[0].keys())

        # Write to file or stdout
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)

        csv_content = output.getvalue()

        if output_file:
            output_path = Path(output_file)
            with output_path.open("w") as f:
                f.write(csv_content)
            self.console.print(f"[green]Data exported to {output_file}[/green]")
        else:
            print(csv_content)

    def print_success(self, message: str) -> None:
        """Print success message.

        Args:
            message: Success message
        """
        self.console.print(f"[green]✓[/green] {message}")

    def print_error(self, message: str) -> None:
        """Print error message.

        Args:
            message: Error message
        """
        error_console = Console(stderr=True, highlight=False)
        error_console.print(f"[red]✗[/red] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def print_info(self, message: str) -> None:
        """Print info message.

        Args:
            message: Info message
        """
        self.console.print(f"[cyan]i[/cyan] {message}")
