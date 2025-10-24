# Lab 08: LangGraph State Persistence

## Learning Objectives
- Understand state persistence in LangGraph
- Integrate with multiple database backends
- Implement checkpointing for long-running workflows
- Resume workflows from saved state
- Handle state versioning

## Prerequisites
- Completion of Labs 01-07
- Understanding of LangGraph basics
- Database connection (PostgreSQL, SQL Server, or Cosmos DB)

## Lab Overview
In this lab, you will:
1. Configure database connection
2. Implement state checkpointing
3. Save and load graph state
4. Resume interrupted workflows
5. Build a persistent conversational agent

## Setup

### Database Configuration
This lab supports three database types:

1. **PostgreSQL** (Recommended for development)
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
   ```
   Connection string:
   ```
   DATABASE_CONNECTION_STRING=postgresql://postgres:postgres@localhost:5432/langraph_db
   ```

2. **SQL Server**
   Connection string:
   ```
   DATABASE_CONNECTION_STRING=mssql+pyodbc://user:password@server:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server
   ```

3. **Azure Cosmos DB**
   Connection string:
   ```
   DATABASE_CONNECTION_STRING=AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key;
   ```

Add your chosen connection string to `.env` file.

## Tasks

### Task 1: Initialize State Persistence
Set up the database connection and initialize tables.

### Task 2: Create Checkpointed Graph
Build a graph that saves state at each step.

### Task 3: Save and Load State
Implement checkpoint saving and loading.

### Task 4: Resume Workflow
Resume a workflow from a saved checkpoint.

### Task 5: Build Persistent Agent
Create a conversational agent that maintains state across sessions.

## Expected Outcomes
- Understand state persistence mechanisms
- Implement database-backed checkpointing
- Handle workflow interruptions gracefully
- Build stateful applications

## Resources
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [State Persistence Module](../../shared/state_persistence/)

## Next Steps
Proceed to **Lab 09: LangSmith Tracing** to learn about monitoring and debugging.
