# app/schemas.py
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ---------- Extraction Rules ----------

class SectionLocator(BaseModel):
    type: Literal["semantic_section", "regex", "heading"]
    start_description: Optional[str] = None
    end_description: Optional[str] = None
    # for regex/heading strategies you can add more fields later


class ExtractionParameter(BaseModel):
    name: str
    type: Literal["string", "number", "date"]
    required: bool = True


class ExtractionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    input_document_type: str
    section_locator: SectionLocator
    extraction_prompt: str
    output_type: Literal["string", "number", "json"]
    parameters: List[ExtractionParameter] = Field(default_factory=list)


class ExtractionRuleRead(ExtractionRuleCreate):
    id: str
    created_by: str
    created_date: datetime
    updated_date: datetime


# ---------- Search Rules ----------

class SearchRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: Optional[str] = None
    source_id: str
    selection_strategy: Literal["file_pattern", "metadata", "semantic_search"]
    file_pattern_template: Optional[str] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    search_index_id: Optional[str] = None


class SearchRuleRead(SearchRuleCreate):
    id: str
    created_by: str
    created_date: datetime
    updated_date: datetime


# ---------- Report Templates ----------

class TemplatePlaceholderConfig(BaseModel):
    name: str
    placeholder_text: str
    # Either use a search_rule + extraction_rule...
    search_rule_id: Optional[str] = None
    extraction_rule_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    runtime_parameters: List[str] = Field(default_factory=list)

    # ...or directly from uploaded files with a section locator:
    source: Optional[Literal["uploaded_files"]] = None
    section_locator: Optional[SectionLocator] = None


class TemplateLocation(BaseModel):
    source_type: Literal["sharepoint"]
    site_url: str
    path: str
    auth_profile: Optional[str] = None


class ReportTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_location: TemplateLocation
    placeholders: List[TemplatePlaceholderConfig]


class ReportTemplateRead(ReportTemplateCreate):
    id: str
    created_by: str
    created_date: datetime
    updated_date: datetime


# ---------- Uploaded Files ----------

class UploadedFileRead(BaseModel):
    id: str
    owner_user: str
    original_name: str
    content_type: str
    size_bytes: int
    created_date: datetime


# ---------- Report Run ----------

class ReportRunMode(str):
    TEST = "test"
    FINAL = "final"


class ReportRunCreate(BaseModel):
    template_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    uploaded_file_ids: List[str] = Field(default_factory=list)
    mode: Literal["test", "final"] = "test"


class PlaceholderResult(BaseModel):
    value: Any
    source_doc: Dict[str, Any]
    debug: Dict[str, Any] = Field(default_factory=dict)


class FinalReportInfo(BaseModel):
    sharepoint_url: Optional[str] = None
    file_name: Optional[str] = None


class ReportRunStatus(BaseModel):
    id: str
    template_id: str
    status: Literal["pending", "running", "failed", "completed"]
    requested_by: str
    requested_date: datetime
    parameters: Dict[str, Any]
    uploaded_file_ids: List[str]
    placeholder_results: Dict[str, PlaceholderResult] = Field(default_factory=dict)
    final_report: Optional[FinalReportInfo] = None
    error: Optional[str] = None
    completed_date: Optional[datetime] = None
