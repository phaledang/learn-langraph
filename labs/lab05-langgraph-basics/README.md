# Lab 05: LangGraph Basics

## Learning Objectives
- Understand LangGraph architecture
- Create state graphs with nodes and edges
- Implement conditional routing
- Build cyclic workflows
- Manage state across graph execution

## Prerequisites
- Completion of Labs 01-04
- Understanding of LangChain concepts
- Familiarity with state management

## Lab Overview
In this lab, you will:
1. Create a simple state graph
2. Add nodes with processing logic
3. Implement conditional edges
4. Build a cyclic workflow
5. Create a multi-step agent

## Step-by-Step Instructions

### Task 1: Define State Schema
**Objective**: Create a typed state dictionary that will be passed between graph nodes.

**Steps**:
1. Import required modules:
   ```python
   from typing import TypedDict, Literal
   from langgraph.graph import StateGraph, END
   from langchain_openai import ChatOpenAI
   ```

2. Define the state schema:
   ```python
   class AgentState(TypedDict):
       """State schema for our graph."""
       messages: list  # Conversation history
       step: int  # Current step number
       user_input: str  # User's query
       result: str  # Final result
       iterations: int  # Number of iterations
   ```

**Expected Result**: A strongly-typed state that ensures consistency across nodes:
```
State Schema Defined: AgentState with 5 fields
✓ Type safety enabled for graph execution
```

### Task 2: Create Processing Nodes
**Objective**: Build functions that modify state and represent processing steps.

**Steps**:
1. Create input processing node:
   ```python
   def process_input(state: AgentState) -> AgentState:
       """Process and validate user input."""
       print(f"\n[Step {state['step']}] Processing input...")
       
       user_input = state.get("user_input", "")
       state["messages"].append(HumanMessage(content=user_input))
       state["step"] += 1
       
       print(f"  User input: {user_input}")
       return state
   ```

2. Create response generation node:
   ```python
   def generate_response(state: AgentState) -> AgentState:
       """Generate LLM response."""
       print(f"\n[Step {state['step']}] Generating response...")
       
       llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
       user_message = state["messages"][-1]
       response = llm.invoke([user_message])
       
       state["messages"].append(AIMessage(content=response.content))
       state["result"] = response.content
       state["step"] += 1
       
       return state
   ```

3. Create validation node:
   ```python
   def validate_response(state: AgentState) -> AgentState:
       """Validate the generated response."""
       print(f"\n[Step {state['step']}] Validating response...")
       
       result = state.get("result", "")
       if len(result) > 20:
           print("  ✓ Response validated successfully")
       else:
           print("  ⚠ Response might be too short")
       
       state["step"] += 1
       state["iterations"] = state.get("iterations", 0) + 1
       return state
   ```

**Expected Result**: Three functional nodes that process state:
```
[Step 1] Processing input...
  User input: Hello, how are you?

[Step 2] Generating response...
  Generated response: I'm doing well, thank you for asking!

[Step 3] Validating response...
  ✓ Response validated successfully
```

### Task 3: Add Regular and Conditional Edges
**Objective**: Connect nodes with both fixed and conditional routing logic.

**Steps**:
1. Create conditional routing function:
   ```python
   def should_continue(state: AgentState) -> Literal["generate_response", "end"]:
       """Determine if we should continue processing or end."""
       iterations = state.get("iterations", 0)
       result = state.get("result", "")
       
       if iterations < 1 and len(result) < 20:
           print("\n[Routing] Continuing to generate_response...")
           return "generate_response"
       else:
           print("\n[Routing] Ending workflow...")
           return "end"
   ```

2. Create output formatting node:
   ```python
   def format_output(state: AgentState) -> AgentState:
       """Format the final output."""
       print(f"\n[Step {state['step']}] Formatting output...")
       
       result = state.get("result", "No result generated")
       state["result"] = f"Final Answer:\n{result}"
       state["step"] += 1
       return state
   ```

**Expected Result**: Routing logic that can loop or terminate:
```
[Routing] Continuing to generate_response...  # If more processing needed
[Routing] Ending workflow...                   # If processing complete
```

### Task 4: Build the Complete Graph
**Objective**: Assemble all components into a working graph with cycles.

**Steps**:
1. Create the graph structure:
   ```python
   def create_graph():
       """Create and return the compiled graph."""
       
       # Initialize graph with state schema
       workflow = StateGraph(AgentState)
       
       # Add nodes
       workflow.add_node("process_input", process_input)
       workflow.add_node("generate_response", generate_response)
       workflow.add_node("validate_response", validate_response)
       workflow.add_node("format_output", format_output)
       
       # Set entry point
       workflow.set_entry_point("process_input")
       
       # Add regular edges
       workflow.add_edge("process_input", "generate_response")
       workflow.add_edge("generate_response", "validate_response")
       
       # Add conditional edge (creates potential loop)
       workflow.add_conditional_edges(
           "validate_response",
           should_continue,
           {
               "generate_response": "generate_response",  # Loop back
               "end": "format_output"  # Move to formatting
           }
       )
       
       # Set finish point
       workflow.add_edge("format_output", END)
       
       return workflow.compile()
   ```

