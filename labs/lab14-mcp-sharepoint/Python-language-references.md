# Python Language References - Lab 14: MCP SharePoint

## Overview
This document explains the Python methods, classes, and concepts used in this lab for building a SharePoint-integrated reporting assistant with FastAPI, Pydantic, LangGraph, and MCP. It covers all syntax found in `main.py`, `schemas.py`, `graph_report.py`, and `report_flow_demo.py`.

---

## `from __future__ import annotations`

```python
from __future__ import annotations
```

**`from __future__ import annotations`:** Makes all annotations in the file evaluated lazily (as strings) instead of eagerly. This allows forward references in type hints without quoting them and is required in older Python versions when a class references its own type.

---

## Pydantic Models (`schemas.py`)

### BaseModel Basics
```python
from pydantic import BaseModel, Field

class ExtractionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    input_document_type: str
    extraction_prompt: str
```

**`BaseModel`:** Pydantic base class that provides automatic data validation, serialisation, and `.dict()` / `.model_dump()` helpers. Any class attribute with a type annotation becomes a validated field.
**`Optional[str] = None`:** Marks a field as optional; if omitted by the caller it defaults to `None`.

### `Field` – Default Factories and Metadata
```python
from pydantic import Field

class ExtractionRuleCreate(BaseModel):
    parameters: List[ExtractionParameter] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
```

**`Field(default_factory=list)`:** Required when the default value is a mutable object (list, dict). Using `= []` directly would share the same list between all instances — `default_factory` creates a fresh object per instance.

### `Literal` – Constrained String Fields
```python
from typing import Literal

class SectionLocator(BaseModel):
    type: Literal["semantic_section", "regex", "heading"]

class ExtractionParameter(BaseModel):
    type: Literal["string", "number", "date"]

class ReportRunStatus(BaseModel):
    status: Literal["pending", "running", "failed", "completed"]
```

**`Literal["a", "b", ...]`:** Constrains a field to one of the listed string values. Pydantic raises a `ValidationError` if any other value is provided. Useful for enum-like fields without defining a full `Enum` class.

### Model Inheritance
```python
class ExtractionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    # ...

class ExtractionRuleRead(ExtractionRuleCreate):
    id: str
    created_by: str
    created_date: datetime
    updated_date: datetime
```

**Pydantic inheritance:** `ExtractionRuleRead` inherits all fields from `ExtractionRuleCreate` and adds `id`, `created_by`, and date fields. This pattern separates the "write" (create) shape from the "read" (response) shape.

### `.dict()` – Serialising a Model to a Dictionary
```python
rule = ExtractionRuleRead(
    id=str(uuid.uuid4()),
    created_by=current_user,
    created_date=now,
    updated_date=now,
    **body.dict(),          # unpack ExtractionRuleCreate fields
)
```

**`body.dict()`:** Returns all fields of the Pydantic model as a plain Python dictionary. Using `**body.dict()` unpacks those fields as keyword arguments to the constructor of the child model.

### `str` Subclass as Enum Constants
```python
class ReportRunMode(str):
    TEST = "test"
    FINAL = "final"
```

**`class ReportRunMode(str)`:** A lightweight alternative to `enum.Enum` – class-level string constants that can be compared directly with `==`. The class inherits from `str` so instances are plain strings at runtime.

---

## `TypedDict` – Typed State Dictionaries (`graph_report.py`, `report_flow_demo.py`)

### Defining a `TypedDict`
```python
from typing import TypedDict, Optional, List, Dict, Any

class ReportState(TypedDict, total=False):
    run_id: str
    template_id: str
    requested_by: str
    parameters: Dict[str, Any]
    uploaded_file_ids: List[str]
    placeholder_results: Dict[str, Any]
    final_report_path: str
    error: str
```

**`TypedDict`:** Declares a dictionary type with known keys and value types. Unlike `BaseModel`, it is a plain `dict` at runtime — no validation is performed.
**`total=False`:** Makes all keys optional by default (none are required). Without it, all keys are required when constructing the dict.

