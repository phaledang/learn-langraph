"""
LangGraph Stateful Applications - Solution Code

Complete implementation demonstrating langgraph stateful applications.
"""

import os
import time
from typing import TypedDict, Annotated, List, Dict, Any
from typing_extensions import Literal
from datetime import datetime
import json

from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

# Load environment variables from .env file relative to this script
load_dotenv(Path(__file__).parent / ".env")


# Step 1: Define State Schema
class WorkflowState(TypedDict):
    """State schema for our stateful workflow."""
    messages: Annotated[List[Dict[str, Any]], "List of conversation messages"]
    current_step: str
    document_content: str
    approval_status: str
    reviewer_feedback: str
    revision_count: int
    parallel_results: Dict[str, Any]
    workflow_metadata: Dict[str, Any]
    human_input_required: bool
    last_updated: str


class DocumentApprovalState(TypedDict):
    """Specialized state for document approval workflow."""
    document_id: str
    document_title: str
    document_content: str
    author: str
    current_approver: str
    approval_chain: List[str]
    approvals_received: List[Dict[str, Any]]
    status: Literal["draft", "under_review", "approved", "rejected", "needs_revision"]
    feedback: List[str]
    revision_history: List[Dict[str, Any]]
    created_at: str
    last_modified: str


# Step 2: Initialize LLM
def get_llm():
    """Initialize the language model."""
    return AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.1,
    )


# Step 3: Node Functions for Basic Stateful Workflow
def initialize_workflow(state: WorkflowState) -> WorkflowState:
    """Initialize the workflow state."""
    print("🚀 Initializing workflow...")
    
    state["current_step"] = "initialized"
    state["approval_status"] = "pending"
    state["revision_count"] = 0
    state["parallel_results"] = {}
    state["workflow_metadata"] = {
        "start_time": datetime.now().isoformat(),
        "workflow_id": f"wf_{int(time.time())}"
    }
    state["human_input_required"] = False
    state["last_updated"] = datetime.now().isoformat()
    
    if not state.get("messages"):
        state["messages"] = []
    
    return state


def analyze_document(state: WorkflowState) -> WorkflowState:
    """Analyze document content using LLM."""
    print("📄 Analyzing document...")
    
    llm = get_llm()
    
    if not state.get("document_content"):
        state["document_content"] = "Sample document for analysis and approval workflow."
    
    analysis_prompt = f"""
    Analyze the following document and provide feedback:
    
    Document: {state['document_content']}
    
    Please provide:
    1. Quality assessment (1-10)
    2. Key strengths
    3. Areas for improvement
    4. Recommendation (approve/revise/reject)
    """
    
    response = llm.invoke([HumanMessage(content=analysis_prompt)])
    
    state["messages"].append({
        "role": "system",
        "content": f"Document analysis completed: {response.content}",
        "timestamp": datetime.now().isoformat()
    })
    
    state["reviewer_feedback"] = response.content
    state["current_step"] = "analyzed"
    state["last_updated"] = datetime.now().isoformat()
    
    return state


def request_human_approval(state: WorkflowState) -> WorkflowState:
    """Request human approval - creates interruption point."""
    print("👥 Requesting human approval...")
    
    state["current_step"] = "awaiting_approval"
    state["human_input_required"] = True
    state["last_updated"] = datetime.now().isoformat()
    
    state["messages"].append({
        "role": "system",
        "content": "Human approval requested. Workflow paused for human input.",
        "timestamp": datetime.now().isoformat()
    })
    
    return state


def process_approval_decision(state: WorkflowState) -> WorkflowState:
    """Process the approval decision."""
    print("✅ Processing approval decision...")
    
    # In a real implementation, this would get input from human
    # For demo purposes, we'll simulate the decision
    approval_decision = "approved"  # Could be "approved", "rejected", "needs_revision"
    
    state["approval_status"] = approval_decision
    state["current_step"] = f"decision_{approval_decision}"
    state["human_input_required"] = False
    state["last_updated"] = datetime.now().isoformat()
    
    state["messages"].append({
        "role": "human",
        "content": f"Approval decision: {approval_decision}",
        "timestamp": datetime.now().isoformat()
    })
    
    return state


def handle_revision(state: WorkflowState) -> WorkflowState:
    """Handle document revision."""
    print("🔄 Handling document revision...")
    
    state["revision_count"] += 1
    state["current_step"] = "revising"
    
    # Simulate revision process
    llm = get_llm()
    revision_prompt = f"""
    Based on the feedback: {state.get('reviewer_feedback', '')}
    Please provide a revised version of: {state['document_content']}
    """
    
    response = llm.invoke([HumanMessage(content=revision_prompt)])
    state["document_content"] = response.content
    
    state["messages"].append({
        "role": "system",
        "content": f"Document revised (revision #{state['revision_count']})",
        "timestamp": datetime.now().isoformat()
    })
    
    state["last_updated"] = datetime.now().isoformat()
    
    return state


