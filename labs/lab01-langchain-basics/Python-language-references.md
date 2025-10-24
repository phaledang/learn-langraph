# Python Language References - Lab 01: LangChain Basics

This document explains the Python methods, classes, and concepts used in Lab 01.

## Imports

### `os` Module
```python
import os
```
- **Purpose**: Provides functions for interacting with the operating system
- **Usage in Lab**: Access environment variables using `os.getenv()`

### `dotenv` - `load_dotenv()`
```python
from dotenv import load_dotenv
load_dotenv()
```
- **Purpose**: Loads environment variables from a `.env` file
- **Returns**: `True` if `.env` file is found, `False` otherwise
- **Usage**: Automatically loads API keys and configuration without hardcoding

## LangChain Components

### `ChatOpenAI` Class
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

**Constructor Parameters:**
- `model` (str): The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4")
- `temperature` (float, 0.0-2.0): Controls randomness. Higher = more creative
- `api_key` (str): Your OpenAI API key

**Purpose**: Creates an interface to OpenAI's chat models

**Common Methods:**
- `invoke(messages)`: Send a single request
- `batch(message_list)`: Send multiple requests in batch
- `stream(messages)`: Stream responses in real-time

### `PromptTemplate` Class
```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a poem about {topic}"
)
```

**Constructor Parameters:**
- `input_variables` (List[str]): Names of variables to be filled in the template
- `template` (str): The template string with placeholders in `{variable}` format

**Purpose**: Creates reusable prompt templates with variable substitution

**Common Methods:**
- `format(**kwargs)`: Fill in template variables and return formatted string
- `invoke(dict)`: Format and return as a prompt value object

**Example:**
```python
prompt.format(topic="AI")  # Returns: "Write a poem about AI"
```

### `StrOutputParser` Class
```python
from langchain.schema.output_parser import StrOutputParser

parser = StrOutputParser()
```

**Purpose**: Parses LLM output into a string format

**Methods:**
- `parse(output)`: Convert AI message to string
- `invoke(output)`: Parse single output
- `batch(outputs)`: Parse multiple outputs

### LangChain Expression Language (LCEL)

#### Pipe Operator (`|`)
```python
chain = prompt | llm | StrOutputParser()
```

**Purpose**: Chains components together in a pipeline
- Data flows left to right through the pipeline
- Each component processes the output of the previous one
- Creates a Runnable object that can be invoked

**Equivalent to:**
```python
# Traditional approach
formatted_prompt = prompt.format(topic="AI")
llm_output = llm.invoke(formatted_prompt)
final_output = parser.parse(llm_output)
```

#### Chain Methods

##### `invoke(input_dict)`
```python
result = chain.invoke({"topic": "nature"})
```
- **Purpose**: Execute the chain with a single input
- **Parameters**: Dictionary with keys matching input variables
- **Returns**: The final output after passing through all components

##### `batch(input_list)`
```python
results = chain.batch([
    {"topic": "ocean"},
    {"topic": "mountain"}
])
```
- **Purpose**: Process multiple inputs efficiently
- **Parameters**: List of input dictionaries
- **Returns**: List of outputs in the same order
- **Benefits**: More efficient than multiple `invoke()` calls

##### `stream(input_dict)`
```python
for chunk in chain.stream({"topic": "AI"}):
    print(chunk, end="", flush=True)
```
- **Purpose**: Stream output as it's generated
- **Yields**: Chunks of output as they become available
- **Use Case**: Real-time display of responses

## Python Concepts Used

### F-strings (Formatted String Literals)
```python
print(f"Topic: {topic}")
```
- **Purpose**: Embed expressions inside string literals
- **Syntax**: `f"text {variable} more text"`
- **Introduced**: Python 3.6

### Dictionary Comprehension
```python
{"topic": "AI"}
```
- **Purpose**: Create dictionaries with key-value pairs
- **Usage**: Pass parameters to functions and methods

### List Operations
```python
topics = ["AI", "nature", "friendship"]
for topic in topics:
    print(topic)
```
- **Iteration**: Loop through list elements
- **Indexing**: Access elements with `list[index]`

### Context Manager Pattern
```python
with open("file.txt") as f:
    content = f.read()
```
- **Purpose**: Automatic resource management
- **Guarantee**: Resources are properly cleaned up
- **Note**: Not used in Lab 01 but important for file operations

## Environment Variables

### `os.getenv(key, default=None)`
```python
api_key = os.getenv("OPENAI_API_KEY")
```
- **Purpose**: Retrieve environment variable value
- **Parameters**: 
  - `key` (str): Environment variable name
  - `default` (optional): Value to return if key not found
- **Returns**: String value or `default`

### Best Practices
1. **Never hardcode API keys**: Use environment variables
2. **Use `.env` file**: Keep secrets out of version control
3. **Add `.env` to `.gitignore`**: Prevent accidental commits
4. **Validate presence**: Check if required variables exist

```python
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not set")
```

## Error Handling

### Basic Try-Except
```python
try:
    result = chain.invoke({"topic": "AI"})
except Exception as e:
    print(f"Error: {e}")
```

### Specific Exceptions
```python
from openai import OpenAIError

try:
    result = chain.invoke({"topic": "AI"})
except OpenAIError as e:
    print(f"OpenAI API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Type Hints (Optional but Recommended)

```python
from typing import Dict, List, Any

def process_topics(topics: List[str]) -> List[str]:
    """
    Process a list of topics and return results.
    
    Args:
        topics: List of topic strings
        
    Returns:
        List of generated poems
    """
    results = []
    for topic in topics:
        result = chain.invoke({"topic": topic})
        results.append(result)
    return results
```

**Benefits:**
- Better code documentation
- IDE autocomplete support
- Easier debugging
- Type checking with tools like mypy

## Summary

Key methods to remember:
1. `load_dotenv()` - Load environment variables
2. `ChatOpenAI()` - Create LLM instance
3. `PromptTemplate()` - Create prompt template
4. `chain.invoke()` - Execute chain with single input
5. `chain.batch()` - Execute chain with multiple inputs
6. `os.getenv()` - Get environment variable

These form the foundation of working with LangChain and will be used throughout all labs.
