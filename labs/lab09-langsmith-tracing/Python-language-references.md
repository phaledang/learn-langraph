# Python Language References - LangSmith Tracing and Monitoring

## Overview
This document explains the Python syntax, methods, classes, and concepts used in Lab 09 (LangSmith Tracing and Monitoring). Each section below maps directly to code found in the README and solution (`solution/main.py`).

---

## 1. Imports

### Standard Library Imports
```python
import os
from dotenv import load_dotenv
```

- **`os`** – Provides access to operating system functions. Used here both to *write* environment variables (`os.environ[...] = ...`) and to *read* them (`os.getenv()`).
- **`load_dotenv`** – Reads a `.env` file and injects its key-value pairs into the process environment.

### Third-Party / LangChain Imports
```python
from langsmith import Client, trace
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks import LangChainTracer
```

| Import | Description |
|---|---|
| `Client` | LangSmith client used to interact with the LangSmith API (list projects, fetch traces, etc.). |
| `trace` | Decorator / context-manager from LangSmith that wraps a function or code block to capture a named trace. |
| `ChatOpenAI` | LangChain wrapper for OpenAI chat models. |
| `PromptTemplate` | Builds a reusable prompt with named placeholder variables. |
| `StrOutputParser` | Output parser that extracts the raw string from an LLM response message. |
| `LangChainTracer` | Callback handler that sends LangChain run data to LangSmith with optional tags. |

---

## 2. Setting Environment Variables with `os.environ`

```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
os.environ["LANGCHAIN_PROJECT"] = "lab09-tracing"
```

`os.environ` is a dictionary-like object that represents the process's environment variables.

| Operation | Syntax | Notes |
|---|---|---|
| Set a variable | `os.environ["KEY"] = "value"` | Changes are visible to subprocesses. |
| Read a variable | `os.getenv("KEY")` | Returns `None` if the key is absent. |
| Read with default | `os.getenv("KEY", "default")` | Returns `"default"` if absent. |

Using `os.environ[...] = ...` is preferred when you need the variable to take effect immediately within the current process (e.g., LangSmith reads these at chain construction time).

---

## 3. The LangSmith `Client`

```python
from langsmith import Client

client = Client()
print("LangSmith configured successfully!")
```

`Client()` reads `LANGCHAIN_API_KEY` and `LANGCHAIN_ENDPOINT` from the environment automatically. The object exposes methods to list runs, projects, and datasets in your LangSmith workspace.

---

## 4. `PromptTemplate`

```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a haiku about {topic}"
)
```

- **`input_variables`** – List of placeholder names that appear in `template` inside `{...}`.
- **`template`** – The prompt string. Each `{variable}` is filled in when the chain is invoked.

At runtime `prompt.invoke({"topic": "spring"})` returns a formatted prompt message ready to pass to an LLM.

---

## 5. Pipe Operator `|` for Chain Composition

```python
from langchain.schema.output_parser import StrOutputParser

chain = prompt | llm | StrOutputParser()
```

LangChain's **LCEL (LangChain Expression Language)** overloads the `|` operator so that `a | b` means "pass the output of `a` as input to `b`". This creates a composable pipeline called a **chain**:

1. `prompt` formats the input dict into a prompt message.
2. `llm` sends the message to the model and returns an `AIMessage`.
3. `StrOutputParser()` extracts the plain-text content from the `AIMessage`.

The full chain is invoked with a single call:
```python
result = chain.invoke({"topic": "spring"})
```

---

## 6. `chain.invoke()` with a Dictionary

```python
result = chain.invoke({"topic": topic})
result = chain.invoke({"message": user_message})
```

**`chain.invoke(input_dict)`** runs the chain synchronously. The dictionary keys must match the `input_variables` declared in the `PromptTemplate`. The return value depends on the last element of the chain (a `str` when `StrOutputParser()` is the last step).

---

## 7. `for` Loop Iteration

```python
topics = ["spring", "technology", "ocean"]

for topic in topics:
    print(f"\nGenerating haiku for: {topic}")
    result = chain.invoke({"topic": topic})
    print(result)
```

**`for item in iterable`** iterates over every element of a sequence. Each iteration binds the current element to `topic`. This is the standard pattern for processing a list of inputs.

---

## 8. The `@trace` Decorator