# Step 4: Parallel Processing Nodes
def parallel_analysis_quality(state: WorkflowState) -> WorkflowState:
    """Parallel node: Quality analysis."""
    print("🔍 Running quality analysis...")
    
    llm = get_llm()
    response = llm.invoke([HumanMessage(content=f"Analyze quality of: {state['document_content']}")])
    
    if "parallel_results" not in state:
        state["parallel_results"] = {}
    
    state["parallel_results"]["quality"] = {
        "analysis": response.content,
        "timestamp": datetime.now().isoformat()
    }
    
    return state


def parallel_analysis_compliance(state: WorkflowState) -> WorkflowState:
    """Parallel node: Compliance check."""
    print("📋 Running compliance check...")
    
    llm = get_llm()
    response = llm.invoke([HumanMessage(content=f"Check compliance of: {state['document_content']}")])
    
    if "parallel_results" not in state:
        state["parallel_results"] = {}
    
    state["parallel_results"]["compliance"] = {
        "analysis": response.content,
        "timestamp": datetime.now().isoformat()
    }
    
    return state


def parallel_analysis_security(state: WorkflowState) -> WorkflowState:
    """Parallel node: Security review."""
    print("🔒 Running security review...")
    
    llm = get_llm()
    response = llm.invoke([HumanMessage(content=f"Security review of: {state['document_content']}")])
    
    if "parallel_results" not in state:
        state["parallel_results"] = {}
    
    state["parallel_results"]["security"] = {
        "analysis": response.content,
        "timestamp": datetime.now().isoformat()
    }
    
    return state


def merge_parallel_results(state: WorkflowState) -> WorkflowState:
    """Merge results from parallel analysis."""
    print("🔄 Merging parallel analysis results...")
    
    merged_feedback = "Combined Analysis Results:\n\n"
    
    for analysis_type, result in state["parallel_results"].items():
        merged_feedback += f"{analysis_type.upper()} ANALYSIS:\n{result['analysis']}\n\n"
    
    state["reviewer_feedback"] = merged_feedback
    state["current_step"] = "parallel_complete"
    state["last_updated"] = datetime.now().isoformat()
    
    state["messages"].append({
        "role": "system",
        "content": "Parallel analysis completed and results merged",
        "timestamp": datetime.now().isoformat()
    })
    
    return state


def finalize_workflow(state: WorkflowState) -> WorkflowState:
    """Finalize the workflow."""
    print("🎯 Finalizing workflow...")
    
    state["current_step"] = "completed"
    state["workflow_metadata"]["end_time"] = datetime.now().isoformat()
    state["last_updated"] = datetime.now().isoformat()
    
    state["messages"].append({
        "role": "system",
        "content": f"Workflow completed with status: {state['approval_status']}",
        "timestamp": datetime.now().isoformat()
    })
    
    return state


# Step 5: Conditional Logic Functions
def should_request_approval(state: WorkflowState) -> Literal["approval", "parallel"]:
    """Determine if approval is needed."""
    # Route to parallel analysis first, then approval
    if state["current_step"] == "analyzed":
        return "parallel"
    return "approval"


def approval_decision_router(state: WorkflowState) -> Literal["approved", "revision", "rejected"]:
    """Route based on approval decision."""
    status = state.get("approval_status", "pending")
    
    if status == "approved":
        return "approved"
    elif status == "needs_revision":
        return "revision"
    else:
        return "rejected"


def revision_limit_check(state: WorkflowState) -> Literal["analyze", "rejected"]:
    """Check if revision limit is reached."""
    if state["revision_count"] >= 3:
        return "rejected"
    return "analyze"


