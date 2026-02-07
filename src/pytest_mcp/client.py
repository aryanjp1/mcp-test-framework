"""Mock MCP client for testing MCP servers in-process."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager, AsyncExitStack
from typing import Any, AsyncIterator, Sequence

import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import (
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
    Resource,
    Tool,
)
from pydantic import AnyUrl

logger = logging.getLogger(__name__)


class MockMCPClient:
    """
    A mock MCP client for testing MCP servers in-process.

    This client connects to an MCP server without requiring network communication,
    making it ideal for unit and integration testing.

    Example:
        >>> async with MockMCPClient(server) as client:
        ...     tools = await client.list_tools()
        ...     result = await client.call_tool("my_tool", {"arg": "value"})
    """

    def __init__(
        self,
        server_params: StdioServerParameters | None = None,
        *,
        command: str | None = None,
        args: Sequence[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the mock MCP client.

        Args:
            server_params: MCP server parameters (command, args, env)
            command: Server command to run (alternative to server_params)
            args: Command arguments (alternative to server_params)
            env: Environment variables (alternative to server_params)
        """
        if server_params is None:
            if command is None:
                raise ValueError("Either server_params or command must be provided")
            server_params = StdioServerParameters(
                command=command, args=args or [], env=env or {}
            )

        self._server_params = server_params
        self._session: ClientSession | None = None
        self._read_stream: MemoryObjectReceiveStream[Any] | None = None
        self._write_stream: MemoryObjectSendStream[Any] | None = None
        self._exit_stack: AsyncExitStack | None = None

    async def __aenter__(self) -> MockMCPClient:
        """Enter async context and initialize connection."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and cleanup connection."""
        await self.disconnect()

    async def connect(self) -> None:
        """Establish connection to the MCP server."""
        if self._session is not None:
            logger.warning("Client is already connected")
            return

        try:
            # Use AsyncExitStack to manage nested context managers
            self._exit_stack = AsyncExitStack()

            # Enter stdio_client context and keep it alive
            read, write = await self._exit_stack.enter_async_context(
                stdio_client(self._server_params)
            )
            self._read_stream = read
            self._write_stream = write

            # Enter ClientSession context and keep it alive
            session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            self._session = session

            # Initialize the session
            await session.initialize()
            logger.debug("MockMCPClient connected successfully")

        except Exception as e:
            # Clean up on error
            if self._exit_stack:
                await self._exit_stack.aclose()
                self._exit_stack = None
            self._session = None
            self._read_stream = None
            self._write_stream = None
            logger.error(f"Failed to connect to MCP server: {e}")
            raise ConnectionError(f"Could not connect to MCP server: {e}") from e

    async def disconnect(self) -> None:
        """Close connection to the MCP server."""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self._exit_stack = None
        self._session = None
        self._read_stream = None
        self._write_stream = None
        logger.debug("MockMCPClient disconnected")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to server."""
        return self._session is not None

    def _ensure_connected(self) -> ClientSession:
        """Ensure client is connected and return session."""
        if not self._session:
            raise RuntimeError(
                "Client is not connected. Use 'async with MockMCPClient(...)' or call connect()"
            )
        return self._session

    async def list_tools(self) -> list[Tool]:
        """
        List all available tools from the MCP server.

        Returns:
            List of available tools

        Raises:
            RuntimeError: If client is not connected
        """
        session = self._ensure_connected()
        result: ListToolsResult = await session.list_tools()
        return result.tools

    async def call_tool(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> CallToolResult:
        """
        Call a tool on the MCP server.

        Args:
            name: Tool name to call
            arguments: Tool arguments as a dictionary

        Returns:
            Tool execution result

        Raises:
            RuntimeError: If client is not connected
            Exception: If tool execution fails
        """
        session = self._ensure_connected()
        try:
            result = await session.call_tool(name, arguments or {})
            logger.debug(f"Tool '{name}' called successfully")
            return result
        except Exception as e:
            logger.error(f"Tool '{name}' call failed: {e}")
            raise

    async def list_resources(self) -> list[Resource]:
        """
        List all available resources from the MCP server.

        Returns:
            List of available resources

        Raises:
            RuntimeError: If client is not connected
        """
        session = self._ensure_connected()
        result: ListResourcesResult = await session.list_resources()
        return result.resources

    async def read_resource(self, uri: str | AnyUrl) -> ReadResourceResult:
        """
        Read a resource from the MCP server.

        Args:
            uri: Resource URI to read

        Returns:
            Resource content

        Raises:
            RuntimeError: If client is not connected
            Exception: If resource reading fails
        """
        session = self._ensure_connected()
        try:
            if isinstance(uri, str):
                uri = AnyUrl(uri)
            result = await session.read_resource(uri)
            logger.debug(f"Resource '{uri}' read successfully")
            return result
        except Exception as e:
            logger.error(f"Resource '{uri}' read failed: {e}")
            raise

    async def get_tool(self, name: str) -> Tool | None:
        """
        Get a specific tool by name.

        Args:
            name: Tool name

        Returns:
            Tool if found, None otherwise
        """
        tools = await self.list_tools()
        return next((tool for tool in tools if tool.name == name), None)

    async def get_resource(self, uri: str | AnyUrl) -> Resource | None:
        """
        Get a specific resource by URI.

        Args:
            uri: Resource URI

        Returns:
            Resource if found, None otherwise
        """
        if isinstance(uri, str):
            uri = AnyUrl(uri)

        resources = await self.list_resources()
        return next(
            (resource for resource in resources if resource.uri == uri), None
        )


@asynccontextmanager
async def create_mock_client(
    server_params: StdioServerParameters | None = None,
    *,
    command: str | None = None,
    args: Sequence[str] | None = None,
    env: dict[str, str] | None = None,
) -> AsyncIterator[MockMCPClient]:
    """
    Create a mock MCP client as an async context manager.

    This is a convenience function that creates and manages a MockMCPClient.

    Args:
        server_params: MCP server parameters
        command: Server command (alternative to server_params)
        args: Command arguments
        env: Environment variables

    Yields:
        Connected MockMCPClient instance

    Example:
        >>> async with create_mock_client(command="python", args=["server.py"]) as client:
        ...     tools = await client.list_tools()
    """
    client = MockMCPClient(server_params, command=command, args=args, env=env)
    async with client:
        yield client
