# Python Language References - Lab 13: PDF and Image to CSV

## Overview
This document explains the Python methods, classes, and concepts used in this lab for extracting content from PDF documents and exporting structured data to CSV using Azure OpenAI.

## Environment Setup

### Loading Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key  = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
```

**`load_dotenv()`:** Reads a `.env` file and injects its key-value pairs into `os.environ`.
**`os.getenv(key)`:** Retrieves the value of an environment variable; returns `None` if the key is not set.

## pathlib – Object-Oriented File Paths

### Path Objects
```python
from pathlib import Path

input_dir   = Path("input/pdf")
output_dir  = Path("output")
process_dir = Path("process") / "20240101_120000_233878"
```

**`Path("...")`:** Creates a path object from a string. Supports `/` operator for joining.
**Advantage over `os.path`:** Paths are objects with methods, making code more readable.

### Listing Files
```python
for pdf_file in input_dir.glob("*.pdf"):
    print(pdf_file.name)        # filename with extension
    print(pdf_file.stem)        # filename without extension
    print(pdf_file.suffix)      # ".pdf"
    print(pdf_file.parent)      # parent directory path
```

**`.glob(pattern)`:** Yields all paths matching the given pattern in the directory.
**`.name`:** File name including extension.
**`.stem`:** File name without extension.
**`.suffix`:** Extension including the leading dot.

### Creating Directories
```python
output_dir.mkdir(parents=True, exist_ok=True)
```

**`parents=True`:** Creates any missing parent directories automatically.
**`exist_ok=True`:** Does not raise an error if the directory already exists.

### Checking Existence
```python
if not input_path.exists():
    raise FileNotFoundError(f"Input folder not found: {input_path}")

pdf_files = list(process_path.glob("*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No PDF files found in {process_folder}")
```

**`.exists()`:** Returns `True` if the path points to an existing file or directory.

## datetime – Timestamps and Formatting

### Generating Timestamps for Folder Names
```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
process_folder = Path("process") / f"{timestamp}_233878"
# e.g. "process/20240615_093045_233878"
```

**`datetime.now()`:** Returns the current local date and time.
**`.strftime(format)`:** Formats a `datetime` as a string.

| Format code | Meaning | Example |
|-------------|---------|---------|
| `%Y` | 4-digit year | `2024` |
| `%m` | 2-digit month | `06` |
| `%d` | 2-digit day | `15` |
| `%H` | Hour (24-hour) | `09` |
| `%M` | Minute | `30` |
| `%S` | Second | `45` |

## shutil – File and Directory Operations

### Copying Files
```python
import shutil

shutil.copy2(source_path, destination_path)
```

**`shutil.copy2(src, dst)`:** Copies a file along with its metadata (timestamps, permissions).
**Use case:** Preserving original files while working in a timestamped process folder.

### Iterating and Copying a Directory
```python
for file_path in input_path.iterdir():
    if file_path.is_file():
        dest_path = process_folder / file_path.name
        shutil.copy2(file_path, dest_path)
        print(f"   Copied: {file_path.name}")
```

**`.iterdir()`:** Yields all entries (files and subdirectories) in a directory.
**`.is_file()`:** Returns `True` if the entry is a regular file.

## pypdf – Reading PDF Files

### Extracting Text from Every Page
```python
from pypdf import PdfReader

reader     = PdfReader(pdf_file)
total_pages = len(reader.pages)

for page_number in range(total_pages):
    page = reader.pages[page_number]
    text = page.extract_text()

    output_file = pages_dir / f"{page_number + 1}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
```

**`PdfReader(path)`:** Opens a PDF file for reading.
**`.pages`:** List of `PageObject` objects; one per page.
**`.extract_text()`:** Returns the text content of a page as a string.
**Page numbering:** `reader.pages` is 0-indexed; adding `1` produces human-readable page numbers.

## re – Regular Expressions

### Extracting a Page Range from Text
```python
import re

guide_content = "read from page 131 to page 198 to extract course information"

range_patterns = [
    r'read from page\s+(\d+)\s+to\s+page\s+(\d+)',
    r'page\s+(\d+)\s+to\s+page\s+(\d+)',
    r'from\s+page\s+(\d+)\s+to\s+(\d+)',
    r'(\d+)\s+to\s+(\d+)',
]

for pattern in range_patterns:
    match = re.search(pattern, guide_content.lower())
    if match:
        start_page = int(match.group(1))
        end_page   = int(match.group(2))
        break
```

**`re.search(pattern, string)`:** Scans the string for the first location where the pattern produces a match; returns a `Match` object or `None`.
**`(\d+)`:** Capturing group matching one or more digits.
**`\s+`:** Matches one or more whitespace characters.
**`.group(1)`, `.group(2)`:** Return the text matched by the first and second capturing groups.

### Removing Matched Text
```python
cleaned = re.sub(
    r'read from page\s+\d+\s+to\s+page\s+\d+,?\s*',
    '',
    guide_content,
    flags=re.IGNORECASE,
)
cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned).strip()
```

**`re.sub(pattern, replacement, string)`:** Replaces all matches of the pattern with the replacement string.
**`re.IGNORECASE`:** Makes the pattern case-insensitive.
**`\n\s*\n`:** Matches blank lines (any whitespace between two newlines).

## File I/O

### Reading a File
```python
with open(guide_file, "r", encoding="utf-8") as f:
    guide_content = f.read()
