"""Pytest fixtures for MCP server testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

import pytest
from mcp import StdioServerParameters

from pytest_mcp.client import MockMCPClient

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
async def mcp_client(mcp_server: Any) -> AsyncIterator[MockMCPClient]:
    """
    Pytest fixture that provides a connected MockMCPClient.

    This fixture automatically discovers the mcp_server fixture defined by the user
    and creates a client connected to it.

    Args:
        mcp_server: User-defined fixture that returns server parameters

    Yields:
        Connected MockMCPClient instance

    Example:
        >>> # In conftest.py
        >>> @pytest.fixture
        >>> def mcp_server():
        ...     return StdioServerParameters(command="python", args=["server.py"])
        >>>
        >>> # In test file
        >>> async def test_my_tool(mcp_client):
        ...     tools = await mcp_client.list_tools()
        ...     assert len(tools) > 0
    """
    # Handle different types of mcp_server fixtures
    if isinstance(mcp_server, StdioServerParameters):
        server_params = mcp_server
    elif isinstance(mcp_server, dict):
        # Support dict format: {"command": "python", "args": ["server.py"]}
        server_params = StdioServerParameters(**mcp_server)
    elif isinstance(mcp_server, tuple) and len(mcp_server) >= 1:
        # Support tuple format: ("python", ["server.py"])
        command = mcp_server[0]
        args = mcp_server[1] if len(mcp_server) > 1 else []
        env = mcp_server[2] if len(mcp_server) > 2 else None
        server_params = StdioServerParameters(command=command, args=args, env=env or {})
    else:
        raise TypeError(
            f"mcp_server fixture must return StdioServerParameters, dict, or tuple, "
            f"got {type(mcp_server)}"
        )

    async with MockMCPClient(server_params) as client:
        yield client


@pytest.fixture
def snapshot_dir(request: pytest.FixtureRequest) -> Path:
    """
    Pytest fixture that provides the snapshot directory path.

    Returns the __snapshots__ directory relative to the test file.

    Args:
        request: Pytest fixture request

    Returns:
        Path to snapshot directory
    """
    from pathlib import Path

    test_file = Path(request.fspath)
    return test_file.parent / "__snapshots__"


@pytest.fixture
def snapshot(request: pytest.FixtureRequest, snapshot_dir: Path) -> Any:
    """
    Pytest fixture that provides snapshot testing functionality.

    Args:
        request: Pytest fixture request
        snapshot_dir: Directory to store snapshots

    Returns:
        Snapshot helper instance
    """
    from pytest_mcp.snapshot import SnapshotHelper

    return SnapshotHelper(request, snapshot_dir)


@pytest.fixture
def mcp_server_env() -> dict[str, str]:
    """
    Pytest fixture that provides default environment variables for MCP servers.

    Can be overridden by users to provide custom environment variables.

    Returns:
        Dictionary of environment variables
    """
    return {}


@pytest.fixture
async def mcp_test_server(
    mcp_server: Any, mcp_server_env: dict[str, str]
) -> AsyncIterator[MockMCPClient]:
    """
    Advanced fixture that provides full server lifecycle management.

    This is an alternative to mcp_client for integration tests that need
    more control over the server lifecycle.

    Args:
        mcp_server: User-defined server parameters
        mcp_server_env: Environment variables

    Yields:
        Connected MockMCPClient instance

    Example:
        >>> async def test_integration(mcp_test_server):
        ...     # Server is started and stopped automatically
        ...     result = await mcp_test_server.call_tool("test", {})
    """
    from pytest_mcp.server import MCPTestServer

    # Parse server parameters
    if isinstance(mcp_server, StdioServerParameters):
        command = mcp_server.command
        args = mcp_server.args
        env = {**mcp_server_env, **mcp_server.env}
    elif isinstance(mcp_server, dict):
        command = mcp_server["command"]
        args = mcp_server.get("args", [])
        env = {**mcp_server_env, **mcp_server.get("env", {})}
    elif isinstance(mcp_server, tuple):
        command = mcp_server[0]
        args = mcp_server[1] if len(mcp_server) > 1 else []
        env = {**mcp_server_env, **(mcp_server[2] if len(mcp_server) > 2 else {})}
    else:
        raise TypeError(f"Unsupported mcp_server type: {type(mcp_server)}")

    async with MCPTestServer(command, args, env) as server:
        client = server.get_client()
        yield client
