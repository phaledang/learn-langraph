# Python Language References - Lab 05: LangGraph Basics

## TypedDict for State Schema

### Defining State
```python
from typing import TypedDict

class AgentState(TypedDict):
    messages: list
    step: int
    result: str
```

**Purpose:** Provides type hints for dictionary keys and values
**Benefits:**
- IDE autocomplete support
- Type checking
- Clear documentation of state structure

**Key Points:**
- Inherits from `TypedDict`
- Each attribute defines a key-value type
- Optional fields use `NotRequired[]` (Python 3.11+) or `total=False`

## LangGraph Core Components

### StateGraph Class
```python
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)
```

**Constructor:**
- `StateGraph(state_schema)`: Creates a graph with typed state

**Methods:**
- `add_node(name, function)`: Add a processing node
- `add_edge(from_node, to_node)`: Add a directed edge
- `add_conditional_edges(from_node, routing_fn, mapping)`: Add conditional routing
- `set_entry_point(node)`: Set starting node
- `compile()`: Compile graph into executable app

### Node Functions
```python
def process_input(state: AgentState) -> AgentState:
    """Node function that processes state."""
    state["step"] += 1
    return state
```

**Requirements:**
- Accept state as parameter
- Return updated state (same type)
- Can modify state in-place or create new dict

**Type Signature:**
```python
NodeFunction = Callable[[State], State]
```

### Adding Nodes
```python
workflow.add_node("node_name", node_function)
```

**Parameters:**
- `name` (str): Unique identifier for the node
- `function`: Callable that processes state

**Best Practice:** Use descriptive names that indicate node purpose

### Regular Edges
```python
workflow.add_edge("node_a", "node_b")
```

**Behavior:**
- Creates direct connection from node_a to node_b
- Execution always follows this path
- Deterministic flow

**Special Node:**
```python
from langgraph.graph import END

workflow.add_edge("final_node", END)
```
- `END`: Special marker indicating graph termination

### Conditional Edges
```python
workflow.add_conditional_edges(
    source_node,
    routing_function,
    edge_mapping
)
```

**Parameters:**
- `source_node` (str): Node where routing decision is made
- `routing_function`: Function that returns next node name
- `edge_mapping` (dict): Maps routing function output to next nodes

**Routing Function Example:**
```python
from typing import Literal

def route(state: AgentState) -> Literal["path_a", "path_b"]:
    if state["count"] > 5:
        return "path_a"
    return "path_b"
```

**Key Points:**
- Routing function receives current state
- Returns string matching a key in edge_mapping
- Use `Literal` type hint for valid return values

### Entry and Exit Points
```python
# Set where graph starts
workflow.set_entry_point("first_node")

# Mark where graph ends
workflow.add_edge("last_node", END)
```

**Entry Point:**
- First node executed when graph is invoked
- Must be set before compilation

**Exit Point:**
- Use `END` constant to mark termination
- Can have multiple paths leading to END

### Compiling the Graph
```python
app = workflow.compile()
```

**Returns:** Runnable application
**Process:** Validates graph structure and creates execution plan

**Validation Checks:**
- Entry point is set
- All nodes are reachable
- No disconnected components
- Conditional edges have valid mappings

### Invoking the Graph
```python
result = app.invoke(initial_state)
```

**Parameters:**
- `initial_state` (dict): Starting state matching schema

**Returns:** Final state after graph execution

**Execution Flow:**
1. Start at entry point
2. Execute node function
3. Update state
4. Follow edges to next node
5. Repeat until END is reached

## Advanced Typing

### Literal Type
```python
from typing import Literal

def route(state) -> Literal["continue", "stop"]:
    return "continue" if state["count"] < 10 else "stop"
```

**Purpose:** Restricts return value to specific strings
**Benefits:**
- Type checker validates return values
- Autocomplete shows valid options
- Documents allowed values

### Generic State Updates
```python
def update_state(state: AgentState) -> AgentState:
    # Method 1: Direct modification
    state["count"] += 1
    
    # Method 2: Create new dict (immutable approach)
    return {**state, "count": state["count"] + 1}
```

**Approaches:**
- **In-place:** Modifies existing dict (mutable)
- **Copy:** Creates new dict (immutable, safer)

## State Management Patterns

### Initializing State
```python
initial_state: AgentState = {
    "messages": [],
    "step": 0,
    "result": "",
    "iterations": 0
}
```

