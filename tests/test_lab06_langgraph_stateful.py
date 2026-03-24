"""
Tests for Lab 06: LangGraph Stateful Applications

Covers:
- WorkflowState and DocumentApprovalState schemas
- Individual node function logic
- Conditional routing functions
- Document approval workflow graph construction
- Workflow graph with checkpointing (MemorySaver)
"""

import pytest
from typing import TypedDict, Annotated, List, Dict, Any
from typing_extensions import Literal
from datetime import datetime
from unittest.mock import patch, MagicMock

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver


# ---------------------------------------------------------------------------
# State schema definitions (mirrored from solution)
# ---------------------------------------------------------------------------

class WorkflowState(TypedDict):
    messages: List[Dict[str, Any]]
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
    document_id: str
    document_title: str
    document_content: str
    author: str
    current_approver: str
    approval_chain: List[str]
    approvals_received: List[Dict[str, Any]]
    status: str
    feedback: List[str]
    revision_history: List[Dict[str, Any]]
    created_at: str
    last_modified: str


# ---------------------------------------------------------------------------
# Node functions (pure logic, no LLM)
# ---------------------------------------------------------------------------

def initialize_workflow(state: WorkflowState) -> WorkflowState:
    state["current_step"] = "initialized"
    state["approval_status"] = "pending"
    state["revision_count"] = 0
    state["parallel_results"] = {}
    state["workflow_metadata"] = {"start_time": datetime.now().isoformat()}
    state["human_input_required"] = False
    state["last_updated"] = datetime.now().isoformat()
    if not state.get("messages"):
        state["messages"] = []
    return state


def finalize_workflow(state: WorkflowState) -> WorkflowState:
    state["current_step"] = "completed"
    state["last_updated"] = datetime.now().isoformat()
    return state


# ---------------------------------------------------------------------------
# Tests: State Schema
# ---------------------------------------------------------------------------

class TestWorkflowState:
    def test_initial_state(self):
        state: WorkflowState = {
            "messages": [],
            "current_step": "start",
            "document_content": "Sample doc",
            "approval_status": "pending",
            "reviewer_feedback": "",
            "revision_count": 0,
            "parallel_results": {},
            "workflow_metadata": {},
            "human_input_required": False,
            "last_updated": "",
        }
        assert state["current_step"] == "start"
        assert state["messages"] == []

    def test_document_approval_state(self):
        state: DocumentApprovalState = {
            "document_id": "",
            "document_title": "Test Doc",
            "document_content": "Content here",
            "author": "tester",
            "current_approver": "",
            "approval_chain": ["reviewer", "manager"],
            "approvals_received": [],
            "status": "draft",
            "feedback": [],
            "revision_history": [],
            "created_at": "",
            "last_modified": "",
        }
        assert state["document_title"] == "Test Doc"
        assert len(state["approval_chain"]) == 2


# ---------------------------------------------------------------------------
# Tests: Node functions
# ---------------------------------------------------------------------------

class TestNodeFunctions:
    def _make_state(self) -> WorkflowState:
        return {
            "messages": [],
            "current_step": "start",
            "document_content": "Test doc",
            "approval_status": "pending",
            "reviewer_feedback": "",
            "revision_count": 0,
            "parallel_results": {},
            "workflow_metadata": {},
            "human_input_required": False,
            "last_updated": "",
        }

    def test_initialize_sets_fields(self):
        state = self._make_state()
        result = initialize_workflow(state)
        assert result["current_step"] == "initialized"
        assert result["approval_status"] == "pending"
        assert result["revision_count"] == 0
        assert result["last_updated"] != ""

    def test_finalize_marks_completed(self):
        state = self._make_state()
        result = finalize_workflow(state)
        assert result["current_step"] == "completed"


# ---------------------------------------------------------------------------
# Tests: Conditional routing
# ---------------------------------------------------------------------------

