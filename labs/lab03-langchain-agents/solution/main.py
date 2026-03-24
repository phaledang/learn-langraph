"""
LangChain Agents and Tools - Solution Code

Complete implementation demonstrating langchain agents and tools.
Implements all 5 tasks from the README:
  1. Create Custom Tools
  2. Build ReAct Agent
  3. Integrate with External APIs
  4. Handle Agent Failures
  5. Build Multi-Tool Agent
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI

# Load environment variables from .env file relative to this script
load_dotenv(Path(__file__).parent / ".env")


# ---------------------------------------------------------------------------
# Task 1: Create Custom Tools
# ---------------------------------------------------------------------------

def calculator(expression: str) -> str:
    """Safely evaluate mathematical expressions."""
    try:
        # Only allow safe math operations
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return f"Error: expression contains invalid characters"
        result = eval(expression)
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="Useful for mathematical calculations. Input should be a valid math expression like '25 * 4 + 10'.",
)


def analyze_text(text: str) -> str:
    """Analyze text and return statistics."""
    if not text or not text.strip():
        return "Analysis: 0 words, 0 sentences, 0 characters (empty text)"
    words = text.split()
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    return (
        f"Analysis: {len(words)} words, {len(sentences)} sentences, {len(text)} characters"
    )


text_analyzer_tool = Tool(
    name="TextAnalyzer",
    func=analyze_text,
    description="Analyze text to get word count, sentence count, and character count. Input should be the text to analyze.",
)


# ---------------------------------------------------------------------------
# Task 3: Integrate with External APIs (mock weather tool)
# ---------------------------------------------------------------------------

def get_weather(location: str) -> str:
    """Get weather information for a location (mock implementation)."""
    weather_data = {
        "New York": "Sunny, 75°F",
        "London": "Cloudy, 60°F",
        "Tokyo": "Rainy, 68°F",
        "Paris": "Partly cloudy, 65°F",
        "Sydney": "Clear, 80°F",
    }
    return weather_data.get(
        location, f"Weather data not available for {location}"
    )


weather_tool = Tool(
    name="WeatherTool",
    func=get_weather,
    description="Get current weather for a specific location. Input should be a city name like 'New York'.",
)


# ---------------------------------------------------------------------------
# Task 5: Additional specialized tools for multi-tool agent
# ---------------------------------------------------------------------------

def file_info(filename: str) -> str:
    """Get information about a file (mock implementation)."""
    return f"File '{filename}': 1024 bytes, created today"


file_info_tool = Tool(
    name="FileInfo",
    func=file_info,
    description="Get information about a file. Input should be a filename.",
)


def unit_converter(conversion: str) -> str:
    """Convert between units (mock implementation)."""
    conversions = {
        "100 cm to m": "1 meter",
        "32 F to C": "0 degrees Celsius",
        "1 kg to lb": "2.205 pounds",
        "1 mile to km": "1.609 kilometers",
    }
    return conversions.get(conversion, f"Conversion not supported: {conversion}")


unit_converter_tool = Tool(
    name="UnitConverter",
    func=unit_converter,
    description="Convert between units. Input should be a conversion like '100 cm to m' or '32 F to C'.",
)


# ---------------------------------------------------------------------------
# Helper: create an Azure OpenAI LLM instance
# ---------------------------------------------------------------------------

def _create_llm(temperature: float = 0) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=temperature,
    )


def _run_agent(agent, query: str) -> str:
    """Invoke a create_react_agent graph and return the final AI message content."""
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


# ---------------------------------------------------------------------------
# Task 1: Demonstrate custom tools
# ---------------------------------------------------------------------------

def task1_create_custom_tools():
    """Demonstrate custom tool creation and direct invocation."""
    print("\n=== Task 1: Creating Custom Tools ===")

    # Test calculator tool
    print(f"\nCalculator: 25 * 4 + 10 → {calculator('25 * 4 + 10')}")
    print(f"Calculator: 200 * 0.15 → {calculator('200 * 0.15')}")

    # Test text analyzer tool
    sample = "The quick brown fox jumps over the lazy dog."
    print(f"\nTextAnalyzer: '{sample}' → {analyze_text(sample)}")

    print("\n✓ Calculator tool created")
    print("✓ Text analyzer tool created")
    print("✓ Tools ready for agent use")


# ---------------------------------------------------------------------------
# Task 2: Build ReAct Agent
# ---------------------------------------------------------------------------

def task2_react_agent():
    """Create and test a ReAct agent with basic tools."""
    print("\n\n=== Task 2: Building ReAct Agent ===")

    llm = _create_llm(temperature=0)
    tools = [calculator_tool, text_analyzer_tool]
    agent = create_agent(llm, tools)

    # Test the agent with a math question
    print("\nQuestion: What is 25 * 4 + 10?")
    result = _run_agent(agent, "What is 25 * 4 + 10?")
    print(f"Answer: {result}")

    # Test with text analysis
    print("\nQuestion: Analyze this text: 'AI is transforming the world of technology.'")
    result = _run_agent(agent, "Analyze this text: 'AI is transforming the world of technology.'")
    print(f"Answer: {result}")


# ---------------------------------------------------------------------------
# Task 3: Integrate with External APIs
# ---------------------------------------------------------------------------

def task3_external_apis():
    """Add external API tools and test the enhanced agent."""
    print("\n\n=== Task 3: External API Integration ===")

    llm = _create_llm(temperature=0)
    enhanced_tools = [calculator_tool, text_analyzer_tool, weather_tool]
    enhanced_agent = create_agent(llm, enhanced_tools)

    print("\nQuestion: What's the weather in New York?")
    result = _run_agent(enhanced_agent, "What's the weather in New York?")
    print(f"Answer: {result}")

    print("\nQuestion: What's the weather in London and what is 20 + 30?")
    result = _run_agent(enhanced_agent, "What's the weather in London and what is 20 + 30?")
    print(f"Answer: {result}")


# ---------------------------------------------------------------------------
# Task 4: Handle Agent Failures
# ---------------------------------------------------------------------------

def safe_agent_run(agent, query: str, max_retries: int = 3) -> str:
    """Run agent with error handling and retries."""
    for attempt in range(max_retries):
        try:
            return _run_agent(agent, query)
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return f"Agent failed after {max_retries} attempts: {str(e)}"
    return "Maximum retries exceeded"


def task4_error_handling():
    """Demonstrate graceful error handling with agents."""
    print("\n\n=== Task 4: Error Handling ===")

    llm = _create_llm(temperature=0)
    tools = [calculator_tool, text_analyzer_tool, weather_tool]
    agent = create_agent(llm, tools)

    challenging_queries = [
        "Calculate the square root of -1",
        "What's the weather on Mars?",
        "Analyze this text: ''",
    ]

    for query in challenging_queries:
        print(f"\nTesting: {query}")
        result = safe_agent_run(agent, query)
        print(f"Result: {result}")
        print("✓ Error handled gracefully")


# ---------------------------------------------------------------------------
# Task 5: Build Multi-Tool Agent
# ---------------------------------------------------------------------------

def task5_multi_tool_agent():
    """Create a comprehensive multi-tool agent for complex tasks."""
    print("\n\n=== Task 5: Multi-Tool Agent ===")

    llm = _create_llm(temperature=0)

    ultimate_tools = [
        calculator_tool,
        text_analyzer_tool,
        weather_tool,
        file_info_tool,
        unit_converter_tool,
    ]

    ultimate_agent = create_agent(llm, ultimate_tools)

    complex_query = (
        "I need to: "
        "1. Calculate 15% of 200, "
        "2. Check the weather in London, "
        "3. Analyze this text: 'The quick brown fox jumps over the lazy dog', "
        "4. Convert 100 cm to meters"
    )

    print(f"\nComplex query: {complex_query}")
    result = safe_agent_run(ultimate_agent, complex_query)
    print(f"\nFinal Answer: {result}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all tasks."""
    print("=" * 80)
    print("Lab 03: LangChain Agents and Tools — Solution")
    print("=" * 80)

    # Check API key
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Error: AZURE_OPENAI_API_KEY not set")
        return

    task1_create_custom_tools()
    task2_react_agent()
    task3_external_apis()
    task4_error_handling()
    task5_multi_tool_agent()

    print("\n=== Lab 03 Complete! ===")


if __name__ == "__main__":
    main()
