#!/usr/bin/env python3
"""
Process Courses - Clean Workflow

This script implements a clean workflow for course extraction:
1. Copy input files to process folder
2. Extract all PDF pages to pages/pagenumber.txt
3. Build guide-on-one-page.txt from guide.txt + sample.csv
4. Execute extraction for the specified page range
"""

import os
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader
import subprocess
from openai import AzureOpenAI
import pandas as pd
from typing import Optional
from dotenv import load_dotenv


def extract_page_range_from_guide(guide_content: str) -> tuple[int, int]:
    """Extract page range from guide.txt content."""
    # Look for patterns like "read from page 131 to page 198"
    range_patterns = [
        r'read from page\s+(\d+)\s+to\s+page\s+(\d+)',
        r'page\s+(\d+)\s+to\s+page\s+(\d+)',
        r'from\s+page\s+(\d+)\s+to\s+(\d+)',
        r'page\s+(\d+)\s+to\s+(\d+)',
        r'(\d+)\s+to\s+(\d+)',
    ]
    
    for pattern in range_patterns:
        match = re.search(pattern, guide_content.lower())
        if match:
            start_page = int(match.group(1))
            end_page = int(match.group(2))
            return start_page, end_page
    
    raise ValueError("Could not extract page range from guide.txt content")


def remove_page_range_text(guide_content: str) -> str:
    """Remove the page range instruction from guide content."""
    # Remove patterns like "read from page 131 to page 198 to extract the course information into csv, "
    patterns_to_remove = [
        r'read from page\s+\d+\s+to\s+page\s+\d+\s+to\s+extract\s+the\s+course\s+information\s+into\s+csv,?\s*',
        r'read from page\s+\d+\s+to\s+page\s+\d+,?\s*',
    ]
    
    cleaned_content = guide_content
    for pattern in patterns_to_remove:
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content)
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content


def setup_process_folder(input_folder: str) -> str:
    """Copy input files to process folder and return process folder path."""
    input_path = Path("input") / input_folder
    if not input_path.exists():
        raise FileNotFoundError(f"Input folder not found: {input_path}")
    
    # Create process folder with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    process_folder = Path("process") / f"{timestamp}_{input_folder}"
    process_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Creating process folder: {process_folder}")
    
    # Copy all files from input folder
    for file_path in input_path.iterdir():
        if file_path.is_file():
            dest_path = process_folder / file_path.name
            shutil.copy2(file_path, dest_path)
            print(f"   Copied: {file_path.name}")
    
    return str(process_folder)


