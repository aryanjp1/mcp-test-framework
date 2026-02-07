# Setup Guide for pytest-mcp

This guide will help you set up pytest-mcp for development or usage.

## Installation

### For Users

Install from PyPI (when published):

```bash
pip install pytest-mcp
```

### For Development

1. Clone the repository

```bash
git clone https://github.com/yourusername/pytest-mcp.git
cd pytest-mcp
```

2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in editable mode

```bash
pip install -e ".[dev]"
```

## Verify Installation

Run these commands to verify everything is set up correctly:

```bash
# Check pytest-mcp version
python -c "import pytest_mcp; print(pytest_mcp.__version__)"

# Check pytest can find the plugin
pytest --version

# Run tests
pytest tests/ -v
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pytest_mcp --cov-report=html
open htmlcov/index.html  # View coverage report

# Run specific test file
pytest tests/test_client.py -v

# Run with pytest-mcp options
pytest --mcp-log-level=DEBUG --mcp-timeout=60
```

## Project Structure

```
pytest-mcp/
├── src/
│   └── pytest_mcp/         # Main package
│       ├── __init__.py     # Public API
│       ├── client.py       # MockMCPClient
│       ├── fixtures.py     # Pytest fixtures
│       ├── plugin.py       # Pytest plugin
│       ├── assertions.py   # Assertion helpers
│       ├── snapshot.py     # Snapshot testing
│       ├── server.py       # Server lifecycle
│       └── utils.py        # Utilities
├── tests/                  # Test suite
├── examples/               # Example servers
│   ├── basic_server/      # Calculator example
│   └── advanced/          # User management example
├── pyproject.toml         # Project config
├── README.md              # Main documentation
└── CONTRIBUTING.md        # Contribution guide
```

## Development Tools

### Code Formatting

```bash
# Format all code
black src/ tests/ examples/

# Check formatting without changes
black --check src/ tests/ examples/
```

### Linting

```bash
# Lint with ruff
ruff check src/ tests/ examples/

# Auto-fix issues
ruff check --fix src/ tests/ examples/
```

### Type Checking

```bash
# Type check with mypy
mypy src/

# Strict mode
mypy --strict src/
```

### All Quality Checks

```bash
# Run all checks at once
black . && ruff check . && mypy src/ && pytest
```

## Creating Your First Test

1. Create an MCP server (e.g., `my_server.py`):

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("my-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="greet",
            description="Greet someone",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "greet":
        return [TextContent(
            type="text",
            text=f"Hello, {arguments['name']}!"
        )]
```

2. Create a test file (`test_my_server.py`):

```python
import pytest
from pytest_mcp import assert_tool_exists

@pytest.fixture
def mcp_server():
    return {"command": "python", "args": ["my_server.py"]}

async def test_greet(mcp_client):
    await assert_tool_exists(mcp_client, "greet")
    result = await mcp_client.call_tool("greet", {"name": "World"})
    assert "Hello, World!" in result.content[0].text
```

3. Run the test:

```bash
pytest test_my_server.py -v
```

## Troubleshooting

### pytest doesn't find pytest-mcp fixtures

**Problem**: `fixture 'mcp_client' not found`

**Solution**: Ensure pytest-mcp is installed and the plugin is loaded:

```bash
pip list | grep pytest-mcp
pytest --version  # Should show pytest-mcp in plugins
```

### Tests hang or timeout

**Problem**: Tests never complete

**Solution**:
- Check that your server starts correctly: `python my_server.py`
- Increase timeout: `pytest --mcp-timeout=120`
- Enable debug logging: `pytest --mcp-log-level=DEBUG`

### Import errors

**Problem**: `ModuleNotFoundError: No module named 'pytest_mcp'`

**Solution**:

```bash
# Verify virtual environment
which python

# Reinstall
pip install -e .
```

### MCP SDK issues

**Problem**: Errors related to MCP SDK

**Solution**:

```bash
# Update MCP SDK
pip install --upgrade mcp

# Check version
python -c "import mcp; print(mcp.__version__)"
```

## Next Steps

- Read the [README.md](README.md) for full documentation
- Check out [examples/](examples/) for real-world usage
- Read [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Join discussions on GitHub

## Getting Help

- GitHub Issues for bug reports
- GitHub Discussions for questions
- Documentation in README.md
