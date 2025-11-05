#!/usr/bin/env python3
"""
Example usage of the batch course extraction system.

This script demonstrates how to use the new batch extraction capabilities
that automatically load guidelines from guide.txt and sample.csv files
in each input folder.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and display its output."""
    print(f"🔧 Running: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print("=" * 60)
    return result.returncode == 0


def main():
    print("🚀 Batch Course Extraction System Demo")
    print("=" * 60)
    
    # Check if the batch script exists
    if not Path("batch_extract_courses.py").exists():
        print("❌ batch_extract_courses.py not found!")
        sys.exit(1)
    
    print("\n1️⃣ List available input folders:")
    run_command([sys.executable, "batch_extract_courses.py", "--list-folders", "dummy"])
    
    print("\n2️⃣ Extract from a specific page range (using guidelines from each folder):")
    print("This will process all folders and extract from page 131 to 135")
    run_command([sys.executable, "batch_extract_courses.py", "read from page 131 to page 135"])
    
    print("\n3️⃣ Extract from a specific folder:")
    print("This will process only folder 233878 from page 131 to 140")
    run_command([sys.executable, "batch_extract_courses.py", "--folder", "233878", "page 131 to 140"])
    
    print("\n4️⃣ Test single page extraction with guidelines:")
    print("This shows how the original script now uses guidelines automatically")
    run_command([sys.executable, "extract_courses.py", "page 131", "--pdf-folder", "233878", "--max-pages", "3"])
    
    print("\n✅ Demo completed!")
    print("\nKey features demonstrated:")
    print("- Automatic guideline loading from guide.txt and sample.csv")
    print("- Batch processing across page ranges")
    print("- Support for multiple input folders")
    print("- Enhanced prompts with folder-specific guidelines")


if __name__ == "__main__":
    main()