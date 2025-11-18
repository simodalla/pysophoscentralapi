"""Progress indicator utilities for exports."""

from collections.abc import Callable
from typing import Any

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)


class ExportProgressTracker:
    """Track and display progress for export operations.

    Provides rich progress bars with estimated time remaining.
    """

    def __init__(self, total: int, description: str = "Exporting") -> None:
        """Initialize progress tracker.

        Args:
            total: Total number of items to process
            description: Description text for progress bar
        """
        self.total = total
        self.description = description
        self.progress: Progress | None = None
        self.task_id: Any | None = None

    def __enter__(self) -> "ExportProgressTracker":
        """Enter context manager."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        )
        self.progress.__enter__()
        self.task_id = self.progress.add_task(
            f"{self.description} {self.total} items...",
            total=self.total,
        )
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        if self.progress:
            self.progress.__exit__(*args)

    def update(self, advance: int = 1) -> None:
        """Update progress.

        Args:
            advance: Number of items completed
        """
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, advance=advance)

    def set_description(self, description: str) -> None:
        """Update description text.

        Args:
            description: New description
        """
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, description=description)


def with_progress(
    total: int,
    description: str = "Processing",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to add progress tracking to a function.

    Args:
        total: Total number of items
        description: Description text

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with ExportProgressTracker(total, description):
                return func(*args, **kwargs)

        return wrapper

    return decorator
