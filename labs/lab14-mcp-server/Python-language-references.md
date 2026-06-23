# Python Language References - Lab 14: MCP Server

## Overview
This document explains the Python methods, classes, and concepts used in this lab for building MCP servers (using `mcp` and `FastAPI`) and LangGraph-powered report generation workflows.

## MCP Server with `mcp.server.fastapi`

### Basic Server Setup
```python
from mcp.server.fastapi import MCPFastAPI
from mcp.types import Tool, TextContent

app = MCPFastAPI(
    name="local-mcp-server",
    version="0.1.0",
)
```

**`MCPFastAPI`:** Creates an ASGI application that implements the MCP protocol over HTTP.
**`name`:** Display name shown in MCP clients.
**`version`:** Semantic version string for the server.

### Defining a Tool
```python
@app.tool()
def ping(message: str) -> str:
    """
    Simple health-check tool.
    """
    return f"PONG: {message}"
```

**`@app.tool()`:** Registers the decorated function as an MCP tool.
**Docstring:** Becomes the tool's description in the MCP tool list.
**Type annotations:** Used to generate the JSON schema for input validation.
**Return value:** Automatically serialised to a `TextContent` response.

### Running the Server with Uvicorn
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Or from Python:
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

**`uvicorn`:** High-performance ASGI server for Python web applications.
**`reload=True`:** Automatically restarts the server when source files change (development only).

## FastAPI – REST API Layer

### Application Instance
```python
from fastapi import FastAPI

app = FastAPI(title="Reporting Assistant API")
```

**`FastAPI(title)`:** Creates the application; `title` appears in the auto-generated `/docs` Swagger UI.

### Route Decorators
```python
@app.post("/api/admin/report/extraction-rules", response_model=ExtractionRuleRead)
async def create_extraction_rule(body: ExtractionRuleCreate):
    ...

@app.get("/api/admin/report/extraction-rules", response_model=List[ExtractionRuleRead])
async def list_extraction_rules():
    ...
```

**`@app.post(path)`:** Handles HTTP POST requests to `path`.
**`@app.get(path)`:** Handles HTTP GET requests to `path`.
**`response_model`:** FastAPI validates and serialises the return value using this Pydantic model.

### Dependency Injection with `Depends`
```python
from fastapi import Depends

def get_current_user() -> str:
    # TODO: wire real authentication
    return "user1@corp.com"

@app.post("/api/reports/run")
async def run_report(
    body: ReportRunCreate,
    current_user: str = Depends(get_current_user),
):
    ...
```

**`Depends(callable)`:** FastAPI calls `callable` and injects its return value as the parameter.
**Use case:** Authentication, database sessions, configuration – anything that should be shared across routes.

### File Upload
```python
from fastapi import UploadFile, File

@app.post("/api/reports/uploads")
async def upload_file(file: UploadFile = File(...)):
    content   = await file.read()
    size      = len(content)
    filename  = file.filename
    mime_type = file.content_type
    return {"filename": filename, "size": size}
```

**`UploadFile`:** FastAPI type for multipart file uploads.
**`File(...)`:** Marks the parameter as required (`...` = no default).
**`await file.read()`:** Reads the entire file content as bytes asynchronously.

## Pydantic – Data Validation and Serialisation

### BaseModel
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

class ExtractionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    input_document_type: str
    extraction_prompt: str
    output_type: Literal["string", "number", "json"]
```

**`BaseModel`:** Base class for all Pydantic models; provides automatic validation, parsing, and serialisation.
**`Optional[str] = None`:** Field is optional and defaults to `None`.
**`Literal["a", "b"]`:** Restricts the value to one of the listed string literals.

### Field with Default Factory
```python
from pydantic import Field

class ExtractionRuleCreate(BaseModel):
    parameters: List[ExtractionParameter] = Field(default_factory=list)
```

**`Field(default_factory=list)`:** Required for mutable defaults; creates a new empty list for each model instance.

### Inheriting Models
```python
class ExtractionRuleRead(ExtractionRuleCreate):
    id: str
    created_by: str
    created_date: datetime
    updated_date: datetime
