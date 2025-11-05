# Python Language References - LangGraph Stateful Applications

## Overview
This document explains the Python methods, classes, and concepts used in Lab 06 for building stateful LangGraph applications with checkpointing, human-in-the-loop workflows, and parallel processing.

## Key Concepts

### State Management
- **TypedDict**: Define typed state schemas for workflow data
- **Annotated**: Add metadata to type hints for state fields
- **State Persistence**: Maintain workflow state across executions
- **Checkpointing**: Save and restore workflow progress

### LangGraph Components
- **StateGraph**: Core graph structure for stateful workflows
- **MemorySaver**: In-memory checkpoint storage
- **Conditional Routing**: Dynamic path selection based on state
- **Parallel Processing**: Concurrent node execution

## Core Classes and Types

### State Schema Definition
```python
from typing import TypedDict, Annotated, List, Dict, Any
from typing_extensions import Literal

class WorkflowState(TypedDict):
    """State schema for workflow data."""
    messages: Annotated[List[Dict[str, Any]], "List of conversation messages"]
    current_step: str
    document_content: str
    approval_status: str
    reviewer_feedback: str
    revision_count: int
    parallel_results: Dict[str, Any]
    workflow_metadata: Dict[str, Any]
    human_input_required: bool
    last_updated: str
```

**Purpose:** Define the structure of workflow state data
**Key Features:**
- Type safety with TypedDict
- Annotated types for documentation
- Required and optional fields
- Nested data structures

### StateGraph Creation
```python
from langgraph.graph import StateGraph, END, START

def create_stateful_workflow():
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("analyze", analyze_document)
    workflow.add_node("approve", request_human_approval)
    
    # Add edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "analyze")
    
    # Conditional edges
    workflow.add_conditional_edges(
        "analyze",
        should_request_approval,
        {
            "parallel": "quality_check",
            "approval": "request_approval"
        }
    )
    
    workflow.add_edge("finalize", END)
    return workflow
```

**Purpose:** Build directed graph with stateful nodes
**Key Methods:**
- `add_node(name, function)`: Add processing nodes
- `add_edge(from, to)`: Add direct connections
- `add_conditional_edges(node, condition, mapping)`: Add dynamic routing

## Core Methods

### Node Functions
```python
def initialize_workflow(state: WorkflowState) -> WorkflowState:
    """Initialize the workflow state."""
    state["current_step"] = "initialized"
    state["approval_status"] = "pending"
    state["revision_count"] = 0
    state["workflow_metadata"] = {
        "start_time": datetime.now().isoformat(),
        "workflow_id": f"wf_{int(time.time())}"
    }
    state["last_updated"] = datetime.now().isoformat()
    return state
```

**Purpose:** Process and modify workflow state
**Pattern:** Input state → Process → Return modified state
**Key Features:**
- Immutable state updates
- Timestamp tracking
- Metadata management

### Conditional Routing Functions
```python
def approval_decision_router(state: WorkflowState) -> Literal["approved", "revision", "rejected"]:
    """Route based on approval decision."""
    status = state.get("approval_status", "pending")
    
    if status == "approved":
        return "approved"
    elif status == "needs_revision":
        return "revision"
    else:
        return "rejected"
```

**Purpose:** Dynamic path selection based on state
**Returns:** String literal for next node
**Pattern:** Analyze state → Return routing decision

### Checkpointing and Persistence
```python
from langgraph.checkpoint.memory import MemorySaver

def create_workflow_with_checkpointing():
    memory = MemorySaver()
    workflow = create_stateful_workflow()
    app = workflow.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "workflow_1"}}
    
    # Execute with checkpointing
    result = app.invoke(initial_state, config)
    
    # Resume from checkpoint
    current_state = app.get_state(config)
    app.stream(None, config)  # Continue from saved state
    
    return app
```

**Purpose:** Persist workflow state across executions
**Key Methods:**
- `MemorySaver()`: In-memory checkpoint storage
- `compile(checkpointer=memory)`: Enable checkpointing
- `get_state(config)`: Retrieve current state
- `stream(state, config)`: Execute with streaming

## Advanced Patterns

### Parallel Processing
```python
def create_parallel_workflow():
    workflow = StateGraph(WorkflowState)
    
    # Parallel nodes
    workflow.add_node("quality_check", parallel_analysis_quality)
    workflow.add_node("compliance_check", parallel_analysis_compliance)
    workflow.add_node("security_check", parallel_analysis_security)
    workflow.add_node("merge_results", merge_parallel_results)
    
    # Sequential execution for parallel effect
    workflow.add_edge("quality_check", "compliance_check")
    workflow.add_edge("compliance_check", "security_check")
    workflow.add_edge("security_check", "merge_results")
    
    return workflow

def merge_parallel_results(state: WorkflowState) -> WorkflowState:
    """Merge results from parallel analysis."""
    merged_feedback = "Combined Analysis Results:\n\n"
    
    for analysis_type, result in state["parallel_results"].items():
        merged_feedback += f"{analysis_type.upper()}: {result['analysis']}\n"
    
    state["reviewer_feedback"] = merged_feedback
    return state
```

**Purpose:** Process multiple analyses concurrently
**Pattern:** Fork → Process → Merge results

### Human-in-the-Loop Integration
```python
def request_human_approval(state: WorkflowState) -> WorkflowState:
    """Request human approval - creates interruption point."""
    state["current_step"] = "awaiting_approval"
    state["human_input_required"] = True
    
    # In real implementation, this would pause execution
    # until human provides input
    state["messages"].append({
        "role": "system",
        "content": "Human approval requested. Workflow paused.",
        "timestamp": datetime.now().isoformat()
    })
    
    return state

def process_approval_decision(state: WorkflowState) -> WorkflowState:
    """Process the approval decision from human."""
    # Get human input (simulated here)
    approval_decision = get_human_input()  # "approved", "rejected", "needs_revision"
    
    state["approval_status"] = approval_decision
    state["human_input_required"] = False
    
    return state
```

