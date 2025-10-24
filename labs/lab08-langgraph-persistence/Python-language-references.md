# Python Language References - Lab 08: LangGraph State Persistence

## Async/Await Programming

### Async Functions
```python
async def my_function():
    """Async function using async/await syntax."""
    result = await some_async_operation()
    return result
```

**Key Concepts:**
- `async def`: Defines an asynchronous function (coroutine)
- `await`: Pauses execution until async operation completes
- Returns a coroutine object, not the result directly

### Running Async Code
```python
import asyncio

# Run single async function
asyncio.run(my_async_function())

# Alternative: Get event loop
loop = asyncio.get_event_loop()
result = loop.run_until_complete(my_async_function())
```

**asyncio.run():**
- Creates new event loop
- Runs the coroutine
- Closes the loop when done
- Use for top-level entry point

### Await Keyword
```python
async def process_data():
    # Wait for async operation
    result = await fetch_from_database()
    
    # Can use await multiple times
    processed = await transform_data(result)
    saved = await save_to_database(processed)
    
    return saved
```

**Rules:**
- Can only use `await` inside `async` functions
- Must await async functions to get their result
- Can await multiple operations sequentially

## State Persistence Module

### create_state_persistence()
```python
from shared.state_persistence import create_state_persistence

persistence = create_state_persistence(
    connection_string=None,  # Optional: reads from env if None
    table_name=None  # Optional: uses default if None
)
```

**Parameters:**
- `connection_string` (str, optional): Database connection string
- `table_name` (str, optional): Table/collection name

**Returns:** BaseStatePersistence instance

**Auto-detection:**
- Detects database type from connection string format
- PostgreSQL: `postgresql://...`
- SQL Server: `mssql+pyodbc://...`
- Cosmos DB: `AccountEndpoint=...;AccountKey=...`

### initialize()
```python
await persistence.initialize()
```

**Purpose:** Initialize database connection and create tables
**Must be called before:** Any save/load operations
**Idempotent:** Safe to call multiple times

### save_state()
```python
success = await persistence.save_state(
    thread_id="conversation_123",
    checkpoint_id="checkpoint_001",
    state={"messages": [], "step": 0},
    metadata={"saved_at": "2024-01-01T12:00:00"}
)
```

**Parameters:**
- `thread_id` (str): Unique conversation/thread identifier
- `checkpoint_id` (str): Unique checkpoint identifier
- `state` (dict): State data to save
- `metadata` (dict, optional): Additional metadata

**Returns:** bool (True if successful)

**Note:** State must be JSON-serializable

### load_state()
```python
# Load latest checkpoint
state_doc = await persistence.load_state(thread_id="conversation_123")

# Load specific checkpoint
state_doc = await persistence.load_state(
    thread_id="conversation_123",
    checkpoint_id="checkpoint_001"
)
```

**Parameters:**
- `thread_id` (str): Thread identifier
- `checkpoint_id` (str, optional): Specific checkpoint to load

**Returns:** StateDocument or None

**StateDocument attributes:**
- `thread_id`: Thread identifier
- `checkpoint_id`: Checkpoint identifier
- `state`: The saved state dict
- `metadata`: Additional metadata
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### list_checkpoints()
```python
checkpoints = await persistence.list_checkpoints(
    thread_id="conversation_123",
    limit=10
)
```

**Parameters:**
- `thread_id` (str): Thread identifier
- `limit` (int): Maximum number to return (default: 10)

**Returns:** List[StateDocument]

**Ordering:** By created_at descending (newest first)

### delete_state()
```python
# Delete specific checkpoint
success = await persistence.delete_state(
    thread_id="conversation_123",
    checkpoint_id="checkpoint_001"
)

# Delete all checkpoints for thread
success = await persistence.delete_state(thread_id="conversation_123")
```

**Parameters:**
- `thread_id` (str): Thread identifier
- `checkpoint_id` (str, optional): Specific checkpoint to delete

**Returns:** bool (True if successful)

### close()
```python
await persistence.close()
```

**Purpose:** Close database connections and cleanup resources
**Should be called:** When done using persistence

## LangGraph with Messages

### add_messages Reducer
```python
from typing import Annotated
from langgraph.graph import add_messages

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

**Purpose:** Automatically appends new messages to list
**Behavior:**
- When state["messages"] = [new_msg], it appends instead of replacing
- Handles message deduplication
- Maintains conversation history

**Without add_messages:**
```python
# Manual append required
state["messages"] = state["messages"] + [new_message]
```

**With add_messages:**
```python
# Automatic append
state["messages"] = [new_message]  # Appends automatically
```

### BaseMessage Types
```python
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# Human message
human_msg = HumanMessage(content="Hello!")

# AI message
ai_msg = AIMessage(content="Hi there!")

