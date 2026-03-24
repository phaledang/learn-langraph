"""
Tests for Lab 07: LangGraph Multi-Agent Systems

Covers:
- Multi-agent state schema
- Agent node patterns
- Supervisor / dispatch routing
- Inter-agent message passing
"""

import pytest
from typing import TypedDict, Literal, List, Dict, Any
from langgraph.graph import StateGraph, END


# ---------------------------------------------------------------------------
# Multi-Agent State
# ---------------------------------------------------------------------------

class MultiAgentState(TypedDict):
    task: str
    agent_outputs: Dict[str, str]
    current_agent: str
    final_answer: str


# ---------------------------------------------------------------------------
# Agent node stubs (no LLM)
# ---------------------------------------------------------------------------

def researcher_agent(state: MultiAgentState) -> MultiAgentState:
    """Simulates a research agent."""
    state["agent_outputs"]["researcher"] = f"Research findings for: {state['task']}"
    return state


def writer_agent(state: MultiAgentState) -> MultiAgentState:
    """Simulates a writing agent."""
    research = state["agent_outputs"].get("researcher", "")
    state["agent_outputs"]["writer"] = f"Article based on: {research}"
    return state


def reviewer_agent(state: MultiAgentState) -> MultiAgentState:
    """Simulates a review agent."""
    article = state["agent_outputs"].get("writer", "")
    state["agent_outputs"]["reviewer"] = f"Review of: {article}"
    state["final_answer"] = f"Reviewed: {article}"
    return state


# ---------------------------------------------------------------------------
# Supervisor routing
# ---------------------------------------------------------------------------

def supervisor_route(state: MultiAgentState) -> Literal["researcher", "writer", "reviewer", "end"]:
    """Simple supervisor logic."""
    outputs = state["agent_outputs"]
    if "researcher" not in outputs:
        return "researcher"
    if "writer" not in outputs:
        return "writer"
    if "reviewer" not in outputs:
        return "reviewer"
    return "end"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMultiAgentState:
    def test_initial_state(self):
        state: MultiAgentState = {
            "task": "Write about AI",
            "agent_outputs": {},
            "current_agent": "",
            "final_answer": "",
        }
        assert state["task"] == "Write about AI"
        assert len(state["agent_outputs"]) == 0


class TestAgentNodes:
    def _make_state(self, task="Test task") -> MultiAgentState:
        return {
            "task": task,
            "agent_outputs": {},
            "current_agent": "",
            "final_answer": "",
        }

    def test_researcher(self):
        state = self._make_state()
        result = researcher_agent(state)
        assert "researcher" in result["agent_outputs"]
        assert "Test task" in result["agent_outputs"]["researcher"]

    def test_writer_uses_research(self):
        state = self._make_state()
        state["agent_outputs"]["researcher"] = "Found facts"
        result = writer_agent(state)
        assert "writer" in result["agent_outputs"]
        assert "Found facts" in result["agent_outputs"]["writer"]

    def test_reviewer_produces_final(self):
        state = self._make_state()
        state["agent_outputs"]["writer"] = "Draft article"
        result = reviewer_agent(state)
        assert "reviewer" in result["agent_outputs"]
        assert result["final_answer"] != ""


class TestSupervisorRouting:
    def test_routes_to_researcher_first(self):
        state: MultiAgentState = {
            "task": "x",
            "agent_outputs": {},
            "current_agent": "",
            "final_answer": "",
        }
        assert supervisor_route(state) == "researcher"

    def test_routes_to_writer_after_research(self):
        state: MultiAgentState = {
            "task": "x",
            "agent_outputs": {"researcher": "done"},
            "current_agent": "",
            "final_answer": "",
        }
        assert supervisor_route(state) == "writer"

    def test_routes_to_reviewer_after_writer(self):
        state: MultiAgentState = {
            "task": "x",
            "agent_outputs": {"researcher": "d", "writer": "d"},
            "current_agent": "",
            "final_answer": "",
        }
        assert supervisor_route(state) == "reviewer"

    def test_routes_to_end_when_all_done(self):
        state: MultiAgentState = {
            "task": "x",
            "agent_outputs": {"researcher": "d", "writer": "d", "reviewer": "d"},
            "current_agent": "",
            "final_answer": "",
        }
        assert supervisor_route(state) == "end"


class TestMultiAgentGraph:
    """Test the full multi-agent pipeline graph."""

    def _build_graph(self):
        wf = StateGraph(MultiAgentState)
        wf.add_node("researcher", researcher_agent)
        wf.add_node("writer", writer_agent)
        wf.add_node("reviewer", reviewer_agent)
        wf.set_entry_point("researcher")
        wf.add_edge("researcher", "writer")
        wf.add_edge("writer", "reviewer")
        wf.add_edge("reviewer", END)
        return wf.compile()

    def test_full_pipeline(self):
        app = self._build_graph()
        result = app.invoke({
            "task": "Write about LangGraph",
            "agent_outputs": {},
            "current_agent": "",
            "final_answer": "",
        })
        assert "researcher" in result["agent_outputs"]
        assert "writer" in result["agent_outputs"]
        assert "reviewer" in result["agent_outputs"]
        assert result["final_answer"] != ""
