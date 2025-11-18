"""CSV export functionality."""

import csv
from io import StringIO
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pysophoscentralapi.exporters.base import BaseExporter, ExportError


class CSVExporter(BaseExporter):
    """Export data to CSV format.

    Supports header customization, delimiter options, nested object flattening,
    and batch processing with progress indicators.
    """

    def __init__(
        self,
        output_file: Path | None = None,
        delimiter: str = ",",
        flatten_nested: bool = True,
        include_headers: bool = True,
        custom_headers: dict[str, str] | None = None,
        max_depth: int = 3,
    ) -> None:
        """Initialize CSV exporter.

        Args:
            output_file: Optional output file path
            delimiter: Field delimiter (default: comma)
            flatten_nested: Flatten nested objects/dicts
            include_headers: Include header row
            custom_headers: Map field names to custom headers
            max_depth: Maximum nesting depth for flattening
        """
        super().__init__(output_file)
        self.delimiter = delimiter
        self.flatten_nested = flatten_nested
        self.include_headers = include_headers
        self.custom_headers = custom_headers or {}
        self.max_depth = max_depth

    def export(self, data: Any) -> str | None:
        """Export data to CSV.

        Args:
            data: Data to export (list of dicts or Pydantic models)

        Returns:
            CSV string if no output_file, None if written to file

        Raises:
            ExportError: If export fails
        """
        try:
            # Ensure data is a list
            if not isinstance(data, list):
                data = [data]

            if not data:
                return "" if not self.output_file else None

            # Convert Pydantic models to dicts
            rows = []
            for item in data:
                if isinstance(item, BaseModel):
                    row = item.model_dump(mode="json")
                elif isinstance(item, dict):
                    row = item
                else:
                    row = {"value": str(item)}

                # Flatten if requested
                if self.flatten_nested:
                    row = self._flatten_dict(row)

                rows.append(row)

            # Get all unique headers
            all_headers = set()
            for row in rows:
                all_headers.update(row.keys())
            headers = sorted(all_headers)

            # Apply custom headers
            display_headers = [self.custom_headers.get(h, h) for h in headers]

            # Write CSV
            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=headers,
                delimiter=self.delimiter,
                extrasaction="ignore",
            )

            if self.include_headers:
                # Write custom headers
                writer.writerow(dict(zip(headers, display_headers, strict=True)))

            # Write data rows
            for row in rows:
                # Ensure all values are strings
                clean_row = {k: self._format_value(v) for k, v in row.items()}
                writer.writerow(clean_row)

            csv_str = output.getvalue()

            # Write to file or return string
            if self.output_file:
                self._write_to_file(csv_str)
                return None
            return csv_str

        except Exception as e:
            msg = f"Failed to export to CSV: {e}"
            raise ExportError(msg) from e

    def export_batch(
        self,
        data_items: list[Any],
        batch_size: int = 100,
        show_progress: bool = False,
    ) -> str | None:
        """Export large datasets in batches with optional progress.

        Args:
            data_items: List of data items to export
            batch_size: Number of items to process at once
            show_progress: Whether to show progress indicator

        Returns:
            CSV string if no output_file, None if written to file

        Raises:
            ExportError: If export fails
        """
        if not data_items:
            return self.export([])

        try:
            all_rows = []
            all_headers = set()

            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                ) as progress:
                    task = progress.add_task(
                        f"Exporting {len(data_items)} items...",
                        total=len(data_items),
                    )

                    for i in range(0, len(data_items), batch_size):
                        batch = data_items[i : i + batch_size]
                        batch_rows, batch_headers = self._process_batch(batch)
                        all_rows.extend(batch_rows)
                        all_headers.update(batch_headers)
                        progress.update(task, advance=len(batch))
            else:
                for i in range(0, len(data_items), batch_size):
                    batch = data_items[i : i + batch_size]
                    batch_rows, batch_headers = self._process_batch(batch)
                    all_rows.extend(batch_rows)
                    all_headers.update(batch_headers)

            # Now write all rows with consistent headers
            headers = sorted(all_headers)
            display_headers = [self.custom_headers.get(h, h) for h in headers]

            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=headers,
                delimiter=self.delimiter,
                extrasaction="ignore",
            )

            if self.include_headers:
                writer.writerow(dict(zip(headers, display_headers, strict=True)))

            for row in all_rows:
                clean_row = {k: self._format_value(v) for k, v in row.items()}
                writer.writerow(clean_row)

            csv_str = output.getvalue()

            if self.output_file:
                self._write_to_file(csv_str)
                return None
            return csv_str

        except Exception as e:
            msg = f"Failed to export batch: {e}"
            raise ExportError(msg) from e

    def _process_batch(self, batch: list[Any]) -> tuple[list[dict[str, Any]], set[str]]:
        """Process a batch of items.

        Args:
            batch: List of items to process

        Returns:
            Tuple of (processed rows, header set)
        """
        rows = []
        headers = set()

        for item in batch:
            if isinstance(item, BaseModel):
                row = item.model_dump(mode="json")
            elif isinstance(item, dict):
                row = item
            else:
                row = {"value": str(item)}

            if self.flatten_nested:
                row = self._flatten_dict(row)

            rows.append(row)
            headers.update(row.keys())

        return rows, headers

    def _flatten_dict(
        self, data: dict[str, Any], parent_key: str = "", depth: int = 0
    ) -> dict[str, Any]:
        """Flatten nested dictionary.

        Args:
            data: Dictionary to flatten
            parent_key: Parent key for nested fields
            depth: Current nesting depth

        Returns:
            Flattened dictionary
        """
        if depth >= self.max_depth:
            return {parent_key: str(data)} if parent_key else {"value": str(data)}

        items: list[tuple[str, Any]] = []

        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key

            if isinstance(value, dict) and self.flatten_nested:
                items.extend(self._flatten_dict(value, new_key, depth + 1).items())
            elif isinstance(value, list) and self.flatten_nested:
                # Convert list to comma-separated string
                items.append((new_key, self._format_list(value)))
            else:
                items.append((new_key, value))

        return dict(items)

    def _format_list(self, value: list[Any]) -> str:
        """Format list as comma-separated string.

        Args:
            value: List to format

        Returns:
            Formatted string
        """
        return ", ".join(str(v) for v in value)

    def _format_value(self, value: Any) -> str:
        """Format value for CSV output.

        Args:
            value: Value to format

        Returns:
            Formatted string
        """
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (list, dict)):
            return str(value)
        return str(value)
