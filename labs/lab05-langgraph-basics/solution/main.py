"""
Lab 05: LangGraph Basics - Solution Code

Complete implementation of LangGraph basics including state management,
nodes, edges, and conditional routing.
"""

import os
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

load_dotenv()


# Task 1: Define State Schema
class AgentState(TypedDict):
    """State schema for our graph."""
    messages: list  # Conversation history
    step: int  # Current step number
    user_input: str  # User's query
    result: str  # Final result
    iterations: int  # Number of iterations


# Task 2: Create Node Functions
def process_input(state: AgentState) -> AgentState:
    """Process and validate user input."""
    print(f"\n[Step {state['step']}] Processing input...")
    
    # Simulate input processing
    user_input = state.get("user_input", "")
    
    state["messages"].append(HumanMessage(content=user_input))
    state["step"] += 1
    
    print(f"  User input: {user_input}")
    return state


def generate_response(state: AgentState) -> AgentState:
    """Generate LLM response."""
    print(f"\n[Step {state['step']}] Generating response...")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Get last user message
    user_message = state["messages"][-1]
    
    # Generate response
    response = llm.invoke([user_message])
    
    state["messages"].append(AIMessage(content=response.content))
    state["result"] = response.content
    state["step"] += 1
    
    print(f"  Generated response (preview): {response.content[:100]}...")
    return state


def validate_response(state: AgentState) -> AgentState:
    """Validate the generated response."""
    print(f"\n[Step {state['step']}] Validating response...")
    
    result = state.get("result", "")
    
    # Simple validation: check if response is not empty and has reasonable length
    if len(result) > 20:
        print("  ✓ Response validated successfully")
    else:
        print("  ⚠ Response might be too short")
    
    state["step"] += 1
    state["iterations"] = state.get("iterations", 0) + 1
    
    return state


def should_continue(state: AgentState) -> Literal["generate_response", "end"]:
    """
    Determine if we should continue processing or end.
    
    This is a conditional routing function.
    """
    iterations = state.get("iterations", 0)
    result = state.get("result", "")
    
    # Continue if we haven't iterated enough or result is empty
    if iterations < 1 and len(result) < 20:
        print("\n[Routing] Continuing to generate_response...")
        return "generate_response"
    else:
        print("\n[Routing] Ending workflow...")
        return "end"


def format_output(state: AgentState) -> AgentState:
    """Format the final output."""
    print(f"\n[Step {state['step']}] Formatting output...")
    
    result = state.get("result", "No result generated")
    state["result"] = f"Final Answer:\n{result}"
    state["step"] += 1
    
    return state


# Task 3 & 4: Build the Graph with Conditional Edges
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
    
    # Add edges
    workflow.add_edge("process_input", "generate_response")
    workflow.add_edge("generate_response", "validate_response")
    
    # Add conditional edge
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
    
    # Compile the graph
    return workflow.compile()


def demonstrate_simple_graph():
    """Demonstrate a simple linear graph."""
    print("\n" + "="*80)
    print("DEMONSTRATION 1: Simple Linear Graph")
    print("="*80)
    
    class SimpleState(TypedDict):
        input: str
        output: str
        count: int
    
    def step1(state: SimpleState) -> SimpleState:
        print("→ Step 1: Receive input")
        state["count"] = 1
        return state
    
    def step2(state: SimpleState) -> SimpleState:
        print("→ Step 2: Process input")
        state["count"] = 2
        return state
    
    def step3(state: SimpleState) -> SimpleState:
        print("→ Step 3: Generate output")
        state["output"] = f"Processed: {state['input']}"
        state["count"] = 3
        return state
    
    # Build simple graph
    simple_workflow = StateGraph(SimpleState)
    simple_workflow.add_node("step1", step1)
    simple_workflow.add_node("step2", step2)
    simple_workflow.add_node("step3", step3)
    
    simple_workflow.set_entry_point("step1")
    simple_workflow.add_edge("step1", "step2")
    simple_workflow.add_edge("step2", "step3")
    simple_workflow.add_edge("step3", END)
    
    simple_app = simple_workflow.compile()
    
    # Run simple graph
    result = simple_app.invoke({"input": "Hello LangGraph!", "output": "", "count": 0})
    print(f"\nResult: {result}")


def demonstrate_conditional_graph():
    """Demonstrate a graph with conditional routing."""
    print("\n" + "="*80)
    print("DEMONSTRATION 2: Conditional Graph")
    print("="*80)
    
    class ConditionalState(TypedDict):
        number: int
        is_even: bool
        message: str
    
    def check_number(state: ConditionalState) -> ConditionalState:
        print(f"→ Checking if {state['number']} is even...")
        state["is_even"] = state["number"] % 2 == 0
        return state
    
    def even_handler(state: ConditionalState) -> ConditionalState:
        print("→ Even number handler")
        state["message"] = f"{state['number']} is even!"
        return state
    
    def odd_handler(state: ConditionalState) -> ConditionalState:
        print("→ Odd number handler")
        state["message"] = f"{state['number']} is odd!"
        return state
    
    def route_number(state: ConditionalState) -> Literal["even", "odd"]:
        return "even" if state["is_even"] else "odd"
    
    # Build conditional graph
    conditional_workflow = StateGraph(ConditionalState)
    conditional_workflow.add_node("check", check_number)
    conditional_workflow.add_node("even_handler", even_handler)
    conditional_workflow.add_node("odd_handler", odd_handler)
    
    conditional_workflow.set_entry_point("check")
    conditional_workflow.add_conditional_edges(
        "check",
        route_number,
        {
            "even": "even_handler",
            "odd": "odd_handler"
        }
    )
    conditional_workflow.add_edge("even_handler", END)
    conditional_workflow.add_edge("odd_handler", END)
    
    conditional_app = conditional_workflow.compile()
    
    # Test with different numbers
    for num in [4, 7, 10]:
        print(f"\n--- Testing with {num} ---")
        result = conditional_app.invoke({
            "number": num,
            "is_even": False,
            "message": ""
        })
        print(f"Result: {result['message']}")


# Task 5: Main execution
def main():
    """Run all demonstrations."""
    print("="*80)
    print("LAB 05: LangGraph Basics - Solution")
    print("="*80)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nNote: OPENAI_API_KEY not set. Skipping LLM demonstrations.")
        print("Simple demonstrations will still run.\n")
    
    # Demonstrate simple graph
    demonstrate_simple_graph()
    
    # Demonstrate conditional graph
    demonstrate_conditional_graph()
    
    # Demonstrate full agent with LLM (if API key available)
    if os.getenv("OPENAI_API_KEY"):
        print("\n" + "="*80)
        print("DEMONSTRATION 3: Full Agent with LLM")
        print("="*80)
        
        app = create_graph()
        
        # Test the complete agent
        initial_state = {
            "messages": [],
            "step": 1,
            "user_input": "Explain what LangGraph is in one paragraph.",
            "result": "",
            "iterations": 0
        }
        
        final_state = app.invoke(initial_state)
        
        print("\n" + "="*80)
        print("FINAL RESULT")
        print("="*80)
        print(f"\n{final_state['result']}")
        print(f"\nTotal steps: {final_state['step']}")
        print(f"Total iterations: {final_state['iterations']}")
    
    print("\n" + "="*80)
    print("LAB 05 COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
