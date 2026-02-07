"""Tests for assertion helpers."""

from __future__ import annotations

import pytest
from mcp.types import CallToolResult, TextContent, Tool

from pytest_mcp.assertions import (
    assert_tool_count,
    assert_tool_exists,
    assert_tool_output_matches,
    assert_tool_schema_valid,
    assert_tools_have_unique_names,
)
from pytest_mcp.client import MockMCPClient


class TestAssertions:
    """Test suite for assertion helpers."""

    @pytest.mark.asyncio
    async def test_assert_tool_exists_success(self, mocker) -> None:
        """Test assert_tool_exists with existing tool."""
        # Mock client that returns tools
        client = mocker.Mock(spec=MockMCPClient)
        tools = [
            Tool(name="tool1", description="Test tool 1", inputSchema={"type": "object"}),
            Tool(name="tool2", description="Test tool 2", inputSchema={"type": "object"}),
        ]
        client.list_tools = mocker.AsyncMock(return_value=tools)

        # Should not raise
        tool = await assert_tool_exists(client, "tool1")
        assert tool.name == "tool1"

    @pytest.mark.asyncio
    async def test_assert_tool_exists_failure(self, mocker) -> None:
        """Test assert_tool_exists with non-existing tool."""
        client = mocker.Mock(spec=MockMCPClient)
        tools = [
            Tool(name="tool1", description="Test tool 1", inputSchema={"type": "object"}),
        ]
        client.list_tools = mocker.AsyncMock(return_value=tools)

        with pytest.raises(AssertionError, match="Tool 'tool2' not found"):
            await assert_tool_exists(client, "tool2")

    @pytest.mark.asyncio
    async def test_assert_tool_count_success(self, mocker) -> None:
        """Test assert_tool_count with correct count."""
        client = mocker.Mock(spec=MockMCPClient)
        tools = [
            Tool(name="tool1", description="Test tool 1", inputSchema={"type": "object"}),
            Tool(name="tool2", description="Test tool 2", inputSchema={"type": "object"}),
        ]
        client.list_tools = mocker.AsyncMock(return_value=tools)

        # Should not raise
        await assert_tool_count(client, 2)

    @pytest.mark.asyncio
    async def test_assert_tool_count_failure(self, mocker) -> None:
        """Test assert_tool_count with wrong count."""
        client = mocker.Mock(spec=MockMCPClient)
        tools = [
            Tool(name="tool1", description="Test tool 1", inputSchema={"type": "object"}),
        ]
        client.list_tools = mocker.AsyncMock(return_value=tools)

        with pytest.raises(AssertionError, match="Expected 2 tools, found 1"):
            await assert_tool_count(client, 2)

    @pytest.mark.asyncio
    async def test_assert_tool_output_matches_exact(self) -> None:
        """Test assert_tool_output_matches with exact match."""
        result = CallToolResult(
            content=[TextContent(type="text", text="42")],
        )

        # Should not raise
        await assert_tool_output_matches(result, "42")

    @pytest.mark.asyncio
    async def test_assert_tool_output_matches_json(self) -> None:
        """Test assert_tool_output_matches with JSON output."""
        result = CallToolResult(
            content=[TextContent(type="text", text='{"value": 42}')],
        )

        # Should parse JSON and match
        await assert_tool_output_matches(result, {"value": 42})

    @pytest.mark.asyncio
    async def test_assert_tool_output_matches_failure(self) -> None:
        """Test assert_tool_output_matches with mismatch."""
        result = CallToolResult(
            content=[TextContent(type="text", text="42")],
        )

        with pytest.raises(AssertionError, match="Tool output mismatch"):
            await assert_tool_output_matches(result, "43")

    @pytest.mark.asyncio
    async def test_assert_tool_output_matches_partial(self) -> None:
        """Test assert_tool_output_matches with partial matching."""
        result = CallToolResult(
            content=[TextContent(type="text", text="Hello, World!")],
        )

        # Should match substring
        await assert_tool_output_matches(result, "Hello", partial=True)

    def test_assert_tool_schema_valid_success(self) -> None:
        """Test assert_tool_schema_valid with valid schema."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            inputSchema={"type": "object", "properties": {}},
        )

        # Should not raise
        assert_tool_schema_valid(tool)

    def test_assert_tool_schema_valid_missing_name(self) -> None:
        """Test assert_tool_schema_valid with missing name."""
        tool = Tool(
            name="",
            description="A test tool",
            inputSchema={"type": "object"},
        )

        with pytest.raises(AssertionError, match="Tool must have a name"):
            assert_tool_schema_valid(tool)

    def test_assert_tool_schema_valid_missing_description(self) -> None:
        """Test assert_tool_schema_valid with missing description."""
        tool = Tool(
            name="test_tool",
            description="",
            inputSchema={"type": "object"},
        )

        with pytest.raises(AssertionError, match="must have a description"):
            assert_tool_schema_valid(tool)

    @pytest.mark.asyncio
    async def test_assert_tools_have_unique_names_success(self, mocker) -> None:
        """Test assert_tools_have_unique_names with unique names."""
        client = mocker.Mock(spec=MockMCPClient)
        tools = [
            Tool(name="tool1", description="Test tool 1", inputSchema={"type": "object"}),
            Tool(name="tool2", description="Test tool 2", inputSchema={"type": "object"}),
        ]
        client.list_tools = mocker.AsyncMock(return_value=tools)

        # Should not raise
        await assert_tools_have_unique_names(client)

    @pytest.mark.asyncio
    async def test_assert_tools_have_unique_names_failure(self, mocker) -> None:
        """Test assert_tools_have_unique_names with duplicate names."""
        client = mocker.Mock(spec=MockMCPClient)
        tools = [
            Tool(name="tool1", description="Test tool 1", inputSchema={"type": "object"}),
            Tool(name="tool1", description="Duplicate tool 1", inputSchema={"type": "object"}),
        ]
        client.list_tools = mocker.AsyncMock(return_value=tools)

        with pytest.raises(AssertionError, match="Duplicate tool names found"):
            await assert_tools_have_unique_names(client)