class TestConditionalRouting:
    def test_approval_decision_approved(self):
        def router(state):
            if state["approval_status"] == "approved":
                return "approved"
            elif state["approval_status"] == "needs_revision":
                return "revision"
            return "rejected"

        assert router({"approval_status": "approved"}) == "approved"
        assert router({"approval_status": "needs_revision"}) == "revision"
        assert router({"approval_status": "rejected"}) == "rejected"

    def test_revision_limit_check(self):
        def revision_check(state):
            return "rejected" if state["revision_count"] >= 3 else "analyze"

        assert revision_check({"revision_count": 0}) == "analyze"
        assert revision_check({"revision_count": 2}) == "analyze"
        assert revision_check({"revision_count": 3}) == "rejected"
        assert revision_check({"revision_count": 5}) == "rejected"


# ---------------------------------------------------------------------------
# Tests: Document Approval Graph
# ---------------------------------------------------------------------------

class TestDocumentApprovalGraph:
    """Build and run the document approval sub-graph."""

    def _build_graph(self):
        def init_doc(state: DocumentApprovalState) -> DocumentApprovalState:
            state["document_id"] = "doc_test"
            state["status"] = "draft"
            state["approval_chain"] = ["reviewer", "manager", "director"]
            state["approvals_received"] = []
            state["feedback"] = []
            state["revision_history"] = []
            state["created_at"] = datetime.now().isoformat()
            state["last_modified"] = datetime.now().isoformat()
            return state

        def submit(state: DocumentApprovalState) -> DocumentApprovalState:
            state["status"] = "under_review"
            state["current_approver"] = state["approval_chain"][0]
            return state

        def approve(state: DocumentApprovalState) -> DocumentApprovalState:
            state["approvals_received"].append({
                "approver": state["current_approver"],
                "decision": "approved",
            })
            idx = state["approval_chain"].index(state["current_approver"])
            if idx + 1 < len(state["approval_chain"]):
                state["current_approver"] = state["approval_chain"][idx + 1]
            else:
                state["status"] = "approved"
                state["current_approver"] = ""
            return state

        wf = StateGraph(DocumentApprovalState)
        wf.add_node("init", init_doc)
        wf.add_node("submit", submit)
        wf.add_node("approve", approve)
        wf.add_edge(START, "init")
        wf.add_edge("init", "submit")
        wf.add_edge("submit", "approve")
        wf.add_edge("approve", END)
        return wf.compile()

    def test_approval_graph_runs(self):
        app = self._build_graph()
        result = app.invoke({
            "document_id": "",
            "document_title": "Test Policy",
            "document_content": "Policy content...",
            "author": "tester",
            "current_approver": "",
            "approval_chain": [],
            "approvals_received": [],
            "status": "",
            "feedback": [],
            "revision_history": [],
            "created_at": "",
            "last_modified": "",
        })
        assert result["document_id"] == "doc_test"
        assert result["status"] == "under_review"
        assert len(result["approvals_received"]) == 1

    def test_approval_graph_first_approver(self):
        app = self._build_graph()
        result = app.invoke({
            "document_id": "",
            "document_title": "T",
            "document_content": "C",
            "author": "a",
            "current_approver": "",
            "approval_chain": [],
            "approvals_received": [],
            "status": "",
            "feedback": [],
            "revision_history": [],
            "created_at": "",
            "last_modified": "",
        })
        # After one approve node, current_approver should advance to "manager"
        assert result["current_approver"] == "manager"


# ---------------------------------------------------------------------------
# Tests: MemorySaver Checkpointing
# ---------------------------------------------------------------------------

class TestMemorySaver:
    """Test that MemorySaver captures graph state."""

    def test_checkpointer_with_simple_graph(self):
        class S(TypedDict):
            value: int

        def inc(state: S) -> S:
            state["value"] += 1
            return state

        wf = StateGraph(S)
        wf.add_node("inc", inc)
        wf.set_entry_point("inc")
        wf.add_edge("inc", END)

        memory = MemorySaver()
        app = wf.compile(checkpointer=memory)

        config = {"configurable": {"thread_id": "t1"}}
        result = app.invoke({"value": 0}, config)
        assert result["value"] == 1

        # State should be retrievable
        saved = app.get_state(config)
        assert saved.values["value"] == 1
