# LangGraph Multi-Agent Systems

## Learning Objectives
Coordinate multiple agents, implement agent communication, build supervisor patterns, handle agent collaboration

## Prerequisites
- Completion of previous labs (especially Lab 06 – Stateful Applications)
- Understanding of `StateGraph`, conditional edges, and state schemas

## Lab Overview
In this lab, you will build practical applications demonstrating LangGraph multi-agent systems.  
Where Lab 06 focused on a **single stateful workflow** (document analysis → approval → revision), Lab 07 introduces **multiple autonomous agents** that collaborate through a **supervisor pattern**.

---

## Key Differences from Lab 06 (Stateful Applications)

### 1. Architecture — Single Workflow vs. Multi-Agent Collaboration

| Aspect | Lab 06 – Stateful | Lab 07 – Multi-Agent |
|---|---|---|
| **Design pattern** | One monolithic workflow with functional nodes | Multiple specialized agents coordinated by a supervisor |
| **Nodes** | Task-oriented functions (`initialize_workflow`, `analyze_document`, `request_human_approval`, `finalize_workflow`, …) | Agent-oriented roles (`researcher`, `writer`, `supervisor`) |
| **Number of nodes** | 10 nodes (initialize, analyze, quality_check, compliance_check, security_check, merge_results, request_approval, process_decision, revise, finalize) | 3 agent nodes (researcher, writer, supervisor) |
| **Node creation** | Plain functions defined at module level | **Agent factory pattern** — `create_researcher_agent()`, `create_writer_agent()`, `create_supervisor_agent()` return closures |

### 2. State Schema

**Lab 06** uses a rich, metadata-heavy state with timestamps, workflow IDs, and nested dicts:

```python
class WorkflowState(TypedDict):
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
```

**Lab 07** uses a lean, agent-oriented state with an **append-only message log** via `operator.add`:

```python
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]   # reducer — messages accumulate
    next_agent: str                           # routing hint
    research_data: str                        # researcher output
    draft_content: str                        # writer output
    final_content: str                        # approved final content
    revision_count: int                       # loop guard
```

Key difference: Lab 07 introduces the **reducer pattern** (`Annotated[List, operator.add]`) so each agent appends to the message log without overwriting previous entries.

### 3. Routing & Control Flow

| Aspect | Lab 06 | Lab 07 |
|---|---|---|
| **Entry point** | `workflow.add_edge(START, "initialize")` | `workflow.set_entry_point("researcher")` |
| **Routing mechanism** | Multiple dedicated router functions (`should_request_approval`, `approval_decision_router`, `revision_limit_check`) with `Literal` return types | Single `should_continue()` function reads `next_agent` from state |
| **Routing decision** | Made by external router functions | Made **by the agents themselves** — each agent sets `next_agent` in its return dict |
| **Revision loop** | `revise` → `analyze` → … (limit 3) | `supervisor` → `writer` → `supervisor` (limit `MAX_REVISIONS = 2`) |

**Lab 06 flow:**
```
START → initialize → analyze → quality_check → compliance_check → security_check
  → merge_results → request_approval → process_decision → finalize → END
                                                       ↘ revise ↗
```

**Lab 07 flow:**
```
researcher → writer → supervisor ──┐
               ▲                    │
               └── (revision) ─────┘
                        │
                        ▼
                       END (approved)
```

### 4. Agent Autonomy & LLM Usage

| Aspect | Lab 06 | Lab 07 |
|---|---|---|
| **LLM calls** | A single `get_llm()` with fixed temperature (`0.1`) | Each agent uses `get_llm(temperature=...)` with **different temperatures** (researcher: 0.1, writer: 0.3, supervisor: 0.1) |
| **System prompts** | Generic analysis prompts | Each agent has a **distinct persona** via its system prompt (research expert, skilled writer, quality supervisor) |
| **Decision making** | Routing functions decide the next step | The **supervisor agent** uses the LLM to decide APPROVED vs. REVISION_NEEDED |

### 5. Features Present in Lab 06 but Not in Lab 07

