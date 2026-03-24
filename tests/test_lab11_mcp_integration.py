"""
Tests for Lab 11: MCP (Model Context Protocol) Integration

Covers:
- MCP tool definition patterns
- Tool schema validation
- Resource and prompt patterns
"""

import pytest


# ---------------------------------------------------------------------------
# MCP Tool patterns
# ---------------------------------------------------------------------------

class TestMCPToolPatterns:
    """Test MCP tool definition and invocation patterns."""

    def test_tool_definition_dict(self):
        """MCP tools are described as JSON schemas."""
        tool_def = {
            "name": "get_weather",
            "description": "Get weather for a city",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        }
        assert tool_def["name"] == "get_weather"
        assert "city" in tool_def["inputSchema"]["properties"]

    def test_tool_result_format(self):
        result = {
            "content": [
                {"type": "text", "text": "Weather in Paris: 22°C, sunny"}
            ]
        }
        assert result["content"][0]["type"] == "text"
        assert "22°C" in result["content"][0]["text"]

    def test_multiple_tools_registry(self):
        tools = [
            {"name": "search", "description": "Search the web"},
            {"name": "calculate", "description": "Calculate math expressions"},
            {"name": "translate", "description": "Translate text"},
        ]
        names = [t["name"] for t in tools]
        assert "search" in names
        assert len(tools) == 3


# ---------------------------------------------------------------------------
# MCP Resource patterns
# ---------------------------------------------------------------------------

class TestMCPResourcePatterns:
    def test_resource_uri(self):
        resource = {
            "uri": "file:///data/report.txt",
            "name": "Monthly Report",
            "mimeType": "text/plain",
        }
        assert resource["uri"].startswith("file://")
        assert resource["mimeType"] == "text/plain"

    def test_resource_template(self):
        template = {
            "uriTemplate": "db://records/{id}",
            "name": "Record by ID",
        }
        uri = template["uriTemplate"].replace("{id}", "123")
        assert uri == "db://records/123"


# ---------------------------------------------------------------------------
# MCP Prompt patterns
# ---------------------------------------------------------------------------

class TestMCPPromptPatterns:
    def test_prompt_definition(self):
        prompt = {
            "name": "code_review",
            "description": "Review code for quality",
            "arguments": [
                {"name": "code", "required": True},
                {"name": "language", "required": False},
            ],
        }
        assert prompt["name"] == "code_review"
        required_args = [a for a in prompt["arguments"] if a["required"]]
        assert len(required_args) == 1
