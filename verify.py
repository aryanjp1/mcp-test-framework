#!/usr/bin/env python
"""
Quick verification script to check that pytest-mcp is set up correctly.

Run this after installation to verify the package structure.
"""

import sys
from pathlib import Path


def check_import(module_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"[OK] {module_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] {module_name}: {e}")
        return False


def check_file(file_path: Path) -> bool:
    """Check if a file exists."""
    if file_path.exists():
        print(f"[OK] {file_path}")
        return True
    else:
        print(f"[FAIL] {file_path} (not found)")
        return False


def main() -> int:
    """Run verification checks."""
    print("pytest-mcp Verification")
    print("=" * 50)
    print()

    all_passed = True

    # Check core imports
    print("Checking imports...")
    imports = [
        "pytest_mcp",
        "pytest_mcp.client",
        "pytest_mcp.fixtures",
        "pytest_mcp.plugin",
        "pytest_mcp.assertions",
        "pytest_mcp.snapshot",
        "pytest_mcp.server",
        "pytest_mcp.utils",
    ]

    for module in imports:
        if not check_import(module):
            all_passed = False

    print()

    # Check public API
    print("Checking public API...")
    try:
        from pytest_mcp import (
            MockMCPClient,
            MCPTestServer,
            assert_tool_exists,
            assert_tool_output_matches,
            SnapshotHelper,
        )

        print("[OK] All main exports available")
    except ImportError as e:
        print(f"[FAIL] Public API incomplete: {e}")
        all_passed = False

    print()

    # Check project structure
    print("Checking project structure...")
    base = Path(__file__).parent

    files_to_check = [
        base / "pyproject.toml",
        base / "README.md",
        base / "LICENSE",
        base / "CHANGELOG.md",
        base / "CONTRIBUTING.md",
        base / "src" / "pytest_mcp" / "__init__.py",
        base / "tests" / "conftest.py",
        base / "examples" / "basic_server" / "server.py",
    ]

    for file_path in files_to_check:
        if not check_file(file_path):
            all_passed = False

    print()

    # Check version
    print("Checking version...")
    try:
        import pytest_mcp

        print(f"[OK] Version: {pytest_mcp.__version__}")
    except Exception as e:
        print(f"[FAIL] Could not get version: {e}")
        all_passed = False

    print()
    print("=" * 50)

    if all_passed:
        print("All checks passed. pytest-mcp is ready.")
        return 0
    else:
        print("Some checks failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
