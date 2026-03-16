# app/main.py
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List
import uuid

from .schemas import (
    ExtractionRuleCreate,
    ExtractionRuleRead,
    SearchRuleCreate,
    SearchRuleRead,
    ReportRunCreate,
    ReportRunStatus,
    UploadedFileRead,
)
from .graph_report import run_report_flow

# from .db import (
#     create_extraction_rule,
#     list_extraction_rules,
#     create_search_rule,
#     list_search_rules,
#     save_report_run,
#     get_report_run,
#     save_uploaded_file,
# )


app = FastAPI(title="Reporting Assistant API")


# ---------- Helper for auth (stub) ----------

def get_current_user():
    # TODO: wire real auth
    return "user1@corp.com"


# ---------- Assistant / Report Admin endpoints ----------

@app.post("/api/admin/report/extraction-rules", response_model=ExtractionRuleRead)
async def create_extraction_rule(
    body: ExtractionRuleCreate,
    current_user: str = Depends(get_current_user),
):
    # rule_id = create_extraction_rule(body, current_user)
    # rule = get_extraction_rule(rule_id)
    now = datetime.utcnow()
    # Stub:
    rule = ExtractionRuleRead(
        id=str(uuid.uuid4()),
        created_by=current_user,
        created_date=now,
        updated_date=now,
        **body.dict(),
    )
    return rule


@app.get("/api/admin/report/extraction-rules", response_model=List[ExtractionRuleRead])
async def list_extraction_rules(
    current_user: str = Depends(get_current_user),
):
    # rules = list_extraction_rules()
    # return rules
    return []  # stub


@app.post("/api/admin/report/search-rules", response_model=SearchRuleRead)
async def create_search_rule(
    body: SearchRuleCreate,
    current_user: str = Depends(get_current_user),
):
    now = datetime.utcnow()
    rule = SearchRuleRead(
        id=str(uuid.uuid4()),
        created_by=current_user,
        created_date=now,
        updated_date=now,
        **body.dict(),
    )
    return rule


@app.get("/api/admin/report/search-rules", response_model=List[SearchRuleRead])
async def list_search_rules(
    current_user: str = Depends(get_current_user),
):
    return []  # stub


# ---------- Report User endpoints ----------

@app.post("/api/reports/uploads", response_model=UploadedFileRead)
async def upload_runtime_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    # Save file to disk or blob storage
    content = await file.read()
    size_bytes = len(content)
    upload_id = f"upl_{uuid.uuid4()}"
    # local_path = save_uploaded_file(upload_id, content, file.content_type, current_user)
    now = datetime.utcnow()

    # Stub response
    return UploadedFileRead(
        id=upload_id,
        owner_user=current_user,
        original_name=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        created_date=now,
    )


@app.post("/api/reports/run", response_model=ReportRunStatus)
async def run_report(
    body: ReportRunCreate,
    current_user: str = Depends(get_current_user),
):
    run_id = f"run_{uuid.uuid4()}"

    # Optional: save a "pending" record to DB here
    # save_report_run(run_id, status="pending", ...)

    try:
        result_dict = run_report_flow(
            run_id=run_id,
            requested_by=current_user,
            req=body,
        )
        # save_report_run(run_id, **result_dict)
    except Exception as ex:
        now = datetime.utcnow()
        error_resp = ReportRunStatus(
            id=run_id,
            template_id=body.template_id,
            status="failed",
            requested_by=current_user,
            requested_date=now,
            parameters=body.parameters,
            uploaded_file_ids=body.uploaded_file_ids,
            placeholder_results={},
            final_report=None,
            error=str(ex),
            completed_date=now,
        )
        # save_report_run(run_id, **error_resp.dict())
        raise HTTPException(status_code=500, detail=str(ex))

    return ReportRunStatus(**result_dict)


@app.get("/api/reports/run/{run_id}", response_model=ReportRunStatus)
async def get_report_run_status(
    run_id: str,
    current_user: str = Depends(get_current_user),
):
    # run_doc = get_report_run(run_id)
    # if not run_doc: raise 404
    # return ReportRunStatus(**run_doc)
    raise HTTPException(status_code=404, detail="Not implemented yet")
