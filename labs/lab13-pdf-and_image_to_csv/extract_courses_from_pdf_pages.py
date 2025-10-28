import json
import os
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LangChain
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.messages import HumanMessage


# ---------- 1) Pydantic schema for structured extraction ----------
class CourseRecord(BaseModel):
    course_code: str = Field(..., description="Course code, e.g., 'ACC 301' or 'PS 320'")
    course_title: str = Field(..., description="Short human title, e.g., 'Intermediate Financial Accounting I'")
    units: Optional[int] = Field(None, description="Integer number of units/credits")
    section: Optional[str] = Field(None, description="Section/letter code, e.g., 'A', 'B', or 'O'")
    frequency: Optional[str] = Field(None, description="Course frequency - A=Annually, B=Biennially, O=Occasionally")
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
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            max_tokens=1000,
            temperature=0,
        )
    else:
        # Standard OpenAI
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            max_tokens=1000,
            temperature=0,
        )


# ---------- 3) System instructions ----------
SYSTEM_INSTRUCTIONS = """
You are an expert at extracting structured course information from academic text.

IMPORTANT FREQUENCY CODES:
- A = Annually (offered every year)
- B = Biennially (offered every other year)  
- O = Occasionally (offered irregularly)

Extract ALL course records from the provided text. Look for patterns like:
- Course codes (e.g., "ACC 200", "PS 320")
- Course titles following the codes
- Units/credits in parentheses (e.g., "(3-1T)")
- Frequency codes (A, B, O) after units
- Course descriptions
- Prerequisites, corequisites, recommendations

For each course found, extract:
1. course_code: The department and number (e.g., "ACC 200")
2. course_title: The full course name
3. units: Number from parentheses (e.g., 3 from "(3-1T)")
4. frequency: A, B, or O based on the code
5. description: Full course description text
6. prerequisites: Any prerequisite information
7. corequisites: Any corequisite information
8. pdf_page: The source page number

Be thorough and extract ALL courses found in the text.
"""

USER_TASK = """
Extract all course information from this academic text and return as a JSON array of course objects.
Each course should be a separate object in the array.
"""


# ---------- 4) Text processing ----------
def extract_courses_from_text(llm: Union[ChatOpenAI, AzureChatOpenAI], text: str, page_number: int) -> List[CourseRecord]:
    """
    Extract course records from text using LLM.
    """
    prompt = f"{SYSTEM_INSTRUCTIONS}\n\n{USER_TASK}\n\nPage {page_number} Text:\n{text}\n\nRespond with ONLY a JSON array and no extra text."
    
    message = HumanMessage(content=prompt)
    
    try:
        raw = llm.invoke([message]).content
        print(f"[debug] LLM response for page {page_number}: {raw[:200]}...")
        
        # Clean up the response - remove any markdown formatting
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        
        # Try to parse as JSON array
        data = json.loads(raw)
        
        # Ensure it's a list
        if not isinstance(data, list):
            data = [data]
        
        records = []
        for item in data:
            try:
                record = CourseRecord(**item)
                record.pdf_page = page_number  # Set the page number
                records.append(record)
            except ValidationError as e:
                print(f"[warning] Failed to parse course record: {e}")
                print(f"[warning] Raw item: {item}")
                continue
        
        return records
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"[error] Failed to parse courses from page {page_number}: {e}")
        print(f"[error] Raw response: {raw}")
        return []


# ---------- 5) Main extraction function ----------
def extract_courses_from_pdf_pages(pdf_folder_name: str, start_page: int, max_pages: int = 5) -> None:
    """
    Extract course information from PDF pages starting from a specific page.
    
    Args:
        pdf_folder_name: Name of the PDF folder in output/ (e.g., "20251028_170700_233878")
        start_page: Starting page number (e.g., 131)
        max_pages: Maximum number of pages to read (default: 5)
    """
    llm = build_llm()
    
    # Setup paths
    pdf_output_dir = Path("output") / pdf_folder_name
    course_output_dir = Path("course") / pdf_folder_name
    course_output_dir.mkdir(parents=True, exist_ok=True)
    
    all_courses = []
    combined_text = ""
    
    # Read text from consecutive pages
    for page_offset in range(max_pages):
        current_page = start_page + page_offset
        page_file = pdf_output_dir / f"{current_page}.txt"
        
        if not page_file.exists():
            print(f"[info] Page {current_page} not found, stopping at page {current_page - 1}")
            break
        
        print(f"[info] Reading page {current_page}: {page_file}")
        
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                page_text = f.read()
            
            combined_text += f"\n--- PAGE {current_page} ---\n{page_text}\n"
            
            # Extract courses from this page
            page_courses = extract_courses_from_text(llm, page_text, current_page)
            all_courses.extend(page_courses)
            
            print(f"[info] Found {len(page_courses)} courses on page {current_page}")
            
        except Exception as e:
            print(f"[error] Failed to read page {current_page}: {e}")
    
    # Save results
    if all_courses:
        # Convert to DataFrame and save
        courses_data = [course.model_dump() for course in all_courses]
        df = pd.DataFrame(courses_data)
        
        output_csv = course_output_dir / f"{start_page}.csv"
        df.to_csv(output_csv, index=False)
        
        print(f"[done] Extracted {len(all_courses)} courses to {output_csv}")
        
        # Also save the combined text for reference
        text_output = course_output_dir / f"{start_page}_combined.txt"
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        print(f"[done] Saved combined text to {text_output}")
    else:
        print("[warning] No courses found in the specified pages")


# ---------- 6) CLI usage ----------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract course info from PDF pages to CSV via LangChain + LLM.")
    parser.add_argument("pdf_folder", help="PDF output folder name (e.g., '20251028_170700_233878')")
    parser.add_argument("start_page", type=int, help="Starting page number (e.g., 131)")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to read (default: 5)")

    args = parser.parse_args()
    
    extract_courses_from_pdf_pages(args.pdf_folder, args.start_page, args.max_pages)