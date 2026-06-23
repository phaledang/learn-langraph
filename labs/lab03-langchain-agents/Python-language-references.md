# Python Language References - LangChain Agents and Tools

## Overview
This document explains the Python syntax, methods, classes, and concepts used in Lab 03 (LangChain Agents and Tools). Each section below maps directly to code found in the README and solution (`solution/main.py`).

---

## 1. Imports

### Standard Library Imports
```python
import os
from pathlib import Path
```

- **`os`** – Provides access to operating system functions, such as reading environment variables with `os.getenv()`.
- **`pathlib.Path`** – Object-oriented filesystem path manipulation. `Path(__file__).parent` resolves the directory that contains the current script.

### Third-Party Imports
```python
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
```

| Import | Description |
|---|---|
| `load_dotenv` | Reads a `.env` file and injects its key-value pairs into the process environment. |
| `Tool` | LangChain class that wraps a plain Python function so an agent can call it. |
| `HumanMessage` | LangChain message type representing a message sent by a human/user. |
| `create_agent` | Helper that builds a ReAct (Reasoning + Acting) agent graph from an LLM and a list of tools. |
| `AzureChatOpenAI` | LangChain wrapper for Azure-hosted OpenAI chat models. |

---

## 2. Loading Environment Variables

```python
load_dotenv(Path(__file__).parent / ".env")
```

- `Path(__file__)` – absolute path to the currently-running Python file.
- `.parent` – the directory containing that file.
- `/ ".env"` – path division operator (equivalent to `os.path.join`); produces the `.env` path in the same directory.
- `load_dotenv(...)` – parses the file and sets matching `os.environ` entries.

Reading a variable after loading:
```python
api_key = os.getenv("AZURE_OPENAI_API_KEY")
```

**`os.getenv(key)`** – returns the value of the environment variable `key`, or `None` if it is not set.

---

## 3. Type Hints

```python
def calculator(expression: str) -> str:
    ...
```

- `expression: str` – annotates the parameter type.
- `-> str` – annotates the return type.

Type hints are optional but improve readability and enable static-analysis tools.

---

## 4. Docstrings

```python
def calculator(expression: str) -> str:
    """Safely evaluate mathematical expressions."""
    ...
```

A **docstring** is a string literal placed immediately after a `def` (or `class`) statement. It is accessible via `function.__doc__` and is used by tools, IDEs, and documentation generators.

---

## 5. `try` / `except` – Error Handling

```python
try:
    result = eval(expression)
    return f"The result is: {result}"
except Exception as e:
    return f"Error calculating: {str(e)}"
```

- The `try` block runs code that might raise an exception.
- If any exception occurs, the `except` block catches it. `Exception` is the base class for most built-in errors.
- `as e` binds the exception object to the name `e`, so `str(e)` can produce a human-readable message.

---

## 6. `set()` and Membership Testing

```python
allowed_chars = set("0123456789+-*/.() ")
if not all(c in allowed_chars for c in expression):
    return "Error: expression contains invalid characters"
```

- **`set(iterable)`** – creates an unordered collection of unique elements; membership lookup (`in`) is O(1).
- **`all(iterable)`** – returns `True` if every element of the iterable is truthy.
- The expression `c in allowed_chars for c in expression` is a **generator expression** that yields `True`/`False` for each character.

---

## 7. `eval()`

```python
result = eval(expression)
```

**`eval(expression)`** parses and evaluates the string `expression` as a Python expression and returns the result. Use with caution — always validate input first (as shown above with `allowed_chars`) to prevent code injection.

---

## 8. f-Strings (Formatted String Literals)

```python
return f"The result is: {result}"
return f"Error calculating: {str(e)}"
return f"Analysis: {len(words)} words, {len(sentences)} sentences, {len(text)} characters"
```

An **f-string** is prefixed with `f` (or `F`). Expressions inside `{}` are evaluated at runtime and their results are inserted into the string.

---

## 9. String Methods

### `.split()`
```python
words = text.split()          # splits on any whitespace
sentences = text.split(".")   # splits on the period character
```

Returns a list of substrings. With no argument, splits on whitespace and removes empty strings.

### `.strip()`
```python
sentences = [s.strip() for s in text.split(".") if s.strip()]
```

Removes leading and trailing whitespace (and newlines) from a string.

### `dict.get(key, default)`
```python
return weather_data.get(location, f"Weather data not available for {location}")
```

Returns the value for `key` if the key is in the dictionary; otherwise returns `default` (avoids a `KeyError`).

---

## 10. List Comprehensions

```python
sentences = [s.strip() for s in text.split(".") if s.strip()]
```

