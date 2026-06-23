# Learn LangChain, LangGraph, LangSmith & MCP

A comprehensive step-by-step learning repository for mastering LangChain, LangGraph, LangSmith, and LangChain MCP with hands-on labs, detailed documentation, and practical examples.

## 📚 Table of Contents

- [Learn LangChain, LangGraph, LangSmith \& MCP](#learn-langchain-langgraph-langsmith--mcp)
  - [📚 Table of Contents](#-table-of-contents)
  - [🎯 Overview](#-overview)
  - [📋 Prerequisites](#-prerequisites)
  - [📁 Project Structure](#-project-structure)
  - [🚀 Setup Instructions](#-setup-instructions)
  - [🎓 Learning Path](#-learning-path)
    - [Phase 1: LangChain Fundamentals (Labs 1-4)](#phase-1-langchain-fundamentals-labs-1-4)
    - [Phase 2: LangGraph (Labs 5-8)](#phase-2-langgraph-labs-5-8)
    - [Phase 3: LangSmith (Labs 9-10)](#phase-3-langsmith-labs-9-10)
    - [Phase 4: LangChain MCP (Labs 11-12)](#phase-4-langchain-mcp-labs-11-12)
  - [💾 Database State Persistence](#-database-state-persistence)
    - [Supported Databases](#supported-databases)
  - [📊 Labs Overview](#-labs-overview)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [🙏 Acknowledgments](#-acknowledgments)

## 🎯 Overview

This repository provides a structured learning path for:
- **LangChain**: Building applications with LLMs
- **LangGraph**: Creating stateful, multi-actor applications
- **LangSmith**: Monitoring, testing, and debugging LLM applications
- **LangChain MCP**: Model Context Protocol integration

Each lab includes:
- 📖 README with learning objectives
- 🎯 Starter code to begin with
- ✅ Solution code for reference
- 📝 Python language reference explaining methods used
- 🎤 Presentation materials

## 📋 Prerequisites

- Python 3.9 or higher
- Basic understanding of Python programming
- OpenAI API key (or other LLM provider API key)
- Git for version control

## 📁 Project Structure

```
learn-langraph/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── presentations/                     # Presentation slides for each topic
│   ├── 01-langchain-basics.md
│   ├── 02-langchain-advanced.md
│   ├── 03-langgraph-fundamentals.md
│   ├── 04-langsmith-monitoring.md
│   ├── 05-langchain-mcp.md
│   ├── 06-langgraph-stateful.md
│   ├── 07-langgraph-multiagent.md
│   ├── 08-langgraph-persistence.md
│   ├── 09-langsmith-tracing.md
│   ├── 10-langsmith-evaluation.md
│   ├── 11-mcp-integration.md
│   ├── 12-mcp-advanced.md
│   ├── 13-pdf-image-to-csv.md
│   ├── 14-mcp-server.md
│   └── 15-mcp-sharepoint.md
├── labs/
│   ├── lab01-langchain-basics/
│   │   ├── README.md
│   │   ├── starter/
│   │   │   └── main.py
│   │   ├── solution/
│   │   │   └── main.py
│   │   └── Python-language-references.md
│   ├── lab02-langchain-chains/
│   ├── lab03-langchain-agents/
│   ├── lab04-langchain-memory/
│   ├── lab05-langgraph-basics/
│   ├── lab06-langgraph-stateful/
│   ├── lab07-langgraph-multiagent/
│   ├── lab08-langgraph-persistence/
│   ├── lab09-langsmith-tracing/
│   ├── lab10-langsmith-evaluation/
│   ├── lab11-mcp-integration/
│   └── lab12-mcp-advanced/
└── shared/
    └── state_persistence/
        ├── __init__.py
        ├── base.py
        ├── cosmosdb.py
        ├── postgresql.py
        └── sqlserver.py
```

## 🚀 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/phaledang/learn-langraph.git
   cd learn-langraph
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database connection string
   ```

## 🎓 Learning Path

### Phase 1: LangChain Fundamentals (Labs 1-4)
1. **Lab 01**: LangChain Basics - Introduction to LLMs and basic chains
2. **Lab 02**: Chains and Prompts - Building complex chains and prompt templates
3. **Lab 03**: Agents and Tools - Creating agents with custom tools
4. **Lab 04**: Memory Systems - Implementing conversation memory

### Phase 2: LangGraph (Labs 5-8)
5. **Lab 05**: LangGraph Basics - Introduction to graph-based workflows
6. **Lab 06**: Stateful Applications - Managing state in multi-step workflows
7. **Lab 07**: Multi-Agent Systems - Coordinating multiple agents
8. **Lab 08**: State Persistence - Saving and loading graph state

### Phase 3: LangSmith (Labs 9-10)
9. **Lab 09**: Tracing and Monitoring - Setting up LangSmith for observability
10. **Lab 10**: Evaluation and Testing - Creating test suites and evaluations

### Phase 4: LangChain MCP (Labs 11-12)
11. **Lab 11**: MCP Integration - Introduction to Model Context Protocol
12. **Lab 12**: Advanced MCP - Building custom MCP servers

## 💾 Database State Persistence

The state persistence module supports multiple databases based on your connection string in `.env`:

### Supported Databases

1. **Azure Cosmos DB**
   ```env
   DATABASE_CONNECTION_STRING=AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key;
   ```

2. **PostgreSQL**
   ```env
   DATABASE_CONNECTION_STRING=postgresql://user:password@localhost:5432/dbname
   ```

3. **SQL Server**
   ```env
   DATABASE_CONNECTION_STRING=mssql+pyodbc://user:password@server:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server
   ```

The system automatically detects the database type from the connection string and uses the appropriate adapter.

## 📊 Labs Overview

Each lab follows a consistent structure:

- **README.md**: Learning objectives, concepts, and instructions
- **starter/**: Starting point for hands-on practice
- **solution/**: Complete working solution
- **Python-language-references.md**: Detailed explanation of Python methods and APIs used

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- New labs or exercises
- Documentation improvements
- Additional examples

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangSmith](https://smith.langchain.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)