# Advanced LangChain

## Building Complex Applications

### Advanced Chains

#### Sequential Chains
- Chain multiple operations together
- Pass outputs between steps
- Build complex workflows

```python
from langchain.chains import SequentialChain

chain = SequentialChain(
    chains=[chain1, chain2, chain3],
    input_variables=["input"],
    output_variables=["output"]
)
```

#### Router Chains
- Conditional logic in chains
- Dynamic routing based on input
- Multi-path workflows

### Retrieval Augmented Generation (RAG)

#### Why RAG?
- Overcome LLM knowledge cutoff
- Use private/domain-specific data
- Reduce hallucinations

#### Components
1. **Document Loaders**: Load various file formats
2. **Text Splitters**: Chunk documents intelligently
3. **Embeddings**: Vector representations
4. **Vector Stores**: Efficient similarity search
5. **Retrievers**: Query and retrieve relevant docs

#### RAG Pipeline
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

# Create vector store
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings()
)

# Create QA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)
```

### Custom Tools and Function Calling

#### Defining Tools
```python
from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """Evaluates mathematical expressions."""
    return str(eval(expression))
```

#### Tool Integration
- Extend LLM capabilities
- Connect to external APIs
- Perform computations

### Advanced Memory Systems

#### Memory Types
1. **Conversation Buffer**: Store entire conversation
2. **Conversation Summary**: Summarize over time
3. **Entity Memory**: Track entities
4. **Knowledge Graph**: Structured memory

#### Implementation
```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(llm=llm)
```

### Streaming and Callbacks

#### Real-time Responses
```python
for chunk in chain.stream({"input": query}):
    print(chunk, end="", flush=True)
```

#### Callbacks
- Track token usage
- Monitor performance
- Custom logging

### Error Handling and Retries

#### Robust Applications
```python
from langchain.schema import OutputParserException

try:
    result = chain.run(input)
except OutputParserException:
    # Handle parsing errors
    pass
```

### Optimization Techniques

1. **Caching**: Reduce API calls
2. **Batching**: Process multiple inputs
3. **Async**: Non-blocking operations
4. **Token Management**: Control costs

### Best Practices

- **Prompt Engineering**: Iterate on prompts
- **Testing**: Validate outputs
- **Monitoring**: Track performance
- **Security**: Sanitize inputs
- **Cost Control**: Monitor usage

### Production Considerations

- Rate limiting
- Error recovery
- Logging and observability
- Version control for prompts
- A/B testing

## Resources
- [LangChain Cookbook](https://python.langchain.com/docs/cookbook/)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)
