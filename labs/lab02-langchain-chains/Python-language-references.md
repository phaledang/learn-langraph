# Python Language References - Lab 02: LangChain Chains

## Sequential Chain Processing

### Chain Composition
```python
chain1 = prompt1 | llm | StrOutputParser()
chain2 = prompt2 | llm | StrOutputParser()

# Sequential execution
result1 = chain1.invoke({"input": data})
result2 = chain2.invoke({"summary": result1})
```

**Key Concepts:**
- Each chain processes output from previous step
- Data flows through pipeline sequentially
- Intermediate results can be stored or passed directly

## Router Chains

### Conditional Routing
```python
def route_query(query: str) -> str:
    """Determine which chain to use based on query content."""
    if "math" in query.lower():
        return "math"
    elif "code" in query.lower():
        return "coding"
    return "general"
```

**Methods Used:**
- `str.lower()`: Convert string to lowercase for case-insensitive matching
- `in` operator: Check if substring exists in string
- `any()`: Check if any element in iterable is True

### Dictionary of Chains
```python
chains = {
    "math": math_chain,
    "coding": coding_chain,
    "general": general_chain
}

# Select and execute chain
result = chains[route].invoke({"query": query})
```

## Retrieval Augmented Generation (RAG)

### Document Class
```python
from langchain.schema import Document

doc = Document(
    page_content="Text content here",
    metadata={"source": "file.txt"}
)
```

**Attributes:**
- `page_content` (str): The actual text content
- `metadata` (dict): Additional information about the document

### Text Splitter
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)
splits = splitter.split_documents(documents)
```

**Parameters:**
- `chunk_size`: Maximum size of each chunk in characters
- `chunk_overlap`: Number of overlapping characters between chunks

**Purpose:** Breaks large documents into manageable pieces for embedding

### OpenAI Embeddings
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
```

**Purpose:** Creates vector representations of text
**Output:** Numerical arrays (typically 1536 dimensions for OpenAI)
**Usage:** Enables semantic similarity search

### Vector Store - Chroma
```python
from langchain.vectorstores import Chroma

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    collection_name="my_docs"
)
```

**Methods:**
- `from_documents()`: Create store from document list
- `as_retriever()`: Convert to retriever interface
- `similarity_search()`: Find similar documents

**Retriever Configuration:**
```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 2}  # Return top 2 results
)
```

### RetrievalQA Chain
```python
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)
```

**Parameters:**
- `llm`: Language model to use
- `chain_type`: How to combine documents ("stuff", "map_reduce", "refine", "map_rerank")
- `retriever`: Document retriever

**Chain Types Explained:**
- **stuff**: Puts all documents into prompt (simple, limited by context)
- **map_reduce**: Processes docs separately, then combines results
- **refine**: Iteratively refines answer with each document
- **map_rerank**: Scores each document's relevance

## Advanced Python Concepts

### List Comprehensions with Conditions
```python
math_keywords = ["calculate", "math", "equation"]
is_math = any(word in query.lower() for word in math_keywords)
```

**Breakdown:**
- Generator expression: `word in query.lower() for word in math_keywords`
- `any()`: Returns True if at least one element is True

### String Methods

#### `str.lower()`
```python
text = "Hello World"
text.lower()  # Returns: "hello world"
```
- Converts all characters to lowercase
- Useful for case-insensitive comparisons

#### `in` Operator for Strings
```python
"hello" in "hello world"  # True
"xyz" in "hello world"    # False
```
- Checks substring existence
- Case-sensitive by default

### Function Type Hints
```python
def route_query(query: str) -> str:
    """Type hints specify input and output types."""
    return "math"
```

**Benefits:**
- Better IDE support
- Documentation
- Type checking

## Dictionary Access Patterns

### Direct Access
```python
chains = {"math": math_chain, "coding": coding_chain}
chain = chains["math"]  # Direct access
```

### Safe Access with get()
```python
chain = chains.get("unknown", default_chain)  # Returns default if key missing
```

### Dictionary Comprehension
```python
chains = {
    name: create_chain(template)
    for name, template in templates.items()
}
```

## Error Handling for Chains

### Try-Except Blocks
```python
try:
    result = chain.invoke({"query": query})
except Exception as e:
    print(f"Error executing chain: {e}")
    result = "Error occurred"
```

### Specific Exception Handling
```python
from langchain.schema import OutputParserException

try:
    result = chain.invoke(input_data)
except OutputParserException as e:
    print(f"Failed to parse output: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Working with Chain Outputs

### Accessing Results
```python
# Simple chain - returns string
result = chain.invoke({"input": "query"})

# QA chain - returns dictionary
qa_result = qa_chain.invoke({"query": "question"})
answer = qa_result["result"]  # Access specific field
```

### Batch Processing
```python
inputs = [
    {"query": "question 1"},
    {"query": "question 2"}
]
results = chain.batch(inputs)
```

## Best Practices

### 1. Organize Chain Logic
```python
def create_specialized_chain(template: str, llm):
    """Factory function for creating chains."""
    prompt = PromptTemplate(template=template, input_variables=["query"])
    return prompt | llm | StrOutputParser()
```

### 2. Parameterize Configurations
```python
CHUNK_SIZE = 200
CHUNK_OVERLAP = 20
TOP_K_RESULTS = 2

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)
```

### 3. Handle Missing Data
```python
if not documents:
    raise ValueError("No documents provided for RAG")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not set")
```

### 4. Log Chain Execution
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Routing query to {route} chain")
result = chains[route].invoke({"query": query})
logger.info("Chain execution complete")
```

## Summary of New Methods

| Method/Class | Purpose | Returns |
|-------------|---------|---------|
| `RecursiveCharacterTextSplitter` | Split documents into chunks | List of documents |
| `OpenAIEmbeddings` | Create text embeddings | Embedding vectors |
| `Chroma.from_documents()` | Create vector store | Chroma instance |
| `as_retriever()` | Convert to retriever | Retriever object |
| `RetrievalQA.from_chain_type()` | Create QA chain | Chain instance |
| `any()` | Check if any element is True | Boolean |
| `str.lower()` | Convert to lowercase | String |

These patterns form the foundation for building complex LangChain applications with multiple processing steps and document retrieval capabilities.
