# PDF to JSON Key-Value Extractor

A Python script to extract text from PDF files and generate JSON files with key-value pairs.

## Usage

```bash
# Basic usage
python pdf_to_json_extractor.py input.pdf

# Specify output file
python pdf_to_json_extractor.py input.pdf -o output.json

# Preview extracted data without saving
python pdf_to_json_extractor.py input.pdf --preview
```

## Features

- Extracts text from PDF files using PyPDF2
- Parses text for key-value patterns:
  - `Key: Value`
  - `Key = Value` 
  - `Key - Value`
- Generates structured JSON output
- Automatic dependency installation

## Output Format

```json
{
  "source_file": "document.pdf",
  "extracted_at": "1699123456.789",
  "total_fields": 25,
  "data": {
    "Field Name": "Field Value",
    "Another Field": "Another Value"
  }
}
```

## Requirements

- Python 3.6+
- PyPDF2 (auto-installed if missing)