```python
from langsmith import trace

@trace(name="haiku_generator", tags=["poetry", "creative"])
def generate_haiku_with_analysis(topic: str):
    """Generate haiku and analyze it."""
    haiku = chain.invoke({"topic": topic})
    ...
```

A **decorator** is a callable placed above a `def` statement with an `@` prefix. It wraps the function, adding behaviour without modifying its body.

`@trace(name=..., tags=...)` is a *parameterised* decorator from LangSmith that:
- Starts a new trace named `"haiku_generator"` each time the function is called.
- Attaches the provided tags to every trace.
- Records the function's inputs, outputs, and execution time automatically.

The decorated function is called exactly like an ordinary function:
```python
result = generate_haiku_with_analysis("mountain")
```

---

## 9. `with` Statement – Context Manager

```python
from langsmith import trace

with trace(name="problematic_test", metadata={"input_length": len(test_input)}):
    result = problematic_chain(test_input)
    print(f"✓ Success: {test_input[:20]}...")
```

The **`with` statement** invokes a *context manager*. `trace(...)` used as a context manager:
- **Enters** – starts a named trace and attaches metadata.
- **Exits** – closes the trace, recording elapsed time and any exception that occurred.

This is functionally equivalent to calling `trace.start()` before the block and `trace.end()` after it, but the `with` syntax guarantees the exit logic runs even if an exception is raised inside the block.

---

## 10. `try` / `except` inside a `with` Block

```python
for test_input in test_inputs:
    try:
        with trace(name="problematic_test", metadata={"input_length": len(test_input)}):
            result = problematic_chain(test_input)
            print(f"✓ Success: {test_input[:20]}...")
    except Exception as e:
        print(f"✗ Error with '{test_input}': {str(e)}")
```

`try` / `except` and `with` are orthogonal and can be freely nested:
- The `with` block records the trace (including errors).
- The surrounding `except` prevents the exception from propagating and prints a user-friendly message.

---

## 11. Raising Exceptions with `raise`

```python
if len(user_input) < 3:
    raise ValueError("Input too short")
```

**`raise ExceptionType(message)`** immediately stops normal execution and propagates an exception up the call stack. `ValueError` signals that a value passed to a function is inappropriate (wrong content, not wrong type).

---

## 12. String Slicing

```python
print(f"✓ Success: {test_input[:20]}...")
print(f"[{user_id}] {message[:30]}... → {result['response'][:50]}...")
```

**`string[start:stop]`** returns a substring from index `start` up to (but not including) `stop`.

| Slice | Meaning |
|---|---|
| `s[:20]` | First 20 characters (start defaults to 0). |
| `s[5:]` | From index 5 to the end. |
| `s[-1]` | Last character (negative index counts from the end). |
| `s[::2]` | Every second character. |

`test_input[:20]` safely truncates any string to 20 characters for display.

---

## 13. Class Definitions and Object-Oriented Programming

```python
class ProductionChatbot:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.conversation_count = 0

    @trace(name="chatbot_response")
    def respond(self, user_message: str, user_id: str = "anonymous"):
        """Generate chatbot response with full tracing."""
        self.conversation_count += 1
        ...
```

| Element | Description |
|---|---|
| `class ProductionChatbot:` | Defines a new class (blueprint for objects). |
| `def __init__(self):` | **Constructor** – runs automatically when `ProductionChatbot()` is called. Initialises instance attributes. |
| `self` | Reference to the current instance. Must be the first parameter of every instance method. |
| `self.llm = ...` | Creates an **instance attribute** `llm` on the object. Each instance has its own copy. |
| `self.conversation_count += 1` | Increments the instance attribute `conversation_count` by 1. |
| `def respond(self, ...)` | Defines an **instance method**. Called as `chatbot.respond(...)`. |

Creating and using an instance:
```python
chatbot = ProductionChatbot()   # calls __init__
chatbot.respond("Hello!")       # calls respond with self=chatbot
```

---

## 14. Returning a Dictionary

```python
return {
    "haiku": haiku,
    "line_count": len(lines),
    "word_pattern": syllable_pattern,
    "topic": topic
}

return {
    "response": response,
    "conversation_id": self.conversation_count,
    "user_id": user_id
}
```

Functions can return a **dictionary literal** `{key: value, ...}` to pass multiple named values back to the caller. The caller accesses individual values with `result["key"]` or `result.get("key")`.

---

## 15. List Comprehension