### Accessing `TypedDict` Keys Safely
```python
month = state.get("month") or ""
dept = state.get("department") or ""
```

**`state.get("key")`:** Returns the value or `None` if the key is absent (safe for `total=False` dicts).
**`value or ""`:** Provides a fallback when the value is `None` or an empty string.

---

## `dataclass` – Lightweight Data Containers
```python
from dataclasses import dataclass

@dataclass
class MyConfig:
    host: str = "localhost"
    port: int = 8000
```

**`@dataclass`:** Auto-generates `__init__`, `__repr__`, and `__eq__` from the annotated class attributes, reducing boilerplate compared to a plain class. Used in `report_flow_demo.py` as an import for potential future configuration classes.

---

## FastAPI (`main.py`)

### Creating the Application
```python
from fastapi import FastAPI

app = FastAPI(title="Reporting Assistant API")
```

**`FastAPI(title=...)`:** Creates the ASGI application instance. The `title` appears in the auto-generated `/docs` (Swagger UI) and `/openapi.json`.

### Route Decorators and `response_model`
```python
@app.post("/api/admin/report/extraction-rules", response_model=ExtractionRuleRead)
async def create_extraction_rule(body: ExtractionRuleCreate, ...):
    ...

@app.get("/api/admin/report/search-rules", response_model=List[SearchRuleRead])
async def list_search_rules(...):
    ...
```

**`@app.post(path, response_model=Model)`:** Registers an HTTP POST route. FastAPI validates the response against `response_model` before serialising it to JSON.
**`@app.get(path)`:** Registers an HTTP GET route.
**`async def`:** FastAPI endpoints are coroutines, allowing non-blocking I/O.

### Dependency Injection with `Depends`
```python
from fastapi import Depends

def get_current_user():
    return "user1@corp.com"

@app.post("/api/reports/run")
async def run_report(
    body: ReportRunCreate,
    current_user: str = Depends(get_current_user),
):
    ...
```

**`Depends(callable)`:** FastAPI resolves the dependency before calling the endpoint function. When `get_current_user` is replaced with a real auth function, no other code needs to change.

### File Uploads with `UploadFile`
```python
from fastapi import UploadFile, File

@app.post("/api/reports/uploads", response_model=UploadedFileRead)
async def upload_runtime_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    content = await file.read()
    size_bytes = len(content)
```

**`UploadFile`:** FastAPI's async wrapper around an uploaded file. Provides `.filename`, `.content_type`, and `await .read()`.
**`File(...)`:** The `...` (Ellipsis) marks the parameter as required (no default value).
**`await file.read()`:** Reads the file bytes asynchronously.

### `HTTPException` – Returning HTTP Errors
```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Not implemented yet")
raise HTTPException(status_code=500, detail=str(ex))
```

**`HTTPException(status_code, detail)`:** Tells FastAPI to return an HTTP error response with the given status code and JSON body `{"detail": "..."}`.

### Relative Imports
```python
from .schemas import ExtractionRuleCreate, ExtractionRuleRead
from .graph_report import run_report_flow
```

**`.schemas`:** The leading dot means "import from the same package (directory)". Used when `main.py` is part of an `app/` package.

---

## `uuid` – Generating Unique Identifiers
```python
import uuid

rule_id = str(uuid.uuid4())
upload_id = f"upl_{uuid.uuid4()}"
run_id = f"run_{uuid.uuid4()}"
```

**`uuid.uuid4()`:** Generates a random UUID (Universally Unique Identifier). The result is a `UUID` object; wrapping it in `str()` converts it to its canonical hyphen-separated string form (e.g., `"3f2a1b4c-..."`).

---

## `datetime` – Working with Timestamps
```python
from datetime import datetime

now = datetime.utcnow()
```

