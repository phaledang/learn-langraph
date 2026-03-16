# Python Language References - Lab 01: LangChain Basics

This document explains the Python methods, classes, and concepts used in Lab 01.

## Imports

### `os` Module
```python
import os
```
- **Purpose**: Provides functions for interacting with the operating system
- **Usage in Lab**: Access environment variables using `os.getenv()`

### `pathlib` - `Path`
```python
from pathlib import Path
```
- **Purpose**: Object-oriented filesystem path handling
- **Usage in Lab**: Resolve the `.env` file path relative to the script location
- **Key Features**:
  - `Path(__file__)` — path to the current script
  - `.parent` — parent directory of the path
  - `/` operator — join paths (e.g., `Path(__file__).parent / ".env"`)

### `dotenv` - `load_dotenv()`
```python
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")
```
- **Purpose**: Loads environment variables from a `.env` file
- **Returns**: `True` if `.env` file is found, `False` otherwise
- **Parameters**:
  - `dotenv_path` (optional): Explicit path to the `.env` file
- **Usage**: Loads API keys and configuration without hardcoding
- **Best Practice**: Use `Path(__file__).parent / ".env"` to resolve the `.env` file relative to the script, so it works regardless of the working directory

## LangChain Components

### `AzureChatOpenAI` Class
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

**Constructor Parameters:**
- `azure_deployment` (str): The name of your Azure OpenAI deployment (e.g., "gpt-5.4")
- `azure_endpoint` (str): Your Azure OpenAI resource endpoint (e.g., `https://<resource>.cognitiveservices.azure.com/`)
- `api_key` (str): Your Azure OpenAI API key
- `api_version` (str): The Azure OpenAI API version (e.g., "2024-05-01-preview")
- `temperature` (float, 0.0-2.0): Controls randomness. Higher = more creative

**Purpose**: Creates an interface to Azure OpenAI's chat models

> **Note**: The endpoint should NOT include `/openai/v1` — the SDK adds the path automatically.

**Common Methods:**
- `invoke(messages)`: Send a single request
- `batch(message_list)`: Send multiple requests in batch
- `stream(messages)`: Stream responses in real-time

### `PromptTemplate` Class
```python
from langchain_core.prompts import PromptTemplate

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
from langchain_core.output_parsers import StrOutputParser

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
api_key = os.getenv("AZURE_OPENAI_API_KEY")
```
- **Purpose**: Retrieve environment variable value
- **Parameters**: 
  - `key` (str): Environment variable name
  - `default` (optional): Value to return if key not found
- **Returns**: String value or `default`

### Azure OpenAI Environment Variables

The following variables are required in your `.env` file:

```dotenv
USE_AZURE_OPENAI=1
AZURE_OPENAI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-05-01-preview
```

### Best Practices
1. **Never hardcode API keys**: Use environment variables
2. **Use `.env` file**: Keep secrets out of version control
3. **Add `.env` to `.gitignore`**: Prevent accidental commits
4. **Validate presence**: Check if required variables exist
5. **Use script-relative paths**: Load `.env` with `Path(__file__).parent / ".env"`

```python
if not os.getenv("AZURE_OPENAI_API_KEY"):
    raise ValueError("AZURE_OPENAI_API_KEY not set")
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
1. `Path(__file__).parent / ".env"` - Resolve `.env` relative to script
2. `load_dotenv(path)` - Load environment variables from a specific path
3. `AzureChatOpenAI()` - Create Azure OpenAI LLM instance
4. `PromptTemplate()` - Create prompt template (from `langchain_core.prompts`)
5. `StrOutputParser()` - Parse LLM output to string (from `langchain_core.output_parsers`)
6. `chain.invoke()` - Execute chain with single input
7. `chain.batch()` - Execute chain with multiple inputs
8. `os.getenv()` - Get environment variable

These form the foundation of working with LangChain and Azure OpenAI, and will be used throughout all labs.
