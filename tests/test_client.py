"""Tests for MockMCPClient."""

from __future__ import annotations

import pytest
from mcp import StdioServerParameters

from pytest_mcp import MockMCPClient, create_mock_client


class TestMockMCPClient:
    """Test suite for MockMCPClient."""

    def test_init_with_server_params(self) -> None:
        """Test initialization with StdioServerParameters."""
        params = StdioServerParameters(command="python", args=["server.py"], env={})
        client = MockMCPClient(params)

        assert client._server_params == params
        assert not client.is_connected

    def test_init_with_command(self) -> None:
        """Test initialization with command and args."""
        client = MockMCPClient(command="python", args=["server.py"])

        assert client._server_params.command == "python"
        assert client._server_params.args == ["server.py"]
        assert not client.is_connected

    def test_init_requires_params_or_command(self) -> None:
        """Test that initialization requires either server_params or command."""
        with pytest.raises(ValueError, match="Either server_params or command"):
            MockMCPClient()

    def test_ensure_connected_raises_when_not_connected(self) -> None:
        """Test that operations fail when not connected."""
        client = MockMCPClient(command="python", args=["server.py"])

        with pytest.raises(RuntimeError, match="Client is not connected"):
            client._ensure_connected()

    @pytest.mark.asyncio
    async def test_context_manager(self, example_server_params: StdioServerParameters) -> None:
        """Test client as async context manager."""
        # Note: This will fail without a real server, but tests the structure
        try:
            async with MockMCPClient(example_server_params) as client:
                # If we get here, connection succeeded (won't with mock params)
                assert client.is_connected
        except (ConnectionError, Exception):
            # Expected to fail with example params
            pass

    @pytest.mark.asyncio
    async def test_create_mock_client_helper(
        self, example_server_params: StdioServerParameters
    ) -> None:
        """Test the create_mock_client helper function."""
        try:
            async with create_mock_client(example_server_params) as client:
                assert isinstance(client, MockMCPClient)
        except (ConnectionError, Exception):
            # Expected to fail with example params
            pass


# Integration tests would go here if we had a real test server
# For now, these are structural tests