2. Test the graph:
   ```python
   app = create_graph()
   
   initial_state = {
       "messages": [],
       "step": 1,
       "user_input": "What is artificial intelligence?",
       "result": "",
       "iterations": 0
   }
   
   result = app.invoke(initial_state)
   ```

**Expected Result**: A complete graph execution with potential loops:
```
[Step 1] Processing input...
  User input: What is artificial intelligence?

[Step 2] Generating response...
  Generated response: Artificial intelligence (AI) refers to...

[Step 3] Validating response...
  ✓ Response validated successfully

[Routing] Ending workflow...

[Step 4] Formatting output...

Final Result: {
  "result": "Final Answer:\nArtificial intelligence (AI) refers to...",
  "step": 5,
  "iterations": 1
}
```

### Task 5: Create Advanced Graph Examples
**Objective**: Build additional examples showing different graph patterns.

**Steps**:
1. Simple linear graph:
   ```python
   def demonstrate_simple_graph():
       """Demonstrate a simple linear graph."""
       
       class SimpleState(TypedDict):
           input: str
           output: str
           count: int
       
       def step1(state: SimpleState) -> SimpleState:
           print("→ Step 1: Receive input")
           state["count"] = 1
           return state
       
       simple_workflow = StateGraph(SimpleState)
       simple_workflow.add_node("step1", step1)
       simple_workflow.add_node("step2", step2)
       simple_workflow.add_node("step3", step3)
       
       simple_workflow.set_entry_point("step1")
       simple_workflow.add_edge("step1", "step2")
       simple_workflow.add_edge("step2", "step3")
       simple_workflow.add_edge("step3", END)
       
       app = simple_workflow.compile()
       result = app.invoke({"input": "Hello!", "output": "", "count": 0})
   ```

2. Conditional routing graph:
   ```python
   def demonstrate_conditional_graph():
       """Demonstrate conditional routing based on state."""
       
       class ConditionalState(TypedDict):
           number: int
           is_even: bool
           result: str
       
       def check_even_odd(state: ConditionalState) -> Literal["even_path", "odd_path"]:
           if state["number"] % 2 == 0:
               return "even_path"
           else:
               return "odd_path"
       
       # Build conditional graph...
   ```

**Expected Result**: Multiple graph patterns demonstrating flexibility:
```
=== Simple Linear Graph ===
→ Step 1: Receive input
→ Step 2: Process input  
→ Step 3: Generate output
Result: {"input": "Hello!", "output": "Processed: Hello!", "count": 3}

=== Conditional Graph ===
Input: 42
→ Checking if even or odd...
→ Taking even path
Result: "42 is an even number"
```

## Expected Outcomes
- Understand graph-based workflows
- Implement stateful applications
- Use conditional logic in graphs
- Build iterative processes

**Complete Program Output**:
When you run the complete lab, you should see structured graph execution:

```
=== Lab 05: LangGraph Basics ===

Task 1: State Schema Definition
✓ AgentState schema created with typed fields
✓ Type safety enabled for graph execution

Task 2: Node Creation  
✓ process_input node created
✓ generate_response node created
✓ validate_response node created
✓ format_output node created

Task 3: Graph Assembly
✓ Regular edges added
✓ Conditional edges configured
✓ Entry and exit points set

Task 4: Graph Execution
[Step 1] Processing input...
  User input: What is artificial intelligence?

[Step 2] Generating response...
  Generated response (preview): Artificial intelligence (AI) refers to the simulation of human intelligence...

[Step 3] Validating response...
  ✓ Response validated successfully

[Routing] Ending workflow...

[Step 4] Formatting output...

Final Answer:
Artificial intelligence (AI) refers to the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction.

Task 5: Advanced Examples

=== Simple Linear Graph ===
→ Step 1: Receive input
→ Step 2: Process input
→ Step 3: Generate output
Result: Processed: Hello LangGraph!

=== Conditional Graph ===
Input number: 42
→ Checking if even or odd...
→ Number is even, taking even path
→ Processing even number: 42
Result: 42 is an even number and can be divided by 2

Input number: 17  
→ Checking if even or odd...
→ Number is odd, taking odd path
→ Processing odd number: 17
Result: 17 is an odd number

=== Lab 05 Complete! ===
```

## Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [State Management Guide](https://langchain-ai.github.io/langgraph/concepts/)

## Next Steps
Proceed to **Lab 06: LangGraph Stateful Applications** for advanced patterns.
