# Python Language References - LangGraph Multi-Agent Systems

## Overview
This document explains **every** Python import, class, method, pattern, and language construct used in the Lab 07 solution (`solution/main.py`). It is organized in the same order the code appears in the file.

---

## 1. Standard Library Imports

### `import os`
```python
import os
```
**Purpose:** Access operating-system services — mainly environment variables.
**Used for:** `os.getenv("USE_AZURE_OPENAI", "0")` to read API keys and configuration from the environment or `.env` file.

### `from pathlib import Path`
```python
from pathlib import Path

_script_dir = Path(__file__).parent
```
**Purpose:** Object-oriented filesystem paths.
- `Path(__file__)` — the absolute path of the current `.py` file.
- `.parent` — the directory that contains the file.
**Used for:** Building relative paths to `.env` files so the script works regardless of the working directory.

### `from dotenv import load_dotenv`
```python
from dotenv import load_dotenv

load_dotenv(_script_dir / ".env")
```
**Purpose:** Read key-value pairs from a `.env` file and set them as environment variables.
**Package:** `python-dotenv`
**Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `dotenv_path` | `str \| Path` | Path to the `.env` file to load |
**Why:** Keeps secrets (API keys, endpoints) out of source code.

### `from typing import TypedDict, Annotated, List`
```python
from typing import TypedDict, Annotated, List
```

#### `TypedDict`
```python
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    next_agent: str
```
**Purpose:** Define a dictionary type where each key has a specific value type. Unlike a regular `dict`, IDEs and type checkers can validate key names and value types.
**Why used here:** LangGraph requires a typed state schema so the graph knows what data flows between nodes.

#### `Annotated`
```python
messages: Annotated[List, operator.add]
```
**Purpose:** Attach extra metadata to a type hint. The first argument is the actual type (`List`), subsequent arguments are metadata.
**Why used here:** LangGraph reads the second argument (`operator.add`) as a **reducer** — it tells the graph *how* to merge updates from different nodes into the existing state value.

#### `List`
```python
from typing import List
```
**Purpose:** Generic list type for type hints. `List` is equivalent to `list[...]` in Python 3.9+.
**Used for:** `messages: Annotated[List, operator.add]` — a list of strings that accumulates over time.

### `import operator`
```python
import operator
```
**Purpose:** Provides function equivalents of Python operators as callable objects.
**Key function used:**

#### `operator.add`
```python
messages: Annotated[List, operator.add]
```
**Purpose:** `operator.add(a, b)` returns `a + b`. For lists this means **concatenation**.
**Why used here:** When a node returns `{"messages": ["new msg"]}`, LangGraph calls `operator.add(existing_messages, ["new msg"])` to **append** rather than **replace**. This is the **reducer pattern**.

**Example:**
```python
import operator
existing = ["msg1", "msg2"]
new = ["msg3"]
result = operator.add(existing, new)  # ["msg1", "msg2", "msg3"]
```

---

## 2. LangChain Imports

### `ChatOpenAI` and `AzureChatOpenAI`
```python
from langchain_openai import ChatOpenAI, AzureChatOpenAI
```

#### `ChatOpenAI`
**Purpose:** LangChain wrapper around the OpenAI Chat Completions API.
```python
ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature)
```
| Parameter | Type | Description |
|---|---|---|
| `model` | `str` | Model name (e.g., `"gpt-3.5-turbo"`, `"gpt-4"`) |
| `temperature` | `float` | Randomness (0.0 = deterministic, 1.0 = creative) |

#### `AzureChatOpenAI`
**Purpose:** LangChain wrapper for Azure-hosted OpenAI deployments.
```python
AzureChatOpenAI(
    azure_deployment="gpt-4",
    azure_endpoint="https://xxx.openai.azure.com/",
    api_key="...",
    api_version="2024-05-01-preview",
    temperature=0.1,
)
```
| Parameter | Type | Description |
|---|---|---|
| `azure_deployment` | `str` | Name of your Azure deployment |
| `azure_endpoint` | `str` | Your Azure OpenAI endpoint URL |
| `api_key` | `str` | Azure API key |
| `api_version` | `str` | API version string |
| `temperature` | `float` | Randomness |

