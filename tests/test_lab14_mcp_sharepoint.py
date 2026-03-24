"""
Tests for Lab 14: MCP SharePoint – Report Flow

Covers:
- Pydantic schema models (ExtractionRuleCreate, SearchRuleCreate, etc.)
- ReportState TypedDict
- Graph node functions (pure logic)
- Routing functions
- Graph construction and execution
"""

import sys
import os
import pytest
from typing import Dict, Any, List, Optional
from typing_extensions import Literal
from datetime import datetime

# Ensure lab14-mcp-sharepoint is importable
LAB14_SP_DIR = os.path.join(
    os.path.dirname(__file__), "..", "labs", "lab14-mcp-sharepoint"
)
if LAB14_SP_DIR not in sys.path:
    sys.path.insert(0, LAB14_SP_DIR)


# ---------------------------------------------------------------------------
# Schema model tests
# ---------------------------------------------------------------------------

class TestSchemas:
    """Test pydantic schema models from lab14-mcp-sharepoint."""

    def test_extraction_rule_create(self):
        from schemas import ExtractionRuleCreate, SectionLocator

        rule = ExtractionRuleCreate(
            name="Test Rule",
            input_document_type="pdf",
            section_locator=SectionLocator(type="heading"),
            extraction_prompt="Extract data from heading",
            output_type="string",
        )
        assert rule.name == "Test Rule"
        assert rule.output_type == "string"

    def test_search_rule_create(self):
        from schemas import SearchRuleCreate

        rule = SearchRuleCreate(
            name="Find Monthly Reports",
            source_id="src-1",
            selection_strategy="file_pattern",
            file_pattern_template="monthly_*.xlsx",
        )
        assert rule.selection_strategy == "file_pattern"

    def test_report_run_create(self):
        from schemas import ReportRunCreate

        run = ReportRunCreate(
            template_id="tpl-001",
            parameters={"month": "2025-07"},
            mode="test",
        )
        assert run.template_id == "tpl-001"
        assert run.mode == "test"

    def test_placeholder_result(self):
        from schemas import PlaceholderResult

        pr = PlaceholderResult(
            value="123.45",
            source_doc={"name": "file.xlsx"},
            debug={"note": "ok"},
        )
        assert pr.value == "123.45"

    def test_final_report_info(self):
        from schemas import FinalReportInfo

        info = FinalReportInfo(
            sharepoint_url="https://sp.example.com/report.docx",
            file_name="report.docx",
        )
        assert info.sharepoint_url.startswith("https://")

    def test_uploaded_file_read(self):
        from schemas import UploadedFileRead

        f = UploadedFileRead(
            id="upl_1",
            owner_user="user@corp.com",
            original_name="data.xlsx",
            content_type="application/vnd.ms-excel",
            size_bytes=1024,
            created_date=datetime.utcnow(),
        )
        assert f.size_bytes == 1024


# ---------------------------------------------------------------------------
# Report flow graph demo – ReportState and node logic
# ---------------------------------------------------------------------------

class ReportState(dict):
    """Minimal ReportState for testing routing functions."""
    pass


class TestReportFlowRouting:
    """Test routing functions from report_flow_demo.py."""

    def test_route_after_templates_success(self):
        from report_flow_demo import route_after_templates

        state = {"selected_template": {"id": "tpl-001"}, "status": "running"}
        assert route_after_templates(state) == "stage_files"

    def test_route_after_templates_failure(self):
        from report_flow_demo import route_after_templates

        state = {"selected_template": None, "status": "failed_no_template"}
        assert route_after_templates(state) == "end_fail"

    def test_route_after_discover_files_success(self):
        from report_flow_demo import route_after_discover_files

        state = {"selected_file": {"id": "f1"}, "status": "running"}
        assert route_after_discover_files(state) == "extract_sections"

    def test_route_after_discover_files_failure(self):
        from report_flow_demo import route_after_discover_files

        state = {"selected_file": None, "status": "failed_no_file"}
        assert route_after_discover_files(state) == "end_fail"

    def test_route_after_review_approve(self):
        from report_flow_demo import route_after_review

        state = {"approved": True}
        assert route_after_review(state) == "publish_report"

    def test_route_after_review_revise(self):
        from report_flow_demo import route_after_review

        state = {"approved": False}
        assert route_after_review(state) == "extract_sections"


# ---------------------------------------------------------------------------
# Mock search helpers
# ---------------------------------------------------------------------------

class TestMockSearchHelpers:
    def test_mock_template_search(self):
        from report_flow_demo import mock_template_search

        results = mock_template_search("monthly report")
        assert len(results) >= 1
        assert "id" in results[0]
        assert "name" in results[0]

    def test_mock_file_search(self):
        from report_flow_demo import mock_file_search

        results = mock_file_search("2025-07", "DeptA")
        assert len(results) >= 1
        assert "id" in results[0]


# ---------------------------------------------------------------------------
# Node function tests (pure logic, no interrupts)
# ---------------------------------------------------------------------------

class TestNodeFunctions:
    def test_extract_sections(self):
        from report_flow_demo import node_extract_sections

        state = {"selected_file": {"id": "f1"}, "extracted_fields": {}}
        result = node_extract_sections(state)
        assert "TotalMonthlySpend" in result["extracted_fields"]
        assert "Summary" in result["extracted_fields"]

    def test_render_draft_report(self):
        from report_flow_demo import node_render_draft_report

        state = {
            "run_id": "run-test",
            "extracted_fields": {"Total": 100},
            "draft_path": None,
        }
        result = node_render_draft_report(state)
        assert result["draft_path"] is not None
        assert "run-test" in result["draft_path"]

    def test_publish_report(self):
        from report_flow_demo import node_publish_report

        state = {"status": "running"}
        result = node_publish_report(state)
        assert result["status"] == "completed"
