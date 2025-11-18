"""Base exporter classes and interfaces."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseExporter(ABC):
    """Abstract base class for all exporters.

    Exporters handle converting API data to various output formats (JSON, CSV, etc.)
    and writing to files or returning formatted strings.
    """

    def __init__(self, output_file: Path | None = None) -> None:
        """Initialize exporter.

        Args:
            output_file: Optional output file path. If None, returns string.
        """
        self.output_file = output_file

    @abstractmethod
    def export(self, data: Any) -> str | None:
        """Export data to format.

        Args:
            data: Data to export (dict, list, or Pydantic model)

        Returns:
            Formatted string if no output_file, None if written to file

        Raises:
            ExportError: If export fails
        """

    @abstractmethod
    def export_batch(
        self,
        data_items: list[Any],
        batch_size: int = 100,
        show_progress: bool = False,
    ) -> str | None:
        """Export large datasets in batches.

        Args:
            data_items: List of data items to export
            batch_size: Number of items to process at once
            show_progress: Whether to show progress indicator

        Returns:
            Formatted string if no output_file, None if written to file

        Raises:
            ExportError: If export fails
        """

    def _write_to_file(self, content: str) -> None:
        """Write content to output file.

        Args:
            content: String content to write

        Raises:
            ExportError: If file write fails
        """
        if not self.output_file:
            return

        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            self.output_file.write_text(content, encoding="utf-8")
        except OSError as e:
            msg = f"Failed to write to {self.output_file}: {e}"
            raise ExportError(msg) from e


class ExportError(Exception):
    """Raised when export operation fails."""
