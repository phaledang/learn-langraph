from __future__ import annotations

from typing import TypedDict, Optional, List, Dict, Any
from dataclasses import dataclass

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command


# -----------------------------
# State
# -----------------------------
class ReportState(TypedDict, total=False):
    run_id: str
    user_request: str

    # required inputs
    month: Optional[str]         # e.g. "2025-07"
    department: Optional[str]    # e.g. "DeptA"

    # selection results
    template_candidates: List[Dict[str, Any]]
    selected_template: Optional[Dict[str, Any]]

    file_candidates: List[Dict[str, Any]]
    selected_file: Optional[Dict[str, Any]]

    # extraction + render
    extracted_fields: Dict[str, Any]
    draft_path: Optional[str]

    # control
    approved: bool
    status: str
    error: Optional[str]


# -----------------------------
# Mock helpers (replace later)
# -----------------------------
def mock_template_search(user_request: str) -> List[Dict[str, Any]]:
    # return 0, 1, or multiple to test different paths
    return [
        {"id": "tpl-001", "name": "Monthly Report Template", "score": 0.88},
        {"id": "tpl-002", "name": "Monthly Report Template - Extended", "score": 0.85},
    ]


def mock_file_search(month: str, department: str) -> List[Dict[str, Any]]:
    return [
        {"id": "sp-101", "name": f"spending_month_{month.replace('-', '_')}.xlsx", "score": 0.86},
        {"id": "sp-102", "name": f"monthly_spending_{month.replace('-', '_')}.xlsx", "score": 0.84},
    ]


# -----------------------------
# Nodes (log only)
# -----------------------------
def node_collect_request(state: ReportState) -> ReportState:
    print("\n[collect_request] start")
    print(f"[collect_request] user_request={state.get('user_request')}")

    # If required info missing, interrupt and ask user
    if not state.get("month") or not state.get("department"):
        payload = {
            "type": "request_missing_inputs",
            "message": "Please provide missing inputs.",
            "missing": [
                k for k in ["month", "department"]
                if not state.get(k)
            ],
            "expected_format": {"month": "YYYY-MM", "department": "DeptA"},
        }
        print("[collect_request] missing inputs -> interrupt")
        reply = interrupt(payload)
        # reply example: {"month": "2025-07", "department": "DeptA"}
        state["month"] = reply.get("month") or state.get("month")
        state["department"] = reply.get("department") or state.get("department")

    print(f"[collect_request] resolved month={state.get('month')} department={state.get('department')}")
    return state


def node_suggest_templates(state: ReportState) -> ReportState:
    print("\n[suggest_templates] start")
    cands = mock_template_search(state.get("user_request", ""))
    state["template_candidates"] = cands
    print(f"[suggest_templates] found {len(cands)} candidates")

    if len(cands) == 0:
        state["status"] = "failed_no_template"
        state["error"] = "No template found. Flag admin to create new template."
        print("[suggest_templates] no template -> fail")
        return state

    if len(cands) == 1:
        state["selected_template"] = cands[0]
        print(f"[suggest_templates] auto selected template={cands[0]['name']}")
        return state

    # Multiple templates -> interrupt for confirmation
    payload = {
        "type": "confirm_template",
        "message": "Multiple templates match. Please select one.",
        "candidates": cands,
    }
    print("[suggest_templates] multiple templates -> interrupt")
    reply = interrupt(payload)
    # reply example: {"selected_id": "tpl-001"}
    sel_id = reply.get("selected_id")
    state["selected_template"] = next((t for t in cands if t["id"] == sel_id), None)
    print(f"[suggest_templates] selected_template={state.get('selected_template')}")
    return state


def node_stage_files(state: ReportState) -> ReportState:
    print("\n[stage_files] start")
    print("[stage_files] simulate: download SharePoint files and save attachments to workspace")
    # later: sp_download_file + save_upload_to_workspace
    return state


