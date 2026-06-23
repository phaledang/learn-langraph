# Python Language References - Lab 12: Advanced MCP Patterns

## Overview
This document explains the Python methods, classes, and concepts used in this lab for building production-ready MCP servers with authentication, caching, rate limiting, error handling, and deployment.

## Authentication

### API Key Validation
```python
import os
from functools import wraps

VALID_API_KEYS = set(os.getenv("MCP_API_KEYS", "").split(","))

def require_api_key(func):
    """Decorator that validates an API key before calling the tool."""
    @wraps(func)
    def wrapper(*args, api_key: str = "", **kwargs):
        if api_key not in VALID_API_KEYS:
            raise PermissionError("Invalid or missing API key")
        return func(*args, **kwargs)
    return wrapper
```

**`functools.wraps(func)`:** Copies `__name__`, `__doc__`, and other metadata from `func` to the wrapper so the decorated function still looks like the original.
**`*args, **kwargs`:** Accept any positional and keyword arguments, forwarding them unchanged.
**`PermissionError`:** Built-in exception for authorization failures.

### Using the Decorator
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("secure-mcp-server")

@mcp.tool()
@require_api_key
def get_sensitive_data(resource_id: str, api_key: str = "") -> dict:
    """
    Return sensitive data for authenticated callers only.

    Args:
        resource_id: Identifier of the resource to fetch.
        api_key: Caller's API key for authentication.
    """
    return fetch_resource(resource_id)
```

**Order of decorators:** `@mcp.tool()` must be outermost so MCP registers the wrapper, not the bare function.

## Caching

### In-Memory Cache with `functools.lru_cache`
```python
from functools import lru_cache

@lru_cache(maxsize=256)
def expensive_lookup(key: str) -> str:
    """Cached lookup – result is reused for repeated identical inputs."""
    return perform_slow_database_query(key)
```

**`@lru_cache(maxsize=N)`:** Stores up to N most-recently-used results.
**When the cache is full:** The least-recently-used entry is evicted.
**Limitation:** Only works with hashable arguments; not suitable for dict/list inputs.

### Time-Based Cache with `cachetools`
```python
from cachetools import TTLCache
import threading

_cache = TTLCache(maxsize=512, ttl=300)  # entries expire after 5 minutes
_cache_lock = threading.Lock()

def get_with_ttl_cache(key: str) -> str:
    with _cache_lock:
        if key in _cache:
            return _cache[key]
    value = perform_slow_lookup(key)
    with _cache_lock:
        _cache[key] = value
    return value
```

**`TTLCache(maxsize, ttl)`:** Cache that automatically expires entries after `ttl` seconds.
**`threading.Lock()`:** Prevents race conditions when multiple threads access the cache simultaneously.
**`with lock`:** Acquires the lock for the duration of the block, releasing it automatically.

## Rate Limiting

### Token Bucket Rate Limiter
```python
import time
import threading

class RateLimiter:
    """Simple token-bucket rate limiter."""

    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._calls: list[float] = []
        self._lock = threading.Lock()

    def is_allowed(self) -> bool:
        now = time.monotonic()
        with self._lock:
            # Remove timestamps outside the current window
            self._calls = [t for t in self._calls if now - t < self.period]
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
        return False

# Usage
limiter = RateLimiter(max_calls=10, period=60.0)  # 10 calls per minute

@mcp.tool()
def rate_limited_tool(query: str) -> str:
    """Tool that enforces a rate limit."""
    if not limiter.is_allowed():
        raise RuntimeError("Rate limit exceeded – please retry after 60 seconds")
    return do_work(query)
```

**`time.monotonic()`:** Returns a float representing elapsed time; guaranteed never to go backwards (unlike `time.time()`).
**List comprehension for cleanup:** `[t for t in self._calls if now - t < self.period]` rebuilds the list keeping only recent timestamps.

## Structured Error Handling

### Custom Exception Hierarchy
```python
class MCPError(Exception):
    """Base class for MCP server errors."""

class AuthenticationError(MCPError):
    """Raised when authentication fails."""

class ResourceNotFoundError(MCPError):
    """Raised when a requested resource does not exist."""

class RateLimitError(MCPError):
    """Raised when the caller exceeds the allowed request rate."""
```

**Why a hierarchy?** Callers can catch `MCPError` to handle all server errors, or catch specific subclasses for fine-grained control.

### Returning Errors as Strings (MCP convention)
```python
@mcp.tool()
def safe_fetch(resource_id: str) -> str:
    """Fetch a resource, returning an error message on failure."""
    try:
        return fetch_resource(resource_id)
    except ResourceNotFoundError:
        return f"Error: resource '{resource_id}' not found"
    except MCPError as e:
        return f"Server error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
```

**MCP best practice:** Tools should return error descriptions as strings so the model can read them and decide how to respond, rather than crashing the server.

## Logging

### Structured Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

@mcp.tool()
def logged_tool(input_text: str) -> str:
    """Tool with structured logging."""
    logger.info("Tool called", extra={"input_length": len(input_text)})
    try:
        result = process(input_text)
        logger.info("Tool succeeded", extra={"output_length": len(result)})
        return result
    except Exception as e:
        logger.error("Tool failed: %s", e, exc_info=True)
        return f"Error: {e}"
```

