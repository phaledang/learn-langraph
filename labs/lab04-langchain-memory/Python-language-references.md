# Python Language References - LangChain Memory Systems

## Overview
This document explains the Python methods, classes, and concepts used in this lab.

---

## 1. LangChain Core Imports

### `AzureChatOpenAI`
```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.7,
)
```

**Purpose:** LangChain wrapper around the Azure OpenAI Chat Completions API.

| Parameter | Type | Description |
|---|---|---|
| `azure_deployment` | `str` | The name of your Azure deployment |
| `azure_endpoint` | `str` | Your Azure OpenAI endpoint URL |
| `api_key` | `str` | Your Azure OpenAI API key |
| `api_version` | `str` | API version string (e.g., `"2024-02-01"`) |
| `temperature` | `float` | Randomness: 0.0 = deterministic, 1.0 = creative |

---

### `HumanMessage` and `AIMessage`
```python
from langchain_core.messages import HumanMessage, AIMessage

human_msg = HumanMessage(content="Hello!")
ai_msg = AIMessage(content="Hi there!")
```

**Purpose:** Typed message objects that represent turns in a conversation.

- `HumanMessage` — represents a message from the user
- `AIMessage` — represents a response from the AI

**Checking message type:**
```python
if isinstance(msg, HumanMessage):
    role = "Human"
else:
    role = "AI"
```

---

### `ChatPromptTemplate` and `MessagesPlaceholder`
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
```

**Purpose:**
- `ChatPromptTemplate` — builds a structured prompt from a list of message tuples or objects.
- `MessagesPlaceholder` — inserts a list of messages (e.g., conversation history) into the prompt at runtime.

**Invoking a prompt-based chain:**
```python
chain = prompt | llm | StrOutputParser()
response = chain.invoke({
    "history": memory.get_messages(),
    "input": "What did I just say?",
})
```

---

### `StrOutputParser`
```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"input": "Hello"})
# result is a plain Python str
```

**Purpose:** Extracts the text content from an LLM response message, returning a plain `str`.

---

## 2. Memory Classes

All memory classes in this lab share a common interface:

| Method | Description |
|---|---|
| `add_user_message(content)` | Append a `HumanMessage` to memory |
| `add_ai_message(content)` | Append an `AIMessage` to memory |
| `get_messages()` | Return the list of messages to inject into the prompt |
| `clear()` | Reset all stored messages |

---

### `ConversationBufferMemory`
Stores **all** messages in an unbounded list.

```python
class ConversationBufferMemory:
    def __init__(self):
        self.messages: list = []

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))

    def get_messages(self) -> list:
        return list(self.messages)

    def clear(self):
        self.messages.clear()

    @property
    def buffer(self):
        return self.messages
```

**Usage:**
```python
memory = ConversationBufferMemory()
memory.add_user_message("Hi, I'm learning about AI")
memory.add_ai_message("That's great!")
print(len(memory.get_messages()))  # 2
```

**Key concept — `@property`:** Exposes `memory.buffer` as an attribute rather than a method call, making it convenient for serialisation.

---

### `ConversationBufferWindowMemory`
Keeps only the last **k exchanges** (k human + k AI messages = 2k messages total).

```python
class ConversationBufferWindowMemory:
    def __init__(self, k: int = 5):
        self.k = k
        self.messages: list = []

    def get_messages(self) -> list:
        # Each exchange = 2 messages; keep last k exchanges
        return self.messages[-(self.k * 2):]
```

**Usage:**
```python
window_memory = ConversationBufferWindowMemory(k=2)
```

**Key concept — negative list slicing:**
```python
items = [1, 2, 3, 4, 5, 6]
items[-4:]   # [3, 4, 5, 6]  — last 4 elements
```

---

### `ConversationSummaryMemory`
Periodically **summarises** older messages when the total count exceeds `max_messages`, keeping only the most recent messages plus a running summary string.

```python
class ConversationSummaryMemory:
    def __init__(self, llm, max_messages: int = 6):
        self.llm = llm
        self.max_messages = max_messages
        self.messages: list = []
        self.summary: str = ""

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))
        if len(self.messages) > self.max_messages:
            self._summarize()

    def get_messages(self) -> list:
        result = []
        if self.summary:
            result.append(AIMessage(content=f"[Previous conversation summary]: {self.summary}"))
        result.extend(self.messages)
        return result