### `SystemMessage`
```python
from langchain_core.messages import HumanMessage, SystemMessage
```
**Purpose:** Typed message classes for the ChatModel API.

#### `SystemMessage(content="...")`
**Purpose:** A message with `role: "system"`. Sets the persona, instructions, and constraints for the LLM.
```python
response = llm.invoke([SystemMessage(content="You are a research agent...")])
```
**Used in this lab:** Every agent sends a single `SystemMessage` to define its role and task.

#### `HumanMessage(content="...")`
**Purpose:** A message with `role: "user"`. Imported but not directly used in this solution (agents use `SystemMessage` only). Available for extensions.

### `llm.invoke(messages)`
```python
response = llm.invoke([SystemMessage(content=research_prompt)])
research_data = response.content
```
**Purpose:** Send a list of messages to the LLM and get a response synchronously.
**Parameters:** A list of message objects (`SystemMessage`, `HumanMessage`, `AIMessage`).
**Returns:** An `AIMessage` object. Access the text with `.content`.

---

## 3. LangGraph Imports

### `StateGraph`
```python
from langgraph.graph import StateGraph, END
```
**Purpose:** The core class for building a directed graph where each node receives and returns a shared state dict.
```python
workflow = StateGraph(AgentState)
```
| Parameter | Type | Description |
|---|---|---|
| `state_schema` | `TypedDict` class | The typed dict that defines the shape of the state |

### `END`
```python
from langgraph.graph import StateGraph, END
```
**Purpose:** A sentinel constant representing the terminal node of the graph. When a conditional edge returns `END`, the workflow stops.
```python
if next_agent == "END":
    return END
```

---

## 4. State Schema — `AgentState`

```python
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]   # append-only message log
    next_agent: str                           # routing hint for conditional edges
    research_data: str                        # output of the researcher
    draft_content: str                        # output of the writer
    final_content: str                        # approved final article
    revision_count: int                       # guard against infinite loops
```

| Field | Type | Reducer | Purpose |
|---|---|---|---|
| `messages` | `List` | `operator.add` (append) | Accumulates a log of all agent actions across the entire run |
| `next_agent` | `str` | overwrite (default) | Each agent sets this to tell the router where to go next |
| `research_data` | `str` | overwrite | The researcher writes its findings here; the writer reads them |
| `draft_content` | `str` | overwrite | The writer writes the article; the supervisor reads it |
| `final_content` | `str` | overwrite | The supervisor writes the approved article here |
| `revision_count` | `int` | overwrite | Tracks how many revision loops have occurred; used as a safety cap |

**Key insight:** Only `messages` uses a reducer. All other fields use the default LangGraph behavior — **last write wins**.

---

## 5. Union Return Type — `ChatOpenAI | AzureChatOpenAI`

```python
def get_llm(temperature: float = 0.1) -> ChatOpenAI | AzureChatOpenAI:
```
**Syntax:** The `X | Y` union type (Python 3.10+) means the function can return either type.
**Why:** The function dynamically picks the provider based on the `USE_AZURE_OPENAI` env var.

### `os.getenv(key, default)`
```python
os.getenv("USE_AZURE_OPENAI", "0")
```
**Purpose:** Read an environment variable. Returns `default` if the variable is not set.
| Parameter | Type | Description |
|---|---|---|
| `key` | `str` | Environment variable name |
| `default` | `str \| None` | Fallback value (default `None`) |

---

## 6. The Factory / Closure Pattern

```python
def create_researcher_agent():
    """Create a research agent that gathers information on a topic."""

    def research_node(state: AgentState) -> dict:
        # ... agent logic ...
        return { "messages": [...], "research_data": data, "next_agent": "writer" }

    return research_node
```