**Syntax**: `[expression for item in iterable if condition]`

Equivalent `for`-loop:
```python
sentences = []
for s in text.split("."):
    if s.strip():
        sentences.append(s.strip())
```

List comprehensions are more concise and generally faster.

---

## 11. `len()`

```python
len(words)      # number of items in a list
len(text)       # number of characters in a string
```

Built-in function that returns the number of items in a sequence or collection.

---

## 12. The `Tool` Class

```python
calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="Useful for mathematical calculations. Input should be a valid math expression like '25 * 4 + 10'.",
)
```

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Unique identifier the agent uses to refer to the tool. |
| `func` | `Callable` | The Python function the tool wraps. Must accept a single `str` argument and return a `str`. |
| `description` | `str` | Tells the LLM what the tool does and what input format to use. |

---

## 13. Dictionaries

```python
weather_data = {
    "New York": "Sunny, 75°F",
    "London": "Cloudy, 60°F",
    "Tokyo": "Rainy, 68°F",
}
```

A **dictionary** maps keys to values. Common operations:

```python
weather_data["New York"]            # direct access (raises KeyError if missing)
weather_data.get("London")          # safe access (returns None if missing)
weather_data.get("Mars", "N/A")     # safe access with default value
```

---

## 14. Creating the LLM

```python
def _create_llm(temperature: float = 0) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=temperature,
    )
```

- **Default parameter value** – `temperature: float = 0` means callers can omit `temperature` and it defaults to `0`.
- `AzureChatOpenAI` is configured entirely from environment variables, keeping credentials out of source code.
- `temperature=0` makes the model deterministic (no randomness).

---

## 15. `create_agent` and the ReAct Pattern

```python
from langchain.agents import create_agent

agent = create_agent(llm, tools)
```

`create_agent` builds a **ReAct** (Reasoning + Acting) agent. The agent repeatedly:
1. **Thinks** (reasons about the next step).
2. **Acts** (calls a tool).
3. **Observes** (reads the tool output).
4. Repeats until it can produce a **Final Answer**.

---

## 16. `HumanMessage` and `agent.invoke()`

```python
from langchain_core.messages import HumanMessage

result = agent.invoke({"messages": [HumanMessage(content=query)]})
final_answer = result["messages"][-1].content
```