| Feature | Lab 06 | Lab 07 |
|---|---|---|
| **Checkpointing** | ✅ `MemorySaver` with `thread_id` config | ❌ Not used |
| **Human-in-the-loop** | ✅ `request_human_approval` interrupt point | ❌ Not used (supervisor is an LLM agent) |
| **Parallel processing** | ✅ Quality, compliance, security analysis nodes | ❌ Sequential agent pipeline |
| **Document approval system** | ✅ Separate `DocumentApprovalState` workflow | ❌ Single workflow only |
| **State metadata** | ✅ Timestamps, workflow IDs, nested metadata | ❌ Minimal state |

### 6. Features New in Lab 07

| Feature | Description |
|---|---|
| **Agent factory pattern** | Functions that return closures, encapsulating agent behavior |
| **Supervisor pattern** | A dedicated agent that reviews output and decides to approve or request revision |
| **Reducer-based state** | `operator.add` on the messages list so agents append without overwriting |
| **Agent-driven routing** | Agents set `next_agent` in their return dict; the graph reads it for routing |
| **Multi-provider LLM support** | Supports both Azure OpenAI (`USE_AZURE_OPENAI=1`) and standard OpenAI |
| **Rich graph visualization** | Four visualization backends: Mermaid, NetworkX, Pyvis (interactive HTML), Graphviz |
| **MAX_REVISIONS guard** | Auto-approve after N revisions to prevent infinite loops |

### 7. Side-by-Side Code Comparison

The table below compares the **actual code patterns** that make Lab 06 a single-workflow approach and Lab 07 a multi-agent system.

#### State Definition

| Concept | Lab 06 — Single Workflow | Lab 07 — Multi-Agent |
|---|---|---|
| **State class** | `WorkflowState(TypedDict)` — 10 fields | `AgentState(TypedDict)` — 6 fields |
| **Messages field** | `messages: Annotated[List[Dict[str, Any]], "..."]` — plain list of dicts, each node **overwrites** the whole list | `messages: Annotated[List, operator.add]` — **reducer** pattern, each agent **appends** |
| **Routing field** | `current_step: str` + `approval_status: str` — two separate fields read by external routers | `next_agent: str` — single field **set by the agent itself** |
| **Agent output fields** | None — all nodes write to the same `document_content` / `reviewer_feedback` | Separate fields per agent: `research_data`, `draft_content`, `final_content` |
| **Metadata** | `workflow_metadata: Dict`, `last_updated: str`, `human_input_required: bool` | None — agents carry only what they need |

#### Node / Agent Creation

| Concept | Lab 06 — Single Workflow | Lab 07 — Multi-Agent |
|---|---|---|
| **How nodes are defined** | Plain top-level functions: `def analyze_document(state): ...` | **Factory functions** returning closures: `def create_researcher_agent(): def research_node(state): ... return research_node` |
| **Node responsibility** | Each node does **one task** (initialize, analyze, check compliance, merge, finalize) | Each agent is **autonomous** — researches, writes, or reviews + decides the next step |
| **Node return value** | Returns the **entire mutated state** (`return state`) | Returns a **partial dict** with only the changed keys (`return {"messages": [...], "next_agent": "writer", ...}`) |
| **LLM configuration** | Single `get_llm()` → fixed `temperature=0.1` | Per-agent temperature: `get_llm(temperature=0.1)` for researcher, `get_llm(temperature=0.3)` for writer |
| **System prompt / persona** | Generic prompts: `"Analyze the following document..."` | Distinct personas: `"You are a research agent..."`, `"You are a skilled content writer..."`, `"You are a supervisor reviewing..."` |

#### Routing Logic

| Concept | Lab 06 — Single Workflow | Lab 07 — Multi-Agent |
|---|---|---|
| **Number of router functions** | 3 separate functions (`should_request_approval`, `approval_decision_router`, `revision_limit_check`) | 1 function: `should_continue(state)` |
| **Router return type** | `Literal["approval", "parallel"]`, `Literal["approved", "revision", "rejected"]` — router **decides** | `str` — router just **reads** `state["next_agent"]` |
| **Who decides the next step** | **Router functions** inspect state and pick the path | **Each agent** sets `next_agent` in its return dict (e.g., `"next_agent": "writer"`) |
| **Revision guard** | `if state["revision_count"] >= 3: return "rejected"` (in router) | `if revision_count >= MAX_REVISIONS:` auto-approve (inside supervisor agent) |