### What is a closure?
A **closure** is an inner function that captures variables from its enclosing scope. When you call `create_researcher_agent()`, it returns the `research_node` function object. That function "closes over" any variables defined in the outer scope.

### Why use this pattern?
1. **Encapsulation** — Agent logic is self-contained inside the factory.
2. **Reusability** — You can call `create_researcher_agent()` multiple times to create multiple instances.
3. **Configuration** — The factory could accept parameters (e.g., `def create_researcher_agent(model="gpt-4"):`) to customize each agent.
4. **LangGraph compatibility** — `workflow.add_node("researcher", create_researcher_agent())` expects a callable that takes `state` and returns a dict.

### Returning a partial dict (not the full state)
```python
return {
    "messages": [f"Research completed on: {topic}"],
    "research_data": research_data,
    "next_agent": "writer",
}
```
**Why:** In LangGraph, nodes return only the **fields they want to update**. The graph engine merges the partial dict into the existing state (using the reducer for `messages`, overwrite for the rest). This is different from Lab 06 where nodes return the **entire state** (`return state`).

---

## 7. `state.get(key, default)`

```python
messages = state.get("messages", [])
topic = messages[-1] if messages else "artificial intelligence"
```
**Purpose:** Safely read a key from the state dict. Returns `default` if the key is missing or `None`.
**Why:** Defensive coding — the first invocation might have an empty state.

### `list[-1]` — Negative Indexing
```python
topic = messages[-1]
```
**Purpose:** Access the **last element** of a list. `-1` is the last, `-2` is second-to-last, etc.
**Used for:** Getting the most recent message (the topic string or the latest supervisor feedback).

---

## 8. f-strings and String Concatenation

### f-strings (formatted string literals)
```python
research_prompt = (
    f"You are a research agent. Research the topic: {topic}\n\n"
    "Provide key facts, statistics, and insights about this topic.\n"
)
```
**Syntax:** Prefix a string with `f` and embed expressions inside `{...}`.
**Why:** Cleanly inject variables (topic, research_data, draft_content) into prompt templates.

### Implicit string concatenation with parentheses
```python
research_prompt = (
    f"Line one {variable}\n"
    "Line two\n"
    "Line three"
)
```
**Purpose:** Python automatically concatenates adjacent string literals. Wrapping in `()` allows multi-line strings without `+` operators. This is cleaner than triple-quoted strings when you need precise control over newlines.

### `str.lower()`
```python
if "revision" in last_msg.lower():
```
**Purpose:** Returns a copy of the string converted to lowercase.
**Why:** Case-insensitive keyword matching — the supervisor might write "Revision" or "REVISION".

### `"keyword" in string`
```python
if "APPROVED" in feedback:
```
**Purpose:** The `in` operator tests substring membership.
**Returns:** `True` if `"APPROVED"` appears anywhere in `feedback`.

### `string[:120]`
```python
print(f"   Findings preview: {research_data[:120]}...")
```
**Purpose:** Slice the first 120 characters for a preview. `[:n]` is shorthand for `[0:n]`.

---

## 9. Module-Level Constants

```python
MAX_REVISIONS = 2  # cap revision loops
```
**Convention:** UPPER_SNAKE_CASE signals that this is a constant.
**Used in:** The supervisor agent checks `if revision_count >= MAX_REVISIONS:` to auto-approve and break infinite loops.

---

## 10. The Routing Function — `should_continue`

```python
def should_continue(state: AgentState) -> str:
    next_agent = state.get("next_agent", "END")
    if next_agent == "END":
        return END
    return next_agent
```
**Purpose:** A **condition function** passed to `add_conditional_edges`. LangGraph calls it after a node finishes, using the return value to pick the next edge.
**How it works:** Each agent sets `next_agent` in its return dict. This function simply reads that field and maps `"END"` to the `END` sentinel.
**Why only one router:** Unlike Lab 06 (which has 3 router functions), Lab 07 agents are autonomous — they decide routing themselves.

