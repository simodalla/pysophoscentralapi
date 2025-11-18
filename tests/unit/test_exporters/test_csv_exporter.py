"""Tests for CSV exporter."""

import csv
from io import StringIO
from pathlib import Path

from pydantic import BaseModel

from pysophoscentralapi.exporters import CSVExporter


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""

    id: str
    name: str
    count: int


class TestCSVExporter:
    """Tests for CSVExporter."""

    def test_export_simple_list(self):
        """Test exporting simple list of dicts."""
        exporter = CSVExporter()
        data = [{"id": "1", "name": "first"}, {"id": "2", "name": "second"}]

        result = exporter.export(data)

        assert result is not None
        lines = result.strip().split("\n")
        assert len(lines) == 3  # Header + 2 data rows

    def test_export_pydantic_models(self):
        """Test exporting Pydantic models."""
        exporter = CSVExporter()
        models = [
            SampleModel(id="1", name="First", count=10),
            SampleModel(id="2", name="Second", count=20),
        ]

        result = exporter.export(models)

        assert result is not None
        reader = csv.DictReader(StringIO(result))
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[0]["name"] == "First"
        assert rows[0]["count"] == "10"

    def test_export_no_headers(self):
        """Test exporting without headers."""
        exporter = CSVExporter(include_headers=False)
        data = [{"id": "1", "name": "first"}]

        result = exporter.export(data)

        assert result is not None
        lines = result.strip().split("\n")
        assert len(lines) == 1  # Only data row

    def test_export_custom_delimiter(self):
        """Test custom delimiter."""
        exporter = CSVExporter(delimiter="|")
        data = [{"id": "1", "name": "first"}]

        result = exporter.export(data)

        assert result is not None
        assert "|" in result
        assert "," not in result

    def test_export_custom_headers(self):
        """Test custom header names."""
        exporter = CSVExporter(custom_headers={"id": "ID", "name": "Full Name"})
        data = [{"id": "1", "name": "test"}]

        result = exporter.export(data)

        assert result is not None
        assert "ID" in result
        assert "Full Name" in result

    def test_export_flatten_nested(self):
        """Test flattening nested objects."""
        exporter = CSVExporter(flatten_nested=True)
        data = [{"id": "1", "user": {"name": "John", "age": 30}}]

        result = exporter.export(data)

        assert result is not None
        assert "user.name" in result
        assert "user.age" in result
        assert "John" in result
        assert "30" in result

    def test_export_no_flatten(self):
        """Test not flattening nested objects."""
        exporter = CSVExporter(flatten_nested=False)
        data = [{"id": "1", "user": {"name": "John"}}]

        result = exporter.export(data)

        assert result is not None
        # Nested object should be stringified
        assert "{'name': 'John'}" in result or '{"name": "John"}' in result

    def test_export_list_values(self):
        """Test handling list values."""
        exporter = CSVExporter()
        data = [{"id": "1", "tags": ["tag1", "tag2", "tag3"]}]

        result = exporter.export(data)

        assert result is not None
        # List should be comma-separated
        assert "tag1, tag2, tag3" in result

    def test_export_to_file(self, tmp_path: Path):
        """Test exporting to file."""
        output_file = tmp_path / "output.csv"
        exporter = CSVExporter(output_file=output_file)
        data = [{"id": "1", "name": "test"}]

        result = exporter.export(data)

        # Should return None when writing to file
        assert result is None
        # File should exist
        assert output_file.exists()
        # Content should be correct
        content = output_file.read_text()
        assert "id" in content
        assert "test" in content

    def test_export_batch(self):
        """Test batch export."""
        exporter = CSVExporter()
        data = [{"id": str(i), "value": i * 10} for i in range(10)]

        result = exporter.export_batch(data, batch_size=3)

        assert result is not None
        reader = csv.DictReader(StringIO(result))
        rows = list(reader)
        assert len(rows) == 10

    def test_export_batch_with_progress(self):
        """Test batch export with progress."""
        exporter = CSVExporter()
        data = [{"id": str(i), "value": i} for i in range(10)]

        result = exporter.export_batch(data, batch_size=3, show_progress=True)

        assert result is not None
        reader = csv.DictReader(StringIO(result))
        rows = list(reader)
        assert len(rows) == 10

    def test_export_empty_list(self):
        """Test exporting empty list."""
        exporter = CSVExporter()
        result = exporter.export([])

        assert result == ""

    def test_export_batch_empty(self):
        """Test batch export with empty list."""
        exporter = CSVExporter()
        result = exporter.export_batch([])

        assert result == ""

    def test_export_single_item(self):
        """Test exporting single item (not in list)."""
        exporter = CSVExporter()
        data = {"id": "1", "name": "single"}

        result = exporter.export(data)

        assert result is not None
        reader = csv.DictReader(StringIO(result))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["id"] == "1"

    def test_export_none_values(self):
        """Test handling None values."""
        exporter = CSVExporter()
        data = [{"id": "1", "name": None, "value": "test"}]

        result = exporter.export(data)

        assert result is not None
        # None should be empty string
        reader = csv.DictReader(StringIO(result))
        rows = list(reader)
        assert rows[0]["name"] == ""

    def test_export_boolean_values(self):
        """Test handling boolean values."""
        exporter = CSVExporter()
        data = [{"id": "1", "active": True, "deleted": False}]

        result = exporter.export(data)

        assert result is not None
        assert "true" in result
        assert "false" in result

    def test_export_max_depth(self):
        """Test maximum nesting depth."""
        exporter = CSVExporter(flatten_nested=True, max_depth=2)
        data = [{"a": {"b": {"c": {"d": "deep"}}}}]

        result = exporter.export(data)

        assert result is not None
        # Should stop flattening at max_depth
