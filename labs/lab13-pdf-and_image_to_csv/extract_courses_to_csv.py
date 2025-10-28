import base64
import json
import os
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

from PIL import Image

# Load environment variables from .env file
load_dotenv()

# LangChain
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.messages import HumanMessage

# Optional OCR fallback (only used if LLM fails and OCR is enabled)
USE_OCR_FALLBACK = False
try:
    import pytesseract  # noqa
    USE_OCR_FALLBACK = True
except Exception:
    pass


# ---------- 1) Pydantic schema for structured extraction ----------
class CourseRecord(BaseModel):
    course_code: str = Field(..., description="Course code, e.g., 'ACC 301' or 'PS 320'")
    course_title: str = Field(..., description="Short human title, e.g., 'Intermediate Financial Accounting I'")
    units: Optional[int] = Field(None, description="Integer number of units/credits")
    section: Optional[str] = Field(None, description="Section/letter code, e.g., 'A', 'B', or 'O'")
    description: Optional[str] = Field(None, description="Long course description paragraph(s)")
    prerequisites: Optional[str] = Field(None, description="Text after 'Prerequisite:' (if any)")
    corequisites: Optional[str] = Field(None, description="Text after 'Corequisite:' (if any)")
    recommended: Optional[str] = Field(None, description="Text after 'Recommended:' (if any)")
    offered: Optional[str] = Field(None, description="When offered, e.g., 'Annually'")
    grade_basis: Optional[str] = Field(None, description="Grading basis if shown")
    pdf_page: Optional[int] = Field(None, description="PDF page number if present")


# ---------- 2) Vision LLM setup ----------
def build_llm() -> Union[ChatOpenAI, AzureChatOpenAI]:
    use_azure = os.getenv("USE_AZURE_OPENAI", "").strip() == "1"

    if use_azure:
        # Azure OpenAI via LangChain
        return AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        )
    else:
        # OpenAI (public) via LangChain
        return ChatOpenAI(
            model=os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )


# ---------- 3) Prompt for the extractor ----------
SYSTEM_INSTRUCTIONS = (
    "You are a data-extraction assistant. Read the course form or catalog image and "
    "return a single JSON object matching the provided schema. If a field is absent, use null."
)

USER_TASK = (
    "Extract these fields if present: course_code, course_title, units, section, description, "
    "prerequisites, corequisites, recommended, offered, grade_basis, pdf_page.\n\n"
    "Important rules:\n"
    "- Keep punctuation and wording as-is where possible.\n"
    "- 'units' must be an integer when present (e.g., 3).\n"
    "- If a field is missing in the image, return null for that field.\n"
)


# ---------- 4) Utilities ----------
def image_to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def to_human_message_with_image(prompt: str, image_path: Path) -> HumanMessage:
    b64 = image_to_base64(image_path)
    return HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/{image_path.suffix[1:]};base64,{b64}"}},
        ]
    )


# ---------- 5) Core extraction with structured output ----------
def extract_record_from_image(llm: ChatOpenAI, image_path: Path) -> CourseRecord:
    """
    Use LangChain + Vision LLM structured output to extract a single CourseRecord from an image.
    """
    # Use with_structured_output to auto-parse JSON into CourseRecord
    extractor = llm.with_structured_output(CourseRecord)

    message = to_human_message_with_image(
        prompt=f"{SYSTEM_INSTRUCTIONS}\n\n{USER_TASK}",
        image_path=image_path,
    )

    try:
        result: CourseRecord = extractor.invoke([message])
        return result
    except Exception as e:
        # If your deployment doesn't support structured output on vision,
        # do a manual JSON parse fallback.
        print(f"[warn] Structured output failed on {image_path.name}: {e}. Trying JSON fallback...")
        return manual_json_fallback(llm, image_path)


def manual_json_fallback(llm: ChatOpenAI, image_path: Path) -> CourseRecord:
    """
    Ask the LLM to produce raw JSON and then parse it into CourseRecord.
    """
    message = to_human_message_with_image(
        prompt=(
            f"{SYSTEM_INSTRUCTIONS}\n\n{USER_TASK}\n"
            "Respond with ONLY a JSON object and no extra text."
        ),
        image_path=image_path,
    )
    raw = llm.invoke([message]).content
    try:
        data = json.loads(raw)
        return CourseRecord(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[error] JSON fallback parse failed on {image_path.name}: {e}")
        if USE_OCR_FALLBACK:
            return ocr_regex_fallback(image_path)
        raise


# ---------- 6) (Optional) OCR fallback if vision not available ----------
def ocr_regex_fallback(image_path: Path) -> CourseRecord:
    """
    Very rough OCR + heuristic parsing. This is a safety net; quality depends on the image.
    """
    import re
    import pytesseract

    text = pytesseract.image_to_string(Image.open(image_path))

    # Heuristics (customize per your form layout)
    def find(pattern, default=None, flags=re.IGNORECASE):
        m = re.search(pattern, text, flags)
        return m.group(1).strip() if m else default

    code = find(r"(?:COURSE CODE|Course Code|Code)\s*[:\-]?\s*([A-Z]{2,}\s*\d{3})")
    title = find(r"(?:COURSE TITLE|Course Title|Title)\s*[:\-]?\s*(.+)")
    units = find(r"(?:UNITS|Units)\s*[:\-]?\s*(\d+)")
    units_val = int(units) if units and units.isdigit() else None

    prereq = find(r"(?:Prerequisite|Prerequisites)\s*:\s*(.+)")
    coreq = find(r"(?:Corequisite|Corequisites)\s*:\s*(.+)")
    offered = find(r"(?:Offered)\s*:\s*(.+)")
    grade_basis = find(r"(?:Grade Basis)\s*:\s*(.+)")
    pdf_page = find(r"(?:PDF Page|Page)\s*:\s*(\d+)")
    pdf_page_val = int(pdf_page) if pdf_page and pdf_page.isdigit() else None

    # Description: grab a big chunk (very heuristic)
    description = None
    desc_match = re.search(r"(?:Description|DESCRIPTION)\s*:?\s*(.+)", text, re.IGNORECASE | re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()

    return CourseRecord(
        course_code=code or "",
        course_title=title or "",
        units=units_val,
        section=None,
        description=description,
        prerequisites=prereq,
        corequisites=coreq,
        recommended=None,
        offered=offered,
        grade_basis=grade_basis,
        pdf_page=pdf_page_val,
    )


# ---------- 7) Batch process and CSV export ----------
def process_images_to_csv(
    image_paths: List[Path],
    out_csv: Path,
) -> None:
    llm = build_llm()
    rows = []

    for p in image_paths:
        print(f"[info] Processing {p} ...")
        record = extract_record_from_image(llm, p)
        rows.append(record.model_dump())

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"[done] Wrote {len(df)} rows to {out_csv}")


# ---------- 8) CLI usage ----------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract course info from image(s) to CSV via LangChain + Vision LLM.")
    parser.add_argument("input", help="Path to an image file OR a folder of images")
    parser.add_argument("--out", default="courses.csv", help="Output CSV file (default: courses.csv)")
    parser.add_argument("--ext", nargs="*", default=[".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"], help="Image extensions when input is a folder")

    args = parser.parse_args()
    input_path = Path(args.input)

    if input_path.is_dir():
        images = sorted([p for p in input_path.iterdir() if p.suffix.lower() in set(args.ext)])
    else:
        images = [input_path]

    if not images:
        raise SystemExit("No images found. Check the path or extensions.")

    process_images_to_csv(images, Path(args.out))
