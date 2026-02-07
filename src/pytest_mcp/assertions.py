"""Custom assertion helpers for MCP testing."""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, Tool

from pytest_mcp.client import MockMCPClient


async def assert_tool_exists(client: MockMCPClient, tool_name: str) -> Tool:
    """
    Assert that a tool exists on the MCP server.

    Args:
        client: MockMCPClient instance
        tool_name: Name of the tool to check

    Returns:
        The Tool object if found

    Raises:
        AssertionError: If tool does not exist

    Example:
        >>> async def test_tool_exists(mcp_client):
        ...     tool = await assert_tool_exists(mcp_client, "calculator")
        ...     assert tool.description is not None
    """
    tools = await client.list_tools()
    tool_names = [t.name for t in tools]

    if tool_name not in tool_names:
        raise AssertionError(
            f"Tool '{tool_name}' not found. Available tools: {', '.join(tool_names)}"
        )

    return next(t for t in tools if t.name == tool_name)


async def assert_tool_count(client: MockMCPClient, expected_count: int) -> None:
    """
    Assert that the server has exactly the expected number of tools.

    Args:
        client: MockMCPClient instance
        expected_count: Expected number of tools

    Raises:
        AssertionError: If tool count doesn't match

    Example:
        >>> async def test_tool_count(mcp_client):
        ...     await assert_tool_count(mcp_client, 3)
    """
    tools = await client.list_tools()
    actual_count = len(tools)

    if actual_count != expected_count:
        tool_names = [t.name for t in tools]
        raise AssertionError(
            f"Expected {expected_count} tools, found {actual_count}: "
            f"{', '.join(tool_names)}"
        )


async def assert_tool_output_matches(
    result: CallToolResult,
    expected: Any,
    *,
    partial: bool = False,
) -> None:
    """
    Assert that tool output matches expected value.

    Args:
        result: Tool call result
        expected: Expected output value
        partial: If True, checks if expected is a subset of actual

    Raises:
        AssertionError: If output doesn't match

    Example:
        >>> result = await mcp_client.call_tool("add", {"a": 1, "b": 2})
        >>> await assert_tool_output_matches(result, 3)
    """
    if not result.content:
        raise AssertionError(f"Tool returned no content. Result: {result}")

    # Extract actual value from result
    actual = None
    if len(result.content) == 1:
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            actual = content_item.text
        else:
            actual = content_item
    else:
        actual = [
            item.text if hasattr(item, "text") else item for item in result.content
        ]

    # Compare values
    if partial:
        if isinstance(expected, dict) and isinstance(actual, dict):
            for key, value in expected.items():
                if key not in actual:
                    raise AssertionError(
                        f"Expected key '{key}' not found in result. Actual: {actual}"
                    )
                if actual[key] != value:
                    raise AssertionError(
                        f"Expected {key}={value}, got {key}={actual[key]}"
                    )
        elif isinstance(expected, str) and isinstance(actual, str):
            if expected not in actual:
                raise AssertionError(
                    f"Expected substring '{expected}' not found in '{actual}'"
                )
        else:
            raise AssertionError(
                f"Partial matching not supported for types {type(expected)} and {type(actual)}"
            )
    else:
        # Try to parse actual as JSON if expected is dict/list
        if isinstance(expected, (dict, list)) and isinstance(actual, str):
            import json

            try:
                actual = json.loads(actual)
            except json.JSONDecodeError:
                pass

        if actual != expected:
            raise AssertionError(
                f"Tool output mismatch.\nExpected: {expected}\nActual: {actual}"
            )


async def assert_tool_returns_error(
    client: MockMCPClient,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    *,
    error_message: str | None = None,
) -> Exception:
    """
    Assert that calling a tool raises an error.

    Args:
        client: MockMCPClient instance
        tool_name: Name of the tool to call
        arguments: Tool arguments
        error_message: Optional expected error message substring

    Returns:
        The caught exception

    Raises:
        AssertionError: If tool doesn't raise an error or message doesn't match

    Example:
        >>> await assert_tool_returns_error(
        ...     mcp_client,
        ...     "divide",
        ...     {"a": 1, "b": 0},
        ...     error_message="division by zero"
        ... )
    """
    try:
        await client.call_tool(tool_name, arguments)
        raise AssertionError(
            f"Tool '{tool_name}' was expected to raise an error but succeeded"
        )
    except AssertionError:
        raise
    except Exception as e:
        if error_message and error_message not in str(e):
            raise AssertionError(
                f"Tool '{tool_name}' raised error but message doesn't match.\n"
                f"Expected substring: {error_message}\n"
                f"Actual error: {e}"
            ) from e
        return e


