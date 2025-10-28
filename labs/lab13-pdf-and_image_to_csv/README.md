# LangChain Image-to-CSV Extractor

This project uses **LangChain** with **OpenAI Vision Models** (or Azure OpenAI) to extract structured course information from images and export it to CSV.

## 🚀 Usage

### 1. Install Dependencies
```bash
python -m venv venv

venv\Scripts\activate


pip install -r requirements.txt
```

### 2. Set Environment Variables
For OpenAI:
```bash
export OPENAI_API_KEY=your_key_here
```

For Azure OpenAI:
```bash
export USE_AZURE_OPENAI=1
export AZURE_OPENAI_API_KEY=your_key
export AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
export AZURE_OPENAI_API_VERSION=2024-08-01-preview
export AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### 3. Run Extraction
Single image:
```bash
python extract_courses_to_csv.py input/image/131-output-1.png --out output/courses.csv
```

Folder of images:
```bash
python extract_courses_to_csv.py ./input/image --out courses.csv
```

The resulting CSV will contain structured course information such as:
- Course Code
- Course Title
- Units
- Section
- Description
- Prerequisites
- Offered
- etc.

---
📦 **Output:** `courses.csv`
