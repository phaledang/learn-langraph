"""
LangGraph Multi-Agent Systems - Solution Code

A multi-agent system with researcher, writer, and supervisor agents
coordinated via a LangGraph StateGraph with conditional routing.

Uses Azure OpenAI when USE_AZURE_OPENAI=1 is set in .env, otherwise
falls back to standard OpenAI.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
import operator
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

_script_dir = Path(__file__).parent
load_dotenv(_script_dir / ".env")          # primary
  # fallback for defaults


# ---------------------------------------------------------------------------
# LLM helper – reads Azure OpenAI env vars from .env.sample / .env
# ---------------------------------------------------------------------------
def get_llm(temperature: float = 0.1) -> ChatOpenAI | AzureChatOpenAI:
    """Return an LLM instance configured from environment variables.

    When USE_AZURE_OPENAI=1, returns an AzureChatOpenAI backed by the
    deployment specified in AZURE_OPENAI_DEPLOYMENT.  Otherwise returns a
    standard ChatOpenAI instance.
    """
    if os.getenv("USE_AZURE_OPENAI", "0") == "1":
        return AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
            temperature=temperature,
        )
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature)


# ---------------------------------------------------------------------------
# Shared state schema
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    """Shared state passed between every agent in the graph."""
    messages: Annotated[List, operator.add]   # append-only message log
    next_agent: str                           # routing hint for conditional edges
    research_data: str                        # output of the researcher
    draft_content: str                        # output of the writer
    final_content: str                        # approved final article
    revision_count: int                       # guard against infinite loops


# ---------------------------------------------------------------------------
# Agent factories
# ---------------------------------------------------------------------------
MAX_REVISIONS = 2  # cap revision loops


def create_researcher_agent():
    """Create a research agent that gathers information on a topic."""

    def research_node(state: AgentState) -> dict:
        llm = get_llm(temperature=0.1)
        print("🔍 Researcher Agent: Starting research...")

        messages = state.get("messages", [])
        topic = messages[-1] if messages else "artificial intelligence"

        research_prompt = (
            f"You are a research agent. Research the topic: {topic}\n\n"
            "Provide key facts, statistics, and insights about this topic.\n"
            "Format your response as bullet points with key information.\n"
            "Keep it concise but informative (150-250 words)."
        )

        response = llm.invoke([SystemMessage(content=research_prompt)])
        research_data = response.content

        print(f"📊 Research completed on: {topic}")
        print(f"   Findings preview: {research_data[:120]}...")

        return {
            "messages": [f"Research completed on: {topic}"],
            "research_data": research_data,
            "next_agent": "writer",
        }

    return research_node


def create_writer_agent():
    """Create a writer agent that produces content from research."""

    def writer_node(state: AgentState) -> dict:
        llm = get_llm(temperature=0.3)
        print("✍️  Writer Agent: Creating content...")

        research_data = state.get("research_data", "")

        # If there was a revision request, include the supervisor feedback
        last_msg = (state.get("messages") or [""])[-1]
        revision_note = ""
        if "revision" in last_msg.lower() or "REVISION_NEEDED" in last_msg:
            revision_note = (
                f"\n\nThe supervisor requested a revision with this feedback:\n"
                f"{last_msg}\n"
                "Please address the feedback in your rewrite."
            )

        writing_prompt = (
            "You are a skilled content writer. Create an engaging article based on "
            "the following research:\n\n"
            f"Research Data:\n{research_data}\n\n"
            "Write a well-structured article with:\n"
            "- A compelling introduction\n"
            "- Main body with key points\n"
            "- A clear conclusion\n\n"
            "Keep it informative but readable. Aim for 200-300 words."
            f"{revision_note}"
        )

        response = llm.invoke([SystemMessage(content=writing_prompt)])
        draft_content = response.content

        print("📝 Draft content created")
        print(f"   Preview: {draft_content[:120]}...")

        return {
            "messages": ["Draft content created"],
            "draft_content": draft_content,
            "next_agent": "supervisor",
        }

    return writer_node


def create_supervisor_agent():
    """Create a supervisor agent that reviews and approves (or requests revision)."""

    def supervisor_node(state: AgentState) -> dict:
        llm = get_llm(temperature=0.1)
        print("👔 Supervisor Agent: Reviewing work...")

        research_data = state.get("research_data", "")
        draft_content = state.get("draft_content", "")
        revision_count = state.get("revision_count", 0)

        # Auto-approve after MAX_REVISIONS to avoid infinite loops
        if revision_count >= MAX_REVISIONS:
            print("⚠️  Max revisions reached – auto-approving.")
            return {
                "messages": [f"Supervisor auto-approved after {revision_count} revisions."],
                "final_content": draft_content,
                "next_agent": "END",
                "revision_count": revision_count,
            }

        review_prompt = (
            "You are a supervisor reviewing the work of a research and writing team.\n\n"
            f"Research Data:\n{research_data}\n\n"
            f"Draft Content:\n{draft_content}\n\n"
            "Review the quality and decide:\n"
            '1. If the work is complete and satisfactory, respond with "APPROVED: [brief feedback]"\n'
            '2. If it needs revision, respond with "REVISION_NEEDED: [specific feedback]"\n\n'
            "Be constructive and specific in your feedback."
        )

        response = llm.invoke([SystemMessage(content=review_prompt)])
        feedback = response.content

        print(f"📋 Supervisor feedback: {feedback[:120]}...")

        if "APPROVED" in feedback:
            print("✅ Work approved by supervisor!")
            return {
                "messages": [f"Supervisor approved: {feedback}"],
                "final_content": draft_content,
                "next_agent": "END",
                "revision_count": revision_count,
            }

        print("🔄 Revision requested by supervisor")
        return {
            "messages": [f"Supervisor requests revision: {feedback}"],
            "next_agent": "writer",
            "revision_count": revision_count + 1,
        }

    return supervisor_node


# ---------------------------------------------------------------------------
# Routing function
# ---------------------------------------------------------------------------
def should_continue(state: AgentState) -> str:
    """Return the next node name, or END to stop the graph."""
    next_agent = state.get("next_agent", "END")
    if next_agent == "END":
        return END
    return next_agent


# ---------------------------------------------------------------------------
# Graph builder (extracted so tests / callers can reuse it)
# ---------------------------------------------------------------------------
def build_multiagent_graph():
    """Build and compile the multi-agent LangGraph workflow.

    Flow:
        researcher ──▶ writer ──▶ supervisor ──┐
                        ▲                       │
                        └── (revision needed) ──┘
                                    │
                                    ▼
                                   END (approved)
    """
    workflow = StateGraph(AgentState)

    # 1. Add agent nodes
    workflow.add_node("researcher", create_researcher_agent())
    workflow.add_node("writer", create_writer_agent())
    workflow.add_node("supervisor", create_supervisor_agent())

    # 2. Entry point
    workflow.set_entry_point("researcher")

    # 3. Conditional edges driven by `next_agent` in state
    workflow.add_conditional_edges(
        "researcher",
        should_continue,
        {"writer": "writer", END: END},
    )
    workflow.add_conditional_edges(
        "writer",
        should_continue,
        {"supervisor": "supervisor", END: END},
    )
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {"writer": "writer", END: END},
    )

    return workflow.compile()


# ---------------------------------------------------------------------------
# Graph visualisation
# ---------------------------------------------------------------------------
def generate_graph_image(graph, output_path: str = None) -> str:
    """Generate a PNG image of the LangGraph workflow."""
    if output_path is None:
        output_path = str(Path(__file__).parent / "multiagent_workflow_graph.png")

    # Accept both compiled and uncompiled graphs
    compiled = graph.compile() if isinstance(graph, StateGraph) else graph

    print("📸 Generating graph image...")
    png_bytes = compiled.get_graph().draw_mermaid_png()

    with open(output_path, "wb") as f:
        f.write(png_bytes)

    print(f"✅ Graph image saved to: {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    """Main function demonstrating multi-agent coordination."""
    print("=" * 80)
    print("LangGraph Multi-Agent Systems - Solution")
    print("=" * 80)

    # Validate credentials
    use_azure = os.getenv("USE_AZURE_OPENAI", "0") == "1"
    if use_azure:
        if not os.getenv("AZURE_OPENAI_API_KEY"):
            print("❌ Error: AZURE_OPENAI_API_KEY not set")
            print("Copy .env.sample to .env and fill in your Azure OpenAI credentials.")
            return
        print(f"☁️  Using Azure OpenAI  |  Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
    else:
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY not set")
            print("Set OPENAI_API_KEY in your environment or .env file.")
            return
        print("🔑 Using OpenAI API")

    try:
        # Build & compile the graph
        app = build_multiagent_graph()

        # Generate graph visualisation (like lab06)
        generate_graph_image(
            app,
            str(Path(__file__).parent / "multiagent_workflow_graph.png"),
        )

        topic = "Machine Learning in Healthcare"
        print(f"\n🤖 Starting multi-agent workflow...")
        print(f"   Topic: {topic}")

        # Initial state
        initial_state: AgentState = {
            "messages": [topic],
            "next_agent": "researcher",
            "research_data": "",
            "draft_content": "",
            "final_content": "",
            "revision_count": 0,
        }

        print("\n" + "=" * 50)
        print("WORKFLOW EXECUTION")
        print("=" * 50)

        result = app.invoke(initial_state)

        print("\n" + "=" * 50)
        print("FINAL RESULTS")
        print("=" * 50)

        if result.get("final_content"):
            print("\n📄 FINAL APPROVED CONTENT:")
            print("-" * 40)
            print(result["final_content"])

        print("\n📊 Workflow Messages:")
        for i, msg in enumerate(result.get("messages", []), 1):
            print(f"   {i}. {msg}")

        print(f"\n🔄 Total revisions: {result.get('revision_count', 0)}")
        print("✅ Multi-agent workflow completed successfully!")

    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        print("Make sure you have the required dependencies installed:")
        print("   pip install langchain langchain-openai langgraph python-dotenv")


if __name__ == "__main__":
    main()
