"""
Example tests for the basic calculator server.

This demonstrates how to use pytest-mcp to test an MCP server.
"""

from __future__ import annotations

import pytest
from mcp import StdioServerParameters

from pytest_mcp import (
    MockMCPClient,
    assert_tool_count,
    assert_tool_exists,
    assert_tool_output_matches,
    assert_tool_returns_error,
    assert_tool_schema_valid,
    assert_tools_have_unique_names,
)


# Configure the server for all tests in this file
@pytest.fixture
def mcp_server() -> StdioServerParameters:
    """
    Configure the calculator server for testing.

    This fixture is automatically discovered by pytest-mcp.
    """
    return StdioServerParameters(
        command="python",
        args=["-m", "examples.basic_server.server"],
        env={},
    )


class TestCalculatorServer:
    """Test suite for calculator server."""

    @pytest.mark.asyncio
    async def test_server_lists_tools(self, mcp_client: MockMCPClient) -> None:
        """Test that server lists all calculator tools."""
        await assert_tool_count(mcp_client, 4)
        await assert_tools_have_unique_names(mcp_client)

    @pytest.mark.asyncio
    async def test_add_tool_exists(self, mcp_client: MockMCPClient) -> None:
        """Test that add tool is available."""
        tool = await assert_tool_exists(mcp_client, "add")
        assert_tool_schema_valid(tool)
        assert "add two numbers" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_add_tool_works(self, mcp_client: MockMCPClient) -> None:
        """Test add tool functionality."""
        result = await mcp_client.call_tool("add", {"a": 5, "b": 3})
        await assert_tool_output_matches(result, "8")

    @pytest.mark.asyncio
    async def test_subtract_tool_works(self, mcp_client: MockMCPClient) -> None:
        """Test subtract tool functionality."""
        result = await mcp_client.call_tool("subtract", {"a": 10, "b": 3})
        await assert_tool_output_matches(result, "7")

    @pytest.mark.asyncio
    async def test_multiply_tool_works(self, mcp_client: MockMCPClient) -> None:
        """Test multiply tool functionality."""
        result = await mcp_client.call_tool("multiply", {"a": 4, "b": 5})
        await assert_tool_output_matches(result, "20")

    @pytest.mark.asyncio
    async def test_divide_tool_works(self, mcp_client: MockMCPClient) -> None:
        """Test divide tool functionality."""
        result = await mcp_client.call_tool("divide", {"a": 10, "b": 2})
        await assert_tool_output_matches(result, "5.0")

    @pytest.mark.asyncio
    async def test_divide_by_zero_raises_error(self, mcp_client: MockMCPClient) -> None:
        """Test that dividing by zero raises an error."""
        await assert_tool_returns_error(
            mcp_client,
            "divide",
            {"a": 10, "b": 0},
            error_message="Cannot divide by zero",
        )

    @pytest.mark.asyncio
    async def test_missing_arguments_raises_error(self, mcp_client: MockMCPClient) -> None:
        """Test that missing arguments raises an error."""
        await assert_tool_returns_error(
            mcp_client,
            "add",
            {"a": 5},  # Missing 'b'
            error_message="Missing required arguments",
        )

    @pytest.mark.asyncio
    async def test_all_tools_have_valid_schemas(self, mcp_client: MockMCPClient) -> None:
        """Test that all tools have valid schemas."""
        tools = await mcp_client.list_tools()

        for tool in tools:
            assert_tool_schema_valid(tool)

    @pytest.mark.asyncio
    async def test_add_with_decimals(self, mcp_client: MockMCPClient) -> None:
        """Test add tool with decimal numbers."""
        result = await mcp_client.call_tool("add", {"a": 1.5, "b": 2.3})
        # Check that result is approximately 3.8
        await assert_tool_output_matches(result, "3.8")

    @pytest.mark.asyncio
    async def test_add_with_snapshot(self, mcp_client: MockMCPClient, snapshot) -> None:
        """Test add tool output with snapshot."""
        result = await mcp_client.call_tool("add", {"a": 100, "b": 200})
        # First run saves snapshot, subsequent runs compare
        snapshot.assert_match(result, "add_100_200")


class TestCalculatorEdgeCases:
    """Test edge cases for calculator server."""

    @pytest.mark.asyncio
    async def test_negative_numbers(self, mcp_client: MockMCPClient) -> None:
        """Test operations with negative numbers."""
        result = await mcp_client.call_tool("add", {"a": -5, "b": 3})
        await assert_tool_output_matches(result, "-2")

    @pytest.mark.asyncio
    async def test_large_numbers(self, mcp_client: MockMCPClient) -> None:
        """Test operations with large numbers."""
        result = await mcp_client.call_tool("multiply", {"a": 1000000, "b": 1000000})
        await assert_tool_output_matches(result, "1000000000000")

    @pytest.mark.asyncio
    async def test_zero_operations(self, mcp_client: MockMCPClient) -> None:
        """Test operations with zero."""
        # Zero + number
        result = await mcp_client.call_tool("add", {"a": 0, "b": 5})
        await assert_tool_output_matches(result, "5")

        # Zero * number
        result = await mcp_client.call_tool("multiply", {"a": 0, "b": 100})
        await assert_tool_output_matches(result, "0")