**`logging.getLogger(__name__)`:** Creates a logger named after the current module, making it easy to filter logs by source.
**`exc_info=True`:** Appends the full traceback to the log entry when logging exceptions.
**`%(asctime)s`:** Inserts the log timestamp automatically.

## Dependency Injection with Context

### Lifespan and Shared Resources
```python
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP

db_connection = None

@asynccontextmanager
async def lifespan(server):
    """Set up shared resources before serving and tear them down after."""
    global db_connection
    db_connection = await create_db_connection()
    yield
    await db_connection.close()

mcp = FastMCP("production-server", lifespan=lifespan)

@mcp.tool()
async def query_database(sql: str) -> list[dict]:
    """Execute a read-only SQL query."""
    rows = await db_connection.fetch(sql)
    return [dict(row) for row in rows]
```

**`@asynccontextmanager`:** Turns an async generator function into an async context manager.
**`yield`:** Separates setup (before) from teardown (after) in a context manager.
**Lifespan pattern:** Ensures expensive resources (DB connections, HTTP clients) are created once and shared across all tool calls.

## Type Hints for Production Code

### TypedDict for Structured Returns
```python
from typing import TypedDict

class SearchResult(TypedDict):
    title: str
    url: str
    score: float
    snippet: str

@mcp.tool()
def search(query: str, top_k: int = 3) -> list[SearchResult]:
    """Search and return structured results."""
    ...
```

**`TypedDict`:** Defines a dictionary with known keys and their value types; useful for return values that the model will read as JSON.

### Optional and Union Types
```python
from typing import Optional, Union

def fetch(resource_id: str) -> Optional[str]:
    """Return the resource string, or None if not found."""
    ...

def parse_value(raw: Union[str, int, float]) -> float:
    """Accept multiple input types."""
    return float(raw)
```

**`Optional[T]`** is equivalent to `Union[T, None]`.

## Dataclasses

### Using `@dataclass` for Configuration
```python
from dataclasses import dataclass, field

@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    max_connections: int = 100
    allowed_origins: list[str] = field(default_factory=list)
    debug: bool = False
```

**`@dataclass`:** Auto-generates `__init__`, `__repr__`, and `__eq__` from the class attributes.
**`field(default_factory=list)`:** Required for mutable defaults (list, dict) to avoid sharing them between instances.

## Deployment Patterns

### Environment-Based Configuration
```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    api_key: str = ""
    rate_limit: int = 60
    cache_ttl: int = 300
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_key=os.getenv("MCP_API_KEY", ""),
            rate_limit=int(os.getenv("MCP_RATE_LIMIT", "60")),
            cache_ttl=int(os.getenv("MCP_CACHE_TTL", "300")),
            debug=os.getenv("MCP_DEBUG", "").lower() == "true",
        )

config = Config.from_env()
```

**`@classmethod`:** Method that receives the class (`cls`) rather than an instance; used as an alternative constructor.
**`int(os.getenv("KEY", "default"))`:** Always cast environment variable strings to the expected type.

### Running with Uvicorn (HTTP transport)
```python
# server.py
import uvicorn
from mcp.server.fastapi import MCPFastAPI

app = MCPFastAPI(name="production-server", version="1.0.0")

@app.tool()
def ping(message: str) -> str:
    """Health-check tool."""
    return f"PONG: {message}"

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
```

**`uvicorn.run("module:app")`:** Production ASGI server; use `reload=False` in production.

## Best Practices

1. **Always authenticate** – never expose sensitive tools without API key or token validation.
2. **Cache aggressively but expire wisely** – use TTL caches for data that changes; use `lru_cache` for static lookups.
3. **Rate-limit at the tool level** – protects downstream services from accidental overuse by the model.
4. **Return errors as strings** – lets the model handle failures gracefully rather than crashing the session.
5. **Log every tool call** – include the caller identity, input size, and result status for auditing.
6. **Use lifespan for shared resources** – avoid creating new connections per tool call.
7. **Type-annotate everything** – MCP uses annotations to build JSON schemas; unannotated parameters may be ignored.

## Summary

| Pattern | Key API / Syntax |
|---------|-----------------|
| Authentication decorator | `@functools.wraps(func)` + `PermissionError` |
| In-memory cache | `@functools.lru_cache(maxsize=N)` |
| TTL cache | `cachetools.TTLCache(maxsize, ttl)` |
| Rate limiting | `time.monotonic()` + `threading.Lock()` |
| Structured errors | Custom exception hierarchy from `Exception` |
| Logging | `logging.getLogger(__name__)` |
| Shared resources | `@asynccontextmanager` lifespan |
| Typed returns | `TypedDict` |
| Config from env | `@classmethod` + `os.getenv()` |
| HTTP deployment | `MCPFastAPI` + `uvicorn.run()` |