---

## 11. Graph Construction — `build_multiagent_graph()`

### `workflow.add_node(name, function)`
```python
workflow.add_node("researcher", create_researcher_agent())
workflow.add_node("writer", create_writer_agent())
workflow.add_node("supervisor", create_supervisor_agent())
```
**Purpose:** Register a named node in the graph. The function must accept the state dict and return a (partial) dict.
| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Unique identifier for the node |
| `function` | `Callable[[AgentState], dict]` | The node's logic (here, the closure returned by the factory) |

### `workflow.set_entry_point(name)`
```python
workflow.set_entry_point("researcher")
```
**Purpose:** Declare which node runs first when the graph is invoked. Equivalent to `add_edge(START, name)`.

### `workflow.add_conditional_edges(source, condition, mapping)`
```python
workflow.add_conditional_edges(
    "supervisor",
    should_continue,
    {"writer": "writer", END: END},
)
```
**Purpose:** After `source` finishes, call `condition(state)` and use the return value to look up the next node in `mapping`.
| Parameter | Type | Description |
|---|---|---|
| `source` | `str` | The node that just finished |
| `condition` | `Callable[[AgentState], str]` | Function returning a routing key |
| `mapping` | `dict[str, str]` | Maps routing keys to node names |

**Example flow:** Supervisor sets `next_agent = "writer"` → `should_continue` returns `"writer"` → mapping finds `"writer": "writer"` → the writer node runs next.

### `workflow.compile()`
```python
return workflow.compile()
```
**Purpose:** Validate the graph (check for dangling edges, unreachable nodes) and return a compiled `CompiledGraph` object that can be invoked.
**Returns:** A `CompiledGraph` with `.invoke()`, `.stream()`, `.get_graph()` methods.

---

## 12. `isinstance()` — Type Checking at Runtime

```python
compiled = graph.compile() if isinstance(graph, StateGraph) else graph
```
**Purpose:** Check if an object is an instance of a particular class (or tuple of classes).
**Returns:** `bool`
**Why:** The visualization helpers accept either an uncompiled `StateGraph` or an already-compiled graph. `isinstance` detects which one was passed so we compile only when needed.

### Ternary (conditional) expression
```python
x = A if condition else B
```
**Purpose:** Inline if/else. Evaluates to `A` when `condition` is `True`, otherwise `B`.

---

## 13. `hasattr(object, name)`

```python
node_ids.append(n.id if hasattr(n, "id") else str(n))
```
**Purpose:** Test whether an object has an attribute named `name`.
**Returns:** `bool`
**Why:** LangGraph's internal API has changed across versions — nodes may be strings, dicts, or objects with an `.id` attribute. `hasattr` provides safe duck-typing.

---

## 14. Graph Invocation — `app.invoke(state)`

```python
result = app.invoke(initial_state)
```
**Purpose:** Run the compiled graph from start to `END`, passing data through each node.
| Parameter | Type | Description |
|---|---|---|
| `state` | `AgentState` dict | The initial state |
**Returns:** The final state dict after all nodes have executed.

### Initial state construction
```python
initial_state: AgentState = {
    "messages": [topic],
    "next_agent": "researcher",
    "research_data": "",
    "draft_content": "",
    "final_content": "",
    "revision_count": 0,
}
```
**Why every field is set:** LangGraph expects the state to contain all declared keys at invocation time (or have defaults). Empty strings and `0` are safe initial values.

---

## 15. Graph Visualization Helpers

### `compiled.get_graph()`
```python
lg = compiled.get_graph()
```
**Purpose:** Return an introspectable graph object with `.nodes` and `.edges` collections.
**Used for:** Extracting node/edge data for all four visualization backends.

