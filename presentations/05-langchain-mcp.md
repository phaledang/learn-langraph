# LangChain Model Context Protocol (MCP)

## Introduction to MCP

### What is Model Context Protocol?
- **Standardized protocol for connecting LLMs to external context**
- Open protocol by Anthropic
- Enables LLMs to access tools, data, and services
- Simplifies integration between AI models and applications

### Why MCP?

#### Current Challenges
- Each integration is custom-built
- No standard way to connect tools
- Difficult to share capabilities
- Limited interoperability

#### MCP Benefits
- **Standardization**: Common interface
- **Reusability**: Share servers across projects
- **Flexibility**: Connect any tool or data source
- **Security**: Controlled access patterns

### Core Components

#### 1. MCP Server
- Exposes resources and tools
- Implements MCP protocol
- Can provide:
  - **Resources**: Data and context
  - **Tools**: Actions the LLM can invoke
  - **Prompts**: Reusable prompt templates

#### 2. MCP Client
- Connects to MCP servers
- Used by LLM applications
- Manages connections and requests

#### 3. Protocol
- JSON-RPC 2.0 based
- Bidirectional communication
- Standard message formats

### MCP Architecture

```
┌─────────────────┐
│  LLM Application│
│   (LangChain)   │
└────────┬────────┘
         │
         │ MCP Client
         │
┌────────┴────────┐
│   MCP Server    │
│                 │
│  ┌───────────┐  │
│  │ Resources │  │
│  ├───────────┤  │
│  │   Tools   │  │
│  ├───────────┤  │
│  │  Prompts  │  │
│  └───────────┘  │
└─────────────────┘
```

### Resources

#### What are Resources?
- Context the LLM can access
- Files, documents, databases
- APIs and external data

#### Resource Example
```json
{
  "uri": "file:///docs/readme.md",
  "name": "README",
  "mimeType": "text/markdown",
  "description": "Project documentation"
}
```

### Tools

#### What are Tools?
- Actions the LLM can perform
- Functions with defined inputs/outputs
- Connected to external systems

#### Tool Example
```json
{
  "name": "search_database",
  "description": "Search the product database",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"}
    }
  }
}
```

### Building MCP Servers

#### Python MCP Server
```python
from mcp.server import Server
from mcp.types import Resource, Tool

server = Server("my-server")

@server.resource("document/{id}")
async def get_document(id: str) -> Resource:
    # Fetch and return document
    content = fetch_document(id)
    return Resource(
        uri=f"document://{id}",
        name=f"Document {id}",
        mimeType="text/plain",
        text=content
    )

@server.tool("calculate")
async def calculate(expression: str) -> str:
    """Evaluate mathematical expressions"""
    result = eval(expression)
    return str(result)
```

#### Running the Server
```python
if __name__ == "__main__":
    server.run()
```

### Integrating with LangChain

#### Connect to MCP Server
```python
from langchain_mcp import MCPToolkit

# Connect to MCP server
toolkit = MCPToolkit(
    server_url="http://localhost:3000"
)

# Get tools
tools = toolkit.get_tools()

# Use with agent
from langchain.agents import initialize_agent

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description"
)
```

#### Using MCP Resources
```python
# Access resources
resources = toolkit.get_resources()

# Fetch specific resource
resource_content = toolkit.get_resource(
    "document://readme"
)
```

### Common Use Cases

#### 1. Data Integration
- Connect to databases
- Access file systems
- Query APIs
- Aggregate data sources

#### 2. Tool Augmentation
- Calculator functions
- Search capabilities
- Code execution
- External service calls

#### 3. Knowledge Bases
- Documentation access
- Wiki integration
- Policy documents
- Training materials

#### 4. Multi-Modal Content
- Image processing
- Audio transcription
- Video analysis
- Document parsing

### MCP Server Examples

#### File System Server
```python
@server.resource("file/{path}")
async def read_file(path: str):
    with open(path, 'r') as f:
        content = f.read()
    return Resource(
        uri=f"file://{path}",
        text=content
    )
```

#### Database Server
```python
@server.tool("query_db")
async def query_database(sql: str):
    """Execute SQL query"""
    results = db.execute(sql)
    return json.dumps(results)
```

#### API Server
```python
@server.tool("get_weather")
async def get_weather(city: str):
    """Get weather for a city"""
    response = requests.get(
        f"https://api.weather.com/{city}"
    )
    return response.json()
```

### Security Considerations

#### Authentication
- API keys
- OAuth integration
- Token-based auth

#### Authorization
- Resource access control
- Tool usage permissions
- Rate limiting

#### Data Privacy
- Sanitize sensitive data
- Audit logging
- Encryption in transit

### Best Practices

1. **Design Clear Interfaces**: Well-defined tools and resources
2. **Document Thoroughly**: Clear descriptions and examples
3. **Handle Errors Gracefully**: Robust error handling
4. **Implement Rate Limiting**: Prevent abuse
5. **Version Your APIs**: Maintain compatibility
6. **Monitor Usage**: Track performance and costs
7. **Test Extensively**: Validate all scenarios

### Advanced Topics

#### Streaming Responses
```python
@server.tool("stream_data")
async def stream_data():
    for chunk in data_stream:
        yield chunk
```

#### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
@server.resource("cached/{id}")
async def cached_resource(id: str):
    return fetch_expensive_resource(id)
```

#### Batch Operations
```python
@server.tool("batch_process")
async def batch_process(items: list):
    results = []
    for item in items:
        results.append(process(item))
    return results
```

### Debugging MCP

#### Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
server.logger.debug("Processing request")
```

#### Testing
```python
import pytest

@pytest.mark.asyncio
async def test_tool():
    result = await calculate("2 + 2")
    assert result == "4"
```

### Ecosystem Integration

#### Compatible Clients
- Claude Desktop
- Custom applications
- IDEs with MCP support

#### Server Registry
- Community servers
- Official integrations
- Custom implementations

## Resources
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP GitHub](https://github.com/anthropics/mcp)
- [Example Servers](https://github.com/anthropics/mcp-servers)
- [LangChain MCP Integration](https://python.langchain.com/docs/integrations/tools/mcp)
