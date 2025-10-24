"""
Lab 08: LangGraph State Persistence - Solution Code

Complete implementation of state persistence with database backend.
Demonstrates saving and resuming graph state across sessions.
"""

import os
import asyncio
from typing import TypedDict, Annotated
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END, add_messages

# Import our custom state persistence module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from shared.state_persistence import create_state_persistence

load_dotenv()


# Task 2: Define State Schema
class ConversationState(TypedDict):
    """State schema for conversational agent."""
    messages: Annotated[list[BaseMessage], add_messages]  # Using add_messages reducer
    thread_id: str
    step: int
    summary: str


# Node functions
def process_message(state: ConversationState) -> ConversationState:
    """Process incoming message."""
    print(f"\n[Step {state['step']}] Processing message...")
    state["step"] += 1
    return state


def generate_response(state: ConversationState) -> ConversationState:
    """Generate AI response using LLM."""
    print(f"[Step {state['step']}] Generating response...")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Get conversation history
    messages = state["messages"]
    
    # Generate response
    response = llm.invoke(messages)
    
    # Add to messages (add_messages will handle this automatically)
    state["messages"] = [response]
    state["step"] += 1
    
    print(f"  AI: {response.content[:100]}...")
    return state


def update_summary(state: ConversationState) -> ConversationState:
    """Update conversation summary."""
    print(f"[Step {state['step']}] Updating summary...")
    
    message_count = len(state["messages"])
    state["summary"] = f"Conversation with {message_count} messages"
    state["step"] += 1
    
    return state


# Task 3: Create the Graph
def create_persistent_graph():
    """Create a graph for conversational agent."""
    
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("process", process_message)
    workflow.add_node("generate", generate_response)
    workflow.add_node("summarize", update_summary)
    
    # Add edges
    workflow.set_entry_point("process")
    workflow.add_edge("process", "generate")
    workflow.add_edge("generate", "summarize")
    workflow.add_edge("summarize", END)
    
    return workflow.compile()


# Task 4: Save and Load Functions
async def save_checkpoint(persistence, thread_id: str, state: dict, checkpoint_id: str):
    """Save a checkpoint to the database."""
    print(f"\n💾 Saving checkpoint '{checkpoint_id}' for thread '{thread_id}'...")
    
    success = await persistence.save_state(
        thread_id=thread_id,
        checkpoint_id=checkpoint_id,
        state=state,
        metadata={
            "saved_at": datetime.utcnow().isoformat(),
            "step": state.get("step", 0)
        }
    )
    
    if success:
        print(f"✓ Checkpoint saved successfully!")
    else:
        print(f"✗ Failed to save checkpoint")
    
    return success


async def load_checkpoint(persistence, thread_id: str, checkpoint_id: str = None):
    """Load a checkpoint from the database."""
    print(f"\n📂 Loading checkpoint for thread '{thread_id}'...")
    
    state_doc = await persistence.load_state(
        thread_id=thread_id,
        checkpoint_id=checkpoint_id
    )
    
    if state_doc:
        print(f"✓ Checkpoint loaded: {state_doc.checkpoint_id}")
        print(f"  Created: {state_doc.created_at}")
        print(f"  Messages: {len(state_doc.state.get('messages', []))}")
        return state_doc.state
    else:
        print(f"✗ No checkpoint found")
        return None


async def list_all_checkpoints(persistence, thread_id: str):
    """List all checkpoints for a thread."""
    print(f"\n📋 Listing checkpoints for thread '{thread_id}'...")
    
    checkpoints = await persistence.list_checkpoints(thread_id=thread_id, limit=10)
    
    if checkpoints:
        print(f"\nFound {len(checkpoints)} checkpoint(s):")
        for i, cp in enumerate(checkpoints, 1):
            print(f"  {i}. {cp.checkpoint_id}")
            print(f"     Created: {cp.created_at}")
            print(f"     Step: {cp.metadata.get('step', 'N/A')}")
    else:
        print("No checkpoints found")
    
    return checkpoints


# Task 5: Demonstration Functions
async def demo_basic_persistence():
    """Demonstrate basic save/load functionality."""
    print("\n" + "="*80)
    print("DEMO 1: Basic State Persistence")
    print("="*80)
    
    # Initialize persistence
    persistence = create_state_persistence()
    await persistence.initialize()
    
    thread_id = "demo_conversation_1"
    
    # Create initial state
    initial_state = {
        "messages": [],
        "thread_id": thread_id,
        "step": 0,
        "summary": ""
    }
    
    # Save checkpoint 1
    await save_checkpoint(
        persistence,
        thread_id,
        initial_state,
        "checkpoint_001"
    )
    
    # Update state
    updated_state = {
        **initial_state,
        "step": 1,
        "summary": "Started conversation"
    }
    
    # Save checkpoint 2
    await save_checkpoint(
        persistence,
        thread_id,
        updated_state,
        "checkpoint_002"
    )
    
    # List all checkpoints
    await list_all_checkpoints(persistence, thread_id)
    
    # Load specific checkpoint
    loaded_state = await load_checkpoint(persistence, thread_id, "checkpoint_001")
    print(f"\nLoaded state: {loaded_state}")
    
    # Load latest checkpoint
    latest_state = await load_checkpoint(persistence, thread_id)
    print(f"\nLatest state: {latest_state}")
    
    await persistence.close()


