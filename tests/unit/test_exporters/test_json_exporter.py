"""Tests for JSON exporter."""

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from pysophoscentralapi.exporters import ExportError, JSONExporter


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""

    id: str
    name: str
    count: int


class TestJSONExporter:
    """Tests for JSONExporter."""

    def test_export_dict(self):
        """Test exporting a simple dictionary."""
        exporter = JSONExporter()
        data = {"name": "test", "value": 123}

        result = exporter.export(data)

        assert result is not None
        parsed = json.loads(result)
        assert parsed == data

    def test_export_list(self):
        """Test exporting a list of dictionaries."""
        exporter = JSONExporter()
        data = [{"id": "1", "name": "first"}, {"id": "2", "name": "second"}]

        result = exporter.export(data)

        assert result is not None
        parsed = json.loads(result)
        assert parsed == data

    def test_export_pydantic_model(self):
        """Test exporting Pydantic model."""
        exporter = JSONExporter()
        model = SampleModel(id="test-1", name="Test", count=42)

        result = exporter.export(model)

        assert result is not None
        parsed = json.loads(result)
        assert parsed["id"] == "test-1"
        assert parsed["name"] == "Test"
        assert parsed["count"] == 42

    def test_export_pydantic_list(self):
        """Test exporting list of Pydantic models."""
        exporter = JSONExporter()
        models = [
            SampleModel(id="1", name="First", count=1),
            SampleModel(id="2", name="Second", count=2),
        ]

        result = exporter.export(models)

        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["id"] == "1"
        assert parsed[1]["id"] == "2"

    def test_export_compact(self):
        """Test compact export (no indentation)."""
        exporter = JSONExporter(compact=True)
        data = {"name": "test", "value": 123}

        result = exporter.export(data)

        assert result is not None
        assert "\n" not in result  # No newlines in compact mode

    def test_export_pretty(self):
        """Test pretty-printed export."""
        exporter = JSONExporter(indent=2)
        data = {"name": "test", "value": 123}

        result = exporter.export(data)

        assert result is not None
        assert "\n" in result  # Has newlines
        assert "  " in result  # Has indentation

    def test_export_sort_keys(self):
        """Test exporting with sorted keys."""
        exporter = JSONExporter(sort_keys=True)
        data = {"zebra": 1, "alpha": 2, "middle": 3}

        result = exporter.export(data)

        assert result is not None
        # Check keys appear in sorted order
        assert result.index("alpha") < result.index("middle")
        assert result.index("middle") < result.index("zebra")

    def test_export_include_fields(self):
        """Test field inclusion filter."""
        exporter = JSONExporter(include_fields=["id", "name"])
        data = {"id": "1", "name": "test", "secret": "hidden", "count": 42}

        result = exporter.export(data)

        assert result is not None
        parsed = json.loads(result)
        assert "id" in parsed
        assert "name" in parsed
        assert "secret" not in parsed
        assert "count" not in parsed

    def test_export_exclude_fields(self):
        """Test field exclusion filter."""
        exporter = JSONExporter(exclude_fields=["secret", "internal"])
        data = {"id": "1", "name": "test", "secret": "hidden", "internal": True}

        result = exporter.export(data)

        assert result is not None
        parsed = json.loads(result)
        assert "id" in parsed
        assert "name" in parsed
        assert "secret" not in parsed
        assert "internal" not in parsed

    def test_export_to_file(self, tmp_path: Path):
        """Test exporting to file."""
        output_file = tmp_path / "output.json"
        exporter = JSONExporter(output_file=output_file)
        data = {"name": "test", "value": 123}

        result = exporter.export(data)

        # Should return None when writing to file
        assert result is None
        # File should exist
        assert output_file.exists()
        # Content should be correct
        content = json.loads(output_file.read_text())
        assert content == data

    def test_export_batch(self):
        """Test batch export."""
        exporter = JSONExporter()
        data = [{"id": str(i), "value": i} for i in range(10)]

        result = exporter.export_batch(data, batch_size=3)

        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 10
        assert parsed[0]["id"] == "0"
        assert parsed[9]["id"] == "9"

    def test_export_batch_with_progress(self):
        """Test batch export with progress indicator."""
        exporter = JSONExporter()
        data = [{"id": str(i), "value": i} for i in range(10)]

        result = exporter.export_batch(data, batch_size=3, show_progress=True)

        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 10

    def test_export_empty_list(self):
        """Test exporting empty list."""
        exporter = JSONExporter()
        result = exporter.export([])

        assert result is not None
        parsed = json.loads(result)
        assert parsed == []

    def test_export_batch_empty(self):
        """Test batch export with empty list."""
        exporter = JSONExporter()
        result = exporter.export_batch([])

        assert result is not None
        parsed = json.loads(result)
        assert parsed == []

    def test_export_invalid_data(self):
        """Test exporting invalid data raises error."""
        exporter = JSONExporter()

        # Create object that can't be JSON serialized
        class CustomClass:
            pass

        with pytest.raises(ExportError):
            exporter.export(CustomClass())
