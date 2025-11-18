"""Unit tests for progress tracker module."""

from unittest.mock import MagicMock, patch

import pytest

from pysophoscentralapi.exporters.progress import (
    ExportProgressTracker,
    with_progress,
)


class TestExportProgressTracker:
    """Test ExportProgressTracker class."""

    def test_initialization(self):
        """Test progress tracker initialization."""
        tracker = ExportProgressTracker(100, "Test Export")

        assert tracker.total == 100
        assert tracker.description == "Test Export"
        assert tracker.progress is None
        assert tracker.task_id is None

    def test_initialization_default_description(self):
        """Test initialization with default description."""
        tracker = ExportProgressTracker(50)

        assert tracker.total == 50
        assert tracker.description == "Exporting"

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_context_manager_enter(self, mock_progress_class):
        """Test context manager entry."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(100, "Test")

        with tracker as t:
            assert t is tracker
            assert tracker.progress is mock_progress
            assert tracker.task_id == "task123"

            # Verify Progress was created with correct columns
            mock_progress_class.assert_called_once()

            # Verify progress context manager was entered
            mock_progress.__enter__.assert_called_once()

            # Verify task was added with correct description
            mock_progress.add_task.assert_called_once_with(
                "Test 100 items...",
                total=100,
            )

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_context_manager_exit(self, mock_progress_class):
        """Test context manager exit."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(100)

        with tracker:
            pass

        # Verify progress context manager was exited
        mock_progress.__exit__.assert_called_once()

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_context_manager_with_exception(self, mock_progress_class):
        """Test context manager handles exceptions."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(100)

        try:
            with tracker:
                msg = "Test error"
                raise ValueError(msg)
        except ValueError:
            pass

        # Verify progress context manager was exited even with exception
        assert mock_progress.__exit__.called

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_update_default_advance(self, mock_progress_class):
        """Test update with default advance."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(100)

        with tracker:
            tracker.update()

        mock_progress.update.assert_called_with("task123", advance=1)

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_update_custom_advance(self, mock_progress_class):
        """Test update with custom advance."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(100)

        with tracker:
            tracker.update(5)
            tracker.update(10)

        # Verify both updates were called
        assert mock_progress.update.call_count == 2
        mock_progress.update.assert_any_call("task123", advance=5)
        mock_progress.update.assert_any_call("task123", advance=10)

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_update_without_context(self, mock_progress_class):
        """Test update without entering context manager."""
        tracker = ExportProgressTracker(100)

        # Should not raise error, just do nothing
        tracker.update()
        tracker.update(5)

        # Progress should not be created
        mock_progress_class.assert_not_called()

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_set_description(self, mock_progress_class):
        """Test setting description."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(100, "Initial")

        with tracker:
            tracker.set_description("Updated description")

        mock_progress.update.assert_called_with(
            "task123",
            description="Updated description",
        )

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_set_description_multiple_times(self, mock_progress_class):
        """Test setting description multiple times."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(100)

        with tracker:
            tracker.set_description("First")
            tracker.set_description("Second")
            tracker.set_description("Third")

        assert mock_progress.update.call_count == 3

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_set_description_without_context(self, mock_progress_class):
        """Test set_description without entering context manager."""
        tracker = ExportProgressTracker(100)

        # Should not raise error, just do nothing
        tracker.set_description("Test")

        mock_progress_class.assert_not_called()

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_full_workflow(self, mock_progress_class):
        """Test complete workflow with progress tracking."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(10, "Processing")

        with tracker:
            for i in range(10):
                tracker.set_description(f"Processing item {i + 1}")
                tracker.update()

        # Verify 10 updates
        assert mock_progress.update.call_count == 20  # 10 description + 10 advance

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_zero_total(self, mock_progress_class):
        """Test with zero total items."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        tracker = ExportProgressTracker(0, "Empty")

        with tracker:
            pass

        mock_progress.add_task.assert_called_once_with(
            "Empty 0 items...",
            total=0,
        )


class TestWithProgressDecorator:
    """Test with_progress decorator."""

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_decorator_basic(self, mock_progress_class):
        """Test basic decorator functionality."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        @with_progress(100, "Testing")
        def test_function():
            return "result"

        result = test_function()

        assert result == "result"
        # Verify Progress was used
        mock_progress_class.assert_called_once()
        mock_progress.__enter__.assert_called_once()
        mock_progress.__exit__.assert_called_once()

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_decorator_with_args(self, mock_progress_class):
        """Test decorator with function arguments."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        @with_progress(50)
        def add_numbers(a, b):
            return a + b

        result = add_numbers(5, 10)

        assert result == 15

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_decorator_with_kwargs(self, mock_progress_class):
        """Test decorator with keyword arguments."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        @with_progress(10, "Processing")
        def process_data(data, multiplier=2):
            return data * multiplier

        result = process_data(5, multiplier=3)

        assert result == 15

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_decorator_with_exception(self, mock_progress_class):
        """Test decorator handles exceptions."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        @with_progress(100, "Testing")
        def failing_function():
            msg = "Function error"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Function error"):
            failing_function()

        # Verify progress was still cleaned up
        mock_progress.__exit__.assert_called_once()

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_decorator_default_description(self, mock_progress_class):
        """Test decorator with default description."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        @with_progress(25)
        def test_func():
            return True

        test_func()

        # Verify default description "Processing" was used
        mock_progress.add_task.assert_called_once()
        call_args = mock_progress.add_task.call_args
        assert "Processing 25 items..." in call_args[0][0]

    @patch("pysophoscentralapi.exporters.progress.Progress")
    def test_decorator_return_value_preserved(self, mock_progress_class):
        """Test decorator preserves return values."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_progress.add_task.return_value = "task123"

        @with_progress(1, "Test")
        def get_dict():
            return {"key": "value", "number": 42}

        result = get_dict()

        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["number"] == 42