# System message
system_msg = SystemMessage(content="You are a helpful assistant.")
```

**Attributes:**
- `content` (str): Message text
- `additional_kwargs` (dict): Extra data
- `type` (str): Message type ("human", "ai", "system")

## Serialization for Persistence

### Message Serialization
```python
# Convert messages to dict for storage
serializable_messages = [
    {
        "type": "human" if isinstance(m, HumanMessage) else "ai",
        "content": m.content
    }
    for m in messages
]
```

### Message Deserialization
```python
# Convert dicts back to message objects
messages = [
    HumanMessage(content=m["content"]) if m["type"] == "human"
    else AIMessage(content=m["content"])
    for m in message_dicts
]
```

**Why needed:**
- Databases store JSON/dict data
- Message objects aren't directly serializable
- Must convert to/from dict format

## Error Handling in Async Code

### Try-Except with Async
```python
async def safe_operation():
    try:
        result = await risky_async_operation()
        return result
    except SpecificError as e:
        print(f"Handled error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

### Context Managers with Async
```python
async with some_async_context() as resource:
    await resource.do_something()
# Automatically cleaned up
```

## Type Hints for Messages

### List of BaseMessage
```python
from langchain.schema import BaseMessage
from typing import List

messages: List[BaseMessage] = []
```

### Annotated Types
```python
from typing import Annotated

# Add metadata to type
messages: Annotated[list[BaseMessage], add_messages]
```

**Purpose:** Attach reducers or validators to types

## Dictionary Operations

### Spread Operator
```python
# Copy dict and update fields
new_state = {
    **old_state,
    "step": old_state["step"] + 1,
    "summary": "Updated"
}
```

**Behavior:**
- `**dict` unpacks dictionary
- Later keys override earlier ones
- Creates shallow copy

### Safe Access
```python
# Get with default
value = state.get("key", default_value)

# Check existence
if "key" in state:
    value = state["key"]
```

## DateTime Handling

### UTC Timestamps
```python
from datetime import datetime

# Get current UTC time
now = datetime.utcnow()

# Convert to ISO format
iso_string = now.isoformat()  # "2024-01-01T12:00:00.123456"

# Parse from ISO format
parsed = datetime.fromisoformat(iso_string)
```

**Methods:**
- `datetime.utcnow()`: Current UTC time
- `isoformat()`: Convert to ISO 8601 string
- `fromisoformat()`: Parse ISO 8601 string

## Path Manipulation

### Add to sys.path
```python
import sys
import os

# Add parent directory to path
parent_dir = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.append(parent_dir)

# Now can import from parent directories
from shared.state_persistence import create_state_persistence
```

**Purpose:** Enable imports from non-standard locations

## Best Practices

### 1. Always Initialize Persistence
```python
persistence = create_state_persistence()
await persistence.initialize()  # Must call before use
```

### 2. Use Try-Finally for Cleanup
```python
persistence = create_state_persistence()
try:
    await persistence.initialize()
    # Use persistence
    await persistence.save_state(...)
finally:
    await persistence.close()  # Ensure cleanup
```

### 3. Serialize Complex Objects
```python
# Don't store objects directly
# state = {"llm": ChatOpenAI()}  # ❌ Not serializable

# Store serializable data
state = {"model_name": "gpt-3.5-turbo"}  # ✓ Serializable
```

### 4. Use Descriptive IDs
```python
thread_id = f"user_{user_id}_conversation_{conv_id}"
checkpoint_id = f"step_{step_number}_{timestamp}"
```

### 5. Handle Missing Checkpoints
```python
state = await persistence.load_state(thread_id)

if state is None:
    # Create new state
    state = initialize_new_state()
else:
    # Resume from saved state
    continue_processing(state)
```

## Common Patterns

### Checkpoint After Each Step
```python
for step in range(10):
    # Process
    state = process_step(state, step)
    
    # Save checkpoint
    await persistence.save_state(
        thread_id=thread_id,
        checkpoint_id=f"step_{step}",
        state=state
    )
```

### Resume from Latest
```python
# Try to load latest
state = await persistence.load_state(thread_id)

if state:
    print(f"Resuming from step {state['step']}")
    start_step = state['step'] + 1
else:
    print("Starting fresh")
    state = initialize_state()
    start_step = 0

# Continue processing
for step in range(start_step, total_steps):
    state = process_step(state, step)
```

### Conversation History
```python
# Load previous conversation
prev_state = await persistence.load_state(thread_id)

if prev_state:
    # Append to history
    messages = prev_state["messages"] + [new_message]
else:
    # Start new conversation
    messages = [new_message]

state = {"messages": messages, ...}
```

## Summary of Key Async Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `async def` | Define async function | Coroutine |
| `await` | Wait for async operation | Result |
| `asyncio.run()` | Execute async function | Result |
| `persistence.initialize()` | Setup database | None |
| `persistence.save_state()` | Save checkpoint | bool |
| `persistence.load_state()` | Load checkpoint | StateDocument |
| `persistence.close()` | Cleanup | None |

This covers the essential concepts for implementing state persistence in LangGraph applications.