def node_load_guidelines(state: ReportState) -> ReportState:
    print("\n[load_guidelines] start")
    print("[load_guidelines] simulate: load guideline docs from Blob Storage and compile to execution plan")
    # later: blob_get_guideline + guideline_compiler
    return state


def node_discover_related_files(state: ReportState) -> ReportState:
    print("\n[discover_related_files] start")
    month = state.get("month") or ""
    dept = state.get("department") or ""
    cands = mock_file_search(month, dept)
    state["file_candidates"] = cands
    print(f"[discover_related_files] found {len(cands)} file candidates")

    if len(cands) == 0:
        state["status"] = "failed_no_file"
        state["error"] = "No source file found for extraction."
        print("[discover_related_files] no files -> fail")
        return state

    if len(cands) == 1:
        state["selected_file"] = cands[0]
        print(f"[discover_related_files] auto selected file={cands[0]['name']}")
        return state

    payload = {
        "type": "confirm_file",
        "message": "Multiple files match. Please choose the correct one.",
        "candidates": cands,
    }
    print("[discover_related_files] ambiguous files -> interrupt")
    reply = interrupt(payload)
    sel_id = reply.get("selected_id")
    state["selected_file"] = next((f for f in cands if f["id"] == sel_id), None)
    print(f"[discover_related_files] selected_file={state.get('selected_file')}")
    return state


def node_extract_sections(state: ReportState) -> ReportState:
    print("\n[extract_sections] start")
    print("[extract_sections] simulate: extract required sections from selected files using deterministic rules + LLM on small chunks")

    # Mock extraction output
    state["extracted_fields"] = {
        "TotalMonthlySpend": 123456.78,
        "TopRowsCount": 50,
        "Summary": "This is a mock summary extracted for the report draft."
    }
    print(f"[extract_sections] extracted_fields keys={list(state['extracted_fields'].keys())}")
    return state


def node_render_draft_report(state: ReportState) -> ReportState:
    print("\n[render_draft_report] start")
    print("[render_draft_report] simulate: render DOCX template placeholders using extracted fields")
    state["draft_path"] = f"/workspace/{state.get('run_id','run')}/draft_report.docx"
    print(f"[render_draft_report] draft_path={state['draft_path']}")
    return state


def node_user_review(state: ReportState) -> ReportState:
    print("\n[user_review] start")
    payload = {
        "type": "review_draft",
        "message": "Please review the draft. Approve or request changes.",
        "draft_path": state.get("draft_path"),
        "preview": state.get("extracted_fields", {}),
        "actions": ["approve", "revise"],
    }
    print("[user_review] waiting for user review -> interrupt")
    reply = interrupt(payload)
    # reply example: {"action": "approve"} or {"action": "revise", "notes": "..."}
    action = reply.get("action")

    if action == "approve":
        state["approved"] = True
        print("[user_review] user approved")
    else:
        state["approved"] = False
        notes = reply.get("notes", "(no notes)")
        print(f"[user_review] user requested revision: {notes}")

        # In a real flow you would update params or re-run extraction/render.
        # Here we just log and loop.
    return state


def node_publish_report(state: ReportState) -> ReportState:
    print("\n[publish_report] start")
    print("[publish_report] simulate: upload final DOCX to SharePoint, set permissions, trigger approval workflow, notify users")
    state["status"] = "completed"
    return state


# -----------------------------
# Routers
# -----------------------------
def route_after_templates(state: ReportState) -> str:
    if state.get("status") in ["failed_no_template"]:
        return "end_fail"
    if state.get("selected_template"):
        return "stage_files"
    return "end_fail"


def route_after_discover_files(state: ReportState) -> str:
    if state.get("status") in ["failed_no_file"]:
        return "end_fail"
    if state.get("selected_file"):
        return "extract_sections"
    return "end_fail"


def route_after_review(state: ReportState) -> str:
    if state.get("approved"):
        return "publish_report"
    return "extract_sections"  # simulate revision loop


