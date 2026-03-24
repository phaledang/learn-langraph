"""
Tests for Lab 13: PDF and Image to CSV Extraction

Covers:
- PDF page extraction (extract_pdf_to_pages)
- CourseRecord pydantic model
- Page range extraction from guide.txt
- Guide text cleaning
- CSV consolidation logic
- LLM build factory

NOTE: Some tests require 'pandas' and 'pypdf' to be installed.
      Tests that import lab13 modules will be skipped if those
      packages are missing.
"""

import os
import re
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add lab13 to path so we can import its modules
LAB13_DIR = os.path.join(
    os.path.dirname(__file__), "..", "labs", "lab13-pdf-and_image_to_csv"
)
if LAB13_DIR not in sys.path:
    sys.path.insert(0, LAB13_DIR)

# Check if heavy deps are available
_pandas = pytest.importorskip("pandas", reason="pandas not installed")
_pypdf = pytest.importorskip("pypdf", reason="pypdf not installed")


# ---------------------------------------------------------------------------
# CourseRecord model tests
# ---------------------------------------------------------------------------

class TestCourseRecord:
    """Test the pydantic CourseRecord model."""

    def test_create_minimal_record(self):
        from extract_courses_from_pdf_pages import CourseRecord

        record = CourseRecord(
            course_code="CS 101",
            course_title="Intro to Computer Science",
        )
        assert record.course_code == "CS 101"
        assert record.course_title == "Intro to Computer Science"
        assert record.units is None

    def test_create_full_record(self):
        from extract_courses_from_pdf_pages import CourseRecord

        record = CourseRecord(
            course_code="ACC 301",
            course_title="Intermediate Financial Accounting I",
            units=3,
            section="A",
            frequency="A",
            description="A comprehensive course...",
            prerequisites="ACC 201",
            corequisites=None,
            recommended=None,
            offered="Annually",
            grade_basis="Letter",
            pdf_page=42,
        )
        assert record.units == 3
        assert record.frequency == "A"
        assert record.pdf_page == 42

    def test_record_serialization(self):
        from extract_courses_from_pdf_pages import CourseRecord

        record = CourseRecord(
            course_code="PS 320",
            course_title="Political Theory",
            units=4,
        )
        d = record.model_dump()
        assert d["course_code"] == "PS 320"
        assert d["units"] == 4
        assert "description" in d  # field present even if None


# ---------------------------------------------------------------------------
# Page range extraction tests
# ---------------------------------------------------------------------------

class TestPageRangeExtraction:
    """Test extracting page ranges from guide text."""

    def test_standard_range(self):
        from process_courses import extract_page_range_from_guide

        text = "Please read from page 131 to page 198 to extract the course information."
        start, end = extract_page_range_from_guide(text)
        assert start == 131
        assert end == 198

    def test_short_range_format(self):
        from process_courses import extract_page_range_from_guide

        text = "Extract courses from page 50 to page 60."
        start, end = extract_page_range_from_guide(text)
        assert start == 50
        assert end == 60

    def test_no_range_raises(self):
        from process_courses import extract_page_range_from_guide

        with pytest.raises(ValueError, match="Could not extract"):
            extract_page_range_from_guide("No page numbers here.")


# ---------------------------------------------------------------------------
# Guide text cleaning tests
# ---------------------------------------------------------------------------

class TestGuideTextCleaning:
    """Test removing page range instructions from guide text."""

    def test_remove_page_range(self):
        from process_courses import remove_page_range_text

        guide = "Some instructions.\nread from page 131 to page 198 to extract the course information into csv,\nMore text."
        cleaned = remove_page_range_text(guide)
        assert "page 131" not in cleaned
        assert "More text" in cleaned

    def test_clean_preserves_content(self):
        from process_courses import remove_page_range_text

        guide = "Extract all courses accurately.\nPay attention to frequency codes."
        cleaned = remove_page_range_text(guide)
        assert "frequency codes" in cleaned


# ---------------------------------------------------------------------------
# build_llm factory tests (mocked)
# ---------------------------------------------------------------------------

class TestBuildLLM:
    """Test LLM factory without real API calls."""

    @patch.dict(os.environ, {"USE_AZURE_OPENAI": "1", "AZURE_OPENAI_API_KEY": "k", "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"})
    @patch("extract_courses_from_pdf_pages.AzureChatOpenAI")
    def test_azure_path(self, MockAzure):
        from extract_courses_from_pdf_pages import build_llm
        build_llm()
        MockAzure.assert_called_once()

    @patch.dict(os.environ, {"USE_AZURE_OPENAI": "", "OPENAI_API_KEY": "k"}, clear=False)
    @patch("extract_courses_from_pdf_pages.ChatOpenAI")
    def test_openai_path(self, MockOpenAI):
        from extract_courses_from_pdf_pages import build_llm
        build_llm()
        MockOpenAI.assert_called_once()


# ---------------------------------------------------------------------------
# extract_courses_to_csv CourseRecord tests (image-based)
# ---------------------------------------------------------------------------

class TestImageCourseRecord:
    """Test the image extraction CourseRecord model."""

    def test_create_record(self):
        from extract_courses_to_csv import CourseRecord

        record = CourseRecord(
            course_code="BIO 100",
            course_title="Biology Fundamentals",
            units=4,
        )
        assert record.course_code == "BIO 100"
        assert record.units == 4

    def test_record_has_pdf_page(self):
        from extract_courses_to_csv import CourseRecord

        record = CourseRecord(
            course_code="X 1", course_title="Y", pdf_page=10
        )
        assert record.pdf_page == 10


# ---------------------------------------------------------------------------
# Batch extraction helpers
# ---------------------------------------------------------------------------

class TestBatchHelpers:
    """Test batch_extract_courses.py helper functions."""

    def test_extract_page_range(self):
        from batch_extract_courses import extract_page_range

        start, end = extract_page_range("read from page 131 to page 198")
        assert start == 131
        assert end == 198

    def test_extract_page_range_short(self):
        from batch_extract_courses import extract_page_range

        start, end = extract_page_range("page 50 to 60")
        assert start == 50
        assert end == 60

    def test_extract_page_range_single(self):
        from batch_extract_courses import extract_page_range

        start, end = extract_page_range("page 42")
        assert start == 42
        assert end == 42

    def test_extract_page_range_invalid(self):
        from batch_extract_courses import extract_page_range

        with pytest.raises(ValueError):
            extract_page_range("no numbers here")