```python
lines = haiku.strip().split('\n')
syllable_pattern = [len(line.split()) for line in lines]
```

**Syntax**: `[expression for item in iterable]`

This produces a new list by applying `expression` to every element of `iterable`. Here it counts the words in each line of the haiku.

Equivalent `for`-loop:
```python
syllable_pattern = []
for line in lines:
    syllable_pattern.append(len(line.split()))
```

---

## 16. Tuple Unpacking in a `for` Loop

```python
scenarios = [
    ("user1", "Hello, how are you?"),
    ("user2", "What's the weather like?"),
    ("user1", "Can you help me with Python?"),
]

for user_id, message in scenarios:
    result = chatbot.respond(message, user_id)
    print(f"[{user_id}] {message[:30]}... → {result['response'][:50]}...")
```

When each element of the iterable is a **tuple** (or any sequence), you can **unpack** it directly into multiple variables in the `for` clause. `for user_id, message in scenarios` is equivalent to:

```python
for item in scenarios:
    user_id, message = item
```

Tuple unpacking makes the code more readable by giving each element a meaningful name.

---

## 17. `LangChainTracer` and Custom Tags

```python
from langchain.callbacks import LangChainTracer

tracer = LangChainTracer(
    project_name="lab09-tracing",
    tags=["haiku-generation", "creative-writing"]
)
```

`LangChainTracer` is a **callback handler** that sends trace data to LangSmith. Passing it to `chain.invoke(..., config={"callbacks": [tracer]})` associates that invocation with the given project and tags, enabling filtering in the LangSmith dashboard.

---

## 18. `if __name__ == "__main__"`

```python
if __name__ == "__main__":
    main()
```

Python sets `__name__` to `"__main__"` when a script is run directly (e.g., `python main.py`). When the file is imported as a module, `__name__` is set to the module name and `main()` is **not** called automatically. This guard is a standard Python pattern for script entry points.

---

## Best Practices Demonstrated in This Lab

1. **Use environment variables for secrets** – never hard-code API keys; set them via `os.environ` or a `.env` file loaded with `load_dotenv()`.
2. **Use the `@trace` decorator for function-level tracing** – captures inputs, outputs, and timing without modifying the function's logic.
3. **Use `with trace(...)` for block-level tracing** – attach metadata to a specific section of code and ensure the trace is always closed, even on error.
4. **Add tags and metadata** – use `tags` and `metadata` in `LangChainTracer` and `trace(...)` to organise and filter traces in the LangSmith dashboard.
5. **Wrap traced calls in `try/except`** – prevent tracing failures from crashing the application.
6. **Use LCEL pipe chains** – composing `prompt | llm | parser` with `|` is concise and automatically traced end-to-end by LangSmith.
7. **Use type hints** – annotate function parameters and return types for clarity and tooling support.

---

## Summary

| Concept | Where Used |
|---|---|
| `import os` / `from … import` | All modules at the top of `main.py` |
| `os.environ["KEY"] = "value"` | Setting LangSmith configuration variables |
| `os.getenv("KEY")` | Reading API key for guard check |
| `load_dotenv()` | Loading credentials from `.env` |
| `Client()` | Instantiating the LangSmith client |
| `PromptTemplate(input_variables, template)` | Building reusable prompts |
| `|` pipe operator | Composing LCEL chains: `prompt \| llm \| StrOutputParser()` |
| `chain.invoke(dict)` | Running a chain with named inputs |
| `for item in list` | Iterating over topics, inputs, scenarios |
| `@trace(name, tags)` | Function-level LangSmith tracing via decorator |
| `with trace(name, metadata)` | Block-level LangSmith tracing via context manager |
| `try` / `except` | Catching and reporting errors inside traced blocks |
| `raise ValueError(...)` | Signalling invalid input |
| `string[:n]` | Truncating strings for display |
| `class` / `__init__` / `self` | `ProductionChatbot` class definition |
| Instance attributes (`self.x`) | `self.llm`, `self.conversation_count` |
| `@trace` on a method | Tracing class method calls |
| Return dictionary `{...}` | Returning multiple named values from functions |
| List comprehension | Computing `syllable_pattern` from haiku lines |
| Tuple unpacking in `for` | `for user_id, message in scenarios` |
| `LangChainTracer` | Callback-based tracing with custom tags |
| `if __name__ == "__main__"` | Script entry-point guard |
