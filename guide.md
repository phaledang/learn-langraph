# Learn LangChain, LangGraph, LangSmith & MCP — Guide

A practical guide for setting up, running labs, and testing in this project.

---

## Prerequisites

- **Python 3.9+** installed
- **Git** for version control
- **Azure OpenAI** API access (or OpenAI API key, depending on the lab)
- **VS Code** recommended as the editor

---

## Initial Setup

### 1. Clone and Enter the Project

```bash
git clone https://github.com/phaledang/learn-langraph.git
cd learn-langraph
```

### 2. Create and Activate a Virtual Environment

```bash
# Create
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS / Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all project dependencies
pip install -r requirements.txt

# Or install for a specific lab only
pip install -r labs/lab02-langchain-chains/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the lab's `solution/` folder (or at the project root) with your credentials:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# OpenAI (if using OpenAI directly)
OPENAI_API_KEY=your-openai-api-key

# LangSmith (Labs 09-10)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=your-project-name

# Database (Lab 08 persistence)
DATABASE_CONNECTION_STRING=your-connection-string
```

> **Tip:** Each lab's solution loads `.env` from its own directory via `load_dotenv(Path(__file__).parent / ".env")`. Place a `.env` in each `solution/` folder, or use a single root-level `.env` and adjust paths as needed.

---

## Running Labs

### Run a Lab Solution Directly

Each lab has a `solution/main.py` that can be run as a standalone script:

```bash
# From the project root (with venv activated)
python labs/lab01-langchain-basics/solution/main.py
python labs/lab02-langchain-chains/solution/main.py
python labs/lab05-langgraph-basics/solution/main.py
python labs/lab06-langgraph-stateful/solution/main.py
python labs/lab08-langgraph-persistence/solution/main.py
python labs/lab13-pdf-and_image_to_csv/solution/main.py
```

> **Note:** Running solutions requires live API credentials. Stub labs (03, 04, 07, 09, 10, 11, 12) have placeholder code that won't produce meaningful output until fully implemented.

### Run with the Starter Code

To practice, work in the `starter/` folder and follow the lab's `README.md`:

```bash
python labs/lab02-langchain-chains/starter/main.py
```

---

## Running Tests

All tests use **mocked** API calls — no credentials or live services needed.

### Run All Tests

```bash
pytest
```

### Run Tests for a Specific Lab

```bash
pytest tests/test_lab02_langchain_chains.py -v
```

### Run a Single Test

```bash
pytest tests/test_lab02_langchain_chains.py::test_task1_sequential_chain_structure -v
```

### Run Tests by Keyword

