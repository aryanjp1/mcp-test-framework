# Contributing to pytest-mcp

Thank you for considering contributing to pytest-mcp. This document provides guidelines and instructions for contributing.

## Ways to Contribute

- Report bugs through GitHub issues
- Suggest new features or improvements
- Improve documentation
- Write additional tests
- Submit code changes
- Share examples of real-world usage

## Getting Started

### Development Setup

1. Fork and clone the repository

```bash
git clone https://github.com/yourusername/pytest-mcp.git
cd pytest-mcp
```

2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode

```bash
pip install -e ".[dev]"
```

4. Verify installation

```bash
pytest --version
python -c "import pytest_mcp; print(pytest_mcp.__version__)"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pytest_mcp --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v

# Skip slow tests
pytest -m "not mcp_slow"
```

### Code Quality

We maintain code quality using these tools:

```bash
# Format code
black src/ tests/ examples/

# Check formatting
black --check src/ tests/ examples/

# Lint
ruff check src/ tests/ examples/

# Auto-fix issues
ruff check --fix src/ tests/ examples/

# Type check
mypy src/

# Run all checks
black . && ruff check . && mypy src/ && pytest
```

## Coding Standards

### Style Guide

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Include type hints for all function signatures

### Code Example

```python
from __future__ import annotations

from typing import Any


async def my_function(
    arg1: str,
    arg2: int,
    *,
    optional: bool = False,
) -> dict[str, Any]:
    """
    Brief description of the function.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        optional: Description of optional parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input is provided

    Example:
        >>> result = await my_function("test", 42)
        >>> print(result)
    """
    pass
```

### Documentation

- Use Google-style docstrings for all public functions and classes
- Include type hints for all parameters and return values
- Add usage examples in docstrings where helpful
- Explain why, not what (code should be self-explanatory)

### Testing

- Maintain test coverage above 90%
- Use descriptive test class and method names
- Use pytest's assert statements
- Mark async tests with `@pytest.mark.asyncio`
- Use fixtures for setup and teardown

Example test:

```python
import pytest
from pytest_mcp import MockMCPClient


class TestMyFeature:
    """Test suite for my feature."""

    @pytest.mark.asyncio
    async def test_basic_functionality(self, mcp_client: MockMCPClient) -> None:
        """Test that basic functionality works as expected."""
        result = await mcp_client.call_tool("test", {})
        assert result is not None
```

## Pull Request Process

### Before Submitting

1. Create a branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bugfix
```

2. Make your changes
   - Write code
   - Add tests
   - Update documentation

3. Run quality checks

```bash
black .
ruff check .
mypy src/
pytest
```

4. Commit your changes

```bash
git add .
git commit -m "feat: add new assertion helper"
# or
git commit -m "fix: correct error handling in client"
```

We follow Conventional Commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### Submitting

1. Push to your fork

```bash
git push origin feature/my-feature
```

2. Create Pull Request
   - Go to GitHub and create a PR
   - Fill out the PR template
   - Link related issues

3. Address review feedback
   - Make requested changes
   - Push additional commits
   - Re-request review

### PR Requirements

- All tests must pass
- Code coverage should not decrease
- Code must be formatted with black
- Linting must pass with ruff
- Type checking must pass with mypy
- Documentation must be updated
- CHANGELOG.md must be updated

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify you're using the latest version
3. Try to reproduce with a minimal example

### Bug Report Template

```markdown
**Description**
Clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Create MCP server with...
2. Run test with...
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Code Example**
# Minimal code to reproduce

**Environment:**
- pytest-mcp version: [e.g. 0.1.0]
- Python version: [e.g. 3.11.0]
- OS: [e.g. Ubuntu 22.04]
- MCP SDK version: [e.g. 1.0.0]

**Additional context**
Any other relevant information.
```

## Requesting Features

### Feature Request Template

```markdown
**Problem**
Description of the problem.

**Proposed Solution**
Description of what you want to happen.

**Alternatives**
Other solutions you've considered.

**Code Example**
# How you'd like to use the feature

**Additional context**
Any other context or screenshots.
```

## Documentation

### Documentation Needs

- API reference
- Tutorials for beginners
- Advanced usage patterns
- Integration guides
- Troubleshooting guide

### Documentation Style

- Use clear, simple language
- Provide code examples
- Include expected output
- Link to related concepts
- Keep content up-to-date

## Community

- GitHub Discussions for questions and ideas
- GitHub Issues for bug reports and feature requests
- Pull Requests for code contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions

If you have questions about contributing, please open a discussion on GitHub or reach out through the issue tracker.
