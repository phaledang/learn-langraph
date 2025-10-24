# LangGraph Fundamentals

## Introduction to LangGraph

### What is LangGraph?
- **Framework for building stateful, multi-actor applications with LLMs**
- Built on top of LangChain
- Uses graph-based workflow orchestration
- Enables complex, cyclical flows

### Why LangGraph?

#### Limitations of Chains
- Linear execution
- Limited conditional logic
- No cycles or loops
- Difficult to maintain state

#### LangGraph Solutions
- **Cyclic Graphs**: Implement loops and iterations
- **State Management**: Persistent state across steps
- **Conditional Edges**: Dynamic routing
- **Human-in-the-Loop**: Pause for human input

### Core Concepts

#### 1. State Graph
```python
from langgraph.graph import StateGraph

graph = StateGraph(State)
```

#### 2. Nodes
- Individual processing units
- Can be LLMs, tools, or functions
- Receive and modify state

```python
def node_function(state: State) -> State:
    # Process and update state
    return updated_state

graph.add_node("node_name", node_function)
```

#### 3. Edges
- Connect nodes
- Define workflow flow
- Can be conditional

```python
# Regular edge
graph.add_edge("node1", "node2")

# Conditional edge
graph.add_conditional_edges(
    "node1",
    route_function,
    {
        "path_a": "node2",
        "path_b": "node3"
    }
)
```

#### 4. State
- Typed dictionary
- Shared across nodes
- Represents workflow data

```python
from typing import TypedDict

class State(TypedDict):
    messages: list
    user_input: str
    result: str
```

### Building Your First Graph

#### Step 1: Define State
```python
class AgentState(TypedDict):
    messages: list
    current_step: int
```

#### Step 2: Create Nodes
```python
def process_input(state):
    # Process user input
    return state

def generate_response(state):
    # Generate LLM response
    return state
```

#### Step 3: Build Graph
```python
workflow = StateGraph(AgentState)
workflow.add_node("process", process_input)
workflow.add_node("generate", generate_response)
workflow.add_edge("process", "generate")
workflow.set_entry_point("process")
workflow.set_finish_point("generate")
```

#### Step 4: Compile and Run
```python
app = workflow.compile()
result = app.invoke({"messages": []})
```

### Graph Patterns

#### 1. Sequential Flow
- Linear execution
- Each node processes in order

#### 2. Conditional Flow
- Branch based on state
- Different paths for different conditions

#### 3. Cyclic Flow
- Loop until condition met
- Iterative refinement

#### 4. Parallel Flow
- Execute nodes concurrently
- Aggregate results

### State Management

#### Reducers
- Control how state updates merge
- Default: replace
- Custom: append, merge, etc.

```python
from typing import Annotated
from langgraph.graph import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

### Checkpointing

#### Save Graph State
```python
from langgraph.checkpoint import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

#### Resume from Checkpoint
```python
config = {"configurable": {"thread_id": "1"}}
result = app.invoke(input, config)
```

### Human-in-the-Loop

#### Interrupt for Input
```python
from langgraph.prebuilt import interrupt

def review_node(state):
    # Show output to human
    interrupt("Please review the output")
    return state
```

### Use Cases

1. **Multi-Agent Systems**: Coordinate multiple agents
2. **Conversational AI**: Complex dialog management
3. **Workflow Automation**: Business process automation
4. **Research Assistants**: Iterative information gathering
5. **Code Generation**: Multi-step code creation

### Advantages

- **Flexibility**: Complex control flows
- **Maintainability**: Clear graph structure
- **Debuggability**: Visualize execution
- **State Persistence**: Resume workflows
- **Scalability**: Handle complex scenarios

### Best Practices

1. Keep nodes focused and simple
2. Use typed state for clarity
3. Implement proper error handling
4. Visualize graphs during development
5. Test edge cases thoroughly

## Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [Example Notebooks](https://github.com/langchain-ai/langgraph/tree/main/examples)