def extract_pdf_to_pages(process_folder: str) -> None:
    """Extract all PDF pages to pages/pagenumber.txt."""
    process_path = Path(process_folder)
    
    # Find PDF files
    pdf_files = list(process_path.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {process_folder}")
    
    # Create pages directory
    pages_dir = process_path / "pages"
    pages_dir.mkdir(exist_ok=True)
    
    for pdf_file in pdf_files:
        print(f"📄 Extracting pages from {pdf_file.name}...")
        
        try:
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            print(f"   Found {total_pages} pages")
            
            # Extract text from each page
            for page_number in range(total_pages):
                try:
                    page = reader.pages[page_number]
                    text = page.extract_text()
                    
                    # Save to pages/pagenumber.txt (page numbers start from 1)
                    page_file = pages_dir / f"{page_number + 1}.txt"
                    with open(page_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    if (page_number + 1) % 50 == 0:  # Progress indicator
                        print(f"   Extracted {page_number + 1} pages...")
                        
                except Exception as e:
                    print(f"   Error extracting page {page_number + 1}: {e}")
                    
            print(f"   ✅ Extracted all {total_pages} pages to {pages_dir}")
                    
        except Exception as e:
            print(f"   ❌ Error processing {pdf_file.name}: {e}")


def build_guide_on_one_page(process_folder: str) -> tuple[int, int]:
    """Build guide-on-one-page.txt from guide.txt + sample.csv and return page range."""
    process_path = Path(process_folder)
    
    # Read guide.txt
    guide_file = process_path / "guide.txt"
    if not guide_file.exists():
        raise FileNotFoundError(f"guide.txt not found in {process_folder}")
    
    with open(guide_file, 'r', encoding='utf-8') as f:
        guide_content = f.read()
    
    # Extract page range before cleaning
    start_page, end_page = extract_page_range_from_guide(guide_content)
    print(f"📖 Detected page range: {start_page} to {end_page}")
    
    # Remove page range text from guide content
    cleaned_guide = remove_page_range_text(guide_content)
    
    # Read sample.csv
    sample_file = process_path / "sample.csv"
    sample_content = ""
    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_content = f.read()
    
    # Build consolidated guide
    consolidated_guide = f"""COURSE EXTRACTION GUIDELINES
=============================

{cleaned_guide}

EXPECTED CSV FORMAT
==================

{sample_content}

EXTRACTION INSTRUCTIONS
=======================

Extract all course information from the provided text and return as a properly formatted CSV.
Follow the exact format shown in the sample above.
Pay attention to the frequency codes: A=Annually, B=Biennially, O=Occasionally.
Include all course details: code, title, units, description, prerequisites, etc.
"""
    
    # Save consolidated guide
    guide_output = process_path / "guide-on-one-page.txt"
    with open(guide_output, 'w', encoding='utf-8') as f:
        f.write(consolidated_guide)
    
    print(f"📋 Created consolidated guide: {guide_output}")
    
    return start_page, end_page


def extract_courses_with_openai(text: str, guide_content: str, page_range: str) -> Optional[str]:
    """Extract courses using Azure OpenAI API."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check Azure OpenAI configuration
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        
        if not api_key or not endpoint:
            print(f"   ⚠️ Azure OpenAI configuration missing - check .env file")
            return None
        
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        
        prompt = f"""
{guide_content}

TEXT TO EXTRACT FROM (Pages {page_range})
===================

{text}

Please extract all course information from the above text and return ONLY the CSV data.
Do not include any explanations, headers, or markdown formatting.
Return only the course data rows in CSV format.
"""
        
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a precise course information extractor. Return only CSV data rows without headers or explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"   ❌ Azure OpenAI extraction error: {e}")
        return None


def extract_courses_for_page_range(process_folder: str, start_page: int, end_page: int, max_pages: int = 3) -> None:
    """Extract courses for the specified page range."""
    process_path = Path(process_folder)
    pages_dir = process_path / "pages"
    results_dir = process_path / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Load the consolidated guide
    guide_file = process_path / "guide-on-one-page.txt"
    if not guide_file.exists():
        raise FileNotFoundError("guide-on-one-page.txt not found")
    
    with open(guide_file, 'r', encoding='utf-8') as f:
        guide_content = f.read()
    
    print(f"🔄 Starting extraction for pages {start_page} to {end_page}")
    print("=" * 60)
    
    # Process pages in batches
    current_page = start_page
    batch_num = 1
    
    while current_page <= end_page:
        batch_end = min(current_page + max_pages - 1, end_page)
        
        print(f"\n📦 Batch {batch_num}: Pages {current_page} to {batch_end}")
        
        # Combine text from pages in this batch
        combined_text = ""
        pages_found = []
        
        for page_num in range(current_page, batch_end + 1):
            page_file = pages_dir / f"{page_num}.txt"
            if page_file.exists():
                with open(page_file, 'r', encoding='utf-8') as f:
                    page_text = f.read()
                combined_text += f"\n--- PAGE {page_num} ---\n{page_text}\n"
                pages_found.append(page_num)
            else:
                print(f"   ⚠️ Page {page_num} not found")
        
        if combined_text:
            # Create extraction prompt
            extraction_prompt = f"""
{guide_content}

TEXT TO EXTRACT FROM
===================

{combined_text}

Please extract all course information from the above text and return as CSV format.
"""
            
            # Save the batch text and prompt for reference
            batch_file = results_dir / f"batch_{batch_num}_pages_{current_page}_{batch_end}.txt"
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(extraction_prompt)
            
            print(f"   📝 Saved batch text: {batch_file}")
            print(f"   📄 Pages processed: {pages_found}")
            
            # Extract courses using OpenAI
            page_range_str = f"{current_page}-{batch_end}"
            print(f"   🤖 Extracting with OpenAI...")
            
            csv_content = extract_courses_with_openai(combined_text, guide_content, page_range_str)
            
            # Create CSV file
            csv_file = results_dir / f"courses_pages_{current_page}_{batch_end}.csv"
            
            if csv_content and csv_content.strip():
                # Add CSV header if not present
                if not csv_content.startswith("course_code"):
                    header = "course_code,course_title,units,section,description,prerequisites,corequisites,recommended,offered,grade_basis,pdf_page,department\n"
                    csv_content = header + csv_content
                
                with open(csv_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                
                print(f"   ✅ Created CSV with courses: {csv_file}")
                
                # Count courses extracted
                lines = csv_content.strip().split('\n')
                course_count = len([line for line in lines if line and not line.startswith('course_code') and not line.startswith('#')])
                print(f"   📊 Courses found: {course_count}")
                
            else:
                # Create placeholder if extraction failed
                with open(csv_file, 'w', encoding='utf-8') as f:
                    f.write("course_code,course_title,units,section,description,prerequisites,corequisites,recommended,offered,grade_basis,pdf_page,department\n")
                    f.write(f"# No courses found or extraction failed for pages {current_page} to {batch_end}\n")
                
                print(f"   ⚠️ No courses extracted: {csv_file}")
        
        current_page += max_pages
        batch_num += 1
    
    print(f"\n✅ Extraction completed! Check {results_dir} for results.")
    
    # Create consolidated CSV
    create_consolidated_csv(results_dir, start_page, end_page)


def create_consolidated_csv(results_dir: Path, start_page: int, end_page: int) -> None:
    """Consolidate all CSV files into a single file."""
    print(f"\n📋 Creating consolidated CSV...")
    
    all_courses = []
    csv_files = list(results_dir.glob("courses_pages_*.csv"))
    
    for csv_file in sorted(csv_files):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # Skip empty files and comment lines
            lines = [line for line in content.split('\n') 
                    if line.strip() and not line.startswith('#') and not line.startswith('course_code')]
            
            if lines:
                all_courses.extend(lines)
                print(f"   📄 Added {len(lines)} courses from {csv_file.name}")
                
        except Exception as e:
            print(f"   ⚠️ Error reading {csv_file.name}: {e}")
    
    # Create consolidated file
    consolidated_file = results_dir / f"all_courses_pages_{start_page}_{end_page}.csv"
    
    with open(consolidated_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("course_code,course_title,units,section,description,prerequisites,corequisites,recommended,offered,grade_basis,pdf_page,department\n")
        
        # Write all courses
        for course in all_courses:
            f.write(course + '\n')
    
    print(f"   ✅ Consolidated CSV created: {consolidated_file}")
    print(f"   📊 Total courses: {len(all_courses)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python process_courses.py <input_folder> [--max-pages N]")
        print("Example: python process_courses.py 233878 --max-pages 3")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    max_pages = 3
    
    # Parse max-pages argument
    if "--max-pages" in sys.argv:
        try:
            idx = sys.argv.index("--max-pages")
            max_pages = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("Invalid --max-pages value")
            sys.exit(1)
    
    try:
        print("🚀 Starting clean course extraction workflow")
        print("=" * 50)
        
        # Step 1: Setup process folder
        process_folder = setup_process_folder(input_folder)
        
        # Step 2: Extract PDF to pages
        extract_pdf_to_pages(process_folder)
        
        # Step 3: Build consolidated guide and get page range
        start_page, end_page = build_guide_on_one_page(process_folder)
        
        # Step 4: Extract courses for page range
        extract_courses_for_page_range(process_folder, start_page, end_page, max_pages)
        
        print("\n🎉 Workflow completed successfully!")
        print(f"📁 Results available in: {process_folder}/results/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()