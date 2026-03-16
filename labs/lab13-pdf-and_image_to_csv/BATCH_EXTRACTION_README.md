# Batch Course Extraction System

This enhanced system allows you to extract course information from PDFs across multiple page ranges using folder-specific guidelines.

## 🏗️ System Architecture

### Directory Structure
```
input/
├── 233878/
│   ├── guide.txt         # Extraction guidelines
│   ├── sample.csv        # Expected CSV format
│   ├── 233878.pdf        # Source PDF
│   └── 131-output-1.png  # Sample images
├── other_folder/
│   ├── guide.txt
│   ├── sample.csv
│   └── ...
output/
└── 233878/              # Extracted page images
course/
└── 233878/              # Extracted course CSV files
```

## 🚀 Usage Examples

### 1. Batch Processing (All Folders)
Extract courses from all input folders across a page range:
```bash
python batch_extract_courses.py "read from page 131 to page 198"
```

### 2. Single Folder Processing
Extract courses from a specific folder:
```bash
python batch_extract_courses.py --folder 233878 "page 131 to 140"
```

### 3. List Available Folders
See which folders have guidelines:
```bash
python batch_extract_courses.py --list-folders "dummy"
```

### 4. Single Page with Guidelines
Extract from a single page using automatic guidelines:
```bash
python extract_courses.py "page 131" --pdf-folder 233878 --max-pages 3
```

## 📋 Guidelines System

### guide.txt Format
Contains extraction instructions and context:
```
read from page 131 to page 198 to extract the course information into csv, refer to the sample input. 
In the header "ACC 200 Introduction to Financial Accounting (3-1T) A": 
- A means Annually, other value is B means Biennially (every other year). 
- 3 means Units = 3

Sample input in page 131
ACC 200 Introduction to Financial Accounting (3-1T) A 
This course focuses on the accounting concepts...
Prerequisite: BUS 100

Expected output csv:
course_code,course_title,units,section,description,prerequisites...
```

### sample.csv Format
Contains the exact CSV structure expected:
```csv
course_code,course_title,units,section,description,prerequisites,corequisites,recommended,offered,grade_basis,pdf_page,department
ACC 301,Intermediate Financial Accounting I,3,,"This course examines...",ACC 200,,,Annually,,131,ACC
```

## 🔄 How It Works

1. **Guideline Loading**: For each folder, the system reads `guide.txt` and `sample.csv`
2. **Enhanced Prompts**: Combines user request with folder-specific guidelines
3. **Batch Processing**: Loops through page ranges calling extraction for each page
4. **Output Organization**: Saves results in structured folders

### Enhanced Prompt Example
```
Extract course information from page 131 using the following guidelines:

EXTRACTION GUIDELINES:
[Content from guide.txt]

SAMPLE CSV FORMAT:
[Content from sample.csv]

Original prompt: page 131

Please extract course information following these exact guidelines and CSV format.
```

## 🛠️ Configuration Options

### batch_extract_courses.py Options
- `--folder FOLDER`: Process specific folder only
- `--max-pages N`: Pages per extraction call (default: 3)
- `--list-folders`: Show available folders

### extract_courses.py Options (Enhanced)
- `--use-guidelines`: Use folder guidelines (default: True)
- `--pdf-folder FOLDER`: Specify folder
- `--max-pages N`: Maximum pages to read

## 📊 Output Structure

### Generated Files
```
course/233878/
├── 131.csv              # Extracted courses from page 131+
├── 131_combined.txt     # Combined text from pages
├── 134.csv              # Next batch starting from page 134
├── 134_combined.txt
└── ...
```

### CSV Columns
- `course_code`: ACC 301
- `course_title`: Intermediate Financial Accounting I
- `units`: 3
- `section`: A, B, or blank
- `description`: Full course description
- `prerequisites`: Required courses
- `corequisites`: Concurrent requirements
- `recommended`: Suggested background
- `offered`: Annually, Biennially, etc.
- `grade_basis`: Grading method
- `pdf_page`: Source page number
- `department`: Academic department

## 🎯 Key Features

1. **Automatic Guidelines**: Loads instructions from each folder
2. **Batch Processing**: Handles page ranges efficiently
3. **Multiple Folders**: Processes all input folders or specific ones
4. **Enhanced Prompts**: Combines user requests with specific guidelines
5. **Structured Output**: Organized results by folder and page
6. **Error Handling**: Graceful failure recovery
7. **Progress Tracking**: Clear status updates

## 📝 Example Workflow

1. **Setup**: Place PDFs and guidelines in `input/folder_name/`
2. **Extract Pages**: Run `extract_pdf_to_pages.py` to create page images
3. **Batch Extract**: Use `batch_extract_courses.py` for page ranges
4. **Review Results**: Check `course/folder_name/` for CSV files

## 🔍 Troubleshooting

### Common Issues
- **No guidelines found**: Ensure `guide.txt` and `sample.csv` exist in input folder
- **Page not found**: Check that page images exist in output folder
- **Extraction errors**: Review guidelines for format consistency

### Debug Mode
Add verbose output by modifying scripts or checking log files in output directories.