# -----------------------------
# Build graph
# -----------------------------
def build_graph():
    g = StateGraph(ReportState)

    g.add_node("collect_request", node_collect_request)
    g.add_node("suggest_templates", node_suggest_templates)
    g.add_node("stage_files", node_stage_files)
    g.add_node("load_guidelines", node_load_guidelines)
    g.add_node("discover_related_files", node_discover_related_files)
    g.add_node("extract_sections", node_extract_sections)
    g.add_node("render_draft_report", node_render_draft_report)
    g.add_node("user_review", node_user_review)
    g.add_node("publish_report", node_publish_report)

    def end_fail(state: ReportState) -> ReportState:
        print("\n[end_fail] status=", state.get("status"), " error=", state.get("error"))
        return state

    g.add_node("end_fail", end_fail)

    g.set_entry_point("collect_request")
    g.add_edge("collect_request", "suggest_templates")
    g.add_conditional_edges("suggest_templates", route_after_templates, {"stage_files": "stage_files", "end_fail": "end_fail"})

    g.add_edge("stage_files", "load_guidelines")
    g.add_edge("load_guidelines", "discover_related_files")
    g.add_conditional_edges("discover_related_files", route_after_discover_files, {"extract_sections": "extract_sections", "end_fail": "end_fail"})

    g.add_edge("extract_sections", "render_draft_report")
    g.add_edge("render_draft_report", "user_review")
    g.add_conditional_edges("user_review", route_after_review, {"publish_report": "publish_report", "extract_sections": "extract_sections"})

    g.add_edge("publish_report", END)
    g.add_edge("end_fail", END)

    return g.compile()


# -----------------------------
# CLI runner with interrupts
# -----------------------------
def run_cli():
    graph = build_graph()

    # initial input (missing month/department on purpose to test interrupts)
    state: ReportState = {
        "run_id": "run-001",
        "user_request": "Generate monthly report for DeptA for July 2025",
        "month": None,
        "department": None,
        "approved": False,
        "status": "running",
    }

    # streaming lets us intercept interrupts and resume with Command(...)
    stream = graph.stream(state, stream_mode="values")

    for event in stream:
        # langgraph uses a special interrupt key in streamed values
        if "__interrupt__" in event:
            interrupts = event["__interrupt__"]
            print("\n=== INTERRUPT ===")
            print(interrupts)

            # Extract the first interrupt payload
            if interrupts and len(interrupts) > 0:
                payload = interrupts[0].value
            else:
                continue

            itype = payload.get("type")

            if itype == "request_missing_inputs":
                month = input("Enter month (YYYY-MM): ").strip()
                dept = input("Enter department: ").strip()
                stream = graph.stream(Command(resume={"month": month, "department": dept}), stream_mode="values")
                continue

            if itype == "confirm_template":
                cands = payload.get("candidates", [])
                for c in cands:
                    print(f"- {c['id']} | {c['name']} | score={c.get('score')}")
                sel = input("Select template id: ").strip()
                stream = graph.stream(Command(resume={"selected_id": sel}), stream_mode="values")
                continue

            if itype == "confirm_file":
                cands = payload.get("candidates", [])
                for c in cands:
                    print(f"- {c['id']} | {c['name']} | score={c.get('score')}")
                sel = input("Select file id: ").strip()
                stream = graph.stream(Command(resume={"selected_id": sel}), stream_mode="values")
                continue

            if itype == "review_draft":
                print("Draft preview:", payload.get("preview"))
                action = input("Action (approve/revise): ").strip().lower()
                if action != "approve":
                    notes = input("Revision notes: ").strip()
                    stream = graph.stream(Command(resume={"action": "revise", "notes": notes}), stream_mode="values")
                else:
                    stream = graph.stream(Command(resume={"action": "approve"}), stream_mode="values")
                continue

        # normal progress events (optional to print)
        # print("[state update]", {k: event.get(k) for k in ["status","approved","selected_template","selected_file"] if k in event})

    print("\n=== FLOW DONE ===")


if __name__ == "__main__":
    run_cli()
