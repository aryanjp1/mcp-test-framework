"""
Tests for the advanced user management server.

This demonstrates advanced pytest-mcp features including:
- Resource testing
- Stateful operations
- Snapshot testing
- Error handling
"""

from __future__ import annotations

import json

import pytest
from mcp import StdioServerParameters

from pytest_mcp import (
    MockMCPClient,
    assert_resource_exists,
    assert_tool_count,
    assert_tool_exists,
    assert_tool_output_matches,
    assert_tool_returns_error,
)


@pytest.fixture
def mcp_server() -> StdioServerParameters:
    """Configure the advanced server for testing."""
    return StdioServerParameters(
        command="python",
        args=["-m", "examples.advanced.server"],
        env={},
    )


class TestUserManagementServer:
    """Test suite for user management server."""

    @pytest.mark.asyncio
    async def test_server_has_expected_tools(self, mcp_client: MockMCPClient) -> None:
        """Test that server provides expected tools."""
        await assert_tool_count(mcp_client, 4)

        await assert_tool_exists(mcp_client, "get_user")
        await assert_tool_exists(mcp_client, "create_user")
        await assert_tool_exists(mcp_client, "list_users")
        await assert_tool_exists(mcp_client, "delete_user")

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, mcp_client: MockMCPClient) -> None:
        """Test getting a user by ID."""
        result = await mcp_client.call_tool("get_user", {"id": "1"})

        # Parse JSON response
        content = result.content[0].text
        user = json.loads(content)

        assert user["id"] == "1"
        assert user["name"] == "Alice"
        assert user["email"] == "alice@example.com"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_raises_error(self, mcp_client: MockMCPClient) -> None:
        """Test that getting non-existent user raises error."""
        await assert_tool_returns_error(
            mcp_client,
            "get_user",
            {"id": "999"},
            error_message="User not found",
        )

    @pytest.mark.asyncio
    async def test_list_users(self, mcp_client: MockMCPClient) -> None:
        """Test listing all users."""
        result = await mcp_client.call_tool("list_users", {})

        content = result.content[0].text
        users = json.loads(content)

        assert isinstance(users, list)
        assert len(users) >= 2  # At least Alice and Bob
        assert any(u["name"] == "Alice" for u in users)
        assert any(u["name"] == "Bob" for u in users)

    @pytest.mark.asyncio
    async def test_create_user(self, mcp_client: MockMCPClient) -> None:
        """Test creating a new user."""
        result = await mcp_client.call_tool(
            "create_user", {"name": "Charlie", "email": "charlie@example.com"}
        )

        content = result.content[0].text
        user = json.loads(content)

        assert user["name"] == "Charlie"
        assert user["email"] == "charlie@example.com"
        assert "id" in user

    @pytest.mark.asyncio
    async def test_create_user_missing_arguments(self, mcp_client: MockMCPClient) -> None:
        """Test that creating user without required args fails."""
        await assert_tool_returns_error(
            mcp_client,
            "create_user",
            {"name": "Charlie"},  # Missing email
            error_message="Missing required arguments",
        )

    @pytest.mark.asyncio
    async def test_delete_user(self, mcp_client: MockMCPClient) -> None:
        """Test deleting a user."""
        # First create a user
        create_result = await mcp_client.call_tool(
            "create_user", {"name": "TempUser", "email": "temp@example.com"}
        )
        user = json.loads(create_result.content[0].text)
        user_id = user["id"]

        # Delete the user
        delete_result = await mcp_client.call_tool("delete_user", {"id": user_id})
        response = json.loads(delete_result.content[0].text)

        assert response["success"] is True

        # Verify user is gone
        await assert_tool_returns_error(
            mcp_client, "get_user", {"id": user_id}, error_message="User not found"
        )

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, mcp_client: MockMCPClient) -> None:
        """Test that deleting non-existent user raises error."""
        await assert_tool_returns_error(
            mcp_client,
            "delete_user",
            {"id": "999"},
            error_message="User not found",
        )


class TestUserResources:
    """Test resource functionality."""

    @pytest.mark.asyncio
    async def test_server_has_resources(self, mcp_client: MockMCPClient) -> None:
        """Test that server provides resources."""
        resources = await mcp_client.list_resources()
        assert len(resources) > 0

    @pytest.mark.asyncio
    async def test_users_resource_exists(self, mcp_client: MockMCPClient) -> None:
        """Test that users resource exists."""
        await assert_resource_exists(mcp_client, "users://all")

    @pytest.mark.asyncio
    async def test_read_users_resource(self, mcp_client: MockMCPClient) -> None:
        """Test reading users resource."""
        result = await mcp_client.read_resource("users://all")

        assert result.contents
        content = result.contents[0].text

        # Parse JSON
        users = json.loads(content)
        assert isinstance(users, list)
        assert len(users) >= 2


class TestWithSnapshots:
    """Test using snapshot testing."""

    @pytest.mark.asyncio
    async def test_get_user_snapshot(self, mcp_client: MockMCPClient, snapshot) -> None:
        """Test user data with snapshot."""
        result = await mcp_client.call_tool("get_user", {"id": "1"})

        # Save/compare snapshot
        snapshot.assert_match(result, "user_1_data")

    @pytest.mark.asyncio
    async def test_list_users_snapshot(self, mcp_client: MockMCPClient, snapshot) -> None:
        """Test user list with snapshot."""
        result = await mcp_client.call_tool("list_users", {})

        snapshot.assert_match(result, "all_users")


class TestWorkflow:
    """Test complete workflows."""

    @pytest.mark.asyncio
    async def test_full_user_lifecycle(self, mcp_client: MockMCPClient) -> None:
        """Test creating, reading, and deleting a user."""
        # Create user
        create_result = await mcp_client.call_tool(
            "create_user", {"name": "TestUser", "email": "test@example.com"}
        )
        user = json.loads(create_result.content[0].text)
        user_id = user["id"]

        # Read user
        get_result = await mcp_client.call_tool("get_user", {"id": user_id})
        retrieved_user = json.loads(get_result.content[0].text)
        assert retrieved_user["name"] == "TestUser"

        # List users (should include our new user)
        list_result = await mcp_client.call_tool("list_users", {})
        all_users = json.loads(list_result.content[0].text)
        assert any(u["id"] == user_id for u in all_users)

        # Delete user
        await mcp_client.call_tool("delete_user", {"id": user_id})

        # Verify deletion
        await assert_tool_returns_error(
            mcp_client, "get_user", {"id": user_id}, error_message="User not found"
        )
