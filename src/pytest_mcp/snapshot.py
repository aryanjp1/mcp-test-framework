"""Snapshot testing support for MCP tool outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


class SnapshotHelper:
    """
    Helper class for snapshot testing MCP tool outputs.

    Snapshots allow you to save tool outputs and compare them across test runs,
    making it easy to detect unexpected changes in behavior.

    Example:
        >>> async def test_tool_output(mcp_client, snapshot):
        ...     result = await mcp_client.call_tool("get_user", {"id": 1})
        ...     snapshot.assert_match(result, "get_user_response")
    """

    def __init__(self, request: pytest.FixtureRequest, snapshot_dir: Path) -> None:
        """
        Initialize snapshot helper.

        Args:
            request: Pytest fixture request
            snapshot_dir: Directory to store snapshots
        """
        self.request = request
        self.snapshot_dir = snapshot_dir
        self.update_snapshots = request.config.getoption("--mcp-update-snapshots", False)

        # Create snapshot directory if it doesn't exist
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _get_snapshot_path(self, snapshot_name: str) -> Path:
        """
        Get the path for a snapshot file.

        Args:
            snapshot_name: Name of the snapshot

        Returns:
            Path to snapshot file
        """
        test_name = self.request.node.name
        # Clean test name (remove parameters)
        test_name = test_name.split("[")[0]

        return self.snapshot_dir / f"{test_name}__{snapshot_name}.json"

    def _serialize(self, value: Any) -> str:
        """
        Serialize a value to JSON string.

        Args:
            value: Value to serialize

        Returns:
            JSON string
        """
        # Handle MCP-specific types
        if hasattr(value, "model_dump"):
            # Pydantic model
            value = value.model_dump()
        elif hasattr(value, "dict"):
            # Older pydantic or dict-like
            value = value.dict()

        return json.dumps(value, indent=2, sort_keys=True, default=str)

    def _deserialize(self, json_str: str) -> Any:
        """
        Deserialize a JSON string.

        Args:
            json_str: JSON string

        Returns:
            Deserialized value
        """
        return json.loads(json_str)

    def assert_match(
        self,
        value: Any,
        snapshot_name: str,
        *,
        update: bool | None = None,
    ) -> None:
        """
        Assert that a value matches the saved snapshot.

        On first run or when update=True, saves the snapshot.
        On subsequent runs, compares against saved snapshot.

        Args:
            value: Value to snapshot
            snapshot_name: Name for this snapshot
            update: Override global update_snapshots setting

        Raises:
            AssertionError: If value doesn't match snapshot

        Example:
            >>> snapshot.assert_match(result, "api_response")
        """
        snapshot_path = self._get_snapshot_path(snapshot_name)
        should_update = update if update is not None else self.update_snapshots

        # Serialize the value
        actual_json = self._serialize(value)

        if should_update or not snapshot_path.exists():
            # Save/update snapshot
            snapshot_path.write_text(actual_json)
            if should_update:
                pytest.skip(f"Updated snapshot: {snapshot_name}")
            return

        # Load and compare snapshot
        expected_json = snapshot_path.read_text()
        expected = self._deserialize(expected_json)
        actual = self._deserialize(actual_json)

        if actual != expected:
            raise AssertionError(
                f"Snapshot mismatch for '{snapshot_name}'.\n"
                f"Expected:\n{expected_json}\n\n"
                f"Actual:\n{actual_json}\n\n"
                f"To update snapshots, run with --mcp-update-snapshots"
            )

    def assert_match_json(
        self,
        value: dict[str, Any] | list[Any],
        snapshot_name: str,
        *,
        update: bool | None = None,
    ) -> None:
        """
        Assert that a JSON-serializable value matches the saved snapshot.

        This is a convenience method for dict/list values.

        Args:
            value: JSON-serializable value
            snapshot_name: Name for this snapshot
            update: Override global update_snapshots setting

        Raises:
            AssertionError: If value doesn't match snapshot
        """
        self.assert_match(value, snapshot_name, update=update)

    def assert_match_text(
        self,
        text: str,
        snapshot_name: str,
        *,
        update: bool | None = None,
    ) -> None:
        """
        Assert that text content matches the saved snapshot.

        Args:
            text: Text content to snapshot
            snapshot_name: Name for this snapshot
            update: Override global update_snapshots setting

        Raises:
            AssertionError: If text doesn't match snapshot
        """
        snapshot_path = self._get_snapshot_path(snapshot_name)
        # Use .txt extension for text snapshots
        snapshot_path = snapshot_path.with_suffix(".txt")

        should_update = update if update is not None else self.update_snapshots

        if should_update or not snapshot_path.exists():
            snapshot_path.write_text(text)
            if should_update:
                pytest.skip(f"Updated snapshot: {snapshot_name}")
            return

        expected_text = snapshot_path.read_text()
        if text != expected_text:
            raise AssertionError(
                f"Text snapshot mismatch for '{snapshot_name}'.\n"
                f"Expected:\n{expected_text}\n\n"
                f"Actual:\n{text}\n\n"
                f"To update snapshots, run with --mcp-update-snapshots"
            )

    def get_snapshot(self, snapshot_name: str) -> Any | None:
        """
        Get a saved snapshot value without asserting.

        Args:
            snapshot_name: Name of the snapshot

        Returns:
            Snapshot value if exists, None otherwise
        """
        snapshot_path = self._get_snapshot_path(snapshot_name)
        if not snapshot_path.exists():
            return None

        json_str = snapshot_path.read_text()
        return self._deserialize(json_str)

    def delete_snapshot(self, snapshot_name: str) -> None:
        """
        Delete a saved snapshot.

        Args:
            snapshot_name: Name of the snapshot to delete
        """
        snapshot_path = self._get_snapshot_path(snapshot_name)
        if snapshot_path.exists():
            snapshot_path.unlink()

    def list_snapshots(self) -> list[str]:
        """
        List all snapshots for the current test.

        Returns:
            List of snapshot names
        """
        test_name = self.request.node.name.split("[")[0]
        pattern = f"{test_name}__*.json"

        snapshots = []
        for path in self.snapshot_dir.glob(pattern):
            # Extract snapshot name from filename
            name = path.stem.replace(f"{test_name}__", "")
            snapshots.append(name)

        return sorted(snapshots)
