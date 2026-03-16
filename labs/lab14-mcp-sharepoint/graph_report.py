# app/graph_report.py
from typing import TypedDict, Dict, Any, List
from datetime import datetime

from langgraph.graph import StateGraph, END

from schemas import ReportRunCreate, PlaceholderResult, FinalReportInfo
# from .db import get_template_by_id, get_search_rule, get_extraction_rule, get_uploaded_files
# from .mcp_clients import sharepoint_client, pdf_docx_client
# from .extraction_chains import run_extraction_llm


class ReportState(TypedDict, total=False):
    run_id: str
    template_id: str
    requested_by: str
    parameters: Dict[str, Any]
    uploaded_file_ids: List[str]
    template_config: Dict[str, Any]
    placeholder_results: Dict[str, Any]
    final_report_path: str
    final_report_url: str
    error: str


# ----- Node implementations (very stubbed, you will fill MCP/DB details) -----

def load_template_node(state: ReportState) -> ReportState:
    template_id = state["template_id"]
    # TODO: load from DB
    template_doc = get_template_by_id(template_id)  # your own function
    state["template_config"] = template_doc
    return state


def resolve_placeholders_node(state: ReportState) -> ReportState:
    template = state["template_config"]
    placeholders = template.get("placeholders", [])
    placeholder_results = {}

    for ph in placeholders:
        name = ph["name"]

        # Very simplified: you will:
        # 1) find docs via search_rule
        # 2) locate section via MCP
        # 3) run LLM extraction

        # For now, stub it:
        placeholder_results[name] = {
            "value": f"[[TEST VALUE for {name}]]",
            "source_doc": {"info": "stub"},
            "debug": {"note": "replace with real search + extraction pipeline"}
        }

    state["placeholder_results"] = placeholder_results
    return state


def generate_docx_node(state: ReportState) -> ReportState:
    # 1. Download template docx via SharePoint MCP
    # 2. Fill placeholders via DOCX MCP
    # 3. Save local path + optionally upload

    # For now stub:
    state["final_report_path"] = f"/tmp/{state['run_id']}.docx"
    state["final_report_url"] = "https://sharepoint.example.com/fake-url"
    return state


def build_report_graph():
    graph = StateGraph(ReportState)

    graph.add_node("load_template", load_template_node)
    graph.add_node("resolve_placeholders", resolve_placeholders_node)
    graph.add_node("generate_docx", generate_docx_node)

    graph.set_entry_point("load_template")
    graph.add_edge("load_template", "resolve_placeholders")
    graph.add_edge("resolve_placeholders", "generate_docx")
    graph.add_edge("generate_docx", END)

    return graph.compile()


compiled_report_graph = build_report_graph()


def run_report_flow(
    run_id: str,
    requested_by: str,
    req: ReportRunCreate
) -> Dict[str, Any]:
    """
    Synchronous helper that runs the LangGraph flow and returns a result
    that can be mapped to ReportRunStatus.
    """
    initial_state: ReportState = {
        "run_id": run_id,
        "template_id": req.template_id,
        "requested_by": requested_by,
        "parameters": req.parameters,
        "uploaded_file_ids": req.uploaded_file_ids,
    }

    final_state = compiled_report_graph.invoke(initial_state)

    # Map to status dict
    now = datetime.utcnow()
    placeholder_results = {
        name: PlaceholderResult(
            value=data["value"],
            source_doc=data.get("source_doc", {}),
            debug=data.get("debug", {})
        ).dict()
        for name, data in final_state.get("placeholder_results", {}).items()
    }

    status = {
        "id": run_id,
        "template_id": req.template_id,
        "status": "completed",
        "requested_by": requested_by,
        "requested_date": now,
        "parameters": req.parameters,
        "uploaded_file_ids": req.uploaded_file_ids,
        "placeholder_results": placeholder_results,
        "final_report": FinalReportInfo(
            sharepoint_url=final_state.get("final_report_url"),
            file_name=None  # set real name when you know it
        ).dict(),
        "error": None,
        "completed_date": now,
    }
    return status