### `compiled.get_graph().draw_mermaid_png()`
```python
png_bytes = compiled.get_graph().draw_mermaid_png()
```
**Purpose:** Render the graph as a PNG image using the Mermaid diagram engine (requires internet — calls the Mermaid Ink API).
**Returns:** `bytes` — raw PNG data.

### Writing binary files
```python
with open(output_path, "wb") as f:
    f.write(png_bytes)
```
**`"wb"`:** Open for **w**riting in **b**inary mode. Required for PNG images.

### matplotlib — `matplotlib.use("Agg")`
```python
import matplotlib
matplotlib.use("Agg")   # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
```
**`matplotlib.use("Agg")`:** Select the "Anti-Grain Geometry" backend that renders to files only (no GUI window). Must be called **before** importing `pyplot`.
**`matplotlib.pyplot`:** MATLAB-style plotting interface — `plt.subplots()`, `fig.savefig()`, `plt.close()`.
**`matplotlib.patches.mpatches.Patch`:** Create colored legend patches.

### NetworkX
```python
import networkx as nx

G = nx.DiGraph()
G.add_node(nid)
G.add_edge(src, tgt, label=lbl)
pos = nx.spring_layout(G, seed=42, k=2.5)
nx.draw_networkx_nodes(G, pos, ...)
nx.draw_networkx_labels(G, pos, ...)
nx.draw_networkx_edges(G, pos, ...)
nx.draw_networkx_edge_labels(G, pos, ...)
```
| Method | Purpose |
|---|---|
| `nx.DiGraph()` | Create an empty **directed** graph |
| `.add_node(id)` | Add a node with a given identifier |
| `.add_edge(src, tgt, label=...)` | Add a directed edge with optional label |
| `nx.spring_layout(G, seed=42, k=2.5)` | Compute node positions using a force-directed algorithm. `seed` makes it reproducible, `k` controls spacing |
| `nx.draw_networkx_nodes(...)` | Draw the circles/shapes for nodes |
| `nx.draw_networkx_labels(...)` | Draw text labels on nodes |
| `nx.draw_networkx_edges(...)` | Draw arrows between nodes |
| `nx.draw_networkx_edge_labels(...)` | Draw text labels on edges |
| `nx.get_edge_attributes(G, "label")` | Return `{(src, tgt): label}` dict |

### Pyvis
```python
from pyvis.network import Network

net = Network(directed=True, height="600px", width="100%",
              bgcolor="#ffffff", font_color="#333333")
net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=200)
net.add_node(nid, label=nid, color="...", shape="ellipse", size=30, font={...})
net.add_edge(src, tgt, label=lbl, arrows="to", color="...", width=2)
net.write_html(output_path)
```
| Method | Purpose |
|---|---|
| `Network(directed=True, ...)` | Create an interactive HTML-based graph |
| `.barnes_hut(...)` | Configure the physics simulation for node layout |
| `.add_node(id, ...)` | Add a node with visual properties (color, shape, size, font) |
| `.add_edge(src, tgt, ...)` | Add a directed edge with visual properties |
| `.write_html(path)` | Save the interactive visualization as an HTML file |

### Graphviz
```python
import graphviz as gv

dot = gv.Digraph("MultiAgentWorkflow", format="png",
                  graph_attr={...}, node_attr={...})
dot.node(nid, label=nid, fillcolor="...", fontcolor="white", shape="box")
dot.edge(src, tgt, label=lbl)
dot.render(output_path, cleanup=True)
```
| Method | Purpose |
|---|---|
| `gv.Digraph(name, format, ...)` | Create a directed graph description in DOT language |
| `.node(id, ...)` | Add a node with visual attributes |
| `.edge(src, tgt, ...)` | Add a directed edge |
| `.render(path, cleanup=True)` | Render to file. `cleanup=True` removes the intermediate `.gv` file |

---

