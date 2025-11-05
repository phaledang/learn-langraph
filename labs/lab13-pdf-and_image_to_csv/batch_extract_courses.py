#!/usr/bin/env python3
"""
Batch Course Extraction Script

This script processes multiple input folders and extracts course information across page ranges
using guidelines from each folder's guide.txt and sample.csv files.

Usage examples:
  python batch_extract_courses.py "read from page 131 to page 198"
  python batch_extract_courses.py "extract courses from page 150 to 160"
  python batch_extract_courses.py --folder 233878 "page 131 to 140"
"""

import argparse
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import csv


def find_input_folders() -> List[str]:
    """Find all input folders that contain guide.txt and sample.csv."""
    input_dir = Path("input")
    if not input_dir.exists():
        return []
    
    valid_folders = []
    for folder in input_dir.iterdir():
        if folder.is_dir() and folder.name not in ['pdf', 'courses.csv']:
            guide_file = folder / "guide.txt"
            sample_file = folder / "sample.csv"
            if guide_file.exists() and sample_file.exists():
                valid_folders.append(folder.name)
    
    return sorted(valid_folders)


def extract_page_range(prompt: str) -> Tuple[int, int]:
    """Extract page range from user prompt."""
    # Look for patterns like "page 131 to page 198", "from page 150 to 160", etc.
    range_patterns = [
        r'page\s+(\d+)\s+to\s+page\s+(\d+)',
        r'from\s+page\s+(\d+)\s+to\s+(\d+)',
        r'page\s+(\d+)\s+to\s+(\d+)',
        r'(\d+)\s+to\s+(\d+)',
    ]
    
    for pattern in range_patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            start_page = int(match.group(1))
            end_page = int(match.group(2))
            return start_page, end_page
    
    # If no range found, look for single page
    single_page_match = re.search(r'page\s+(\d+)', prompt.lower())
    if single_page_match:
        page = int(single_page_match.group(1))
        return page, page
    
    raise ValueError("Could not extract page range from prompt")


def load_folder_guidelines(folder_name: str) -> Tuple[str, str]:
    """Load guide.txt and sample.csv content from a folder."""
    folder_path = Path("input") / folder_name
    
    # Read guide.txt
    guide_file = folder_path / "guide.txt"
    if not guide_file.exists():
        raise FileNotFoundError(f"guide.txt not found in {folder_path}")
    
    with open(guide_file, 'r', encoding='utf-8') as f:
        guide_content = f.read().strip()
    
    # Read sample.csv
    sample_file = folder_path / "sample.csv"
    if not sample_file.exists():
        raise FileNotFoundError(f"sample.csv not found in {folder_path}")
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        sample_content = f.read().strip()
    
    return guide_content, sample_content


def build_extraction_message(folder_name: str, page_number: int, guide_content: str, sample_content: str) -> str:
    """Build the user message for extraction based on guidelines."""
    message = f"""Extract course information from page {page_number} using the following guidelines:

FOLDER: {folder_name}
PAGE: {page_number}

EXTRACTION GUIDELINES:
{guide_content}

SAMPLE CSV FORMAT:
{sample_content}

Please extract course information from page {page_number} following these exact guidelines and CSV format."""
    
    return message


def extract_courses_for_page(folder_name: str, page_number: int, max_pages: int = 3) -> bool:
    """Extract courses for a specific page using the extract_courses.py script."""
    try:
        # Load guidelines for this folder
        guide_content, sample_content = load_folder_guidelines(folder_name)
        
        # Build the extraction message
        message = build_extraction_message(folder_name, page_number, guide_content, sample_content)
        
        print(f"📄 Processing page {page_number} for folder {folder_name}")
        print(f"💬 Using guidelines from {folder_name}/guide.txt and sample.csv")
        
        # Call extract_courses.py with the built message
        cmd = [
            sys.executable, 
            "extract_courses.py", 
            f"page {page_number}",
            "--pdf-folder", folder_name,
            "--max-pages", str(max_pages)
        ]
        
        print(f"🔧 Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully processed page {page_number}")
            print(result.stdout)
            return True
        else:
            print(f"❌ Error processing page {page_number}")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception processing page {page_number}: {e}")
        return False


def batch_extract_courses(folder_name: str, start_page: int, end_page: int, max_pages: int = 3) -> None:
    """Extract courses for a range of pages."""
    print(f"🚀 Starting batch extraction for folder: {folder_name}")
    print(f"📖 Page range: {start_page} to {end_page}")
    print(f"📚 Max pages per extraction: {max_pages}")
    print("-" * 60)
    
    successful_pages = []
    failed_pages = []
    
    current_page = start_page
    while current_page <= end_page:
        success = extract_courses_for_page(folder_name, current_page, max_pages)
        
        if success:
            successful_pages.append(current_page)
        else:
            failed_pages.append(current_page)
        
        # Move to next page (accounting for max_pages overlap)
        current_page += max_pages
        
        print("-" * 40)
    
    # Summary
    print(f"\n📊 BATCH EXTRACTION SUMMARY")
    print(f"📁 Folder: {folder_name}")
    print(f"✅ Successful pages: {successful_pages}")
    print(f"❌ Failed pages: {failed_pages}")
    print(f"📈 Success rate: {len(successful_pages)}/{len(successful_pages) + len(failed_pages)}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch extract course information from PDF pages across multiple folders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_extract_courses.py "read from page 131 to page 198"
  python batch_extract_courses.py "extract courses from page 150 to 160"
  python batch_extract_courses.py --folder 233878 "page 131 to 140"
  python batch_extract_courses.py --max-pages 5 "page 100 to 200"
        """
    )
    
    parser.add_argument("prompt", help="Natural language prompt with page range")
    parser.add_argument("--folder", help="Specific folder to process (processes all if not specified)")
    parser.add_argument("--max-pages", type=int, default=3, help="Maximum pages per extraction (default: 3)")
    parser.add_argument("--list-folders", action="store_true", help="List available input folders")
    
    args = parser.parse_args()
    
    # List folders if requested
    if args.list_folders:
        folders = find_input_folders()
        print("📁 Available input folders:")
        for folder in folders:
            print(f"  - {folder}")
        return
    
    # Extract page range from prompt
    try:
        start_page, end_page = extract_page_range(args.prompt)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please include a page range like 'page 131 to page 198' in your prompt.")
        sys.exit(1)
    
    # Determine which folders to process
    if args.folder:
        folders_to_process = [args.folder]
        # Validate folder exists
        folder_path = Path("input") / args.folder
        if not folder_path.exists():
            print(f"Error: Folder {args.folder} not found in input directory.")
            sys.exit(1)
    else:
        folders_to_process = find_input_folders()
        if not folders_to_process:
            print("Error: No valid input folders found.")
            print("Each folder must contain guide.txt and sample.csv files.")
            sys.exit(1)
    
    print(f"🎯 Processing {len(folders_to_process)} folder(s): {folders_to_process}")
    print(f"📄 Page range: {start_page} to {end_page}")
    print(f"📖 Max pages per extraction: {args.max_pages}")
    print("=" * 60)
    
    # Process each folder
    for folder in folders_to_process:
        try:
            batch_extract_courses(folder, start_page, end_page, args.max_pages)
            print("\n" + "=" * 60)
        except Exception as e:
            print(f"❌ Error processing folder {folder}: {e}")
            continue
    
    print("🎉 Batch extraction completed!")


if __name__ == "__main__":
    main()