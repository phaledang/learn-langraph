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


def extract_page_range_from_guide(guide_content: str) -> tuple[int, int]:
    """Extract page range from guide.txt content."""
    # Look for patterns like "read from page 131 to page 198", "page 131 to 198", etc.
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
    
    # If no range found, look for single page
    single_page_match = re.search(r'page\s+(\d+)', guide_content.lower())
    if single_page_match:
        page = int(single_page_match.group(1))
        return page, page
    
    raise ValueError("Could not extract page range from guide.txt content")


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


def load_folder_guidelines(pdf_folder: str) -> tuple[str, str]:
    """Load guide.txt and sample.csv content from the input folder.

    pdf_folder may be either a simple folder name (under ./input/) or a path to the
    input folder (e.g. "process/233878"). This function tries both locations.
    """
    # Resolve candidate input folder paths
    candidate_path = Path(pdf_folder)
    if candidate_path.exists() and candidate_path.is_dir():
        input_folder_path = candidate_path
    else:
        input_folder_path = Path("input") / pdf_folder
    
    guide_content = ""
    sample_content = ""
    
    # Try to load guide.txt
    guide_file = input_folder_path / "guide.txt"
    if guide_file.exists():
        with open(guide_file, 'r', encoding='utf-8') as f:
            guide_content = f.read().strip()
    
    # Try to load sample.csv
    sample_file = input_folder_path / "sample.csv"
    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_content = f.read().strip()
    
    return guide_content, sample_content


def main():
    parser = argparse.ArgumentParser(
        description="Extract course information from PDF pages using guidelines from guide.txt.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_courses.py --pdf-folder input/233878 --max-pages 3
  python extract_courses.py --pdf-folder process/233878
  python extract_courses.py --pdf-folder 233878
  
Legacy usage (with explicit prompt):
  python extract_courses.py "page 131" --pdf-folder 233878 --max-pages 3
        """
    )
    
    parser.add_argument("prompt", nargs="?", help="Optional natural language prompt (will auto-extract from guide.txt if not provided)")
    parser.add_argument("--pdf-folder", required=True, help="PDF folder name or path to input folder")
    parser.add_argument("--max-pages", type=int, default=3, help="Maximum pages per extraction batch (default: 3)")
    parser.add_argument("--use-guidelines", action="store_true", default=True, help="Use guidelines from input folder (default: True)")
    
    args = parser.parse_args()
    
    # Load guidelines first to determine page range
    try:
        guide_content, sample_content = load_folder_guidelines(args.pdf_folder)
        if not guide_content:
            print(f"❌ Error: No guide.txt found for folder {args.pdf_folder}")
            print("Please ensure guide.txt exists in the input folder.")
            sys.exit(1)
        
        print(f"📋 Loaded guidelines from {args.pdf_folder}")
        
        # Extract page range from guide.txt
        start_page, end_page = extract_page_range_from_guide(guide_content)
        print(f"📖 Page range from guide.txt: {start_page} to {end_page}")
        
    except Exception as e:
        print(f"❌ Error loading guidelines: {e}")
        
        # Fallback to prompt-based extraction if guide.txt fails
        if not args.prompt:
            print("No prompt provided and could not read page range from guide.txt")
            sys.exit(1)
        
        page_number = extract_page_number(args.prompt)
        if page_number is None:
            print("Error: Could not detect page number from prompt.")
            print("Please include a page number like 'page 131' or ensure guide.txt contains page range.")
            sys.exit(1)
        
        start_page = page_number
        end_page = page_number
        guide_content = ""
        sample_content = ""
    
    # Build enhanced prompt with guidelines
    enhanced_prompt = f"""Extract course information using the following guidelines:

EXTRACTION GUIDELINES:
{guide_content}

SAMPLE CSV FORMAT:
{sample_content}

Please extract course information following these exact guidelines and CSV format."""
    
    print(f"� Starting batch extraction:")
    print(f"   📁 PDF Folder: {args.pdf_folder}")
    print(f"   📄 Page Range: {start_page} to {end_page}")
    print(f"   📖 Max Pages per Batch: {args.max_pages}")
    print("=" * 60)
    
    # Process pages in batches
    successful_pages = []
    failed_pages = []
    
    current_page = start_page
    while current_page <= end_page:
        try:
            print(f"\n🔄 Processing batch starting at page {current_page}")
            
            # Calculate how many pages to process in this batch
            pages_remaining = end_page - current_page + 1
            batch_size = min(args.max_pages, pages_remaining)
            
            # Run extraction for this batch
            extract_courses_from_pdf_pages(
                args.pdf_folder, 
                current_page, 
                batch_size, 
                user_prompt=enhanced_prompt
            )
            
            successful_pages.extend(range(current_page, current_page + batch_size))
            print(f"✅ Successfully processed pages {current_page} to {current_page + batch_size - 1}")
            
        except Exception as e:
            print(f"❌ Error processing batch starting at page {current_page}: {e}")
            failed_pages.append(current_page)
        
        # Move to next batch
        current_page += args.max_pages
        
        print("-" * 40)
    
    # Show final summary
    print(f"\n📊 EXTRACTION SUMMARY")
    print(f"📁 Folder: {args.pdf_folder}")
    print(f"� Page Range: {start_page} to {end_page}")
    print(f"✅ Successful pages: {len(successful_pages)}")
    print(f"❌ Failed batches: {len(failed_pages)}")
    
    # Show output locations
    matches = list(Path("course").rglob("*.csv"))
    if matches:
        print(f"\n📊 Generated CSV files:")
        for csv_file in sorted(matches):
            print(f"   - {csv_file}")
    else:
        print(f"\n⚠️  No CSV files found. Please check the 'course' directory.")
    
    print(f"\n🎉 Batch extraction completed!")


if __name__ == "__main__":
    main()