## 16. `generate_all_graph_images` — Graceful Degradation

```python
def generate_all_graph_images(graph) -> list[str]:
    results = []
    attempts = [
        ("Mermaid",    generate_graph_image),
        ("NetworkX",   generate_graph_networkx),
        ("Pyvis",      generate_graph_pyvis),
        ("Graphviz",   generate_graph_graphviz),
    ]
    for name, fn in attempts:
        try:
            path = fn(graph)
            results.append(path)
        except ImportError as e:
            print(f"⏭️  Skipping {name} visualisation (missing dependency: {e})")
        except Exception as e:
            print(f"⚠️  {name} visualisation failed: {e}")
    return results
```

### `try / except ImportError`
**Purpose:** Catch the error raised when `import matplotlib` or `import graphviz` fails because the package isn't installed. This lets the program continue with the backends that *are* available.

### `except Exception as e`
**Purpose:** Catch any other runtime error (network failure for Mermaid, file permission issues, etc.) without crashing the entire program.

### Tuple unpacking in a loop
```python
for name, fn in attempts:
```
**Purpose:** Each element of `attempts` is a 2-tuple `(str, function)`. Python unpacks them into `name` and `fn` on each iteration.

---

## 17. `enumerate(iterable, start)`

```python
for i, msg in enumerate(result.get("messages", []), 1):
    print(f"   {i}. {msg}")
```
**Purpose:** Loop over an iterable while also getting a counter. `start=1` makes the counter 1-based instead of 0-based.
**Returns:** An iterator of `(index, element)` tuples.

---

## 18. `result.get(key, default)`

```python
if result.get("final_content"):
```
**Purpose:** Same as `state.get()` — safely access a dict key with a fallback.
**Truthiness:** An empty string `""` is falsy in Python, so this check passes only when `final_content` has actual content.

---

## 19. `if __name__ == "__main__":`

```python
if __name__ == "__main__":
    main()
```
**Purpose:** The standard Python idiom to run code only when the file is executed directly (not when imported as a module).
- `__name__` is `"__main__"` when running `python main.py`.
- `__name__` is `"main"` (the module name) when doing `from solution import main`.

---

## 20. `list[str]` — Lowercase Generic Syntax (Python 3.9+)

```python
def generate_all_graph_images(graph) -> list[str]:
```
```python
node_ids: list[str] = []
edge_list: list[tuple[str, str, str]] = []
```
**Purpose:** Since Python 3.9, you can use `list[str]` directly instead of `List[str]` from `typing`. Same for `dict[str, str]`, `tuple[str, ...]`, etc.
**Note:** The state schema still uses `List` from `typing` because `Annotated[List, operator.add]` is a LangGraph convention.

---

## Summary of Key Patterns

| Pattern | Where Used | Why It Matters |
|---|---|---|
| **TypedDict + Annotated + operator.add** | `AgentState` | Defines shared state with a reducer for append-only fields |
| **Factory / closure** | `create_researcher_agent()`, etc. | Encapsulates agent logic and returns a LangGraph-compatible callable |
| **Partial dict return** | Every agent node | Agents update only the fields they own; LangGraph merges the rest |
| **Agent-driven routing** | `next_agent` field | Agents decide the next step, not external router functions |
| **Single routing function** | `should_continue()` | Reads `next_agent` and maps to node names or `END` |
| **Conditional edges everywhere** | `add_conditional_edges(...)` | Every edge is dynamic, enabling the revision loop |
| **MAX_REVISIONS guard** | Supervisor agent | Prevents infinite loops by auto-approving after N revisions |
| **Graceful degradation** | `generate_all_graph_images` | `try/except ImportError` skips unavailable visualization libraries |
| **f-string prompt templates** | All agents | Dynamically inject state data into LLM prompts |
| **Per-agent temperature** | `get_llm(temperature=...)` | Researcher (0.1, precise) vs. Writer (0.3, creative) |
