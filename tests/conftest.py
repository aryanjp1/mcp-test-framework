"""Pytest configuration for pytest-mcp tests."""

from __future__ import annotations

import pytest
from mcp import StdioServerParameters


@pytest.fixture
def example_server_params() -> StdioServerParameters:
    """
    Example server parameters for testing.

    Returns server params for a mock calculator server.
    """
    return StdioServerParameters(
        command="python",
        args=["-m", "examples.basic_server.server"],
        env={},
    )


@pytest.fixture
def mcp_server() -> dict[str, any]:
    """
    Example mcp_server fixture for testing the fixtures themselves.
    """
    return {
        "command": "python",
        "args": ["-m", "examples.basic_server.server"],
    }
