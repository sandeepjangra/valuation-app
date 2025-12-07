#!/usr/bin/env python3
"""
PDF to JSON Key-Value Extractor
Extracts text from PDF files and generates JSON with key-value pairs
"""

import os
import sys
import json
import argparse
from pathlib import Path
import re

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not found. Installing...")
    os.system("pip install PyPDF2")
    import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    return text

def parse_text_to_key_value(text):
    """Parse extracted text into key-value pairs"""
    key_value_pairs = {}
    
    # Split text into lines
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Pattern 1: Key: Value
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if key and value:
                    key_value_pairs[key] = value
        
        # Pattern 2: Key = Value
        elif '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if key and value:
                    key_value_pairs[key] = value
        
        # Pattern 3: Key - Value
        elif ' - ' in line:
            parts = line.split(' - ', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if key and value:
                    key_value_pairs[key] = value
    
    return key_value_pairs

def process_pdf_to_json(pdf_path, output_path=None):
    """Process PDF file and generate JSON"""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("Error: Could not extract text from PDF")
        return False
    
    # Parse text to key-value pairs
    key_value_pairs = parse_text_to_key_value(text)
    
    # Create output JSON structure
    output_data = {
        "source_file": os.path.basename(pdf_path),
        "extracted_at": str(Path(pdf_path).stat().st_mtime),
        "total_fields": len(key_value_pairs),
        "data": key_value_pairs
    }
    
    # Determine output path
    if not output_path:
        pdf_name = Path(pdf_path).stem
        output_path = f"{pdf_name}_extracted.json"
    
    # Write JSON file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"JSON file created: {output_path}")
        print(f"Extracted {len(key_value_pairs)} key-value pairs")
        return True
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Extract key-value pairs from PDF and generate JSON')
    parser.add_argument('pdf_file', help='Path to PDF file')
    parser.add_argument('-o', '--output', help='Output JSON file path')
    parser.add_argument('--preview', action='store_true', help='Preview extracted data without saving')
    
    args = parser.parse_args()
    
    if args.preview:
        text = extract_text_from_pdf(args.pdf_file)
        if text:
            key_value_pairs = parse_text_to_key_value(text)
            print(f"Found {len(key_value_pairs)} key-value pairs:")
            for key, value in key_value_pairs.items():
                print(f"  {key}: {value}")
    else:
        success = process_pdf_to_json(args.pdf_file, args.output)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()