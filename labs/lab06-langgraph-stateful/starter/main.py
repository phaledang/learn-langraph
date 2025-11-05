"""
LangGraph Stateful Applications - Starter Code

Complete the TODOs to implement this lab.
"""

import os
from typing import TypedDict, Annotated, List, Dict, Any
from typing_extensions import Literal
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


# TODO: Step 1 - Define State Schema
class WorkflowState(TypedDict):
    """State schema for our stateful workflow."""
    # TODO: Add required state fields
    pass


class DocumentApprovalState(TypedDict):
    """Specialized state for document approval workflow."""
    # TODO: Add document approval specific fields
    pass


# TODO: Step 2 - Initialize LLM
def get_llm():
    """Initialize the language model."""
    # TODO: Return ChatOpenAI instance
    pass


# TODO: Step 3 - Implement Node Functions
def initialize_workflow(state: WorkflowState) -> WorkflowState:
    """Initialize the workflow state."""
    print("🚀 Initializing workflow...")
    # TODO: Set initial state values
    return state


def analyze_document(state: WorkflowState) -> WorkflowState:
    """Analyze document content using LLM."""
    print("📄 Analyzing document...")
    # TODO: Implement document analysis
    return state


def request_human_approval(state: WorkflowState) -> WorkflowState:
    """Request human approval - creates interruption point."""
    print("👥 Requesting human approval...")
    # TODO: Set up human-in-the-loop interruption
    return state


def process_approval_decision(state: WorkflowState) -> WorkflowState:
    """Process the approval decision."""
    print("✅ Processing approval decision...")
    # TODO: Handle approval/rejection/revision decisions
    return state


def handle_revision(state: WorkflowState) -> WorkflowState:
    """Handle document revision."""
    print("🔄 Handling document revision...")
    # TODO: Implement revision logic
    return state


# TODO: Step 4 - Implement Parallel Processing Nodes
def parallel_analysis_quality(state: WorkflowState) -> WorkflowState:
    """Parallel node: Quality analysis."""
    print("🔍 Running quality analysis...")
    # TODO: Implement quality analysis
    return state


def parallel_analysis_compliance(state: WorkflowState) -> WorkflowState:
    """Parallel node: Compliance check."""
    print("📋 Running compliance check...")
    # TODO: Implement compliance check
    return state


def parallel_analysis_security(state: WorkflowState) -> WorkflowState:
    """Parallel node: Security review."""
    print("🔒 Running security review...")
    # TODO: Implement security review
    return state


def merge_parallel_results(state: WorkflowState) -> WorkflowState:
    """Merge results from parallel analysis."""
    print("🔄 Merging parallel analysis results...")
    # TODO: Combine results from parallel nodes
    return state


def finalize_workflow(state: WorkflowState) -> WorkflowState:
    """Finalize the workflow."""
    print("🎯 Finalizing workflow...")
    # TODO: Complete workflow and update final state
    return state


# TODO: Step 5 - Implement Conditional Logic Functions
def should_request_approval(state: WorkflowState) -> Literal["approval", "parallel"]:
    """Determine if approval is needed."""
    # TODO: Implement routing logic
    return "approval"


def approval_decision_router(state: WorkflowState) -> Literal["approved", "revision", "rejected"]:
    """Route based on approval decision."""
    # TODO: Route based on approval status
    return "approved"


def revision_limit_check(state: WorkflowState) -> Literal["analyze", "rejected"]:
    """Check if revision limit is reached."""
    # TODO: Check revision count and route accordingly
    return "analyze"


# TODO: Step 6 - Build Stateful Workflow Graph
def create_stateful_workflow():
    """Create the main stateful workflow graph."""
    print("🏗️ Building stateful workflow graph...")
    
    # TODO: Initialize StateGraph with WorkflowState
    workflow = StateGraph(WorkflowState)
    
    # TODO: Add nodes to the workflow
    # workflow.add_node("node_name", node_function)
    
    # TODO: Add edges and conditional edges
    # workflow.add_edge(START, "first_node")
    # workflow.add_conditional_edges(...)
    
    # TODO: Add final edge to END
    
    return workflow


# TODO: Step 7 - Implement Document Approval System
def create_document_approval_system():
    """Create specialized document approval workflow."""
    print("📋 Creating document approval system...")
    
    # TODO: Define document approval nodes
    def init_document(state: DocumentApprovalState) -> DocumentApprovalState:
        # TODO: Initialize document state
        return state
    
    def submit_for_review(state: DocumentApprovalState) -> DocumentApprovalState:
        # TODO: Submit for review
        return state
    
    def approve_document(state: DocumentApprovalState) -> DocumentApprovalState:
        # TODO: Process approval
        return state
    
    # TODO: Create and return document workflow graph
    doc_workflow = StateGraph(DocumentApprovalState)
    # Add nodes and edges...
    
    return doc_workflow


# TODO: Step 8 - Implement Execution Functions
def run_stateful_workflow_demo():
    """Run demonstration of stateful workflow."""
    print("🎯 Running Stateful Workflow Demo")
    print("=" * 50)
    
    # TODO: Create workflow with checkpointing
    # memory = MemorySaver()
    # workflow = create_stateful_workflow()
    # app = workflow.compile(checkpointer=memory)
    
    # TODO: Define initial state
    initial_state = {
        # TODO: Set initial state values
    }
    
    # TODO: Execute workflow and return result
    # config = {"configurable": {"thread_id": "demo_workflow_1"}}
    # result = app.invoke(initial_state, config)
    
    print("TODO: Implement workflow execution")
    return {}


def run_document_approval_demo():
    """Run document approval system demo."""
    print("\n🏢 Running Document Approval Demo")
    print("=" * 50)
    
    # TODO: Implement document approval demo
    print("TODO: Implement document approval system")
    return {}


def demonstrate_checkpointing():
    """Demonstrate checkpoint persistence and resumption."""
    print("\n💾 Demonstrating Checkpointing")
    print("=" * 50)
    
    # TODO: Implement checkpointing demonstration
    print("TODO: Implement checkpointing demo")


def main():
    """Main function."""
    print("="*80)
    print("LangGraph Stateful Applications - Starter")
    print("="*80)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        print("Please set your OpenAI API key in the .env file")
        return
    
    print("\n📋 TODO List:")
    print("1. ✅ Define state schemas (WorkflowState, DocumentApprovalState)")
    print("2. ✅ Implement LLM initialization")
    print("3. ⏳ Create node functions for workflow steps")
    print("4. ⏳ Implement parallel processing nodes")
    print("5. ⏳ Add conditional routing logic")
    print("6. ⏳ Build the stateful workflow graph")
    print("7. ⏳ Create document approval system")
    print("8. ⏳ Implement execution and demo functions")
    print("9. ⏳ Add checkpointing and state persistence")
    
    try:
        # TODO: Uncomment and implement each demo
        # print("\n🎯 Running Demonstrations")
        # run_stateful_workflow_demo()
        # run_document_approval_demo()
        # demonstrate_checkpointing()
        
        print("\n⚠️ Complete the TODOs to run the full demonstrations!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
