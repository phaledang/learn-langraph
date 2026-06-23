# Python Language References - Lab 11: Model Context Protocol Integration

## Overview
This document explains the Python methods, classes, and concepts used in this lab for creating MCP servers, exposing tools and resources, and integrating them with LangChain.

## Environment Setup

### Loading Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment")
```

**`load_dotenv()`:** Reads a `.env` file and populates `os.environ`.
**`os.getenv(key)`:** Safely retrieves an environment variable, returning `None` if absent.

## MCP Core Concepts

### What is MCP?
Model Context Protocol (MCP) is an open standard that allows AI models to interact with external tools and data sources through a structured server–client protocol. An MCP server exposes **tools** (callable functions) and **resources** (readable data) that a connected client (e.g., Claude, a LangChain agent) can discover and invoke.

## Creating an MCP Server with FastMCP

### Basic Server Setup
```python
from mcp.server.fastmcp import FastMCP

# Create the server instance
mcp = FastMCP("my-mcp-server")
```

**`FastMCP(name)`:** Creates a new MCP server with the given display name.
**`name` (str):** Human-readable identifier for the server, shown in MCP clients.

### Defining a Tool
```python
@mcp.tool()
def get_weather(city: str) -> str:
    """
    Return current weather for a city.

    Args:
        city: Name of the city to query.
    """
    # Implementation
    return f"Weather in {city}: 22°C, partly cloudy"
```

**`@mcp.tool()`:** Decorator that registers the function as an MCP tool.
**Docstring:** The first line becomes the tool description shown to the model.
**Type annotations:** MCP uses them to validate inputs and generate the JSON schema automatically.

### Defining a Tool with Multiple Parameters
```python
@mcp.tool()
def search_documents(query: str, max_results: int = 5) -> list[dict]:
    """
    Search internal documents and return matching results.

    Args:
        query: Search string.
        max_results: Maximum number of results to return (default 5).
    """
    results = document_store.search(query, limit=max_results)
    return [{"title": r.title, "snippet": r.snippet} for r in results]
```

**Default parameter values:** Supported natively; the model can omit optional arguments.
**Return type `list[dict]`:** MCP serializes return values as JSON automatically.

### Defining a Resource
```python
@mcp.resource("config://app-settings")
def get_app_settings() -> str:
    """Expose application configuration as a readable resource."""
    return """
    max_tokens: 1024
    temperature: 0.7
    model: gpt-4o-mini
    """
```

**`@mcp.resource(uri)`:** Registers the function as a readable MCP resource at the given URI.
**URI format:** Conventionally `scheme://path` (e.g., `config://`, `data://`, `file://`).
**Returns:** A string (typically JSON or plain text) that the model can read.

### Running the Server
```python
if __name__ == "__main__":
    mcp.run()
```

**`mcp.run()`:** Starts the MCP server (default transport: stdio for local use).

## Integrating MCP with LangChain

### Using MCPToolkit
```python
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Connect to a running MCP server
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["my_mcp_server.py"],
)
```

### Creating an Agent with MCP Tools
```python
async def run_agent_with_mcp():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Load tools from the MCP server
            tools = await load_mcp_tools(session)

            # Build a ReAct agent with those tools
            llm = ChatOpenAI(model="gpt-4o-mini")
            agent = create_react_agent(llm, tools)

            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": "What is the weather in Paris?"}]}
            )
            print(response["messages"][-1].content)
```

**`stdio_client(server_params)`:** Async context manager that spawns the MCP server as a subprocess and opens stdio streams.
**`ClientSession(read, write)`:** Manages the MCP protocol handshake and message framing.
**`session.initialize()`:** Performs the MCP capability negotiation; must be called before using tools.
**`load_mcp_tools(session)`:** Fetches the tool list from the server and wraps each as a LangChain `BaseTool`.

## Async / Await

### Async Context Managers
```python
async with some_context_manager() as resource:
    await resource.do_something()
# resource is automatically cleaned up here
```

**`async with`:** Like `with`, but for context managers that perform async setup/teardown.
**Use case:** Network connections, subprocess pipes, database sessions.

### Running Async Code from Sync Context
```python
import asyncio

asyncio.run(run_agent_with_mcp())
```

**`asyncio.run(coroutine)`:** Creates a new event loop, runs the coroutine to completion, then closes the loop.
**Rule:** Call `asyncio.run()` only at the top level (not inside another async function).

## Type Hints

### Common Annotations
```python
from typing import Optional, List, Dict, Any

def search(query: str, filters: Optional[Dict[str, Any]] = None) -> List[str]:
    ...
```

**`Optional[T]`:** Equivalent to `T | None`.
**`Dict[str, Any]`:** A dictionary with string keys and values of any type.
**`List[str]`:** A list of strings.

## String Formatting

### f-strings and Multi-line Strings
```python
tool_description = (
    f"Server '{server_name}' exposes {len(tools)} tools:\n"
    + "\n".join(f"  - {t.name}: {t.description}" for t in tools)
)
```

**f-string:** `f"..."` allows embedding expressions directly in string literals.
**`str.join(iterable)`:** Concatenates items of an iterable with the string as separator.

## List Comprehensions and Generator Expressions
```python
tool_names = [tool.name for tool in tools]
descriptions = "\n".join(t.description for t in tools if t.description)
```

**List comprehension:** `[expr for item in iterable if condition]` – builds a list.
**Generator expression:** `(expr for item in iterable)` – lazy; use inside function calls to avoid creating an intermediate list.

## Error Handling

### Try / Except in Async Code
```python
async def safe_tool_call(session, tool_name: str, args: dict):
    try:
        result = await session.call_tool(tool_name, args)
        return result.content
    except Exception as e:
        print(f"Tool call failed: {e}")
        return None
```

**`except Exception as e`:** Catches any exception and binds it to `e` for logging.
**Best practice:** Log the error and return a safe fallback rather than letting the program crash.

## Best Practices

1. **Document every tool** – the docstring is the model's only description of what a tool does; make it clear and specific.
2. **Use type annotations** – MCP uses them to build JSON schema for the model; missing annotations cause validation errors.
3. **Keep tools focused** – each tool should do one thing well; compose complex behaviour at the agent level.
4. **Handle errors in tools** – return an error message string rather than raising; the model can then decide what to do.
5. **Use `async` throughout** – MCP clients are async; mixing sync and async leads to hard-to-debug issues.

## Summary

| Concept | Key API / Syntax |
|---------|-----------------|
| Create MCP server | `FastMCP("name")` |
| Register tool | `@mcp.tool()` decorator |
| Register resource | `@mcp.resource("uri://path")` decorator |
| Start server | `mcp.run()` |
| Connect client | `stdio_client(StdioServerParameters(...))` |
| Load tools for LangChain | `await load_mcp_tools(session)` |
| Build ReAct agent | `create_react_agent(llm, tools)` |
| Run async code | `asyncio.run(coroutine)` |