```

**Inheritance:** `ExtractionRuleRead` has all fields from `ExtractionRuleCreate` plus the extra fields declared here.
**Use case:** `Create` models represent incoming requests; `Read` models represent database records with server-assigned fields.

### `.dict()` Method
```python
rule = ExtractionRuleRead(
    id=str(uuid.uuid4()),
    created_by=current_user,
    created_date=now,
    updated_date=now,
    **body.dict(),
)
```

**`body.dict()`:** Converts a Pydantic model to a plain Python dictionary.
**`**body.dict()`:** Unpacks the dictionary as keyword arguments.

## TypedDict – Typed Dictionaries for State

### Defining State
```python
from typing import TypedDict, Dict, Any, List

class ReportState(TypedDict, total=False):
    run_id: str
    template_id: str
    requested_by: str
    parameters: Dict[str, Any]
    uploaded_file_ids: List[str]
    template_config: Dict[str, Any]
    placeholder_results: Dict[str, Any]
    final_report_path: str
    error: str
```

**`TypedDict`:** Creates a dictionary type with known string keys and specified value types.
**`total=False`:** All keys are optional (equivalent to `Optional` for each field).
**Use case:** LangGraph state – the graph passes this dict between nodes.

## LangGraph – Stateful Workflow Graphs

### Building a Graph
```python
from langgraph.graph import StateGraph, END

def build_report_graph():
    graph = StateGraph(ReportState)

    graph.add_node("load_template",       load_template_node)
    graph.add_node("resolve_placeholders", resolve_placeholders_node)
    graph.add_node("generate_docx",       generate_docx_node)

    graph.set_entry_point("load_template")
    graph.add_edge("load_template",        "resolve_placeholders")
    graph.add_edge("resolve_placeholders", "generate_docx")
    graph.add_edge("generate_docx",        END)

    return graph.compile()
```

**`StateGraph(StateType)`:** Creates a graph whose nodes operate on `StateType`.
**`add_node(name, fn)`:** Registers `fn` as a node; `fn` receives and returns the state dict.
**`set_entry_point(name)`:** Designates the first node to execute.
**`add_edge(from, to)`:** Adds an unconditional transition between nodes.
**`END`:** Sentinel value marking a terminal node.
**`graph.compile()`:** Validates the graph and returns a runnable `CompiledGraph`.

### Node Functions
```python
def load_template_node(state: ReportState) -> ReportState:
    template_id = state["template_id"]
    template_doc = get_template_by_id(template_id)
    state["template_config"] = template_doc
    return state
```

**Signature:** Each node takes the current state and returns the (updated) state.
**Mutation pattern:** Modify the state dict in-place or create a new dict; both are valid.

### Invoking the Graph
```python
compiled_graph = build_report_graph()

initial_state: ReportState = {
    "run_id":            run_id,
    "template_id":       req.template_id,
    "requested_by":      requested_by,
    "parameters":        req.parameters,
    "uploaded_file_ids": req.uploaded_file_ids,
}

result = compiled_graph.invoke(initial_state)
```

**`graph.invoke(state)`:** Runs the graph synchronously from the entry point to `END` and returns the final state.

## uuid – Unique Identifiers

### Generating UUIDs
```python
import uuid

run_id    = f"run_{uuid.uuid4()}"
upload_id = f"upl_{uuid.uuid4()}"
rule_id   = str(uuid.uuid4())
```

**`uuid.uuid4()`:** Generates a random UUID (version 4).
**`str(uuid.uuid4())`:** Converts to a string like `"550e8400-e29b-41d4-a716-446655440000"`.
**Use case:** Generating unique IDs for database records, run IDs, upload IDs.

## datetime – Timestamps

### Current UTC Time
```python
from datetime import datetime

now = datetime.utcnow()
```

**`datetime.utcnow()`:** Returns the current UTC date and time as a naive `datetime` object.
**Use case:** Storing `created_date` and `updated_date` in database records.

## typing – Type Hints

### Common Annotations
```python
from typing import List, Optional, Dict, Any, Literal

