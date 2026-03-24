"""
Tests for Lab 12: Advanced MCP Patterns

Covers:
- Error handling in MCP servers
- Input validation
- Rate limiting patterns
- Authentication patterns
"""

import pytest
import time


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------

class TestMCPErrorHandling:
    """Test error-handling patterns for MCP tools."""

    def test_tool_error_response(self):
        def invoke_tool(name: str, args: dict) -> dict:
            if name not in ("search", "calculate"):
                return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}
            return {"isError": False, "content": [{"type": "text", "text": "OK"}]}

        result = invoke_tool("unknown_tool", {})
        assert result["isError"] is True
        assert "Unknown tool" in result["content"][0]["text"]

        result = invoke_tool("search", {"query": "test"})
        assert result["isError"] is False

    def test_missing_required_param(self):
        def validate_params(params: dict, required: list) -> list:
            return [r for r in required if r not in params]

        missing = validate_params({"city": "Paris"}, ["city", "date"])
        assert missing == ["date"]

        missing = validate_params({"city": "Paris", "date": "today"}, ["city", "date"])
        assert missing == []


# ---------------------------------------------------------------------------
# Input Validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_type_validation(self):
        def validate_type(value, expected_type: str) -> bool:
            type_map = {"string": str, "number": (int, float), "boolean": bool}
            return isinstance(value, type_map.get(expected_type, object))

        assert validate_type("hello", "string") is True
        assert validate_type(42, "number") is True
        assert validate_type(True, "boolean") is True
        assert validate_type(42, "string") is False

    def test_string_length_validation(self):
        def validate_length(value: str, max_len: int = 1000) -> bool:
            return len(value) <= max_len

        assert validate_length("short") is True
        assert validate_length("x" * 1001) is False


# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------

class TestRateLimiting:
    def test_simple_rate_limiter(self):
        class RateLimiter:
            def __init__(self, max_calls: int, period: float):
                self.max_calls = max_calls
                self.period = period
                self.calls = []

            def allow(self) -> bool:
                now = time.monotonic()
                self.calls = [t for t in self.calls if now - t < self.period]
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return True
                return False

        limiter = RateLimiter(max_calls=3, period=1.0)
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False  # 4th call exceeds limit


# ---------------------------------------------------------------------------
# Authentication patterns
# ---------------------------------------------------------------------------

class TestAuthPatterns:
    def test_api_key_validation(self):
        valid_keys = {"key-abc", "key-def"}

        def authenticate(api_key: str) -> bool:
            return api_key in valid_keys

        assert authenticate("key-abc") is True
        assert authenticate("invalid") is False

    def test_bearer_token_extraction(self):
        def extract_token(header: str) -> str | None:
            if header.startswith("Bearer "):
                return header[7:]
            return None

        assert extract_token("Bearer mytoken123") == "mytoken123"
        assert extract_token("Basic abc") is None
        assert extract_token("") is None