### Reading State Values
```python
# Direct access (may raise KeyError)
value = state["key"]

# Safe access with default
value = state.get("key", default_value)
```

### Updating State
```python
# Single field
state["step"] += 1

# Multiple fields
state.update({
    "step": state["step"] + 1,
    "result": "processed"
})

# Spread operator (dictionary unpacking)
new_state = {
    **state,
    "step": state["step"] + 1,
    "result": "processed"
}
```

## Control Flow Patterns

### Linear Flow
```
start → node1 → node2 → node3 → END
```
```python
workflow.set_entry_point("node1")
workflow.add_edge("node1", "node2")
workflow.add_edge("node2", "node3")
workflow.add_edge("node3", END)
```

### Conditional Branching
```
         ┌→ node_a → END
start → check
         └→ node_b → END
```
```python
workflow.add_conditional_edges(
    "check",
    routing_function,
    {"path_a": "node_a", "path_b": "node_b"}
)
```

### Cyclic Flow (Loops)
```
start → process → check → END
              ↑        |
              └────────┘
```
```python
def should_continue(state) -> Literal["continue", "end"]:
    return "continue" if state["iterations"] < 5 else "end"

workflow.add_conditional_edges(
    "check",
    should_continue,
    {"continue": "process", "end": END}
)
```

## Error Handling

### Node-Level Error Handling
```python
def safe_node(state: AgentState) -> AgentState:
    try:
        # Process state
        state["result"] = process_data(state["input"])
    except Exception as e:
        state["error"] = str(e)
        state["result"] = "Error occurred"
    return state
```

### Graph-Level Error Handling
```python
try:
    result = app.invoke(initial_state)
except Exception as e:
    print(f"Graph execution failed: {e}")
```

## Debugging Tips

### Add Logging to Nodes
```python
def debug_node(state: AgentState) -> AgentState:
    print(f"[DEBUG] Current state: {state}")
    # Process state
    return state
```

### Track Execution Steps
```python
def tracked_node(state: AgentState) -> AgentState:
    state["step"] += 1
    print(f"Step {state['step']}: Executing node")
    return state
```

### Visualize Graph Structure
```python
# Print graph structure
print(workflow.get_graph().draw_ascii())
```

## Best Practices

### 1. Clear State Schema
```python
class AgentState(TypedDict):
    """Complete state for agent execution."""
    input: str  # User input
    output: str  # Final output
    intermediate_results: list  # Processing steps
    metadata: dict  # Additional information
```

### 2. Focused Node Functions
```python
def process_input(state: AgentState) -> AgentState:
    """Single responsibility: validate and clean input."""
    state["input"] = state["input"].strip().lower()
    return state
```

### 3. Explicit Routing Logic
```python
def determine_next_step(state: AgentState) -> Literal["process", "finalize", "retry"]:
    """Clear routing logic with documented conditions."""
    if not state.get("input"):
        return "retry"
    elif state.get("processed", False):
        return "finalize"
    else:
        return "process"
```

### 4. Validate State
```python
def validate_state(state: AgentState) -> AgentState:
    """Ensure state has required fields."""
    required_fields = ["input", "step", "result"]
    for field in required_fields:
        if field not in state:
            raise ValueError(f"Missing required field: {field}")
    return state
```

## Summary of Key Methods

| Component | Method | Purpose |
|-----------|--------|---------|
| StateGraph | `add_node()` | Add processing node |
| StateGraph | `add_edge()` | Add direct connection |
| StateGraph | `add_conditional_edges()` | Add conditional routing |
| StateGraph | `set_entry_point()` | Set starting node |
| StateGraph | `compile()` | Build executable graph |
| App | `invoke()` | Execute graph |
| App | `stream()` | Stream execution steps |

## Common Patterns

### Iteration with Counter
```python
def should_continue(state: AgentState) -> Literal["loop", "exit"]:
    max_iterations = 10
    current = state.get("iteration", 0)
    return "loop" if current < max_iterations else "exit"
```

### Accumulating Results
```python
def accumulate(state: AgentState) -> AgentState:
    results = state.get("results", [])
    results.append(new_result)
    state["results"] = results
    return state
```

### Error Recovery
```python
def retry_on_error(state: AgentState) -> Literal["retry", "fail"]:
    attempts = state.get("attempts", 0)
    has_error = state.get("error") is not None
    
    if has_error and attempts < 3:
        return "retry"
    return "fail"
```

This covers the essential LangGraph concepts and Python patterns used in Lab 05.
