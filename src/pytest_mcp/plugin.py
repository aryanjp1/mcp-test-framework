"""Pytest plugin registration for pytest-mcp."""

from __future__ import annotations

import logging
from typing import Any

import pytest

from pytest_mcp.fixtures import (
    mcp_client,
    mcp_server_env,
    mcp_test_server,
    snapshot,
    snapshot_dir,
)

logger = logging.getLogger(__name__)

# Export fixtures so pytest can discover them
__all__ = [
    "mcp_client",
    "mcp_server_env",
    "mcp_test_server",
    "snapshot",
    "snapshot_dir",
]


def pytest_configure(config: pytest.Config) -> None:
    """
    Pytest hook to configure the plugin.

    Registers custom markers and configuration options.

    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers",
        "mcp: mark test as an MCP server test",
    )
    config.addinivalue_line(
        "markers",
        "mcp_integration: mark test as an MCP integration test",
    )
    config.addinivalue_line(
        "markers",
        "mcp_slow: mark test as a slow MCP test",
    )

    # Add asyncio support if not already configured
    if not config.option.asyncio_mode:
        config.option.asyncio_mode = "auto"

    logger.debug("pytest-mcp plugin configured")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """
    Pytest hook to modify collected test items.

    Automatically marks tests that use mcp fixtures.

    Args:
        config: Pytest configuration object
        items: List of collected test items
    """
    for item in items:
        # Auto-mark tests using MCP fixtures
        if hasattr(item, "fixturenames"):
            fixture_names = getattr(item, "fixturenames", [])

            if "mcp_client" in fixture_names or "mcp_test_server" in fixture_names:
                item.add_marker(pytest.mark.mcp)

            if "mcp_test_server" in fixture_names:
                item.add_marker(pytest.mark.mcp_integration)


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Pytest hook to add command-line options.

    Args:
        parser: Pytest parser object
    """
    group = parser.getgroup("mcp")
    group.addoption(
        "--mcp-log-level",
        action="store",
        default="WARNING",
        help="Set log level for MCP client (DEBUG, INFO, WARNING, ERROR)",
    )
    group.addoption(
        "--mcp-timeout",
        action="store",
        type=float,
        default=30.0,
        help="Default timeout for MCP operations in seconds",
    )
    group.addoption(
        "--mcp-update-snapshots",
        action="store_true",
        default=False,
        help="Update snapshot files instead of comparing",
    )


def pytest_report_header(config: pytest.Config) -> list[str]:
    """
    Pytest hook to add header information to test report.

    Args:
        config: Pytest configuration object

    Returns:
        List of header lines
    """
    headers = []
    if hasattr(config.option, "mcp_log_level"):
        headers.append(f"mcp: log-level={config.option.mcp_log_level}")
    if hasattr(config.option, "mcp_timeout"):
        headers.append(f"mcp: timeout={config.option.mcp_timeout}s")
    return headers


@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(
    node: pytest.Item,
    call: pytest.CallInfo[Any],
    report: pytest.TestReport,
) -> None:
    """
    Pytest hook called when an exception is raised during test execution.

    Provides better error messages for common MCP errors.

    Args:
        node: Test item
        call: Call information
        report: Test report
    """
    if call.excinfo is None:
        return

    exc_type = call.excinfo.type
    exc_value = call.excinfo.value

    # Enhance error messages for common MCP issues
    if exc_type.__name__ == "ConnectionError":
        logger.error(
            f"MCP connection failed in {node.nodeid}: {exc_value}\n"
            "Check that your mcp_server fixture returns valid server parameters."
        )
    elif exc_type.__name__ == "TimeoutError":
        logger.error(
            f"MCP operation timed out in {node.nodeid}: {exc_value}\n"
            "Consider increasing timeout with --mcp-timeout option."
        )
