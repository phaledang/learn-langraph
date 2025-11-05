# PDF Course Extraction System

This project provides a **clean, automated workflow** for extracting course information from PDF documents using **Azure OpenAI** and **LangChain**. The system automatically processes PDF pages, detects course content, and exports structured data to CSV format.

## 🌟 Key Features

- **🔄 Clean Workflow**: Automated 4-step process from PDF to CSV
- **📖 Auto Page Range Detection**: Reads page ranges from guide.txt files
- **🤖 Azure OpenAI Integration**: Uses GPT-4o-mini for intelligent course extraction
- **📁 Organized Processing**: Timestamped process folders with complete traceability
- **📊 Batch Processing**: Handles large PDF documents efficiently
- **💾 Consolidated Output**: Individual batch files plus master CSV

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Azure OpenAI
Create a `.env` file with your Azure OpenAI credentials:
```env
USE_AZURE_OPENAI=1
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 3. Prepare Input Folder
Organize your files in the `input/` directory:
```
input/
  └── 233878/
      ├── 233878.pdf          # PDF document to process
      ├── guide.txt           # Extraction guidelines with page range
      └── sample.csv          # Expected CSV format sample
```

### 4. Run Clean Extraction Workflow
```bash
python process_courses.py 233878 --max-pages 3
```

## 📋 Clean Workflow Steps

The `process_courses.py` script implements a **4-step clean workflow**:

### Step 1: 📁 Setup Process Folder
- Creates timestamped process folder: `process/YYYYMMDD_HHMMSS_foldername/`
- Copies all input files to process folder for clean organization
- Maintains complete traceability of processing

### Step 2: 📄 Extract PDF to Pages
- Extracts all PDF pages to individual text files: `pages/1.txt`, `pages/2.txt`, etc.
- Preserves page numbering from original PDF
- Creates searchable text corpus for batch processing

### Step 3: 📋 Build Consolidated Guide
- Combines `guide.txt` + `sample.csv` into `guide-on-one-page.txt`
- Automatically detects and extracts page range (e.g., "read from page 131 to page 198")
- Removes page range instructions from final guide
- Creates clean, unified extraction guidelines

### Step 4: 🤖 Execute Extraction
- Processes detected page range in configurable batches
- Uses Azure OpenAI GPT-4o-mini for intelligent course extraction
- Creates individual CSV files per batch
- Generates consolidated CSV with all extracted courses

## 📊 Sample Results

**Extraction Statistics from Real Run:**
- **Pages Processed**: 131-198 (68 pages)
- **Batches Created**: 34 batches
- **Courses Extracted**: 591 courses
- **Success Rate**: 100%


## 🔧 Configuration Options

### Command Line Arguments
```bash
python process_courses.py <input_folder> [--max-pages N]

# Examples:
python process_courses.py 233878                    # Default 3 pages per batch
python process_courses.py 233878 --max-pages 5     # 5 pages per batch
python process_courses.py my_catalog --max-pages 2  # 2 pages per batch
```

### Guide.txt Format
Your `guide.txt` should include:
1. **Page range instruction**: "read from page X to page Y"
2. **Extraction guidelines**: Detailed instructions for course extraction
3. **Format specifications**: How to handle frequency codes (A=Annually, B=Biennially)

Example:
```
read from page 131 to page 198 to extract the course information into csv, refer to the sample input. 
In the header "ACC 200 Introduction to Financial Accounting (3-1T) A": A means Annually, B means Biennially. 
3 means Units = 3

Sample input in page 131
include your sample there
```

## 🛠️ Advanced Usage

### Legacy Scripts (Still Available)
```bash
# Original single-file extraction
python extract_courses.py --pdf-folder input/233878 --max-pages 3

# Image-based extraction
python extract_courses_to_csv.py input/image/131-output-1.png --out output/courses.csv

# Batch processing multiple folders
python batch_extract_courses.py
```

### Testing Azure OpenAI Connection
```bash
python test_openai.py
```

## 📦 Dependencies

Key packages (see `requirements.txt` for complete list):
- `openai` - Azure OpenAI integration
- `pypdf` - PDF text extraction
- `python-dotenv` - Environment configuration
- `pandas` - Data processing

## ⚡ Performance Tips

1. **Batch Size**: Use `--max-pages 2-5` for optimal performance
2. **Large PDFs**: Process will automatically handle pagination
3. **API Limits**: Script includes error handling for rate limits
4. **Memory**: Each page extracted to individual files for efficient processing

## 🎯 Use Cases

- **University Catalogs**: Extract course information from academic catalogs
- **Training Materials**: Process corporate training course documents  
- **Curriculum Analysis**: Bulk extraction for educational research
- **Data Migration**: Convert legacy PDF catalogs to structured data

## ✅ Success Metrics

The system has been successfully tested with:
- ✅ 206-page PDF documents
- ✅ 591 course extractions in single run
- ✅ Complex course descriptions with prerequisites
- ✅ Multiple department classifications
- ✅ Frequency coding (Annual/Biennial/Occasional)

## 🔧 Troubleshooting

**Common Issues:**
- **API Key Error**: Ensure `.env` file is properly configured
- **Page Range Not Found**: Check `guide.txt` format for page range instruction
- **Empty Results**: Verify PDF contains extractable text (not scanned images)
- **Batch Failures**: Check Azure OpenAI service availability and quotas

**Debug Commands:**
```bash
python test_openai.py                    # Test API connection
python process_courses.py 233878 --max-pages 1  # Test with smaller batches
```

