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
# Graph visualisation helpers
# ---------------------------------------------------------------------------
def _extract_nodes_and_edges(graph):
    """Extract node IDs and (source, target, label) tuples from a LangGraph graph.

    Handles multiple LangGraph API versions where nodes/edges may be
    strings, dicts, named tuples, or objects with attributes.
    """
    compiled = graph.compile() if isinstance(graph, StateGraph) else graph
    lg = compiled.get_graph()

    # --- nodes ---
    node_ids: list[str] = []
    if isinstance(lg.nodes, dict):
        node_ids = list(lg.nodes.keys())
    else:
        for n in lg.nodes:
            node_ids.append(n.id if hasattr(n, "id") else str(n))

    # --- edges ---
    edge_list: list[tuple[str, str, str]] = []
    for e in lg.edges:
        if isinstance(e, (list, tuple)):
            src, tgt = str(e[0]), str(e[1])
            lbl = str(e[2]) if len(e) > 2 else ""
        elif hasattr(e, "source"):
            src, tgt = str(e.source), str(e.target)
            lbl = str(e.data) if hasattr(e, "data") and e.data else ""
        else:
            continue
        edge_list.append((src, tgt, lbl))

    return node_ids, edge_list, compiled


# ---------------------------------------------------------------------------
# Graph visualisation
# ---------------------------------------------------------------------------
def generate_graph_image(graph, output_path: str = None) -> str:
    """Generate a PNG image of the LangGraph workflow using Mermaid (requires internet)."""
    if output_path is None:
        output_path = str(_script_dir / "multiagent_workflow_graph.png")

    compiled = graph.compile() if isinstance(graph, StateGraph) else graph

    print("📸 Generating graph image (Mermaid)...")
    png_bytes = compiled.get_graph().draw_mermaid_png()

    with open(output_path, "wb") as f:
        f.write(png_bytes)

    print(f"✅ Graph image saved to: {output_path}")
    return output_path


def generate_graph_networkx(graph, output_path: str = None) -> str:
    """Generate a PNG image using matplotlib + networkx (works offline, no external tools)."""
    import matplotlib
    matplotlib.use("Agg")                     # non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import networkx as nx

    if output_path is None:
        output_path = str(_script_dir / "multiagent_workflow_networkx.png")

    node_ids, edge_list, _ = _extract_nodes_and_edges(graph)

    G = nx.DiGraph()
    for nid in node_ids:
        G.add_node(nid)
    for src, tgt, lbl in edge_list:
        G.add_edge(src, tgt, label=lbl)

    # Agent-role colours
    colour_map = {
        "__start__": "#9E9E9E",
        "researcher": "#42A5F5",   # blue
        "writer": "#66BB6A",       # green
        "supervisor": "#FFA726",   # orange
        "__end__": "#9E9E9E",
    }
    node_colours = [colour_map.get(n, "#CE93D8") for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, seed=42, k=2.5)

    nx.draw_networkx_nodes(G, pos, node_color=node_colours, node_size=3000,
                           edgecolors="black", linewidths=1.5, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color="#555555", width=2,
                           arrows=True, arrowsize=25,
                           connectionstyle="arc3,rad=0.15", ax=ax)

    edge_labels = nx.get_edge_attributes(G, "label")
    edge_labels = {k: v for k, v in edge_labels.items() if v}
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8,
                                     font_color="#888888", ax=ax)

    legend_handles = [
        mpatches.Patch(color="#42A5F5", label="Researcher"),
        mpatches.Patch(color="#66BB6A", label="Writer"),
        mpatches.Patch(color="#FFA726", label="Supervisor"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", fontsize=9)

    ax.set_title("Multi-Agent Workflow", fontsize=14, fontweight="bold")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"✅ NetworkX graph image saved to: {output_path}")
    return output_path


def generate_graph_pyvis(graph, output_path: str = None) -> str:
    """Generate an interactive HTML graph using pyvis (open in browser)."""
    from pyvis.network import Network

    if output_path is None:
        output_path = str(_script_dir / "multiagent_workflow_pyvis.html")

    node_ids, edge_list, _ = _extract_nodes_and_edges(graph)

    net = Network(directed=True, height="600px", width="100%",
                  bgcolor="#ffffff", font_color="#333333")
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=200)

    colour_map = {
        "__start__": "#9E9E9E",
        "researcher": "#42A5F5",
        "writer": "#66BB6A",
        "supervisor": "#FFA726",
        "__end__": "#9E9E9E",
    }
    shape_map = {
        "__start__": "diamond",
        "__end__": "diamond",
    }

    for nid in node_ids:
        net.add_node(
            nid,
            label=nid,
            color=colour_map.get(nid, "#CE93D8"),
            shape=shape_map.get(nid, "ellipse"),
            size=30,
            font={"size": 16, "face": "arial", "bold": True},
        )

    for src, tgt, lbl in edge_list:
        net.add_edge(src, tgt, label=lbl,
                     arrows="to", color="#555555", width=2)

    net.write_html(output_path)
    print(f"✅ Interactive pyvis graph saved to: {output_path}")
    return output_path


def generate_graph_graphviz(graph, output_path: str = None) -> str:
    """Generate a PNG using Graphviz (requires 'graphviz' system install + Python package)."""
    import graphviz as gv

    if output_path is None:
        output_path = str(_script_dir / "multiagent_workflow_graphviz")

    node_ids, edge_list, _ = _extract_nodes_and_edges(graph)

    dot = gv.Digraph("MultiAgentWorkflow", format="png",
                      graph_attr={"rankdir": "TB", "bgcolor": "white",
                                  "fontname": "Helvetica", "pad": "0.5"},
                      node_attr={"style": "filled", "fontname": "Helvetica",
                                 "fontsize": "11", "shape": "box",
                                 "margin": "0.3,0.15"})

    colour_map = {
        "__start__": "#9E9E9E",
        "researcher": "#42A5F5",
        "writer": "#66BB6A",
        "supervisor": "#FFA726",
        "__end__": "#9E9E9E",
    }

    for nid in node_ids:
        shape = "diamond" if nid in ("__start__", "__end__") else "box"
        dot.node(nid, label=nid, fillcolor=colour_map.get(nid, "#CE93D8"),
                 fontcolor="white", shape=shape)

    for src, tgt, lbl in edge_list:
        dot.edge(src, tgt, label=lbl)

    dot.render(output_path, cleanup=True)
    final = output_path + ".png"
    print(f"✅ Graphviz image saved to: {final}")
    return final


def generate_all_graph_images(graph) -> list[str]:
    """Try all available visualisation methods; skip any whose deps are missing."""
    results = []
    attempts = [
        ("Mermaid",    generate_graph_image),
        ("NetworkX",   generate_graph_networkx),
        ("Pyvis",      generate_graph_pyvis),
        ("Graphviz",   generate_graph_graphviz),
    ]
    for name, fn in attempts:
        try:
            path = fn(graph)
            results.append(path)
        except ImportError as e:
            print(f"⏭️  Skipping {name} visualisation (missing dependency: {e})")
        except Exception as e:
            print(f"⚠️  {name} visualisation failed: {e}")
    return results


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

        # Generate graph visualisations using all available libraries
        print("\n📸 Generating workflow visualisations...")
        generated = generate_all_graph_images(app)
        print(f"   Generated {len(generated)} image(s)\n")

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
