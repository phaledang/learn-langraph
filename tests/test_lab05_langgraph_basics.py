"""
Tests for Lab 05: LangGraph Basics

Covers:
- TypedDict state schema definition
- StateGraph node and edge wiring
- Conditional edges and routing
- Simple linear graph execution
- Conditional graph (even/odd) execution
"""

import pytest
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ---------------------------------------------------------------------------
# State Schema tests
# ---------------------------------------------------------------------------

class TestStateSchema:
    """Test TypedDict state definitions."""

    def test_simple_state(self):
        class SimpleState(TypedDict):
            input: str
            output: str
            count: int

        state: SimpleState = {"input": "hi", "output": "", "count": 0}
        assert state["input"] == "hi"
        assert state["count"] == 0

    def test_agent_state_schema(self):
        class AgentState(TypedDict):
            messages: list
            step: int
            user_input: str
            result: str
            iterations: int

        state: AgentState = {
            "messages": [],
            "step": 0,
            "user_input": "test",
            "result": "",
            "iterations": 0,
        }
        assert state["step"] == 0
        assert state["messages"] == []


# ---------------------------------------------------------------------------
# Simple Linear Graph tests
# ---------------------------------------------------------------------------

class SimpleState(TypedDict):
    input: str
    output: str
    count: int


def step1(state: SimpleState) -> SimpleState:
    state["count"] = 1
    return state


def step2(state: SimpleState) -> SimpleState:
    state["count"] = 2
    return state


def step3(state: SimpleState) -> SimpleState:
    state["output"] = f"Processed: {state['input']}"
    state["count"] = 3
    return state


class TestSimpleLinearGraph:
    """Test a simple 3-step linear graph."""

    def _build_graph(self):
        workflow = StateGraph(SimpleState)
        workflow.add_node("step1", step1)
        workflow.add_node("step2", step2)
        workflow.add_node("step3", step3)
        workflow.set_entry_point("step1")
        workflow.add_edge("step1", "step2")
        workflow.add_edge("step2", "step3")
        workflow.add_edge("step3", END)
        return workflow.compile()

    def test_linear_graph_runs(self):
        app = self._build_graph()
        result = app.invoke({"input": "Hello LangGraph!", "output": "", "count": 0})
        assert result["count"] == 3
        assert result["output"] == "Processed: Hello LangGraph!"

    def test_linear_graph_initial_state_preserved(self):
        app = self._build_graph()
        result = app.invoke({"input": "Test", "output": "", "count": 0})
        assert result["input"] == "Test"

    def test_linear_graph_step_progression(self):
        """Verify all steps execute in order."""
        app = self._build_graph()
        result = app.invoke({"input": "X", "output": "", "count": 0})
        # step3 sets count to 3, meaning all 3 nodes ran
        assert result["count"] == 3


# ---------------------------------------------------------------------------
# Conditional Graph tests (even / odd)
# ---------------------------------------------------------------------------

class ConditionalState(TypedDict):
    number: int
    is_even: bool
    message: str


def check_number(state: ConditionalState) -> ConditionalState:
    state["is_even"] = state["number"] % 2 == 0
    return state


def even_handler(state: ConditionalState) -> ConditionalState:
    state["message"] = f"{state['number']} is even!"
    return state


def odd_handler(state: ConditionalState) -> ConditionalState:
    state["message"] = f"{state['number']} is odd!"
    return state


def route_number(state: ConditionalState) -> Literal["even", "odd"]:
    return "even" if state["is_even"] else "odd"


class TestConditionalGraph:
    """Test graph with conditional routing (even/odd)."""

    def _build_graph(self):
        workflow = StateGraph(ConditionalState)
        workflow.add_node("check", check_number)
        workflow.add_node("even_handler", even_handler)
        workflow.add_node("odd_handler", odd_handler)
        workflow.set_entry_point("check")
        workflow.add_conditional_edges(
            "check",
            route_number,
            {"even": "even_handler", "odd": "odd_handler"},
        )
        workflow.add_edge("even_handler", END)
        workflow.add_edge("odd_handler", END)
        return workflow.compile()

    def test_even_number(self):
        app = self._build_graph()
        result = app.invoke({"number": 4, "is_even": False, "message": ""})
        assert result["is_even"] is True
        assert result["message"] == "4 is even!"

    def test_odd_number(self):
        app = self._build_graph()
        result = app.invoke({"number": 7, "is_even": False, "message": ""})
        assert result["is_even"] is False
        assert result["message"] == "7 is odd!"

    @pytest.mark.parametrize("num,expected_even", [
        (0, True), (1, False), (2, True), (99, False), (100, True),
    ])
    def test_multiple_numbers(self, num, expected_even):
        app = self._build_graph()
        result = app.invoke({"number": num, "is_even": False, "message": ""})
        assert result["is_even"] is expected_even
        kind = "even" if expected_even else "odd"
        assert kind in result["message"]