```

**`open(path, mode, encoding)`:** Opens a file. Mode `"r"` = read, `"w"` = write, `"a"` = append.
**`encoding="utf-8"`:** Always specify encoding explicitly to avoid platform-specific behaviour.
**`with` statement:** Automatically closes the file when the block exits, even if an exception occurs.

### Writing a File
```python
with open(output_file, "w", encoding="utf-8") as f:
    f.write(text)
```

### Reading Lines
```python
lines = content.strip().split("\n")
data_lines = [line for line in lines if line and not line.startswith("#")]
```

**`.split("\n")`:** Splits a string on newline characters, returning a list of lines.
**List comprehension with condition:** Filters out empty lines and comment lines in one expression.

## Azure OpenAI – AI-Powered Extraction

### Creating the Client
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
)
```

**`AzureOpenAI`:** Client for Azure-hosted OpenAI models. Requires `api_key`, `azure_endpoint`, and `api_version`.

### Sending a Chat Completion Request
```python
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

response = client.chat.completions.create(
    model=deployment,
    messages=[
        {"role": "system", "content": "You are a precise data extractor. Return only CSV rows."},
        {"role": "user",   "content": prompt},
    ],
    temperature=0.1,
    max_tokens=2000,
)

csv_content = response.choices[0].message.content.strip()
```

**`temperature=0.1`:** Low temperature → more deterministic, factual output; suitable for structured extraction.
**`max_tokens=2000`:** Maximum number of tokens in the response.
**`response.choices[0].message.content`:** The model's reply text.

## subprocess – Running External Commands

### Running a Python Script
```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "batch_extract_items.py", "--list-folders", "dummy"],
    capture_output=True,
    text=True,
)

if result.stdout:
    print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

success = result.returncode == 0
```

**`subprocess.run(cmd)`:** Executes a command and waits for it to finish.
**`sys.executable`:** Path to the current Python interpreter; ensures the subprocess uses the same environment.
**`capture_output=True`:** Captures stdout and stderr instead of printing them to the terminal.
**`text=True`:** Returns stdout/stderr as strings rather than bytes.
**`.returncode`:** Exit code; `0` means success.

## sys – Command-Line Arguments

### Parsing Arguments Manually
```python
import sys

if len(sys.argv) < 2:
    print("Usage: python process_items.py <input_folder> [--max-pages N]")
    sys.exit(1)

input_folder = sys.argv[1]
max_pages    = 3

if "--max-pages" in sys.argv:
    idx       = sys.argv.index("--max-pages")
    max_pages = int(sys.argv[idx + 1])
```

**`sys.argv`:** List of command-line arguments; `sys.argv[0]` is the script name.
**`sys.exit(code)`:** Terminates the program; `1` signals an error to the calling shell.
**`list.index(value)`:** Returns the index of the first occurrence of `value` in the list.

## pandas – CSV Handling

### Reading a CSV
```python
import pandas as pd

df = pd.read_csv("items_pages_131_134.csv")
print(df.head())
print(f"Total rows: {len(df)}")
```

### Writing a DataFrame to CSV
```python
df.to_csv("all_items.csv", index=False)
```

**`index=False`:** Omits the row numbers from the output file.