async def assert_resource_exists(client: MockMCPClient, resource_uri: str) -> None:
    """
    Assert that a resource exists on the MCP server.

    Args:
        client: MockMCPClient instance
        resource_uri: URI of the resource to check

    Raises:
        AssertionError: If resource does not exist

    Example:
        >>> async def test_resource_exists(mcp_client):
        ...     await assert_resource_exists(mcp_client, "file:///path/to/file.txt")
    """
    resources = await client.list_resources()
    resource_uris = [str(r.uri) for r in resources]

    if resource_uri not in resource_uris:
        raise AssertionError(
            f"Resource '{resource_uri}' not found. "
            f"Available resources: {', '.join(resource_uris)}"
        )


async def assert_resource_content_matches(
    client: MockMCPClient,
    resource_uri: str,
    expected_content: str,
    *,
    partial: bool = False,
) -> None:
    """
    Assert that resource content matches expected value.

    Args:
        client: MockMCPClient instance
        resource_uri: URI of the resource
        expected_content: Expected content
        partial: If True, checks if expected is a substring of actual

    Raises:
        AssertionError: If content doesn't match

    Example:
        >>> await assert_resource_content_matches(
        ...     mcp_client,
        ...     "file:///config.json",
        ...     '{"debug": true}',
        ... )
    """
    result = await client.read_resource(resource_uri)

    if not result.contents:
        raise AssertionError(f"Resource '{resource_uri}' returned no content")

    actual_content = result.contents[0].text if result.contents[0].text else ""

    if partial:
        if expected_content not in actual_content:
            raise AssertionError(
                f"Expected substring not found in resource '{resource_uri}'.\n"
                f"Expected: {expected_content}\n"
                f"Actual: {actual_content}"
            )
    else:
        if actual_content != expected_content:
            raise AssertionError(
                f"Resource content mismatch for '{resource_uri}'.\n"
                f"Expected: {expected_content}\n"
                f"Actual: {actual_content}"
            )


def assert_tool_schema_valid(tool: Tool) -> None:
    """
    Assert that a tool has a valid schema definition.

    Args:
        tool: Tool object to validate

    Raises:
        AssertionError: If schema is invalid

    Example:
        >>> tool = await mcp_client.get_tool("calculator")
        >>> assert_tool_schema_valid(tool)
    """
    if not tool.name:
        raise AssertionError("Tool must have a name")

    if not tool.description:
        raise AssertionError(f"Tool '{tool.name}' must have a description")

    if not tool.inputSchema:
        raise AssertionError(f"Tool '{tool.name}' must have an input schema")

    # Validate schema is a valid JSON schema
    schema = tool.inputSchema
    if not isinstance(schema, dict):
        raise AssertionError(
            f"Tool '{tool.name}' input schema must be a dictionary, got {type(schema)}"
        )

    if "type" not in schema:
        raise AssertionError(
            f"Tool '{tool.name}' input schema must have a 'type' field"
        )


async def assert_tools_have_unique_names(client: MockMCPClient) -> None:
    """
    Assert that all tools have unique names.

    Args:
        client: MockMCPClient instance

    Raises:
        AssertionError: If duplicate tool names exist

    Example:
        >>> async def test_unique_tools(mcp_client):
        ...     await assert_tools_have_unique_names(mcp_client)
    """
    tools = await client.list_tools()
    tool_names = [t.name for t in tools]
    unique_names = set(tool_names)

    if len(tool_names) != len(unique_names):
        duplicates = [name for name in tool_names if tool_names.count(name) > 1]
        raise AssertionError(
            f"Duplicate tool names found: {', '.join(set(duplicates))}"
        )
