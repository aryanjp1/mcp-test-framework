# Changelog

All notable changes to pytest-mcp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-07

### Fixed
- Fixed stdio client connection issue using AsyncExitStack to properly manage nested context managers
- Streams and session now stay alive for the entire client lifetime
- Fixed ClosedResourceError when calling MCP tools
- Added hasattr check for asyncio_mode in plugin to prevent AttributeError
- Updated repository URLs in pyproject.toml to match renamed repo

### Changed
- Build configuration now uses metadata version 2.1 for PyPI compatibility

## [0.1.0] - 2026-02-07

### Added
- Initial release of pytest-mcp
- MockMCPClient for in-process server testing
- Auto-injected pytest fixtures (mcp_client, mcp_test_server)
- Rich assertion helpers
  - assert_tool_exists
  - assert_tool_count
  - assert_tool_output_matches
  - assert_tool_returns_error
  - assert_resource_exists
  - assert_resource_content_matches
  - assert_tool_schema_valid
  - assert_tools_have_unique_names
- Snapshot testing support
  - JSON snapshots
  - Text snapshots
  - Update mode via --mcp-update-snapshots CLI flag
- Server lifecycle management with MCPTestServer
- Pytest plugin with automatic fixture registration
- Custom pytest markers (@pytest.mark.mcp, @pytest.mark.mcp_integration)
- Command-line options
  - --mcp-log-level for debugging
  - --mcp-timeout for operation timeouts
- Comprehensive documentation and examples
- Full type hints (mypy strict compatible)
- Example calculator server with tests
- Example user management server with tests

### Features
- Async-first design using anyio
- Support for tools and resources
- Flexible server configuration (StdioServerParameters, dict, tuple)
- Environment variable support
- Snapshot versioning and comparison
- Detailed error messages

### Documentation
- Comprehensive README with quick start guide
- API reference documentation
- Multiple usage examples
- Contributing guidelines
- MIT License

## [Unreleased]

### Planned
- Support for SSE (Server-Sent Events) transport
- HTTP transport support
- Test fixtures for common MCP patterns
- Performance benchmarking utilities
- Mock server generator
- Integration with popular MCP servers
- VS Code extension for test running
- Docker support for isolated testing
- Multi-server orchestration helpers
- Test coverage reporting integration

---

Legend:
- Added - New features
- Changed - Changes in existing functionality
- Deprecated - Soon-to-be removed features
- Removed - Removed features
- Fixed - Bug fixes
- Security - Vulnerability fixes