#### Graph Construction

| Concept | Lab 06 — Single Workflow | Lab 07 — Multi-Agent |
|---|---|---|
| **Entry point** | `workflow.add_edge(START, "initialize")` | `workflow.set_entry_point("researcher")` |
| **Edge style** | Mix of `add_edge()` (fixed) + `add_conditional_edges()` | **All edges are conditional** — every node uses `add_conditional_edges` with `should_continue` |
| **Edge map example** | `{"parallel": "quality_check", "approval": "request_approval"}` — hard-coded task names | `{"writer": "writer", END: END}` — agent names as routing targets |
| **Compile** | `workflow.compile(checkpointer=memory)` — with `MemorySaver` | `workflow.compile()` — no checkpointer needed |
| **Invocation config** | `app.invoke(state, {"configurable": {"thread_id": "..."}})` | `app.invoke(state)` — no thread config |

#### How the Supervisor Pattern Works (Lab 07 Only)

| Step | What Happens | Code |
|---|---|---|
| 1. Researcher runs | Gathers facts, sets `next_agent: "writer"` | `return {"research_data": data, "next_agent": "writer"}` |
| 2. Writer runs | Creates article from research, sets `next_agent: "supervisor"` | `return {"draft_content": content, "next_agent": "supervisor"}` |
| 3. Supervisor reviews | LLM decides `APPROVED` or `REVISION_NEEDED` | If approved → `"next_agent": "END"`, if revision → `"next_agent": "writer"` |
| 4. Loop or finish | `should_continue()` reads `next_agent` and routes accordingly | `if next_agent == "END": return END` |

#### Why Lab 06 Uses One Workflow (Not Multiple Agents)

| Reason | Explanation |
|---|---|
| **Single domain** | All nodes operate on the same document — no need for specialized expertise |
| **Centralized control** | The graph itself controls routing; nodes are passive workers |
| **Parallel processing** | Multiple analysis nodes (quality, compliance, security) run on the **same input** — they're parallel tasks, not collaborating agents |
| **Human-in-the-loop** | Requires interrupts and checkpointing — agents don't pause for human input |
| **Predictable flow** | The workflow follows a fixed pipeline: init → analyze → check → approve → finalize |

#### Why Lab 07 Uses Multiple Agents

| Reason | Explanation |
|---|---|
| **Specialized roles** | Each agent has a distinct skill: research, writing, quality review |
| **Agent autonomy** | Each agent decides what happens next by setting `next_agent` |
| **Supervisor pattern** | The supervisor uses **LLM reasoning** to approve or request revision — not a hard-coded rule |
| **Emergent behavior** | The number of revision loops depends on the LLM's judgment, not a fixed condition |
| **Composability** | New agents (editor, fact-checker, translator) can be added by creating a factory + adding one node + one conditional edge |
| **Isolation** | Each agent's output goes into a dedicated state field (`research_data`, `draft_content`) — no shared mutation |

### 8. Summary

> **Lab 06** teaches you how to build **complex stateful workflows** — checkpointing, human-in-the-loop, parallel processing, and document approval chains. It uses a **single workflow** because all nodes work on the same document and routing is centrally controlled.
>
> **Lab 07** shifts the focus to **agent collaboration** — each node is an autonomous agent with its own persona, temperature, and decision-making ability, coordinated by a supervisor agent through a shared state and reducer pattern. It uses **multiple agents** because the task (research → write → review) benefits from specialized roles with LLM-driven coordination.

---

## Tasks
Create multiple agents, Build supervisor, Implement communication, Handle conflicts, Create collaborative workflow

## Expected Outcomes
- Master LangGraph multi-agent systems
- Build production-ready applications
- Understand best practices
- Know when to choose a multi-agent design over a monolithic stateful workflow

## Resources
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Multi-Agent Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)

## Next Steps
Proceed to **Lab 08: LangGraph Persistence**.
