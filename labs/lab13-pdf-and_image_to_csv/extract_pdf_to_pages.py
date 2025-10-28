from pypdf import PdfReader
import os
from pathlib import Path
from datetime import datetime

def extract_pdf_to_pages():
    """
    Extract all pages from PDF files in input/pdf directory and save each page as a text file.
    Output format: output/datetime_input_filename_without_pdf_extension/pagenumber.txt
    """
    # Setup paths
    input_dir = Path("input/pdf")
    output_base_dir = Path("output")
    
    # Get current datetime for folder naming
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Process all PDF files in the input directory
    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processing {pdf_file.name}...")
        
        # Create output directory for this PDF
        filename_without_ext = pdf_file.stem
        output_dir = output_base_dir / f"{current_datetime}_{filename_without_ext}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Open the PDF file
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            print(f"Found {total_pages} pages in {pdf_file.name}")
            
            # Extract text from each page
            for page_number in range(total_pages):
                try:
                    page = reader.pages[page_number]
                    text = page.extract_text()
                    
                    # Save to text file (page numbers start from 1 for filename)
                    output_file = output_dir / f"{page_number + 1}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    print(f"  Extracted page {page_number + 1} -> {output_file}")
                    
                except Exception as e:
                    print(f"  Error extracting page {page_number + 1}: {e}")
                    
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
    
    print("PDF extraction complete!")

if __name__ == "__main__":
    extract_pdf_to_pages()