**`datetime.utcnow()`:** Returns the current UTC date and time as a naive `datetime` object (no timezone info). Use this when storing timestamps that will be interpreted as UTC.

---

## `try / except` – Exception Handling
```python
try:
    result_dict = run_report_flow(run_id=run_id, requested_by=current_user, req=body)
except Exception as ex:
    error_resp = ReportRunStatus(
        id=run_id,
        status="failed",
        error=str(ex),
        ...
    )
    raise HTTPException(status_code=500, detail=str(ex))
```

**`except Exception as ex`:** Catches any exception derived from `Exception` (i.e., all standard errors) and binds it to `ex`.
**`str(ex)`:** Converts the exception to a human-readable message.
**Re-raising with `HTTPException`:** After recording the error, the handler raises a FastAPI HTTP error so the client receives a proper 500 response.

---

## LangGraph Core (`graph_report.py`, `report_flow_demo.py`)

### `StateGraph` – Defining the Graph
```python
from langgraph.graph import StateGraph, END

graph = StateGraph(ReportState)
```

**`StateGraph(StateType)`:** Creates a new directed graph whose nodes receive and return state objects of `StateType` (typically a `TypedDict`).
**`END`:** A special LangGraph sentinel that marks the terminal node of the graph.

### Adding Nodes and Edges
```python
graph.add_node("load_template", load_template_node)
graph.add_node("resolve_placeholders", resolve_placeholders_node)

graph.set_entry_point("load_template")
graph.add_edge("load_template", "resolve_placeholders")
graph.add_edge("resolve_placeholders", "generate_docx")
graph.add_edge("generate_docx", END)
```

**`add_node(name, fn)`:** Registers a callable as a named graph node. `fn` must accept the state dict and return an updated state dict.
**`set_entry_point(name)`:** Designates the first node to execute when the graph is invoked.
**`add_edge(from, to)`:** Creates an unconditional transition between two nodes.

### Conditional Edges – Routing
```python
def route_after_templates(state: ReportState) -> str:
    if state.get("status") in ["failed_no_template"]:
        return "end_fail"
    if state.get("selected_template"):
        return "stage_files"
    return "end_fail"

g.add_conditional_edges(
    "suggest_templates",
    route_after_templates,
    {"stage_files": "stage_files", "end_fail": "end_fail"},
)
```

**`add_conditional_edges(from_node, router_fn, path_map)`:** After `from_node` completes, `router_fn(state)` is called. The returned string is looked up in `path_map` to determine the next node.
**`path_map`:** A dict mapping router return values to node names. Provides an explicit whitelist of allowed transitions.

### Compiling and Invoking the Graph
```python
compiled_report_graph = graph.compile()

final_state = compiled_report_graph.invoke(initial_state)
```

**`graph.compile()`:** Validates the graph structure and returns a `CompiledGraph` that can be invoked or streamed.
**`.invoke(state)`:** Runs the graph synchronously from the entry point to `END` and returns the final state dict.

### Streaming the Graph
```python
stream = graph.stream(state, stream_mode="values")

for event in stream:
    if "__interrupt__" in event:
        ...
```

**`.stream(state, stream_mode="values")`:** Runs the graph and yields the state dict after each node executes. With `stream_mode="values"` the full state snapshot is emitted, not just the diff.
**`"__interrupt__"`:** A special key injected by LangGraph into the streamed event when a node calls `interrupt(...)`.

---

## LangGraph Human-in-the-Loop (`report_flow_demo.py`)

### `interrupt` – Pausing for User Input
```python
from langgraph.types import interrupt

def node_collect_request(state: ReportState) -> ReportState:
    if not state.get("month") or not state.get("department"):
        payload = {
            "type": "request_missing_inputs",
            "message": "Please provide missing inputs.",
            "missing": [k for k in ["month", "department"] if not state.get(k)],
        }
        reply = interrupt(payload)
        state["month"] = reply.get("month") or state.get("month")
        state["department"] = reply.get("department") or state.get("department")
    return state
```

