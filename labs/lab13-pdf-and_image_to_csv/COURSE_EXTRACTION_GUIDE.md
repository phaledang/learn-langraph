# Course Extraction System - Usage Guide

This system processes PDF course catalogs and extracts structured course information into CSV files.

## 🚀 Quick Start

### 1. Extract PDF to Text Pages
```bash
python extract_pdf_to_pages.py
```
This reads all PDFs from `input/pdf/` and creates text files for each page in `output/datetime_filename/`

### 2. Extract Course Information
```bash
python extract_courses.py "read from page 131 to extract course information"
```
This processes specific pages and extracts course data to CSV files in `course/datetime_filename/`

## 📂 File Structure

```
input/
├── pdf/              # Place PDF files here
│   └── 233878.pdf
└── image/            # Place image files here
    └── 131-output-1.png

output/
└── 20251028_170700_233878/  # Auto-generated folder with timestamp_filename
    ├── 1.txt         # Page 1 text
    ├── 2.txt         # Page 2 text
    └── ...

course/
└── 20251028_170700_233878/  # Course extraction results
    ├── 131.csv       # Extracted courses from page 131
    └── 131_combined.txt  # Combined text used for extraction
```

## 📊 CSV Output Format

The extracted CSV contains these columns:
- `course_code`: Course code (e.g., "ACC 200")
- `course_title`: Course title (e.g., "Introduction to Financial Accounting")
- `units`: Number of credit units
- `frequency`: A=Annually, B=Biennially, O=Occasionally
- `description`: Full course description
- `prerequisites`: Required prerequisite courses
- `corequisites`: Required corequisite courses
- `pdf_page`: Source page number

## 💡 Usage Examples

### Natural Language Prompts
```bash
# Basic extraction
python extract_courses.py "read from page 131 to extract course information"

# Specify more pages
python extract_courses.py "extract courses starting from page 150"

# Different page
python extract_courses.py "get course data from page 200"
```

### Advanced Usage
```bash
# Specify PDF folder and limit pages
python extract_courses.py "page 131" --pdf-folder 20251028_170700_233878 --max-pages 3

# Direct script usage
python extract_courses_from_pdf_pages.py 20251028_170700_233878 131 --max-pages 2
```

### Image Processing (Alternative)
```bash
# Process image directly
python extract_courses_to_csv.py input/image/131-output-1.png --out output/courses.csv
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# For Azure OpenAI
USE_AZURE_OPENAI=1
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# For OpenAI
OPENAI_API_KEY=your_key
```

## 📝 Key Features

- **Automatic PDF Processing**: Converts PDF pages to individual text files
- **Intelligent Course Extraction**: Uses LLM to identify and structure course information
- **Frequency Code Recognition**: Understands A=Annual, B=Biennial, O=Occasional
- **Prerequisite Detection**: Extracts prerequisite and corequisite information
- **Natural Language Interface**: Simple prompts like "read from page 131"
- **Auto-detection**: Automatically finds the latest PDF folder
- **Error Handling**: Continues processing even if individual pages fail

## 🎯 Workflow

1. **Place PDF** in `input/pdf/` directory
2. **Run PDF extraction** to create text files: `python extract_pdf_to_pages.py`
3. **Extract courses** from specific pages: `python extract_courses.py "read from page 131"`
4. **Find results** in `course/datetime_folder/page.csv`

## 📋 Sample Output

From page 131, the system extracted:
- ACC 200: Introduction to Financial Accounting (3 units, Annual)
- ACC 205: Introduction to Financial Accounting II (3 units, Annual)  
- ACC 210: Managerial Accounting (3 units, Annual)
- ACC 301: Intermediate Financial Accounting I (3 units, Biennial)
- ACC 302: Intermediate Financial Accounting II (3 units, Biennial)

Each record includes full descriptions, prerequisites, and frequency information.