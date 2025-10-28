#!/usr/bin/env python3
"""
Course Extraction Helper Script

This script helps users extract course information from PDF pages using natural language prompts.
It automatically detects the PDF folder and page numbers from user input.

Usage examples:
  python extract_courses.py "read from page 131 to extract course information"
  python extract_courses.py "extract courses starting from page 150"
  python extract_courses.py "get course data from page 200, may continue to next pages"
"""

import argparse
import re
import sys
from pathlib import Path
from extract_courses_from_pdf_pages import extract_courses_from_pdf_pages


def find_latest_pdf_folder():
    """Find the most recent PDF output folder."""
    output_dir = Path("output")
    if not output_dir.exists():
        raise FileNotFoundError("No output directory found. Please run extract_pdf_to_pages.py first.")
    
    # Find folders that match the pattern: YYYYMMDD_HHMMSS_filename
    pdf_folders = [d for d in output_dir.iterdir() if d.is_dir() and not d.name.endswith('.csv')]
    
    if not pdf_folders:
        raise FileNotFoundError("No PDF folders found in output directory.")
    
    # Sort by name (which includes timestamp) and get the latest
    latest_folder = sorted(pdf_folders)[-1]
    return latest_folder.name


def extract_page_number(prompt):
    """Extract page number from user prompt."""
    # Look for patterns like "page 131", "from page 150", etc.
    page_match = re.search(r'page\s+(\d+)', prompt.lower())
    if page_match:
        return int(page_match.group(1))
    
    # Look for just numbers that might be page references
    number_match = re.search(r'\b(\d{2,3})\b', prompt)
    if number_match:
        return int(number_match.group(1))
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Extract course information from PDF pages using natural language prompts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_courses.py "read from page 131 to extract course information"
  python extract_courses.py "extract courses starting from page 150"
  python extract_courses.py "get course data from page 200"
  
Advanced usage:
  python extract_courses.py "page 131" --pdf-folder 20251028_170700_233878 --max-pages 3
        """
    )
    
    parser.add_argument("prompt", help="Natural language prompt describing what to extract")
    parser.add_argument("--pdf-folder", help="Specific PDF folder name (auto-detected if not provided)")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum pages to read (default: 5)")
    
    args = parser.parse_args()
    
    # Extract page number from prompt
    page_number = extract_page_number(args.prompt)
    if page_number is None:
        print("Error: Could not detect page number from prompt.")
        print("Please include a page number like 'page 131' or just '131' in your prompt.")
        sys.exit(1)
    
    # Determine PDF folder
    if args.pdf_folder:
        pdf_folder = args.pdf_folder
    else:
        try:
            pdf_folder = find_latest_pdf_folder()
            print(f"Auto-detected PDF folder: {pdf_folder}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    # Display extraction info
    print(f"📚 Extracting course information:")
    print(f"   📁 PDF Folder: {pdf_folder}")
    print(f"   📄 Starting Page: {page_number}")
    print(f"   📖 Max Pages: {args.max_pages}")
    print(f"   💬 User Prompt: {args.prompt}")
    print()
    
    # Run the extraction
    try:
        extract_courses_from_pdf_pages(pdf_folder, page_number, args.max_pages)
        
        # Show output location
        course_output_dir = Path("course") / pdf_folder
        csv_file = course_output_dir / f"{page_number}.csv"
        print()
        print(f"✅ Course extraction completed!")
        print(f"📊 Results saved to: {csv_file}")
        print(f"📝 Combined text saved to: {course_output_dir / f'{page_number}_combined.txt'}")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()