```bash
pytest -k "rag" -v          # all tests with "rag" in the name
pytest -k "lab05 or lab06"  # tests for labs 05 and 06
```

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=labs --cov-report=term-missing
```

### Test Summary

| Test File | Lab | Tests |
|-----------|-----|-------|
| `test_hello.py` | Smoke tests | 13 |
| `test_lab01_langchain_basics.py` | Lab 01 — LangChain Basics | 6 |
| `test_lab02_langchain_chains.py` | Lab 02 — Chains & Prompts | 9 |
| `test_lab03_langchain_agents.py` | Lab 03 — Agents & Tools | 7 |
| `test_lab04_langchain_memory.py` | Lab 04 — Memory Systems | 8 |
| `test_lab05_langgraph_basics.py` | Lab 05 — LangGraph Basics | 10 |
| `test_lab06_langgraph_stateful.py` | Lab 06 — Stateful Apps | 8 |
| `test_lab07_langgraph_multiagent.py` | Lab 07 — Multi-Agent | 9 |
| `test_lab08_langgraph_persistence.py` | Lab 08 — Persistence | 10 |
| `test_lab09_langsmith_tracing.py` | Lab 09 — Tracing | 5 |
| `test_lab10_langsmith_evaluation.py` | Lab 10 — Evaluation | 7 |
| `test_lab11_mcp_integration.py` | Lab 11 — MCP Integration | 5 |
| `test_lab12_mcp_advanced.py` | Lab 12 — MCP Advanced | 6 |
| `test_lab13_pdf_to_csv.py` | Lab 13 — PDF to CSV | 16 |
| `test_lab14_mcp_server.py` | Lab 14 — MCP Server | 4 |
| `test_lab14_mcp_sharepoint.py` | Lab 14 — MCP SharePoint | 12 |

**Total: 107 tests** — all mocked, no live API needed.

---

## Learning Path

### Phase 1: LangChain Fundamentals (Labs 1–4)

| Lab | Topic | Key Concepts |
|-----|-------|-------------|
| 01 | LangChain Basics | Prompt templates, LLM invocation, output parsing |
| 02 | Chains & Prompts | Sequential chains, router chains, RAG with ChromaDB |
| 03 | Agents & Tools | Custom tools, agent executors, tool selection |
| 04 | Memory Systems | Buffer memory, summary memory, conversation history |

### Phase 2: LangGraph (Labs 5–8)

| Lab | Topic | Key Concepts |
|-----|-------|-------------|
| 05 | LangGraph Basics | StateGraph, nodes, edges, conditional routing |
| 06 | Stateful Applications | Multi-step state, message annotations, checkpoints |
| 07 | Multi-Agent Systems | Supervisor pattern, agent communication, collaboration |
| 08 | State Persistence | Cosmos DB, PostgreSQL, SQL Server state backends |

### Phase 3: LangSmith (Labs 9–10)

| Lab | Topic | Key Concepts |
|-----|-------|-------------|
| 09 | Tracing & Monitoring | LangSmith setup, `@trace` decorator, custom metadata |
| 10 | Evaluation & Testing | Datasets, custom evaluators, metrics comparison |

### Phase 4: MCP & Advanced (Labs 11–14)

| Lab | Topic | Key Concepts |
|-----|-------|-------------|
| 11 | MCP Integration | Model Context Protocol, MCP servers, tool exposure |
| 12 | MCP Advanced | Auth, caching, rate limiting, production patterns |
| 13 | PDF & Image to CSV | PDF extraction, OCR, pydantic models, data pipelines |
| 14 | MCP Server / SharePoint | FastAPI MCP server, SharePoint integration, LangGraph workflows |

---

## Project Structure

```
learn-langraph/
├── requirements.txt          # Root dependencies (all labs)
├── pytest.ini                # Test configuration
├── guide.md                  # This file
├── test-guide.md             # Detailed testing guide
├── steps.md                  # Project setup history
├── labs/
│   └── labXX-<topic>/
│       ├── README.md             # Instructions & objectives
│       ├── requirements.txt      # Lab-specific dependencies
│       ├── Python-language-references.md
│       ├── starter/main.py       # Start here for practice
│       └── solution/main.py      # Reference solution
├── tests/
│   ├── conftest.py           # Shared fixtures & path setup
│   └── test_labXX_*.py       # Tests per lab (mocked)
├── shared/
│   └── state_persistence/    # DB adapters (Cosmos, Postgres, SQL Server)
└── presentations/            # Slide decks per topic
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv activated |
| `AZURE_OPENAI_API_KEY not set` | Create a `.env` file in the lab's `solution/` folder |
| Tests skip with `SKIPPED` | Some tests use `pytest.importorskip()` for optional packages — install them to unskip |
| `429 Request Rate Too Large` | You're hitting API rate limits — wait and retry, or reduce concurrent calls |
| ChromaDB errors | Run `pip install chromadb>=0.4.0` |
| Lab 13 skips | Install `pandas`, `pypdf`, and `pillow` |

---

## Useful Commands Quick Reference

```bash
# Activate venv
.\venv\Scripts\Activate.ps1          # Windows PowerShell
source venv/bin/activate              # macOS / Linux

# Install everything
pip install -r requirements.txt

# Run a lab
python labs/lab02-langchain-chains/solution/main.py

# Run all tests
pytest

# Run one lab's tests
pytest tests/test_lab02_langchain_chains.py -v

# Run tests matching a keyword
pytest -k "sequential" -v

# Check installed packages
pip list | findstr langchain         # Windows
pip list | grep langchain            # macOS / Linux
```
