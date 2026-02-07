"""
pytest-mcp: A pytest plugin for testing MCP (Model Context Protocol) servers.

This library provides a comprehensive testing framework for MCP servers,
including mock clients, fixtures, assertions, and snapshot testing.

Example:
    >>> import pytest
    >>> from pytest_mcp import MockMCPClient, assert_tool_exists
    >>>
    >>> @pytest.fixture
    >>> def mcp_server():
    ...     return {"command": "python", "args": ["server.py"]}
    >>>
    >>> async def test_my_tool(mcp_client):
    ...     await assert_tool_exists(mcp_client, "my_tool")
    ...     result = await mcp_client.call_tool("my_tool", {"arg": "value"})
    ...     assert result is not None
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = [
    # Client
    "MockMCPClient",
    "create_mock_client",
    # Server
    "MCPTestServer",
    "MCPTestServerFactory",
    # Assertions
    "assert_tool_exists",
    "assert_tool_count",
    "assert_tool_output_matches",
    "assert_tool_returns_error",
    "assert_resource_exists",
    "assert_resource_content_matches",
    "assert_tool_schema_valid",
    "assert_tools_have_unique_names",
    # Snapshot
    "SnapshotHelper",
    # Utils
    "format_tool_signature",
    "validate_tool_arguments",
]

# Client imports
from pytest_mcp.client import MockMCPClient, create_mock_client

# Server imports
from pytest_mcp.server import MCPTestServer, MCPTestServerFactory

# Assertion imports
from pytest_mcp.assertions import (
    assert_resource_content_matches,
    assert_resource_exists,
    assert_tool_count,
    assert_tool_exists,
    assert_tool_output_matches,
    assert_tool_returns_error,
    assert_tool_schema_valid,
    assert_tools_have_unique_names,
)

# Snapshot imports
from pytest_mcp.snapshot import SnapshotHelper

# Utils imports
from pytest_mcp.utils import format_tool_signature, validate_tool_arguments

# Fixtures are auto-loaded via plugin.py entry point
# Users don't need to import them explicitly
