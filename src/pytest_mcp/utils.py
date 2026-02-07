"""Shared utility functions for pytest-mcp."""

from __future__ import annotations

import asyncio
from typing import Any, TypeVar, Callable
from functools import wraps

T = TypeVar("T")


def is_async_test(func: Callable[..., Any]) -> bool:
    """
    Check if a function is an async test.

    Args:
        func: Function to check

    Returns:
        True if function is async
    """
    return asyncio.iscoroutinefunction(func)


def format_tool_signature(tool_name: str, arguments: dict[str, Any] | None) -> str:
    """
    Format a tool call as a readable signature.

    Args:
        tool_name: Name of the tool
        arguments: Tool arguments

    Returns:
        Formatted signature string

    Example:
        >>> format_tool_signature("add", {"a": 1, "b": 2})
        'add(a=1, b=2)'
    """
    if not arguments:
        return f"{tool_name}()"

    args_str = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
    return f"{tool_name}({args_str})"


def truncate_string(s: str, max_length: int = 100) -> str:
    """
    Truncate a string to maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length

    Returns:
        Truncated string with ellipsis if needed
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - 3] + "..."


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def extract_error_message(exception: Exception) -> str:
    """
    Extract a clean error message from an exception.

    Args:
        exception: Exception instance

    Returns:
        Clean error message
    """
    message = str(exception)

    # Remove common prefixes
    prefixes = ["Error: ", "Exception: ", "RuntimeError: "]
    for prefix in prefixes:
        if message.startswith(prefix):
            message = message[len(prefix) :]

    return message.strip()


def safe_repr(obj: Any, max_length: int = 200) -> str:
    """
    Get a safe string representation of an object.

    Args:
        obj: Object to represent
        max_length: Maximum length of representation

    Returns:
        String representation
    """
    try:
        if hasattr(obj, "model_dump"):
            # Pydantic model
            obj_dict = obj.model_dump()
            repr_str = repr(obj_dict)
        else:
            repr_str = repr(obj)

        return truncate_string(repr_str, max_length)

    except Exception:
        return f"<{type(obj).__name__} object>"


class TimeoutContext:
    """
    Context manager for operation timeouts.

    Example:
        >>> async with TimeoutContext(5.0):
        ...     await some_long_operation()
    """

    def __init__(self, timeout: float, error_message: str | None = None) -> None:
        """
        Initialize timeout context.

        Args:
            timeout: Timeout in seconds
            error_message: Custom error message
        """
        self.timeout = timeout
        self.error_message = error_message or f"Operation timed out after {timeout}s"

    async def __aenter__(self) -> None:
        """Enter context."""
        pass

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        pass


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to retry async functions on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        backoff: Backoff multiplier for delay

    Returns:
        Decorated function

    Example:
        >>> @retry_on_failure(max_attempts=3)
        ... async def flaky_operation():
        ...     # May fail sometimes
        ...     pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            # All attempts failed
            raise last_exception  # type: ignore

        return wrapper  # type: ignore

    return decorator


def validate_tool_arguments(
    arguments: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    """
    Validate tool arguments against a JSON schema.

    Args:
        arguments: Tool arguments to validate
        schema: JSON schema to validate against

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in arguments:
            errors.append(f"Missing required argument: {field}")

    # Check field types
    properties = schema.get("properties", {})
    for field, value in arguments.items():
        if field in properties:
            expected_type = properties[field].get("type")
            if expected_type:
                actual_type = type(value).__name__
                type_map = {
                    "str": "string",
                    "int": "integer",
                    "float": "number",
                    "bool": "boolean",
                    "list": "array",
                    "dict": "object",
                }
                if type_map.get(actual_type) != expected_type:
                    errors.append(
                        f"Argument '{field}' has wrong type: "
                        f"expected {expected_type}, got {actual_type}"
                    )

    return errors