- **`HumanMessage(content=query)`** – wraps the user's query into a typed message object.
- **`agent.invoke(input_dict)`** – runs the agent graph with the provided input and returns a dictionary containing a `"messages"` list.
- **`result["messages"][-1].content`** – retrieves the last message (the agent's final answer) from the result.

---

## 17. `for` Loop with `range()` and Retries

```python
def safe_agent_run(agent, query: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return _run_agent(agent, query)
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return f"Agent failed after {max_retries} attempts: {str(e)}"
    return "Maximum retries exceeded"
```

- **`range(n)`** – produces integers `0, 1, …, n-1`.
- The loop retries the agent up to `max_retries` times, catching any exception on each attempt.
- **Early return** (`return`) exits the function immediately on success.
- On the last attempt (`attempt == max_retries - 1`) the error message is returned instead of re-raising.

---

## 18. `print()` with f-Strings

```python
print(f"Calculator: 25 * 4 + 10 → {calculator('25 * 4 + 10')}")
print("✓ Calculator tool created")
```

`print()` writes to standard output. Combining it with f-strings allows embedding computed values directly in the output.

---

## 19. `if __name__ == "__main__"`

```python
if __name__ == "__main__":
    main()
```

Python sets `__name__` to `"__main__"` when a script is run directly (e.g., `python main.py`). When the file is imported as a module, `__name__` is the module name and `main()` is **not** called automatically. This guard is a standard Python pattern.

---

## 20. `initialize_agent`, `AgentType`, and `DuckDuckGoSearchRun`

The README uses the classic `initialize_agent` API alongside `AgentType` enums and a built-in search tool:

```python
from langchain.tools import Tool, DuckDuckGoSearchRun
from langchain.agents import AgentType, initialize_agent

tools = [calculator_tool, text_analyzer, DuckDuckGoSearchRun()]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
)
```

| Component | Description |
|---|---|
| `DuckDuckGoSearchRun()` | Pre-built LangChain tool that performs a DuckDuckGo web search. No API key required. |
| `AgentType.ZERO_SHOT_REACT_DESCRIPTION` | Enum value selecting the ReAct strategy where the agent picks tools based solely on their descriptions (no example shots). |
| `initialize_agent(tools, llm, agent, ...)` | Convenience factory that creates and configures an agent executor. |
| `verbose=True` | Prints the agent's internal reasoning steps (Thought / Action / Observation) to stdout. |
| `handle_parsing_errors=True` | Instructs the agent to recover gracefully when the LLM produces malformed output instead of raising an exception. |
| `max_iterations=10` | Caps how many Thought–Action–Observation cycles the agent may perform before stopping. |

Running the agent with `initialize_agent` uses `.run()` instead of `.invoke()`:

```python
result = agent.run("What is 25 * 4 + 10?")
```

**`agent.run(query)`** accepts a plain string and returns the agent's final answer as a string (compare with `agent.invoke()`, which accepts a dict and returns a dict).

---

## 21. Boolean Operators: `not`, `or`, `and`

```python
if not text or not text.strip():
    return "Analysis: 0 words, 0 sentences, 0 characters (empty text)"
```

```python
if not os.getenv("AZURE_OPENAI_API_KEY"):
    print("Error: AZURE_OPENAI_API_KEY not set")
    return
```

| Operator | Meaning |
|---|---|
| `not x` | `True` if `x` is falsy (empty string, `None`, `0`, empty list, …). |
| `x or y` | Evaluates to `x` if `x` is truthy, otherwise to `y`. Used here as a short-circuit guard. |
| `x and y` | Evaluates to `x` if `x` is falsy, otherwise to `y`. |

The pattern `if not text or not text.strip()` is a **guard clause** – it exits the function early when the input is `None`, an empty string, or a string of only whitespace.

---

## 22. String Repetition

```python
print("=" * 80)
```

The `*` operator applied to a string and an integer repeats the string that many times. `"=" * 80` produces a line of 80 equals signs, commonly used as a visual separator in terminal output.

---

## 23. Multi-Line String with Parentheses

```python
return (
    f"Analysis: {len(words)} words, {len(sentences)} sentences, {len(text)} characters"
)

complex_query = (
    "I need to: "
    "1. Calculate 15% of 200, "
    "2. Check the weather in London, "
    "3. Analyze this text: 'The quick brown fox jumps over the lazy dog', "
    "4. Convert 100 cm to meters"
)
```

Wrapping an expression in parentheses `(...)` lets you split it across multiple lines without needing a backslash `\`. Adjacent string literals are automatically **concatenated** by Python at compile time, so the second example produces a single long string. This is the preferred style for long strings or expressions.

---

## Best Practices Demonstrated in This Lab

1. **Validate `eval()` input** – restrict allowed characters before calling `eval()` to prevent injection attacks.
2. **Use environment variables for secrets** – never hard-code API keys; read them with `os.getenv()`.
3. **Write descriptive docstrings** – LangChain uses docstrings and `description` fields to guide the LLM's tool selection.
4. **Handle errors gracefully** – wrap agent calls in `try/except` and implement retry logic for transient failures.
5. **Use type hints** – annotate function parameters and return types for clarity and tooling support.
6. **Use f-strings** – prefer f-strings over `%`-formatting or `.format()` for readability.

---

## Summary

| Concept | Where Used |
|---|---|
| `import` / `from … import` | All modules at the top of `main.py` |
| `Path(__file__).parent` | Locating the `.env` file relative to the script |
| `os.getenv()` | Reading Azure OpenAI credentials |
| `load_dotenv()` | Loading credentials from `.env` |
| Type hints | All function signatures |
| Docstrings | All functions (also used as tool descriptions) |
| `try` / `except` | `calculator()`, `safe_agent_run()` |
| `set()` + `all()` + generator expression | Input validation in `calculator()` |
| `eval()` | Evaluating math expressions safely |
| f-strings | All string formatting throughout |
| `.split()` / `.strip()` | Text analysis in `analyze_text()` |
| `dict.get(key, default)` | Safe dictionary lookup in `get_weather()` |
| List comprehension | Sentence splitting in `analyze_text()` |
| `Tool(name, func, description)` | Wrapping functions as agent tools |
| `AzureChatOpenAI` | LLM instantiation |
| `create_agent(llm, tools)` | Building the ReAct agent |
| `HumanMessage` | Formatting queries for the agent |
| `agent.invoke()` | Running the agent |
| `for` loop + `range()` | Retry loop in `safe_agent_run()` |
| `if __name__ == "__main__"` | Script entry-point guard |
| `initialize_agent`, `AgentType`, `DuckDuckGoSearchRun` | Alternative agent construction API shown in README |
| `agent.run()` | Running an `initialize_agent`-style agent with a plain string query |
| `not` / `or` / `and` | Boolean guard clauses (`if not text or not text.strip()`) |
| `"=" * 80` | String repetition for terminal separators |
| Multi-line string with `()` | Splitting long strings/expressions across lines |
