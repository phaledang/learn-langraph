"""
Tests for Lab 03: LangChain Agents and Tools

Covers:
- Custom tool definition with @tool decorator
- Tool invocation and schema validation
- Agent pattern fundamentals (ReAct)
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# Custom Tool tests
# ---------------------------------------------------------------------------

class TestCustomTools:
    """Test creating and invoking custom LangChain tools."""

    def test_tool_decorator_creates_tool(self):
        @tool
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        assert add.name == "add"
        assert "Add two numbers" in add.description
        result = add.invoke({"a": 3, "b": 5})
        assert result == 8

    def test_tool_with_string_input(self):
        @tool
        def greet(name: str) -> str:
            """Greet a person by name."""
            return f"Hello, {name}!"

        result = greet.invoke({"name": "Alice"})
        assert result == "Hello, Alice!"

    def test_tool_schema(self):
        @tool
        def multiply(x: int, y: int) -> int:
            """Multiply two integers."""
            return x * y

        schema = multiply.args_schema.schema()
        assert "x" in schema["properties"]
        assert "y" in schema["properties"]

    def test_multiple_tools_list(self):
        @tool
        def search(query: str) -> str:
            """Search for information."""
            return f"Results for: {query}"

        @tool
        def calculate(expression: str) -> str:
            """Evaluate a math expression."""
            return f"Result: {eval(expression)}"

        tools = [search, calculate]
        assert len(tools) == 2
        assert tools[0].name == "search"
        assert tools[1].name == "calculate"


# ---------------------------------------------------------------------------
# Agent initialization tests (mocked)
# ---------------------------------------------------------------------------

class TestAgentSetup:
    """Test agent construction without calling LLM."""

    def test_tool_names_accessible(self):
        @tool
        def get_weather(city: str) -> str:
            """Get weather for a city."""
            return f"Sunny in {city}"

        @tool
        def search_web(query: str) -> str:
            """Search the web."""
            return f"Results for {query}"

        tools = [get_weather, search_web]
        tool_names = [t.name for t in tools]
        assert "get_weather" in tool_names
        assert "search_web" in tool_names

    def test_tool_error_handling(self):
        @tool
        def risky_tool(data: str) -> str:
            """A tool that may raise errors."""
            if not data:
                raise ValueError("Data cannot be empty")
            return f"Processed: {data}"

        with pytest.raises(Exception):
            risky_tool.invoke({"data": ""})