**`interrupt(payload)`:** Pauses graph execution and surfaces `payload` to the caller via the `"__interrupt__"` key in the stream. Execution resumes when `Command(resume=...)` is passed to `.stream()`.
**`reply`:** The value provided by the caller in `Command(resume=value)`; typically a dict with the user's answers.

### `Command` – Resuming After an Interrupt
```python
from langgraph.types import Command

stream = graph.stream(
    Command(resume={"month": "2025-07", "department": "DeptA"}),
    stream_mode="values",
)
```

**`Command(resume=value)`:** Wraps the user's response for delivery back to the waiting `interrupt()` call. Pass it to `.stream()` instead of the initial state dict to resume a paused graph.

---

## `next()` with a Generator – Finding the First Match
```python
state["selected_template"] = next(
    (t for t in cands if t["id"] == sel_id), None
)
```

**`next(iterable, default)`:** Returns the first item from the iterable, or `default` if the iterable is empty.
**Generator expression `(t for t in cands if ...)`:** A lazy sequence that yields only matching items. Combining with `next()` is an idiomatic way to find the first matching element in a list without iterating the whole list.

---

## List Comprehensions
```python
# Build a list of missing field names
missing = [k for k in ["month", "department"] if not state.get(k)]

# Get all keys of extracted fields
keys = list(state["extracted_fields"].keys())
```

**`[expr for item in iterable if condition]`:** Creates a new list by evaluating `expr` for each `item` that satisfies `condition`.

---

## Dict Comprehensions
```python
placeholder_results = {
    name: PlaceholderResult(
        value=data["value"],
        source_doc=data.get("source_doc", {}),
        debug=data.get("debug", {})
    ).dict()
    for name, data in final_state.get("placeholder_results", {}).items()
}
```

**`{key: value for key, value in iterable}`:** Creates a new dict from an iterable of `(key, value)` pairs.
**`.items()`:** Returns `(key, value)` pairs for each entry in a dictionary.

---

## f-strings – String Interpolation
```python
state["final_report_path"] = f"/tmp/{state['run_id']}.docx"
state["draft_path"] = f"/workspace/{state.get('run_id','run')}/draft_report.docx"
print(f"[collect_request] user_request={state.get('user_request')}")
```

**`f"...{expression}..."`:** Embeds the result of `expression` directly into the string at runtime. Expressions inside `{}` can be variable names, method calls, or any valid Python expression.
**Note on quotes:** Inside an f-string, use the opposite quote style for string literals within `{}` (e.g., `f"{state['key']}"` uses single quotes inside).

---

## String Methods
```python
name = f"spending_month_{month.replace('-', '_')}.xlsx"
action = input("Action: ").strip().lower()
```

**`.replace(old, new)`:** Returns a new string with all occurrences of `old` replaced by `new`.
**`.strip()`:** Removes leading and trailing whitespace.
**`.lower()`:** Returns the string converted to lowercase.

---

## `input()` – Reading from stdin
```python
month = input("Enter month (YYYY-MM): ").strip()
dept  = input("Enter department: ").strip()
action = input("Action (approve/revise): ").strip().lower()
```

**`input(prompt)`:** Prints `prompt`, waits for the user to type a line, and returns it as a string (without the newline). Always call `.strip()` to remove accidental whitespace.

---

## Nested Functions
```python
def build_graph():
    g = StateGraph(ReportState)

    def end_fail(state: ReportState) -> ReportState:
        print("\n[end_fail] status=", state.get("status"), " error=", state.get("error"))
        return state

    g.add_node("end_fail", end_fail)
    ...
```

**Nested function:** A function defined inside another function. It has access to the enclosing scope's variables (closure). Here `end_fail` is defined inside `build_graph()` so it can be registered as a node without polluting the module namespace.

---

## `if __name__ == "__main__"`
```python
if __name__ == "__main__":
    run_cli()
```