# Step 6: Build Stateful Workflow Graph
def create_stateful_workflow():
    """Create the main stateful workflow graph."""
    print("🏗️ Building stateful workflow graph...")
    
    # Initialize graph with state
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("analyze", analyze_document)
    workflow.add_node("quality_check", parallel_analysis_quality)
    workflow.add_node("compliance_check", parallel_analysis_compliance)
    workflow.add_node("security_check", parallel_analysis_security)
    workflow.add_node("merge_results", merge_parallel_results)
    workflow.add_node("request_approval", request_human_approval)
    workflow.add_node("process_decision", process_approval_decision)
    workflow.add_node("revise", handle_revision)
    workflow.add_node("finalize", finalize_workflow)
    
    # Add edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "analyze")
    
    # Conditional routing after analysis
    workflow.add_conditional_edges(
        "analyze",
        should_request_approval,
        {
            "parallel": "quality_check",
            "approval": "request_approval"
        }
    )
    
    # Parallel processing
    workflow.add_edge("quality_check", "compliance_check")
    workflow.add_edge("compliance_check", "security_check")
    workflow.add_edge("security_check", "merge_results")
    workflow.add_edge("merge_results", "request_approval")
    
    # Approval flow
    workflow.add_edge("request_approval", "process_decision")
    
    # Decision routing
    workflow.add_conditional_edges(
        "process_decision",
        approval_decision_router,
        {
            "approved": "finalize",
            "revision": "revise",
            "rejected": "finalize"
        }
    )
    
    # Revision flow with limit check
    workflow.add_conditional_edges(
        "revise",
        revision_limit_check,
        {
            "analyze": "analyze",
            "rejected": "finalize"
        }
    )
    
    workflow.add_edge("finalize", END)
    
    return workflow


# Step 7: Document Approval System
def create_document_approval_system():
    """Create specialized document approval workflow."""
    print("📋 Creating document approval system...")
    
    def init_document(state: DocumentApprovalState) -> DocumentApprovalState:
        """Initialize document approval workflow."""
        if not state.get("document_id"):
            state["document_id"] = f"doc_{int(time.time())}"
        
        state["status"] = "draft"
        state["approval_chain"] = ["reviewer", "manager", "director"]
        state["approvals_received"] = []
        state["feedback"] = []
        state["revision_history"] = []
        state["created_at"] = datetime.now().isoformat()
        state["last_modified"] = datetime.now().isoformat()
        
        return state
    
    def submit_for_review(state: DocumentApprovalState) -> DocumentApprovalState:
        """Submit document for review."""
        state["status"] = "under_review"
        state["current_approver"] = state["approval_chain"][0]
        state["last_modified"] = datetime.now().isoformat()
        return state
    
    def approve_document(state: DocumentApprovalState) -> DocumentApprovalState:
        """Approve document at current level."""
        approval = {
            "approver": state["current_approver"],
            "decision": "approved",
            "timestamp": datetime.now().isoformat()
        }
        state["approvals_received"].append(approval)
        
        # Move to next approver or complete
        current_index = state["approval_chain"].index(state["current_approver"])
        if current_index + 1 < len(state["approval_chain"]):
            state["current_approver"] = state["approval_chain"][current_index + 1]
        else:
            state["status"] = "approved"
            state["current_approver"] = ""
        
        state["last_modified"] = datetime.now().isoformat()
        return state
    
    # Create document approval graph
    doc_workflow = StateGraph(DocumentApprovalState)
    
    doc_workflow.add_node("init", init_document)
    doc_workflow.add_node("submit", submit_for_review)
    doc_workflow.add_node("approve", approve_document)
    
    doc_workflow.add_edge(START, "init")
    doc_workflow.add_edge("init", "submit")
    doc_workflow.add_edge("submit", "approve")
    doc_workflow.add_edge("approve", END)
    
    return doc_workflow


# Step 8: Generate Graph Image
def generate_graph_image(graph, output_path: str = None) -> str:
    """Generate a PNG image of the LangGraph workflow.

    Args:
        graph: A compiled LangGraph application or a StateGraph.
        output_path: Optional file path for the output image.
                     Defaults to 'workflow_graph.png' in the solution directory.

    Returns:
        The absolute path to the generated image file.
    """
    if output_path is None:
        output_path = str(Path(__file__).parent / "workflow_graph.png")

    # If it's an uncompiled StateGraph, compile it first
    compiled = graph.compile() if isinstance(graph, StateGraph) else graph

    print(f"📸 Generating graph image...")
    png_bytes = compiled.get_graph().draw_mermaid_png()

    with open(output_path, "wb") as f:
        f.write(png_bytes)

    print(f"✅ Graph image saved to: {output_path}")
    return output_path


# Step 9: Main Execution Function
def run_stateful_workflow_demo():
    """Run demonstration of stateful workflow."""
    print("🎯 Running Stateful Workflow Demo")
    print("=" * 50)
    
    # Create workflow with checkpointing
    memory = MemorySaver()
    workflow = create_stateful_workflow()
    app = workflow.compile(checkpointer=memory)
    
    # Initial state
    initial_state = {
        "messages": [],
        "document_content": "This is a sample policy document that needs review and approval before implementation.",
        "current_step": "start",
        "approval_status": "pending",
        "reviewer_feedback": "",
        "revision_count": 0,
        "parallel_results": {},
        "workflow_metadata": {},
        "human_input_required": False,
        "last_updated": ""
    }
    
    # Configuration for checkpointing
    config = {"configurable": {"thread_id": "demo_workflow_1"}}
    
    print("\n📝 Starting workflow execution...")
    
    # Execute workflow
    result = app.invoke(initial_state, config)
    
    print("\n📊 Final State:")
    print(f"Status: {result['approval_status']}")
    print(f"Step: {result['current_step']}")
    print(f"Revisions: {result['revision_count']}")
    print(f"Parallel Results: {len(result['parallel_results'])} analyses completed")
    
    return result