def get_items() -> List[str]:             ...
def find(id: str) -> Optional[str]:      ...
def config() -> Dict[str, Any]:          ...
def mode() -> Literal["read", "write"]:  ...
```

**`List[T]`:** A list whose elements are of type `T`.
**`Optional[T]`:** Equivalent to `Union[T, None]`; the value may be absent.
**`Dict[K, V]`:** A dictionary with keys of type `K` and values of type `V`.
**`Any`:** Disables type checking for this value; use sparingly.
**`Literal["a", "b"]`:** Restricts the value to exactly one of the listed literals.

## async / await

### Async Route Handlers
```python
@app.post("/api/reports/uploads")
async def upload_runtime_file(file: UploadFile = File(...)):
    content = await file.read()
    ...
```

**`async def`:** Declares a coroutine function.
**`await`:** Suspends the coroutine until the awaited operation completes, freeing the event loop to handle other requests.

### Async Tool Calls
```python
@app.post("/api/reports/run")
async def run_report(body: ReportRunCreate):
    try:
        result = run_report_flow(run_id=run_id, req=body, ...)
        return ReportRunStatus(**result)
    except Exception as ex:
        return ReportRunStatus(status="failed", error=str(ex), ...)
```

**Note:** `run_report_flow` in this lab is synchronous; for a fully async pipeline wrap it with `asyncio.to_thread()`.

## Error Handling

### try / except in Route Handlers
```python
try:
    result_dict = run_report_flow(run_id=run_id, requested_by=current_user, req=body)
except Exception as ex:
    now = datetime.utcnow()
    return ReportRunStatus(
        id=run_id,
        status="failed",
        error=str(ex),
        completed_date=now,
        ...
    )
```

**Pattern:** Catch all exceptions at the route handler level; return a structured error response rather than letting FastAPI return a 500.
**`str(ex)`:** Converts any exception to a human-readable string.

## f-strings and String Formatting

### Embedding Expressions
```python
print(f"PONG: {message}")
run_id = f"run_{uuid.uuid4()}"
```

**`f"...{expression}..."`:** Evaluates `expression` at runtime and inserts its string representation.

### Multi-line f-strings
```python
error_message = (
    f"Report generation failed for run '{run_id}'.\n"
    f"Template: {body.template_id}\n"
    f"Error: {str(ex)}"
)
```

## Best Practices

1. **Separate `Create` and `Read` Pydantic models** – request bodies use `Create` models; response bodies use `Read` models with server-assigned fields.
2. **Use `Depends()` for authentication** – centralises auth logic and makes it easy to swap implementations.
3. **Return structured error responses** – catch exceptions in route handlers and return a typed error model rather than a raw 500.
4. **Use `TypedDict` for LangGraph state** – provides IDE autocompletion and type checking for state keys.
5. **Compile the graph once** – call `graph.compile()` at module level so it is reused across requests.
6. **Generate UUIDs for all IDs** – avoids collisions and removes the need for a database auto-increment sequence.
7. **Store `datetime.utcnow()`** – always use UTC for `created_date`/`updated_date` to avoid timezone issues.

## Summary

| Concept | Key API / Syntax |
|---------|-----------------|
| MCP server (HTTP) | `MCPFastAPI(name, version)` |
| Register MCP tool | `@app.tool()` decorator |
| REST API | `FastAPI(title)` + `@app.post/get(path)` |
| Dependency injection | `Depends(callable)` |
| File upload | `UploadFile` + `await file.read()` |
| Request/response models | `class Model(BaseModel)` |
| Optional field | `field: Optional[str] = None` |
| Restricted values | `field: Literal["a", "b"]` |
| Mutable default | `Field(default_factory=list)` |
| Graph state | `class State(TypedDict, total=False)` |
| Build graph | `StateGraph(State)` + `add_node/add_edge` |
| Run graph | `graph.compile().invoke(initial_state)` |
| Unique IDs | `str(uuid.uuid4())` |
| UTC timestamp | `datetime.utcnow()` |
