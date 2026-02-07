"""
Basic example MCP server with calculator tools.

This demonstrates a simple MCP server that can be tested with pytest-mcp.
"""

from __future__ import annotations

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Create server instance
app = Server("example-calculator")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available calculator tools.

    Returns:
        List of calculator tools
    """
    return [
        Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="subtract",
            description="Subtract two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="multiply",
            description="Multiply two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="divide",
            description="Divide two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Numerator"},
                    "b": {"type": "number", "description": "Denominator"},
                },
                "required": ["a", "b"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Execute a calculator tool.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool result as text content

    Raises:
        ValueError: If tool name is unknown or arguments are invalid
    """
    if name == "add":
        a = arguments.get("a")
        b = arguments.get("b")
        if a is None or b is None:
            raise ValueError("Missing required arguments: a and b")
        result = a + b
        return [TextContent(type="text", text=str(result))]

    elif name == "subtract":
        a = arguments.get("a")
        b = arguments.get("b")
        if a is None or b is None:
            raise ValueError("Missing required arguments: a and b")
        result = a - b
        return [TextContent(type="text", text=str(result))]

    elif name == "multiply":
        a = arguments.get("a")
        b = arguments.get("b")
        if a is None or b is None:
            raise ValueError("Missing required arguments: a and b")
        result = a * b
        return [TextContent(type="text", text=str(result))]

    elif name == "divide":
        a = arguments.get("a")
        b = arguments.get("b")
        if a is None or b is None:
            raise ValueError("Missing required arguments: a and b")
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        return [TextContent(type="text", text=str(result))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