```

**Summarisation chain:**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the following conversation concisely:\n\n{conversation}"),
])
chain = prompt | self.llm | StrOutputParser()
new_summary = chain.invoke({"conversation": conversation_text})
```

**Usage:**
```python
summary_memory = ConversationSummaryMemory(llm=llm, max_messages=6)
```

---

### `ConversationEntityMemory`
Tracks **named entities** (people, places, organisations) by calling the LLM to extract them from each user message. Entities are stored in a `dict`.

```python
class ConversationEntityMemory:
    def __init__(self, llm):
        self.llm = llm
        self.messages: list = []
        self.entities: dict = {}  # entity_name -> description

    def extract_entities(self, text: str):
        """Use the LLM to extract entities from text."""
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Extract named entities from the text. "
             "Return as JSON with names as keys and descriptions as values.\n\n"
             "Text: {text}"),
        ])
        chain = prompt | self.llm | StrOutputParser()
        raw = chain.invoke({"text": text})
        try:
            new_entities = json.loads(raw)
            self.entities.update(new_entities)
        except json.JSONDecodeError:
            pass  # ignore unparseable responses
```

**Usage:**
```python
entity_memory = ConversationEntityMemory(llm=llm)
entity_memory.extract_entities("My name is Bob and I work at Microsoft.")
print(entity_memory.entities)  # {"Bob": "...", "Microsoft": "..."}
```

**Key concepts:**

`json.loads()` — parses a JSON string into a Python dict:
```python
import json
data = json.loads('{"name": "Bob", "company": "Microsoft"}')
# data == {"name": "Bob", "company": "Microsoft"}
```

`dict.update()` — merges another dict into the current one:
```python
d = {"a": 1}
d.update({"b": 2})
# d == {"a": 1, "b": 2}
```

`try / except json.JSONDecodeError` — handles malformed JSON gracefully:
```python
try:
    result = json.loads(raw_text)
except json.JSONDecodeError:
    result = {}
```

---

### `ConversationSummaryBufferMemory`
Combines buffer and summary strategies: recent messages are kept as-is; when estimated **token usage** exceeds `max_token_limit`, the oldest message pairs are progressively summarised.

```python
class ConversationSummaryBufferMemory:
    def __init__(self, llm, max_token_limit: int = 300):
        self.llm = llm
        self.max_token_limit = max_token_limit
        self.messages: list = []
        self.summary: str = ""

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return len(text) // 4  # rough estimate: 1 token ≈ 4 chars
```

**Usage:**
```python
limited_memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)
```

**Key concept — `@staticmethod`:** A method that belongs to the class but does not need access to `self` or `cls`. It can be called on an instance or the class directly:
```python
ConversationSummaryBufferMemory._estimate_tokens("Hello world")  # 2
```

---

## 3. Conversation Runner (`chat` helper)

```python
def chat(llm, memory, user_input: str, system_prompt: str = "You are a helpful assistant.") -> str:
    memory.add_user_message(user_input)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "history": memory.get_messages()[:-1],  # exclude the just-added human message
        "input": user_input,
    })

    memory.add_ai_message(response)
    return response
```

**Purpose:** Central function that adds the user message to memory, builds the prompt with conversation history, invokes the LLM, and stores the AI reply.

**Key concept — list slicing `[:-1]`:** Returns all elements except the last one. Used here to pass history without the message that was just appended:
```python
items = [1, 2, 3, 4, 5]
items[:-1]  # [1, 2, 3, 4]
```

---

## 4. Persistent Memory

### `json` — saving and loading memory as JSON
```python
import json

# Save
data = {"messages": [...], "summary": "..."}
with open("memory.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# Load
with open("memory.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

| Function | Description |
|---|---|
| `json.dump(obj, fp)` | Serialise `obj` to a file object `fp` |
| `json.load(fp)` | Deserialise from a file object `fp` |
| `json.dumps(obj)` | Serialise `obj` to a JSON string |
| `json.loads(s)` | Deserialise from a JSON string `s` |

---

### `pickle` — binary serialisation
```python
import pickle