**`__name__`:** A special module attribute set to `"__main__"` when the file is run directly (e.g., `python report_flow_demo.py`), and to the module name when it is imported. The guard ensures `run_cli()` is only called when the file is the entry point, not when it is imported as a library.

---

## `continue` in a Loop
```python
for event in stream:
    if "__interrupt__" in event:
        ...
        stream = graph.stream(Command(resume={"month": month, ...}), stream_mode="values")
        continue   # skip the rest of this iteration and go back to `for`

    # normal progress events
```

**`continue`:** Immediately jumps to the next iteration of the enclosing loop, skipping any remaining code in the current iteration.

---

## Unpacking Operators

### `**kwargs` – Dictionary Unpacking
```python
rule = ExtractionRuleRead(
    id=str(uuid.uuid4()),
    created_by=current_user,
    created_date=now,
    updated_date=now,
    **body.dict(),   # spread all fields from ExtractionRuleCreate
)
```

**`**mapping`:** Unpacks a dictionary into keyword arguments. Each key-value pair becomes a separate `key=value` argument in the function call.

---

## Type Hints Summary

| Annotation | Meaning |
|---|---|
| `str`, `int`, `bool`, `float` | Built-in scalar types |
| `Optional[T]` | `T` or `None` |
| `List[T]` | A list whose elements are all of type `T` |
| `Dict[K, V]` | A dict with keys of type `K` and values of type `V` |
| `Any` | Any type; opts out of type checking for that field |
| `Literal["a", "b"]` | Exactly one of the listed string values |
| `TypedDict` | A dict with a fixed schema of named keys |

---

## Best Practices

1. **Use `TypedDict` for LangGraph state** – the graph engine passes state as a dict; `TypedDict` provides IDE type hints without runtime overhead.
2. **Use `Pydantic BaseModel` for API boundaries** – input validation, serialisation, and OpenAPI schema generation are all automatic.
3. **Separate create/read schemas** – keep "input" models (e.g., `ExtractionRuleCreate`) separate from "output" models (`ExtractionRuleRead`) to control which fields clients can set.
4. **Use `Field(default_factory=list)` for mutable defaults** – never use `= []` or `= {}` directly in model field definitions.
5. **Return early from router functions** – keeps conditional routing logic flat and readable.
6. **Keep interrupt payloads self-describing** – include a `"type"` key so the CLI/client knows how to respond without inspecting multiple fields.
7. **Use `stream_mode="values"` for human-in-the-loop flows** – it provides the full state snapshot at each step, making interrupt detection straightforward.

---

## Summary

| Concept | Key API / Syntax |
|---|---|
| Pydantic model | `class M(BaseModel): field: Type` |
| Optional field | `field: Optional[str] = None` |
| Mutable default | `Field(default_factory=list)` |
| Constrained string | `Literal["a", "b", "c"]` |
| Typed state dict | `class S(TypedDict, total=False): ...` |
| FastAPI app | `FastAPI(title="...")` |
| HTTP endpoint | `@app.post(path, response_model=M)` |
| Dependency injection | `Depends(callable)` |
| File upload | `UploadFile = File(...)` + `await file.read()` |
| HTTP error | `raise HTTPException(status_code, detail)` |
| Unique ID | `str(uuid.uuid4())` |
| UTC timestamp | `datetime.utcnow()` |
| LangGraph graph | `StateGraph(StateType)` |
| Compile graph | `graph.compile()` |
| Invoke graph | `compiled.invoke(initial_state)` |
| Stream graph | `graph.stream(state, stream_mode="values")` |
| Conditional routing | `add_conditional_edges(node, router_fn, path_map)` |
| Pause for input | `interrupt(payload)` |
| Resume from pause | `Command(resume=value)` |
| First match | `next((x for x in xs if cond), default)` |
| Dict comprehension | `{k: v for k, v in d.items()}` |
| String interpolation | `f"text {variable}"` |
| Entry-point guard | `if __name__ == "__main__":` |
