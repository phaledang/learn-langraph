"""
Tests for Lab 03: LangChain Agents and Tools

Covers:
- Custom tool definition with @tool decorator
- Tool invocation and schema validation
- Agent pattern fundamentals (ReAct)
- Solution functions: calculator, text analyzer, weather, file info, unit converter
- Agent initialization, error handling, safe_agent_run
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.tools import tool

# Ensure the solution module is importable
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "labs", "lab03-langchain-agents", "solution"),
)
import main as lab03


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


# ---------------------------------------------------------------------------
# Lab 03 solution: Custom tool functions
# ---------------------------------------------------------------------------

class TestSolutionCalculator:
    """Test the calculator helper from the solution."""

    def test_basic_addition(self):
        assert "110" in lab03.calculator("25 * 4 + 10")

    def test_float_result(self):
        assert "30.0" in lab03.calculator("200 * 0.15")

    def test_invalid_expression(self):
        result = lab03.calculator("import os")
        assert "Error" in result

    def test_division_by_zero(self):
        result = lab03.calculator("1/0")
        assert "Error" in result


class TestSolutionTextAnalyzer:
    """Test the analyze_text helper from the solution."""

    def test_normal_text(self):
        result = lab03.analyze_text("The quick brown fox jumps over the lazy dog.")
        assert "9 words" in result

    def test_empty_text(self):
        result = lab03.analyze_text("")
        assert "0 words" in result


class TestSolutionWeather:
    """Test the mock weather tool from the solution."""

    def test_known_city(self):
        assert "Sunny" in lab03.get_weather("New York")
        assert "Cloudy" in lab03.get_weather("London")

    def test_unknown_city(self):
        assert "not available" in lab03.get_weather("Mars")


class TestSolutionFileInfo:
    """Test the mock file_info tool."""

    def test_returns_info(self):
        result = lab03.file_info("test.txt")
        assert "test.txt" in result
        assert "1024" in result


class TestSolutionUnitConverter:
    """Test the mock unit_converter tool."""

    def test_known_conversion(self):
        assert "1 meter" in lab03.unit_converter("100 cm to m")

    def test_unknown_conversion(self):
        assert "not supported" in lab03.unit_converter("100 miles to light years")


class TestSolutionSafeAgentRun:
    """Test safe_agent_run error handling without a real LLM."""

    def _make_mock_agent(self, invoke_side_effect=None, invoke_return=None):
        """Create a mock agent whose .invoke() returns message dicts."""
        mock_agent = MagicMock()
        if invoke_side_effect is not None:
            mock_agent.invoke.side_effect = invoke_side_effect
        elif invoke_return is not None:
            mock_agent.invoke.return_value = invoke_return
        return mock_agent

    def test_returns_result_on_success(self):
        msg = MagicMock()
        msg.content = "Success"
        mock_agent = self._make_mock_agent(invoke_return={"messages": [msg]})
        result = lab03.safe_agent_run(mock_agent, "test query")
        assert result == "Success"

    def test_retries_on_failure(self):
        msg = MagicMock()
        msg.content = "OK"
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = [
            Exception("fail"),
            Exception("fail"),
            {"messages": [msg]},
        ]
        result = lab03.safe_agent_run(mock_agent, "test query", max_retries=3)
        assert result == "OK"
        assert mock_agent.invoke.call_count == 3

    def test_returns_error_after_max_retries(self):
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = Exception("always fails")
        result = lab03.safe_agent_run(mock_agent, "test query", max_retries=2)
        assert "failed after 2 attempts" in result


class TestSolutionToolObjects:
    """Verify the Tool objects are properly constructed."""

    def test_calculator_tool_name(self):
        assert lab03.calculator_tool.name == "Calculator"

    def test_text_analyzer_tool_name(self):
        assert lab03.text_analyzer_tool.name == "TextAnalyzer"

    def test_weather_tool_name(self):
        assert lab03.weather_tool.name == "WeatherTool"

    def test_all_tools_have_descriptions(self):
        tools = [
            lab03.calculator_tool,
            lab03.text_analyzer_tool,
            lab03.weather_tool,
            lab03.file_info_tool,
            lab03.unit_converter_tool,
        ]
        for t in tools:
            assert t.description, f"Tool {t.name} has no description"