# Save
with open("memory.pkl", "wb") as f:
    pickle.dump(memory.buffer, f)

# Load
with open("memory.pkl", "rb") as f:
    restored_buffer = pickle.load(f)
```

**When to use `pickle` vs `json`:**
- `pickle` — handles any Python object (including `HumanMessage` / `AIMessage` instances); binary format; Python-only.
- `json` — human-readable text; language-agnostic; only supports basic types (str, int, list, dict).

---

### `pathlib.Path`
```python
from pathlib import Path

MEMORY_DIR = Path(__file__).parent / "memory_store"

# Create directory if it doesn't exist
MEMORY_DIR.mkdir(exist_ok=True)

# Build a file path
filepath = MEMORY_DIR / "session_memory.json"

# Check existence
if filepath.exists():
    ...
```

**Key attributes and methods:**

| Attribute / Method | Description |
|---|---|
| `Path(__file__).parent` | Directory containing the current script |
| `path / "subdir"` | Join path segments with `/` operator |
| `path.mkdir(exist_ok=True)` | Create directory; no error if it already exists |
| `path.exists()` | Return `True` if the path points to an existing file or directory |
| `path.iterdir()` | Iterate over the contents of a directory |
| `path.unlink()` | Delete the file |

---

### `hasattr()` — checking optional attributes
```python
if hasattr(memory, "summary"):
    data["summary"] = memory.summary

if hasattr(memory, "entities"):
    data["entities"] = memory.entities
```

**Purpose:** Returns `True` if the object has the named attribute. Useful when handling multiple memory types that may or may not have certain fields.

---

## 5. Best Practices

### 1. Use `os.getenv()` for secrets
```python
import os

api_key = os.getenv("AZURE_OPENAI_API_KEY")
if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY not set")
```

### 2. Use `load_dotenv` for local development
```python
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")
```

### 3. Type hints improve readability
```python
def chat(llm, memory, user_input: str, system_prompt: str = "You are a helpful assistant.") -> str:
    ...
```

### 4. Handle `JSONDecodeError` when parsing LLM output
```python
try:
    result = json.loads(llm_response)
except json.JSONDecodeError:
    result = {}
    print("Could not parse LLM response as JSON")
```

### 5. Use `f-strings` for readable output
```python
print(f"Human: {user_input}")
print(f"AI: {response[:150]}...")  # truncate long responses
print(f"Messages in memory: {len(memory.get_messages())}")
```

---

## Summary of Methods and Classes

| Class / Function | Purpose | Returns |
|---|---|---|
| `AzureChatOpenAI(...)` | Azure-hosted LLM instance | LLM object |
| `HumanMessage(content=...)` | User turn message | `HumanMessage` |
| `AIMessage(content=...)` | AI turn message | `AIMessage` |
| `ChatPromptTemplate.from_messages([...])` | Build a chat prompt | `ChatPromptTemplate` |
| `MessagesPlaceholder(variable_name=...)` | Slot for history list in prompt | `MessagesPlaceholder` |
| `StrOutputParser()` | Extract plain string from LLM response | `StrOutputParser` |
| `ConversationBufferMemory` | Store all messages | Memory object |
| `ConversationBufferWindowMemory(k=n)` | Keep last n exchanges | Memory object |
| `ConversationSummaryMemory(llm=...)` | Summarise old messages | Memory object |
| `ConversationEntityMemory(llm=...)` | Track named entities | Memory object |
| `ConversationSummaryBufferMemory(llm=..., max_token_limit=n)` | Token-limited summary buffer | Memory object |
| `json.dump(obj, fp)` | Save object to JSON file | `None` |
| `json.load(fp)` | Load object from JSON file | `dict` / `list` |
| `json.loads(s)` | Parse JSON string | `dict` / `list` |
| `pickle.dump(obj, fp)` | Serialise object to binary file | `None` |
| `pickle.load(fp)` | Deserialise object from binary file | Python object |
| `Path(__file__).parent` | Directory of current script | `Path` |
| `path.mkdir(exist_ok=True)` | Create directory safely | `None` |
| `hasattr(obj, name)` | Check if attribute exists | `bool` |