### Concatenating DataFrames
```python
frames = [pd.read_csv(f) for f in csv_files]
combined = pd.concat(frames, ignore_index=True)
combined.to_csv("consolidated.csv", index=False)
```

**`pd.concat(frames)`:** Stacks a list of DataFrames vertically.
**`ignore_index=True`:** Resets the row index in the combined DataFrame.

## Error Handling

### try / except / finally
```python
try:
    reader = PdfReader(pdf_file)
    text   = reader.pages[page_number].extract_text()
except Exception as e:
    print(f"Error extracting page {page_number + 1}: {e}")
finally:
    pass  # cleanup if needed
```

**`except Exception as e`:** Catches any exception and binds it to variable `e`.
**`finally`:** Executes regardless of whether an exception occurred; use for cleanup.

### Raising Custom Errors
```python
def extract_page_range(content: str) -> tuple[int, int]:
    # ... pattern matching ...
    raise ValueError("Could not extract page range from guide.txt content")
```

**`ValueError`:** Built-in exception for invalid input values.
**`tuple[int, int]`:** Return type hint indicating a 2-tuple of integers.

## Type Hints

### Function Signatures
```python
from typing import Optional

def extract_items_with_openai(
    text: str,
    guide_content: str,
    page_range: str,
) -> Optional[str]:
    ...
```

**`Optional[str]`:** The function may return a `str` or `None`.

### tuple Type Hint (Python 3.9+)
```python
def build_guide(process_folder: str) -> tuple[int, int]:
    ...
    return start_page, end_page
```

**`tuple[int, int]`:** A tuple containing exactly two integers (start page and end page).

## String Operations

### Multi-line f-strings
```python
consolidated_guide = f"""COURSE EXTRACTION GUIDELINES
=============================

{cleaned_guide}

EXPECTED CSV FORMAT
==================

{sample_content}
"""
```

**Triple-quoted strings (`"""`)**  span multiple lines and preserve newlines literally.
**`{variable}`:** Embeds the value of a variable at that position.

### String Checking and Filtering
```python
lines = csv_content.strip().split("\n")
course_count = len([
    line for line in lines
    if line and not line.startswith("course_code") and not line.startswith("#")
])
```

**`.startswith(prefix)`:** Returns `True` if the string begins with `prefix`.
**Boolean `if line`:** Filters out empty strings (falsy in Python).

## Progress Indicators
```python
for page_number in range(total_pages):
    # ...
    if (page_number + 1) % 50 == 0:
        print(f"   Extracted {page_number + 1} pages...")
```

**`% 50 == 0`:** Modulo operator; prints progress every 50 pages without printing every single page.

## Best Practices

1. **Use `pathlib.Path`** instead of string concatenation for file paths; it is cross-platform and more readable.
2. **Always specify `encoding="utf-8"`** when opening files to avoid platform-specific encoding issues.
3. **Use timestamped process folders** to keep each run's files isolated and traceable.
4. **Set low `temperature`** (e.g., `0.1`) for extraction tasks to get consistent, structured output.
5. **Handle `None` from `os.getenv()`** before using the value; missing keys cause cryptic errors later.
6. **Use batch processing** for large PDFs to stay within the model's context window.
7. **Validate page ranges** before starting extraction to give a clear error message early.

## Summary

| Concept | Key API / Syntax |
|---------|-----------------|
| File paths | `pathlib.Path` |
| List files | `path.glob("*.pdf")` |
| Create directories | `path.mkdir(parents=True, exist_ok=True)` |
| Copy files | `shutil.copy2(src, dst)` |
| Current timestamp | `datetime.now().strftime("%Y%m%d_%H%M%S")` |
| Read PDF | `PdfReader(path)` / `.pages[n].extract_text()` |
| Regex search | `re.search(pattern, text)` / `.group(1)` |
| Regex replace | `re.sub(pattern, replacement, text)` |
| File I/O | `open(path, "r", encoding="utf-8")` |
| Azure OpenAI | `AzureOpenAI(api_key, azure_endpoint, api_version)` |
| Run subprocess | `subprocess.run(cmd, capture_output=True, text=True)` |
| CLI arguments | `sys.argv` |
| CSV handling | `pd.read_csv()` / `pd.concat()` / `df.to_csv()` |
