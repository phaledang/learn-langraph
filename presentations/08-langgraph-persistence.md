# Lab 08: LangGraph State Persistence

## Learning Focus
- Persist graph checkpoints across runs
- Resume workflows using thread/session identifiers
- Compare in-memory vs durable persistence

## Key Concepts
- Checkpointer lifecycle
- Recovery after interruption
- Thread-scoped state history

## Hands-on Walkthrough
1. Configure a persistence backend
2. Compile graph with checkpointer
3. Run and store checkpoints
4. Resume and verify restored state

## Validation Checklist
- Checkpoints are written successfully
- Resume returns expected state
- Recovery works after process restart

## Resources
- Lab guide: `labs/lab08-langgraph-persistence/README.md`
