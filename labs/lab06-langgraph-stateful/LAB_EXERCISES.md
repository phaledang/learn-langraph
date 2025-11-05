# Lab 06: LangGraph Stateful Applications - Exercise Guide

## 🎯 Learning Objectives
By completing this lab, you will learn to:
- Build complex stateful workflows with LangGraph
- Implement human-in-the-loop interactions
- Use persistent checkpointing for workflow recovery
- Handle parallel node execution
- Create advanced routing logic
- Build production-ready approval systems

## 🚀 Getting Started

### Prerequisites
1. Complete Labs 01-05
2. Understanding of Python typing and async concepts
3. Basic LangGraph knowledge

### Setup
1. Navigate to `lab06-langgraph-stateful`
2. Copy `.env.template` to `.env` and add your OpenAI API key
3. Install dependencies: `pip install -r requirements.txt`
4. Run starter code: `python starter/main.py`

## 📚 Exercise Steps

### Exercise 1: Basic State Management (15 minutes)

**Objective:** Create a simple stateful workflow that tracks document processing.

**Tasks:**
1. Complete the `WorkflowState` TypedDict with required fields
2. Implement `initialize_workflow()` to set initial state
3. Create `analyze_document()` that uses LLM to analyze content
4. Test basic state flow

**Key Concepts:**
- TypedDict for state schema
- State immutability patterns
- LLM integration

**Solution Check:**
```python
# Should work after completion
state = initialize_workflow({})
print(state["current_step"])  # Should print "initialized"
```

### Exercise 2: Graph Construction (20 minutes)

**Objective:** Build a StateGraph with nodes and edges.

**Tasks:**
1. Complete `create_stateful_workflow()` function
2. Add all nodes to the graph
3. Connect nodes with edges
4. Test graph compilation

**Key Concepts:**
- StateGraph initialization
- Node addition
- Edge connections
- Graph compilation

**Solution Check:**
```python
# Should compile without errors
workflow = create_stateful_workflow()
app = workflow.compile()
print("Graph compiled successfully!")
```

### Exercise 3: Conditional Routing (25 minutes)

**Objective:** Implement dynamic routing based on state conditions.

**Tasks:**
1. Complete routing functions (`should_request_approval`, etc.)
2. Add conditional edges to the graph
3. Test different routing paths
4. Handle edge cases

**Key Concepts:**
- Conditional edge logic
- State-based routing
- Literal return types
- Decision trees

**Solution Check:**
```python
# Test routing logic
state = {"approval_status": "needs_revision"}
route = approval_decision_router(state)
print(route)  # Should print "revision"
```

### Exercise 4: Human-in-the-Loop (30 minutes)

**Objective:** Create interruption points for human input.

**Tasks:**
1. Implement `request_human_approval()` with interruption logic
2. Complete `process_approval_decision()` to handle human input
3. Add human input tracking to state
4. Test interruption and resumption

**Key Concepts:**
- Workflow interruption
- Human input integration
- State persistence during pauses
- Resumption logic

**Solution Check:**
```python
# Should set human_input_required flag
state = request_human_approval({})
print(state["human_input_required"])  # Should be True
```

### Exercise 5: Parallel Processing (35 minutes)

**Objective:** Implement parallel analysis nodes with result merging.

**Tasks:**
1. Complete parallel analysis functions (quality, compliance, security)
2. Implement `merge_parallel_results()` to combine outputs
3. Add parallel nodes to graph structure
4. Test concurrent processing simulation

**Key Concepts:**
- Parallel node execution
- Result aggregation
- State management across parallel branches
- Coordination patterns

**Solution Check:**
```python
# Should have multiple analysis results
state = {"parallel_results": {}}
state = parallel_analysis_quality(state)
state = parallel_analysis_compliance(state)
print(len(state["parallel_results"]))  # Should be 2
```

### Exercise 6: Document Approval System (40 minutes)

**Objective:** Build a complete multi-level approval workflow.

**Tasks:**
1. Complete `DocumentApprovalState` schema
2. Implement document approval nodes
3. Create approval chain logic
4. Test multi-level approval process

**Key Concepts:**
- Specialized state schemas
- Multi-step approval chains
- Approval tracking
- Status management