async def demo_conversational_agent():
    """Demonstrate persistent conversational agent."""
    print("\n" + "="*80)
    print("DEMO 2: Persistent Conversational Agent")
    print("="*80)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\nSkipping: OPENAI_API_KEY not set")
        return
    
    # Initialize persistence
    persistence = create_state_persistence()
    await persistence.initialize()
    
    # Create graph
    app = create_persistent_graph()
    
    thread_id = "user_conversation_123"
    
    # Conversation turns
    user_messages = [
        "Hello! Can you explain what LangGraph is?",
        "How is it different from regular LangChain?",
        "Can you give me an example use case?"
    ]
    
    for i, user_msg in enumerate(user_messages):
        checkpoint_id = f"turn_{i+1}"
        
        print(f"\n{'='*80}")
        print(f"TURN {i+1}")
        print(f"{'='*80}")
        print(f"User: {user_msg}\n")
        
        # Load previous state or create new
        if i == 0:
            state = {
                "messages": [HumanMessage(content=user_msg)],
                "thread_id": thread_id,
                "step": 0,
                "summary": ""
            }
        else:
            # Load previous state
            prev_state = await load_checkpoint(persistence, thread_id)
            if prev_state:
                # Convert message dicts back to objects if needed
                messages = prev_state.get("messages", [])
                if messages and isinstance(messages[0], dict):
                    messages = [
                        HumanMessage(content=m["content"]) if m["type"] == "human"
                        else AIMessage(content=m["content"])
                        for m in messages
                    ]
                
                state = {
                    **prev_state,
                    "messages": messages + [HumanMessage(content=user_msg)],
                    "step": prev_state.get("step", 0)
                }
            else:
                state = {
                    "messages": [HumanMessage(content=user_msg)],
                    "thread_id": thread_id,
                    "step": 0,
                    "summary": ""
                }
        
        # Run graph
        result = app.invoke(state)
        
        # Save checkpoint
        # Convert messages to serializable format
        serializable_state = {
            **result,
            "messages": [
                {"type": "human" if isinstance(m, HumanMessage) else "ai", "content": m.content}
                for m in result["messages"]
            ]
        }
        
        await save_checkpoint(
            persistence,
            thread_id,
            serializable_state,
            checkpoint_id
        )
        
        print(f"\n✓ Turn {i+1} completed and saved")
    
    # Show final conversation history
    print("\n" + "="*80)
    print("CONVERSATION HISTORY")
    print("="*80)
    
    await list_all_checkpoints(persistence, thread_id)
    
    # Load final state
    final_state = await load_checkpoint(persistence, thread_id)
    if final_state:
        print(f"\nFinal summary: {final_state['summary']}")
        print(f"Total steps: {final_state['step']}")
    
    await persistence.close()


async def demo_resume_workflow():
    """Demonstrate resuming an interrupted workflow."""
    print("\n" + "="*80)
    print("DEMO 3: Resume Interrupted Workflow")
    print("="*80)
    
    persistence = create_state_persistence()
    await persistence.initialize()
    
    thread_id = "workflow_resume_demo"
    
    # Simulate a workflow that gets interrupted
    print("\n--- Starting workflow ---")
    
    state = {
        "messages": [],
        "thread_id": thread_id,
        "step": 0,
        "summary": "Processing started"
    }
    
    # Save at step 0
    await save_checkpoint(persistence, thread_id, state, "step_0")
    
    # Simulate progress
    for step in range(1, 4):
        state["step"] = step
        state["summary"] = f"Completed step {step}"
        await save_checkpoint(persistence, thread_id, state, f"step_{step}")
        print(f"  ✓ Step {step} completed")
    
    print("\n--- Simulating interruption ---")
    print("Workflow interrupted at step 3!")
    
    print("\n--- Resuming workflow ---")
    
    # Resume from last checkpoint
    resumed_state = await load_checkpoint(persistence, thread_id)
    
    if resumed_state:
        print(f"Resumed from: {resumed_state['summary']}")
        print(f"Continuing from step {resumed_state['step']}...")
        
        # Continue workflow
        for step in range(resumed_state['step'] + 1, 6):
            resumed_state["step"] = step
            resumed_state["summary"] = f"Completed step {step}"
            await save_checkpoint(persistence, thread_id, resumed_state, f"step_{step}")
            print(f"  ✓ Step {step} completed")
        
        print("\n✓ Workflow completed successfully!")
    
    await persistence.close()


async def main():
    """Run all demonstrations."""
    print("="*80)
    print("LAB 08: LangGraph State Persistence - Solution")
    print("="*80)
    
    # Check database connection
    if not os.getenv("DATABASE_CONNECTION_STRING"):
        print("\n⚠ WARNING: DATABASE_CONNECTION_STRING not set in .env")
        print("Please configure a database connection to run this lab.")
        print("\nSupported databases:")
        print("  - PostgreSQL: postgresql://user:pass@localhost:5432/dbname")
        print("  - SQL Server: mssql+pyodbc://user:pass@server:1433/dbname?driver=...")
        print("  - Cosmos DB: AccountEndpoint=...;AccountKey=...;")
        return
    
    try:
        # Run demonstrations
        await demo_basic_persistence()
        await demo_conversational_agent()
        await demo_resume_workflow()
        
        print("\n" + "="*80)
        print("LAB 08 COMPLETE!")
        print("="*80)
        print("\nKey Takeaways:")
        print("  ✓ State can be persisted to multiple database types")
        print("  ✓ Checkpoints enable workflow resumption")
        print("  ✓ Conversation history is maintained across sessions")
        print("  ✓ The system automatically detects database type")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  - Database connection string is correct")
        print("  - Database server is running and accessible")
        print("  - Required dependencies are installed")


if __name__ == "__main__":
    asyncio.run(main())
