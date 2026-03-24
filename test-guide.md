# Test Guide

A complete guide for setting up and running the pytest test suite for the LangChain / LangGraph labs.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Running Tests](#running-tests)
4. [Test File Overview](#test-file-overview)
5. [Shared Fixtures (conftest.py)](#shared-fixtures-conftestpy)
6. [Writing New Tests](#writing-new-tests)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement       | Version   | Purpose                                       |
|-------------------|-----------|-----------------------------------------------|
| Python            | ≥ 3.10    | Runtime                                       |
| pip               | latest    | Package management                            |
| pytest            | ≥ 7.4.3   | Test framework                                |
| Virtual env       | any       | Isolation (`venv`, `conda`, etc.)             |

> **No API keys are required to run the tests.** All LLM and external service calls are mocked.

---

## Project Setup

### 1. Create & activate a virtual environment

```bash
# Create
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS / Linux)
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs all project packages **including pytest**. If you only want the test tooling:

```bash
pip install pytest
```

### 3. Verify the installation

```bash
pytest --version
```

You should see output like `pytest 7.x.x` or later.

---

## Running Tests

### Configuration

Tests are configured in `pytest.ini` at the project root:

```ini
[pytest]
addopts = -v
testpaths = tests
python_files = test_*.py
```

- **`-v`** — verbose output (shows each test name and result)
- **`testpaths = tests`** — pytest only scans the `tests/` directory
- **`python_files = test_*.py`** — only files matching `test_*.py` are collected

### Run all tests

```bash
pytest
```

### Run a single test file

```bash
# All tests in lab05
pytest tests/test_lab05_langgraph_basics.py

# All tests in lab08
pytest tests/test_lab08_langgraph_persistence.py
```

### Run a specific test class

```bash
pytest tests/test_lab05_langgraph_basics.py::TestConditionalGraph
```

### Run a specific test function

```bash
pytest tests/test_lab05_langgraph_basics.py::TestConditionalGraph::test_even_number
```

### Run tests by keyword expression

```bash
# Run all tests with "router" in the name
pytest -k "router"

# Run all tests with "chain" but not "batch"
pytest -k "chain and not batch"
```

### Run tests for a specific lab range

```bash
# Labs 01-04 (LangChain labs)
pytest tests/test_lab01_langchain_basics.py tests/test_lab02_langchain_chains.py tests/test_lab03_langchain_agents.py tests/test_lab04_langchain_memory.py

# Labs 05-08 (LangGraph labs)
pytest tests/test_lab05_langgraph_basics.py tests/test_lab06_langgraph_stateful.py tests/test_lab07_langgraph_multiagent.py tests/test_lab08_langgraph_persistence.py
```

### Useful flags

| Flag                  | Description                                      |
|-----------------------|--------------------------------------------------|
| `-v`                  | Verbose — show each test name (already in ini)   |
| `-s`                  | Show `print()` output (not captured)             |
| `--tb=short`          | Shorter traceback on failure                     |
| `--tb=long`           | Full traceback on failure                        |
| `-x`                  | Stop on first failure                            |
| `--lf`                | Re-run only last-failed tests                    |
| `--co`                | Collect & list tests without running them        |
| `-q`                  | Quiet — minimal output                           |
| `--durations=10`      | Show the 10 slowest tests                        |

### Example: fast feedback loop

```bash
# Stop on first failure, short traceback, show prints
pytest -x --tb=short -s
```

---

## Test File Overview

| Test File                            | Lab    | Tests | What's Covered                                                        |
|--------------------------------------|--------|------:|-----------------------------------------------------------------------|
| `test_hello.py`                      | —      |    13 | Smoke tests (arithmetic, strings, collections, types)                 |
| `test_lab01_langchain_basics.py`     | Lab 01 |     6 | `PromptTemplate`, `StrOutputParser`, LCEL chain invoke & batch        |
| `test_lab02_langchain_chains.py`     | Lab 02 |     9 | Sequential chains, keyword router logic, RAG components               |
| `test_lab03_langchain_agents.py`     | Lab 03 |     7 | `@tool` decorator, schema validation, tool registry, error handling   |
| `test_lab04_langchain_memory.py`     | Lab 04 |     8 | `HumanMessage` / `AIMessage`, sliding window, serialization           |
| `test_lab05_langgraph_basics.py`     | Lab 05 |    10 | `TypedDict` state, linear graph, conditional routing, parametrized    |
| `test_lab06_langgraph_stateful.py`   | Lab 06 |     8 | Workflow / approval states, node functions, routing, `MemorySaver`    |
| `test_lab07_langgraph_multiagent.py` | Lab 07 |     9 | Multi-agent state, agent nodes, supervisor routing, pipeline graph    |
| `test_lab08_langgraph_persistence.py`| Lab 08 |    10 | `StateDocument`, `detect_database_type`, factory, checkpoint graph    |
| `test_lab09_langsmith_tracing.py`    | Lab 09 |     5 | Tracing env vars, metadata, tags, run config                         |
| `test_lab10_langsmith_evaluation.py` | Lab 10 |     7 | Evaluators (exact match, contains, length, numeric), dataset struct   |
| `test_lab11_mcp_integration.py`      | Lab 11 |     5 | MCP tool / resource / prompt schema patterns                         |
| `test_lab12_mcp_advanced.py`         | Lab 12 |     6 | Error handling, input validation, rate limiting, auth patterns        |
| `test_lab13_pdf_to_csv.py`           | Lab 13 |    16 | `CourseRecord`, page-range parsing, guide cleaning, `build_llm`      |
| `test_lab14_mcp_server.py`           | Lab 14 |     4 | `ping` tool, server metadata                                        |
| `test_lab14_mcp_sharepoint.py`       | Lab 14 |    12 | Pydantic schemas, routing functions, mock search, node logic          |

> **Lab 13 note:** Tests auto-skip via `pytest.importorskip` if `pandas` or `pypdf` are not installed.

---

## Shared Fixtures (conftest.py)

The file `tests/conftest.py` provides reusable fixtures available to **all** test files:

| Fixture                      | What It Does                                                         |
|------------------------------|----------------------------------------------------------------------|
| `mock_env_openai`            | Sets fake `OPENAI_API_KEY` and `OPENAI_MODEL` env vars              |
| `mock_env_azure_openai`      | Sets fake Azure OpenAI env vars (key, endpoint, deployment, version) |
| `mock_llm_response`          | Factory that returns a `MagicMock` LLM with a configurable response |
| `mock_db_connection_string`  | Sets a fake PostgreSQL `DATABASE_CONNECTION_STRING` env var          |

### Using a fixture in your test

```python
def test_something(mock_env_azure_openai):
    """This test has Azure env vars available automatically."""
    import os
    assert os.getenv("AZURE_OPENAI_API_KEY") == "test-azure-key-fake"
```

Fixtures that use `monkeypatch` are **automatically cleaned up** after each test.

---

## Writing New Tests

### 1. File naming

Create your test file in `tests/` with the prefix `test_`:

```
tests/test_lab15_my_new_lab.py
```

### 2. Basic test structure

```python
"""
Tests for Lab 15: My New Lab
"""

import pytest


class TestMyFeature:
    """Group related tests in a class."""

    def test_basic_behavior(self):
        result = 1 + 1
        assert result == 2

    def test_with_fixture(self, mock_env_openai):
        import os
        assert os.getenv("OPENAI_API_KEY") is not None

    @pytest.mark.parametrize("input_val,expected", [
        (2, 4),
        (3, 9),
        (0, 0),
    ])
    def test_square(self, input_val, expected):
        assert input_val ** 2 == expected
```

### 3. Mocking LLM calls

Never call real APIs in tests. Use `RunnableLambda` for LCEL chains:

```python
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

fake_llm = RunnableLambda(lambda _: AIMessage(content="Mocked response"))

chain = prompt | fake_llm | StrOutputParser()
result = chain.invoke({"topic": "test"})
```

### 4. Skipping tests conditionally

```python
# Skip if a package is missing
pandas = pytest.importorskip("pandas", reason="pandas not installed")

# Skip with a custom condition
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires real API key"
)
def test_live_api_call():
    ...
```

### 5. Testing LangGraph graphs

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class MyState(TypedDict):
    value: int

def increment(state: MyState) -> MyState:
    state["value"] += 1
    return state

def test_my_graph():
    wf = StateGraph(MyState)
    wf.add_node("inc", increment)
    wf.set_entry_point("inc")
    wf.add_edge("inc", END)
    app = wf.compile()

    result = app.invoke({"value": 0})
    assert result["value"] == 1
```

---

## Troubleshooting

### Tests not discovered

- Ensure the file is in `tests/` and starts with `test_`.
- Ensure test functions start with `test_` or are inside a `Test*` class.
- Run `pytest --co` to see what pytest collects.

### ModuleNotFoundError

- Verify your virtual environment is activated.
- Run `pip install -r requirements.txt`.
- For Lab 13 specifically: `pip install pandas pypdf`.

### Import errors from lab modules

`conftest.py` adds lab directories to `sys.path`. If you add a new lab, add its path there:

```python
# In tests/conftest.py
_paths_to_add = [
    ...
    os.path.join(PROJECT_ROOT, "labs", "lab15-my-new-lab", "solution"),
]
```

### Tests pass locally but fail in CI

- Check that all env vars are mocked (use `monkeypatch`, not real `.env` files).
- Ensure no test depends on file system paths that differ across OS.

### Slow tests

```bash
# Find the 10 slowest tests
pytest --durations=10
```

---

## VS Code Integration

1. Open the **Testing** panel (beaker icon in the sidebar).
2. VS Code auto-detects pytest from `pytest.ini`.
3. Click ▶ to run all, or click individual tests to run/debug them.
4. Set breakpoints and use **Debug Test** for step-through debugging.

> **Tip:** Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for full testing UI support.
