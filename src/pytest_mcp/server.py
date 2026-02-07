"""Test server lifecycle management for MCP integration tests."""

from __future__ import annotations

import logging
from typing import Any, Sequence

from mcp import StdioServerParameters

from pytest_mcp.client import MockMCPClient

logger = logging.getLogger(__name__)


class MCPTestServer:
    """
    Manages the lifecycle of an MCP server for integration testing.

    This class handles starting, stopping, and connecting to MCP servers,
    making it easy to write integration tests.

    Example:
        >>> async with MCPTestServer("python", ["server.py"]) as server:
        ...     client = server.get_client()
        ...     result = await client.call_tool("hello", {"name": "world"})
    """

    def __init__(
        self,
        command: str,
        args: Sequence[str] | None = None,
        env: dict[str, str] | None = None,
        *,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize the test server.

        Args:
            command: Command to start the server
            args: Command arguments
            env: Environment variables
            timeout: Timeout for server operations in seconds
        """
        self.command = command
        self.args = list(args) if args else []
        self.env = env or {}
        self.timeout = timeout

        self._client: MockMCPClient | None = None
        self._server_params = StdioServerParameters(
            command=command,
            args=self.args,
            env=self.env,
        )

    async def __aenter__(self) -> MCPTestServer:
        """Enter async context and start server."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and stop server."""
        await self.stop()

    async def start(self) -> None:
        """
        Start the MCP server and establish connection.

        Raises:
            RuntimeError: If server fails to start
            TimeoutError: If connection times out
        """
        logger.info(f"Starting MCP test server: {self.command} {' '.join(self.args)}")

        try:
            # Create and connect client
            self._client = MockMCPClient(self._server_params)
            await self._client.connect()
            logger.info("MCP test server started successfully")

        except Exception as e:
            logger.error(f"Failed to start MCP test server: {e}")
            await self.stop()
            raise RuntimeError(f"Could not start MCP server: {e}") from e

    async def stop(self) -> None:
        """
        Stop the MCP server and cleanup resources.
        """
        if self._client:
            try:
                await self._client.disconnect()
                logger.info("MCP test server stopped")
            except Exception as e:
                logger.warning(f"Error stopping MCP test server: {e}")
            finally:
                self._client = None

    def get_client(self) -> MockMCPClient:
        """
        Get the connected client for this server.

        Returns:
            MockMCPClient instance

        Raises:
            RuntimeError: If server is not started
        """
        if not self._client or not self._client.is_connected:
            raise RuntimeError(
                "Server is not started. Use 'async with MCPTestServer(...)' or call start()"
            )
        return self._client

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._client is not None and self._client.is_connected

    async def restart(self) -> None:
        """
        Restart the server.

        Useful for testing server initialization or cleanup logic.
        """
        logger.info("Restarting MCP test server")
        await self.stop()
        await self.start()

    async def wait_for_ready(self, timeout: float | None = None) -> None:
        """
        Wait for server to be ready to accept requests.

        Args:
            timeout: Timeout in seconds (uses server timeout if not specified)

        Raises:
            TimeoutError: If server doesn't become ready in time
        """
        if timeout is None:
            timeout = self.timeout

        # Try to list tools as a health check
        try:
            client = self.get_client()
            await client.list_tools()
            logger.debug("MCP test server is ready")
        except Exception as e:
            raise TimeoutError(f"Server did not become ready: {e}") from e


class MCPTestServerFactory:
    """
    Factory for creating multiple test server instances.

    Useful for tests that need multiple servers or server pools.

    Example:
        >>> factory = MCPTestServerFactory("python", ["server.py"])
        >>> async with factory.create() as server1:
        ...     async with factory.create() as server2:
        ...         # Test with multiple servers
        ...         pass
    """

    def __init__(
        self,
        command: str,
        args: Sequence[str] | None = None,
        env: dict[str, str] | None = None,
        *,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize the server factory.

        Args:
            command: Command to start servers
            args: Command arguments
            env: Environment variables
            timeout: Timeout for server operations
        """
        self.command = command
        self.args = args
        self.env = env
        self.timeout = timeout
        self._servers: list[MCPTestServer] = []

    def create(self) -> MCPTestServer:
        """
        Create a new test server instance.

        Returns:
            MCPTestServer instance
        """
        server = MCPTestServer(
            self.command,
            self.args,
            self.env,
            timeout=self.timeout,
        )
        self._servers.append(server)
        return server

    async def stop_all(self) -> None:
        """
        Stop all created servers.
        """
        for server in self._servers:
            try:
                await server.stop()
            except Exception as e:
                logger.warning(f"Error stopping server: {e}")

        self._servers.clear()

    async def __aenter__(self) -> MCPTestServerFactory:
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and stop all servers."""
        await self.stop_all()
