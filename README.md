# pytest-mcp

A pytest plugin for testing MCP (Model Context Protocol) servers.

[![PyPI version](https://img.shields.io/pypi/v/pytest-mcp.svg)](https://pypi.org/project/pytest-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-mcp.svg)](https://pypi.org/project/pytest-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/github/actions/workflow/status/yourusername/pytest-mcp/ci.yml?label=tests)](https://github.com/yourusername/pytest-mcp/actions)

## Quick Start

```bash
pip install pytest-mcp
```

```python
import pytest
from mcp import StdioServerParameters
from pytest_mcp import assert_tool_exists

@pytest.fixture
def mcp_server():
    return StdioServerParameters(
        command="python", args=["my_server.py"]
    )

async def test_my_tool(mcp_client):
    await assert_tool_exists(mcp_client, "my_tool")
    result = await mcp_client.call_tool("my_tool", {"arg": "value"})
    assert result is not None
```

The plugin automatically handles server lifecycle, connection management, and provides rich assertions.

## Features

### Mock MCP Client

Test servers in-process without network overhead:

```python
from pytest_mcp import MockMCPClient

async with MockMCPClient(command="python", args=["server.py"]) as client:
    tools = await client.list_tools()
    result = await client.call_tool("add", {"a": 1, "b": 2})
```

### Auto-Injected Fixtures

Define your server fixture and get a connected client automatically:

```python
@pytest.fixture
def mcp_server():
    return {"command": "python", "args": ["server.py"]}

async def test_tool(mcp_client):
    tools = await mcp_client.list_tools()
    assert len(tools) > 0
```

### Rich Assertions

Use descriptive assertions designed for MCP testing:

```python
from pytest_mcp import (
    assert_tool_exists,
    assert_tool_output_matches,
    assert_tool_returns_error,
    assert_resource_exists,
)

async def test_calculator(mcp_client):
    await assert_tool_exists(mcp_client, "add")

    result = await mcp_client.call_tool("add", {"a": 2, "b": 3})
    await assert_tool_output_matches(result, 5)

    await assert_tool_returns_error(
        mcp_client, "divide", {"a": 1, "b": 0},
        error_message="division by zero"
    )

    await assert_resource_exists(mcp_client, "config://settings")
```

### Snapshot Testing

Save and compare tool outputs across test runs:

```python
async def test_user_data(mcp_client, snapshot):
    result = await mcp_client.call_tool("get_user", {"id": 1})
    snapshot.assert_match(result, "user_1_response")
```

Update snapshots when needed:

```bash
pytest --mcp-update-snapshots
```

### Server Lifecycle Management

Control server startup and shutdown for integration tests:

```python
from pytest_mcp import MCPTestServer

async def test_integration():
    async with MCPTestServer("python", ["server.py"]) as server:
        client = server.get_client()
        result = await client.call_tool("hello", {"name": "world"})
        await server.restart()
```

## API Reference

### Client

#### MockMCPClient

```python
MockMCPClient(
    server_params: StdioServerParameters | None = None,
    *,
    command: str | None = None,
    args: Sequence[str] | None = None,
    env: dict[str, str] | None = None,
)
```

Methods:
- `async list_tools() -> list[Tool]` - List available tools
- `async call_tool(name: str, arguments: dict) -> CallToolResult` - Execute a tool
- `async list_resources() -> list[Resource]` - List available resources
- `async read_resource(uri: str) -> ReadResourceResult` - Read a resource
- `async get_tool(name: str) -> Tool | None` - Get specific tool by name

### Fixtures

- `mcp_client` - Auto-injected client connected to your server
- `mcp_server` - User-defined fixture that returns server parameters
- `mcp_test_server` - Advanced fixture with lifecycle control
- `snapshot` - Snapshot testing helper
- `mcp_server_env` - Environment variables for server

### Assertions

```python
# Tool assertions
await assert_tool_exists(client, "tool_name")
await assert_tool_count(client, expected_count)
await assert_tool_output_matches(result, expected_value, partial=False)
await assert_tool_returns_error(client, "tool_name", args, error_message="...")
await assert_tools_have_unique_names(client)

# Schema validation
assert_tool_schema_valid(tool)

# Resource assertions
await assert_resource_exists(client, "resource://uri")
await assert_resource_content_matches(client, "resource://uri", expected_content)
```

### Snapshot Testing

```python
# JSON snapshots
snapshot.assert_match(data, "snapshot_name")
snapshot.assert_match_json({"key": "value"}, "json_snapshot")

# Text snapshots
snapshot.assert_match_text("output", "text_snapshot")

# Utilities
snapshot.get_snapshot("name")
snapshot.delete_snapshot("name")
snapshot.list_snapshots()
```

### Server Management

```python
async with MCPTestServer(command, args, env) as server:
    client = server.get_client()
    await server.restart()
    await server.wait_for_ready()
```

## Usage Examples

### Basic Calculator Server

**server.py:**

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("calculator")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "add":
        result = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=str(result))]
```

**test_server.py:**

```python
import pytest
from pytest_mcp import assert_tool_exists, assert_tool_output_matches

@pytest.fixture
def mcp_server():
    return {"command": "python", "args": ["server.py"]}

async def test_add(mcp_client):
    await assert_tool_exists(mcp_client, "add")
    result = await mcp_client.call_tool("add", {"a": 5, "b": 3})
    await assert_tool_output_matches(result, "8")
```

### Advanced Features

**Testing Resources:**

```python
async def test_resources(mcp_client):
    resources = await mcp_client.list_resources()
    assert len(resources) > 0

    content = await mcp_client.read_resource("config://settings")
    assert content is not None
```

**Error Handling:**

```python
async def test_validation(mcp_client):
    await assert_tool_returns_error(
        mcp_client,
        "divide",
        {"a": 10, "b": 0},
        error_message="Cannot divide by zero"
    )
```

**Snapshot Testing:**

```python
async def test_complex_output(mcp_client, snapshot):
    result = await mcp_client.call_tool("get_report", {"id": 123})
    snapshot.assert_match(result, "report_123")
```

## Configuration

### pytest.ini / pyproject.toml

```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"

markers = [
    "mcp: MCP server test (auto-applied)",
    "mcp_integration: MCP integration test",
    "mcp_slow: Slow MCP test",
]
```

### Command-Line Options

```bash
# Set log level
pytest --mcp-log-level=DEBUG

# Set operation timeout
pytest --mcp-timeout=60

# Update snapshots
pytest --mcp-update-snapshots
```

## Integration with FastMCP

Works with [FastMCP](https://github.com/modelcontextprotocol/python-sdk):

```python
from fastmcp import FastMCP
from pytest_mcp import MockMCPClient

mcp = FastMCP("My Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

@pytest.fixture
def mcp_server():
    return mcp.get_server_params()

async def test_greet(mcp_client):
    result = await mcp_client.call_tool("greet", {"name": "Alice"})
    await assert_tool_output_matches(result, "Hello, Alice!")
```

## Contributing

Contributions are welcome. To get started:

```bash
git clone https://github.com/yourusername/pytest-mcp.git
cd pytest-mcp
pip install -e ".[dev]"
pytest
black .
ruff check .
mypy src/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- Built for the [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- Inspired by pytest plugin architecture
- Uses the [mcp](https://github.com/modelcontextprotocol/python-sdk) Python SDK

## Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [pytest Documentation](https://docs.pytest.org/)

## Community

- [GitHub Issues](https://github.com/yourusername/pytest-mcp/issues) - Bug reports and feature requests
- [Discussions](https://github.com/yourusername/pytest-mcp/discussions) - Questions and ideas
