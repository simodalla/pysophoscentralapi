"""JSON export functionality."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pysophoscentralapi.exporters.base import BaseExporter, ExportError


class JSONExporter(BaseExporter):
    """Export data to JSON format.

    Supports pretty-printing, compact output, field selection,
    and batch processing with progress indicators.
    """

    def __init__(
        self,
        output_file: Path | None = None,
        indent: int | None = 2,
        compact: bool = False,
        sort_keys: bool = False,
        include_fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
    ) -> None:
        """Initialize JSON exporter.

        Args:
            output_file: Optional output file path
            indent: Indentation level (None for compact)
            compact: Use compact output (overrides indent)
            sort_keys: Sort dictionary keys alphabetically
            include_fields: Only include these fields (whitelist)
            exclude_fields: Exclude these fields (blacklist)
        """
        super().__init__(output_file)
        self.indent = None if compact else indent
        self.sort_keys = sort_keys
        self.include_fields = set(include_fields) if include_fields else None
        self.exclude_fields = set(exclude_fields) if exclude_fields else None

    def export(self, data: Any) -> str | None:
        """Export data to JSON.

        Args:
            data: Data to export (dict, list, or Pydantic model)

        Returns:
            JSON string if no output_file, None if written to file

        Raises:
            ExportError: If export fails
        """
        try:
            # Convert Pydantic models to dict
            if isinstance(data, BaseModel):
                data = data.model_dump(mode="json")
            elif isinstance(data, list) and data and isinstance(data[0], BaseModel):
                data = [item.model_dump(mode="json") for item in data]

            # Apply field filtering
            if self.include_fields or self.exclude_fields:
                data = self._filter_fields(data)

            # Convert to JSON
            json_str = json.dumps(
                data,
                indent=self.indent,
                sort_keys=self.sort_keys,
                ensure_ascii=False,
            )

            # Write to file or return string
            if self.output_file:
                self._write_to_file(json_str)
                return None
            return json_str

        except (TypeError, ValueError) as e:
            msg = f"Failed to export to JSON: {e}"
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
            batch_size: Number of items to process at once (for memory efficiency)
            show_progress: Whether to show progress indicator

        Returns:
            JSON string if no output_file, None if written to file

        Raises:
            ExportError: If export fails
        """
        if not data_items:
            return self.export([])

        try:
            all_data = []

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
                        all_data.extend(self._process_batch(batch))
                        progress.update(task, advance=len(batch))
            else:
                for i in range(0, len(data_items), batch_size):
                    batch = data_items[i : i + batch_size]
                    all_data.extend(self._process_batch(batch))

            return self.export(all_data)

        except Exception as e:
            msg = f"Failed to export batch: {e}"
            raise ExportError(msg) from e

    def _process_batch(self, batch: list[Any]) -> list[dict[str, Any]]:
        """Process a batch of items.

        Args:
            batch: List of items to process

        Returns:
            List of processed dictionaries
        """
        processed = []
        for item in batch:
            if isinstance(item, BaseModel):
                processed.append(item.model_dump(mode="json"))
            elif isinstance(item, dict):
                processed.append(item)
            else:
                processed.append({"value": item})
        return processed

    def _filter_fields(self, data: Any) -> Any:
        """Filter fields based on include/exclude lists.

        Args:
            data: Data to filter

        Returns:
            Filtered data
        """
        if isinstance(data, dict):
            return self._filter_dict(data)
        if isinstance(data, list):
            return [self._filter_fields(item) for item in data]
        return data

    def _filter_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter a dictionary's fields.

        Args:
            data: Dictionary to filter

        Returns:
            Filtered dictionary
        """
        result = {}
        for key, value in data.items():
            # Apply include filter
            if self.include_fields and key not in self.include_fields:
                continue

            # Apply exclude filter
            if self.exclude_fields and key in self.exclude_fields:
                continue

            result[key] = value

        return result
