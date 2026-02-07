"""Tests for snapshot testing functionality."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pytest_mcp.snapshot import SnapshotHelper


class TestSnapshotHelper:
    """Test suite for SnapshotHelper."""

    @pytest.fixture
    def temp_snapshot_dir(self, tmp_path: Path) -> Path:
        """Create a temporary snapshot directory."""
        snapshot_dir = tmp_path / "__snapshots__"
        snapshot_dir.mkdir()
        return snapshot_dir

    @pytest.fixture
    def snapshot_helper(
        self, request: pytest.FixtureRequest, temp_snapshot_dir: Path
    ) -> SnapshotHelper:
        """Create a SnapshotHelper instance for testing."""
        return SnapshotHelper(request, temp_snapshot_dir)

    def test_get_snapshot_path(self, snapshot_helper: SnapshotHelper) -> None:
        """Test snapshot path generation."""
        path = snapshot_helper._get_snapshot_path("test_snapshot")
        assert path.name.endswith("__test_snapshot.json")

    def test_serialize_dict(self, snapshot_helper: SnapshotHelper) -> None:
        """Test serialization of dictionary."""
        data = {"key": "value", "number": 42}
        serialized = snapshot_helper._serialize(data)

        # Should be valid JSON
        parsed = json.loads(serialized)
        assert parsed == data

    def test_serialize_with_model_dump(self, snapshot_helper: SnapshotHelper, mocker) -> None:
        """Test serialization of Pydantic models."""
        # Mock a Pydantic model
        mock_model = mocker.Mock()
        mock_model.model_dump.return_value = {"id": 1, "name": "test"}

        serialized = snapshot_helper._serialize(mock_model)
        parsed = json.loads(serialized)

        assert parsed == {"id": 1, "name": "test"}

    def test_assert_match_creates_snapshot(
        self, snapshot_helper: SnapshotHelper, temp_snapshot_dir: Path
    ) -> None:
        """Test that assert_match creates a snapshot on first run."""
        data = {"test": "data"}
        snapshot_helper.assert_match(data, "first_run")

        # Check snapshot was created
        snapshots = list(temp_snapshot_dir.glob("*.json"))
        assert len(snapshots) == 1
        assert "first_run" in snapshots[0].name

    def test_assert_match_compares_on_second_run(
        self, snapshot_helper: SnapshotHelper, temp_snapshot_dir: Path
    ) -> None:
        """Test that assert_match compares on subsequent runs."""
        data = {"test": "data"}

        # First run - create snapshot
        snapshot_helper.assert_match(data, "compare_test")

        # Second run - should compare and pass
        snapshot_helper.assert_match(data, "compare_test")

    def test_assert_match_fails_on_mismatch(
        self, snapshot_helper: SnapshotHelper, temp_snapshot_dir: Path
    ) -> None:
        """Test that assert_match fails when data doesn't match."""
        original_data = {"test": "data"}
        changed_data = {"test": "changed"}

        # Create snapshot
        snapshot_helper.assert_match(original_data, "mismatch_test")

        # Try with different data
        with pytest.raises(AssertionError, match="Snapshot mismatch"):
            snapshot_helper.assert_match(changed_data, "mismatch_test")

    def test_assert_match_text(
        self, snapshot_helper: SnapshotHelper, temp_snapshot_dir: Path
    ) -> None:
        """Test text snapshot functionality."""
        text = "Hello, World!\nThis is a test."

        # Create snapshot
        snapshot_helper.assert_match_text(text, "text_snapshot")

        # Verify file was created with .txt extension
        txt_files = list(temp_snapshot_dir.glob("*.txt"))
        assert len(txt_files) == 1

        # Second run should pass
        snapshot_helper.assert_match_text(text, "text_snapshot")

    def test_get_snapshot(
        self, snapshot_helper: SnapshotHelper, temp_snapshot_dir: Path
    ) -> None:
        """Test getting saved snapshot."""
        data = {"test": "data"}

        # Create snapshot
        snapshot_helper.assert_match(data, "get_test")

        # Get snapshot
        retrieved = snapshot_helper.get_snapshot("get_test")
        assert retrieved == data

    def test_get_snapshot_returns_none_if_not_exists(
        self, snapshot_helper: SnapshotHelper
    ) -> None:
        """Test that get_snapshot returns None for non-existent snapshots."""
        result = snapshot_helper.get_snapshot("nonexistent")
        assert result is None

    def test_delete_snapshot(
        self, snapshot_helper: SnapshotHelper, temp_snapshot_dir: Path
    ) -> None:
        """Test deleting a snapshot."""
        data = {"test": "data"}

        # Create snapshot
        snapshot_helper.assert_match(data, "delete_test")
        assert len(list(temp_snapshot_dir.glob("*.json"))) == 1

        # Delete snapshot
        snapshot_helper.delete_snapshot("delete_test")
        assert len(list(temp_snapshot_dir.glob("*.json"))) == 0

    def test_list_snapshots(
        self, snapshot_helper: SnapshotHelper, temp_snapshot_dir: Path
    ) -> None:
        """Test listing snapshots."""
        # Create multiple snapshots
        snapshot_helper.assert_match({"test": 1}, "snapshot1")
        snapshot_helper.assert_match({"test": 2}, "snapshot2")

        # List snapshots
        snapshots = snapshot_helper.list_snapshots()
        assert "snapshot1" in snapshots
        assert "snapshot2" in snapshots