**Solution Check:**
```python
# Should process approval chain
doc_state = {"approval_chain": ["reviewer", "manager"]}
doc_state = approve_document(doc_state)
print(doc_state["current_approver"])  # Should be "manager"
```

### Exercise 7: Checkpointing and Persistence (30 minutes)

**Objective:** Add state persistence and recovery capabilities.

**Tasks:**
1. Configure MemorySaver for checkpointing
2. Implement checkpoint-enabled execution
3. Add state recovery logic
4. Test workflow resumption

**Key Concepts:**
- Checkpoint configuration
- State persistence
- Recovery mechanisms
- Thread-based execution

**Solution Check:**
```python
# Should save and restore state
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "test"}}
# Execute and check state persistence
```

### Exercise 8: Error Handling and Recovery (25 minutes)

**Objective:** Add robust error handling with automatic recovery.

**Tasks:**
1. Add try-catch blocks to node functions
2. Implement error state tracking
3. Create recovery logic
4. Test failure scenarios

**Key Concepts:**
- Exception handling
- Error state management
- Graceful degradation
- Recovery strategies

**Solution Check:**
```python
# Should handle errors gracefully
try:
    result = app.invoke(invalid_state, config)
except Exception as e:
    print(f"Handled error: {e}")
```

## 🧪 Testing Your Implementation

### Unit Tests
Run individual components:
```python
# Test state initialization
state = initialize_workflow({})
assert state["current_step"] == "initialized"

# Test routing logic
route = approval_decision_router({"approval_status": "approved"})
assert route == "approved"

# Test parallel processing
state = parallel_analysis_quality({})
assert "parallel_results" in state
```

### Integration Tests
Test complete workflows:
```python
# Test full workflow execution
result = run_stateful_workflow_demo()
assert result["current_step"] == "completed"

# Test document approval
doc_result = run_document_approval_demo()
assert doc_result["status"] in ["approved", "rejected"]

# Test checkpointing
demonstrate_checkpointing()  # Should not raise exceptions
```

### Performance Tests
Check execution efficiency:
```python
import time

start = time.time()
result = app.invoke(initial_state, config)
duration = time.time() - start
print(f"Execution time: {duration:.2f}s")
```

## 🎯 Success Criteria

Your implementation should:

### ✅ Basic Requirements
- [ ] All TypedDict schemas properly defined
- [ ] All node functions implemented and working
- [ ] Graph compiles without errors
- [ ] Basic workflow executes successfully

### ✅ Intermediate Features
- [ ] Conditional routing works correctly
- [ ] Human-in-the-loop interruptions function
- [ ] Parallel processing nodes execute
- [ ] State persistence configured

### ✅ Advanced Features
- [ ] Document approval system complete
- [ ] Checkpointing and recovery working
- [ ] Error handling implemented
- [ ] All demos run successfully

### ✅ Code Quality
- [ ] Type hints used throughout
- [ ] Proper error handling
- [ ] Clear documentation
- [ ] Consistent coding style

## 🚀 Extension Challenges

### Challenge 1: Advanced Routing
Implement more complex routing logic:
- Multi-condition routing
- Weighted decision making
- Dynamic approval chains

### Challenge 2: Enhanced Checkpointing
Add advanced persistence features:
- File-based checkpointing
- State versioning
- Backup and restore

### Challenge 3: Real-time Integration
Connect to external systems:
- Database integration
- API callbacks
- Real-time notifications

### Challenge 4: Performance Optimization
Optimize for production use:
- Async execution
- Resource management
- Scalability improvements

## 📖 Additional Resources

### Documentation
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain State Management](https://python.langchain.com/docs/guides/state/)
- [Python TypedDict Guide](https://docs.python.org/3/library/typing.html#typing.TypedDict)

### Examples
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Human-in-the-Loop Patterns](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)
- [Checkpointing Guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)

## 🎉 Completion

Congratulations! You've built a comprehensive stateful workflow system with:
- Complex state management
- Human-in-the-loop interactions
- Parallel processing capabilities
- Persistent checkpointing
- Production-ready error handling

**Next Steps:** Proceed to Lab 07: LangGraph Multi-Agent to learn about coordinating multiple AI agents in complex workflows.