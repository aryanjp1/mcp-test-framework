"""
Advanced example MCP server with resources and error handling.

This demonstrates a more complex MCP server with:
- Multiple tools
- Resources
- Error handling
- State management
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl


# Create server instance with state
app = Server("example-advanced")

# In-memory data store
DATA_STORE: dict[str, Any] = {
    "users": {
        "1": {"id": "1", "name": "Alice", "email": "alice@example.com"},
        "2": {"id": "2", "name": "Bob", "email": "bob@example.com"},
    }
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_user",
            description="Get user by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "User ID"},
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="create_user",
            description="Create a new user",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "User name"},
                    "email": {"type": "string", "description": "User email"},
                },
                "required": ["name", "email"],
            },
        ),
        Tool(
            name="list_users",
            description="List all users",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="delete_user",
            description="Delete user by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "User ID"},
                },
                "required": ["id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool."""
    if name == "get_user":
        user_id = arguments.get("id")
        if not user_id:
            raise ValueError("Missing required argument: id")

        user = DATA_STORE["users"].get(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        return [TextContent(type="text", text=json.dumps(user))]

    elif name == "create_user":
        name_val = arguments.get("name")
        email = arguments.get("email")

        if not name_val or not email:
            raise ValueError("Missing required arguments: name and email")

        # Generate new ID
        new_id = str(len(DATA_STORE["users"]) + 1)
        user = {"id": new_id, "name": name_val, "email": email}
        DATA_STORE["users"][new_id] = user

        return [TextContent(type="text", text=json.dumps(user))]

    elif name == "list_users":
        users = list(DATA_STORE["users"].values())
        return [TextContent(type="text", text=json.dumps(users))]

    elif name == "delete_user":
        user_id = arguments.get("id")
        if not user_id:
            raise ValueError("Missing required argument: id")

        if user_id not in DATA_STORE["users"]:
            raise ValueError(f"User not found: {user_id}")

        del DATA_STORE["users"][user_id]
        return [TextContent(type="text", text=json.dumps({"success": True}))]

    else:
        raise ValueError(f"Unknown tool: {name}")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri=AnyUrl("users://all"),
            name="All Users",
            description="List of all users in the system",
            mimeType="application/json",
        ),
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read a resource."""
    if str(uri) == "users://all":
        users = list(DATA_STORE["users"].values())
        return json.dumps(users, indent=2)

    raise ValueError(f"Unknown resource: {uri}")


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
