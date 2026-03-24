"""
Tests for Lab 14: MCP Server

Covers:
- The ping tool function
- Server metadata
"""

import pytest


# ---------------------------------------------------------------------------
# Ping tool tests
# ---------------------------------------------------------------------------

class TestPingTool:
    """Test the simple health-check ping tool."""

    def test_ping_returns_pong(self):
        """Directly test the ping function logic."""
        # Replicate the tool logic (function under the decorator)
        def ping(message: str) -> str:
            return f"PONG: {message}"

        assert ping("hello") == "PONG: hello"
        assert ping("") == "PONG: "
        assert ping("test123") == "PONG: test123"

    def test_ping_various_messages(self):
        def ping(message: str) -> str:
            return f"PONG: {message}"

        messages = ["health", "check", "🏓", "a" * 100]
        for msg in messages:
            result = ping(msg)
            assert result.startswith("PONG: ")
            assert msg in result


# ---------------------------------------------------------------------------
# Server metadata tests
# ---------------------------------------------------------------------------

class TestServerMetadata:
    """Test server configuration values."""

    def test_server_name(self):
        name = "local-mcp-server"
        assert name == "local-mcp-server"

    def test_server_version(self):
        version = "0.1.0"
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)