**Purpose:** Integrate human decision points in automated workflows
**Key Features:**
- Pause execution for human input
- Resume after decision
- Track human interaction history

### Document Approval Workflow
```python
class DocumentApprovalState(TypedDict):
    document_id: str
    document_title: str
    document_content: str
    author: str
    current_approver: str
    approval_chain: List[str]
    approvals_received: List[Dict[str, Any]]
    status: Literal["draft", "under_review", "approved", "rejected", "needs_revision"]
    feedback: List[str]
    revision_history: List[Dict[str, Any]]

def approve_document(state: DocumentApprovalState) -> DocumentApprovalState:
    """Approve document at current level."""
    approval = {
        "approver": state["current_approver"],
        "decision": "approved",
        "timestamp": datetime.now().isoformat()
    }
    state["approvals_received"].append(approval)
    
    # Move to next approver
    current_index = state["approval_chain"].index(state["current_approver"])
    if current_index + 1 < len(state["approval_chain"]):
        state["current_approver"] = state["approval_chain"][current_index + 1]
    else:
        state["status"] = "approved"
    
    return state
```

**Purpose:** Multi-level approval process with tracking
**Features:**
- Approval chain management
- Status tracking
- History preservation

## Execution Patterns

### Streaming Execution
```python
def execute_with_streaming():
    app = workflow.compile(checkpointer=memory)
    config = {"configurable": {"thread_id": "demo_1"}}
    
    for chunk in app.stream(initial_state, config):
        node_name = list(chunk.keys())[0]
        node_output = chunk[node_name]
        print(f"Completed: {node_name}")
        
        # Can inspect intermediate results
        if node_name == "analyze":
            print(f"Analysis: {node_output['reviewer_feedback']}")
```

**Purpose:** Process workflow step-by-step with intermediate access
**Benefits:**
- Monitor progress
- Inspect intermediate states
- Handle interruptions

### Error Handling and Recovery
```python
def robust_workflow_execution():
    try:
        result = app.invoke(initial_state, config)
        return result
    except Exception as e:
        print(f"Workflow error: {e}")
        
        # Recover from checkpoint
        current_state = app.get_state(config)
        if current_state:
            print("Recovering from last checkpoint...")
            return app.stream(None, config)
        else:
            print("No checkpoint found, restarting...")
            return app.invoke(initial_state, config)
```

**Purpose:** Handle failures with automatic recovery
**Features:**
- Exception handling
- Checkpoint recovery
- Graceful degradation

## Best Practices

### 1. State Design
```python
# Good: Clear, typed state schema
class WorkflowState(TypedDict):
    current_step: str  # Always track progress
    last_updated: str  # Timestamp updates
    metadata: Dict[str, Any]  # Extensible data

# Bad: Untyped, unclear state
state = {"data": {}, "stuff": [], "things": None}
```

### 2. Node Functions
```python
# Good: Pure functions with clear inputs/outputs
def process_document(state: WorkflowState) -> WorkflowState:
    """Process document with clear side effects."""
    new_state = state.copy()  # Avoid mutations
    new_state["processed"] = True
    new_state["last_updated"] = datetime.now().isoformat()
    return new_state

# Bad: Functions with unclear side effects
def process_doc(state):
    state["x"] = do_something()  # What does this do?
    return state
```

### 3. Error Handling
```python
# Good: Graceful error handling
def analyze_with_fallback(state: WorkflowState) -> WorkflowState:
    try:
        result = llm.invoke(prompt)
        state["analysis"] = result.content
    except Exception as e:
        state["analysis"] = f"Analysis failed: {e}"
        state["error"] = True
    
    return state

# Bad: Unhandled exceptions crash workflow
def analyze_document(state):
    result = llm.invoke(prompt)  # Can fail
    state["analysis"] = result.content
    return state
```

### 4. Checkpointing Strategy
```python
# Good: Strategic checkpoint placement
workflow.add_node("checkpoint_1", save_checkpoint)  # Before expensive operations
workflow.add_node("process_data", process_large_dataset)
workflow.add_node("checkpoint_2", save_checkpoint)  # Before human input
workflow.add_node("get_approval", request_human_approval)

# Bad: No checkpointing or too frequent
# (workflow crashes lose all progress or performance issues)
```

## Summary

### Key Takeaways

1. **State Management**: Use TypedDict for clear state schemas
2. **Graph Construction**: Build workflows with nodes and conditional edges
3. **Checkpointing**: Enable persistence with MemorySaver
4. **Human Integration**: Design interruption points for human input
5. **Parallel Processing**: Coordinate concurrent operations
6. **Error Recovery**: Handle failures gracefully with checkpoints
7. **Type Safety**: Use type hints for better code quality

### Essential Methods
- `StateGraph(StateType)`: Create stateful graph
- `add_node(name, function)`: Add processing nodes
- `add_conditional_edges()`: Dynamic routing
- `compile(checkpointer)`: Enable persistence
- `invoke(state, config)`: Execute workflow
- `stream(state, config)`: Streaming execution
- `get_state(config)`: Retrieve current state

### Advanced Features
- **Conditional Routing**: Dynamic path selection
- **Parallel Execution**: Concurrent node processing
- **State Persistence**: Workflow checkpointing
- **Human-in-the-Loop**: Interactive workflows
- **Error Recovery**: Automatic resumption from failures