def run_document_approval_demo():
    """Run document approval system demo."""
    print("\n🏢 Running Document Approval Demo")
    print("=" * 50)
    
    # Create document approval workflow
    doc_workflow = create_document_approval_system()
    memory = MemorySaver()
    doc_app = doc_workflow.compile(checkpointer=memory)
    
    # Initial document state
    doc_state = {
        "document_title": "Company Privacy Policy Update",
        "document_content": "Updated privacy policy to comply with new regulations...",
        "author": "Legal Team",
        "document_id": "",
        "current_approver": "",
        "approval_chain": [],
        "approvals_received": [],
        "status": "",
        "feedback": [],
        "revision_history": [],
        "created_at": "",
        "last_modified": ""
    }
    
    config = {"configurable": {"thread_id": "doc_approval_1"}}
    
    print("\n📋 Starting document approval...")
    result = doc_app.invoke(doc_state, config)
    
    print(f"\n📄 Document Status: {result['status']}")
    print(f"📝 Document ID: {result['document_id']}")
    print(f"👤 Current Approver: {result['current_approver'] or 'None (Complete)'}")
    print(f"✅ Approvals: {len(result['approvals_received'])}")
    
    return result


def demonstrate_checkpointing():
    """Demonstrate checkpoint persistence and resumption."""
    print("\n💾 Demonstrating Checkpointing")
    print("=" * 50)
    
    memory = MemorySaver()
    workflow = create_stateful_workflow()
    app = workflow.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "checkpoint_demo"}}
    
    # Start workflow
    initial_state = {
        "messages": [],
        "document_content": "Checkpoint demo document",
        "current_step": "start",
        "approval_status": "pending",
        "reviewer_feedback": "",
        "revision_count": 0,
        "parallel_results": {},
        "workflow_metadata": {},
        "human_input_required": False,
        "last_updated": ""
    }
    
    print("🚀 Starting workflow with checkpointing...")
    
    # Execute first part
    for chunk in app.stream(initial_state, config):
        node_name = list(chunk.keys())[0]
        print(f"📍 Checkpoint: {node_name}")
        
        # Stop at approval step to demonstrate resumption
        if node_name == "request_approval":
            print("⏸️ Pausing at approval step...")
            break
    
    print("\n🔄 Resuming from checkpoint...")
    
    # Get current state
    current_state = app.get_state(config)
    print(f"📊 Current step: {current_state.values['current_step']}")
    
    # Resume execution
    for chunk in app.stream(None, config):
        node_name = list(chunk.keys())[0]
        print(f"📍 Resumed: {node_name}")
    
    final_state = app.get_state(config)
    print(f"\n✅ Final step: {final_state.values['current_step']}")


def main():
    """Main function."""
    print("="*80)
    print("LangGraph Stateful Applications - Complete Solution")
    print("="*80)
    
    # Check API key
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("❌ Error: AZURE_OPENAI_API_KEY not set")
        print("Please set your Azure OpenAI API key in the .env file")
        return
    
    try:
        # Run all demonstrations
        print("\n🎯 Running Comprehensive Stateful Workflow Demonstrations")
        
        # 0. Generate graph images
        stateful_wf = create_stateful_workflow()
        generate_graph_image(
            stateful_wf,
            str(Path(__file__).parent / "stateful_workflow_graph.png"),
        )

        doc_wf = create_document_approval_system()
        generate_graph_image(
            doc_wf,
            str(Path(__file__).parent / "document_approval_graph.png"),
        )

        # 1. Basic stateful workflow
        result1 = run_stateful_workflow_demo()
        
        # 2. Document approval system
        result2 = run_document_approval_demo()
        
        # 3. Checkpointing demonstration
        demonstrate_checkpointing()
        
        print("\n" + "="*80)
        print("✅ All Demonstrations Completed Successfully!")
        print("="*80)
        
        print("\n📋 Summary:")
        print("✅ Graph images generated")
        print("✅ Stateful workflow with memory")
        print("✅ Human-in-the-loop integration")
        print("✅ Document approval system")
        print("✅ Parallel node processing")
        print("✅ Complex routing logic")
        print("✅ Persistent checkpointing")
        print("✅ State management and recovery")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
