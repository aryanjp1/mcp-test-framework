"""Tests for pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from mcp import StdioServerParameters

from pytest_mcp.fixtures import mcp_server_env, snapshot_dir


class TestFixtures:
    """Test suite for pytest fixtures."""

    def test_snapshot_dir_fixture(self, request: pytest.FixtureRequest) -> None:
        """Test snapshot_dir fixture returns correct path."""
        result = snapshot_dir(request)

        assert isinstance(result, Path)
        assert result.name == "__snapshots__"
        assert result.parent == Path(request.fspath).parent

    def test_mcp_server_env_fixture(self) -> None:
        """Test mcp_server_env fixture returns dict."""
        result = mcp_server_env()

        assert isinstance(result, dict)
        # Default should be empty
        assert len(result) == 0


# Note: Testing mcp_client fixture requires a real server
# Those tests would go in integration tests
