"""
PDF Processing Service for Property Valuation Reports
Extracts field data from uploaded PDF documents using pattern matching
"""

import os
import re
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
import pdfplumber
import PyPDF2
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)

class PDFFieldExtractor:
    """Extracts structured data from property valuation PDF reports"""
    
    def __init__(self):
        self.field_patterns = {
            # Reference Number patterns
            'reference_number': [
                r'(?:Reference\s*No\.?|Ref\.?\s*No\.?|Report\s*No\.?)[:\s]*([A-Z0-9/_-]+)',
                r'([A-Z]{2,4}[/_][A-Z]{2,4}[/_]\d+[/_]\d+[/_]\d+)',
                r'Report\s*(?:Reference|No\.?)[:\s]*([A-Z0-9/_-]+)',
            ],
            
            # Applicant Name patterns (improved for VR_70.pdf format)
            'applicant_name': [
                r'([A-Za-z]+\s+W/o\s+[A-Za-z\s]+)',  # "Manisha W/o Deepak Jangid" format
                r'(?:Name|Applicant)[:\s]*([A-Za-z\s,./W/o S/o D/o]+?)(?:\s*\n|$|Address)',
                r'(?:M/s\.?|Mr\.?|Mrs\.?|Ms\.?)\s*([A-Za-z\s.,/]+?)(?:\n|Address|Phone)',
                r'Client[:\s]*([A-Za-z\s,./W/o S/o D/o]+?)(?:\s*\n|$)',
            ],
            
            # Property Address patterns (improved)
            'property_address': [
                r'(?:Postal\s*address\s*of\s*the\s*property|Brief\s*description\s*of\s*the\s*property)[:\s]*(H\.\s*No\.\s*\d+.*?)(?:\s*\n\s*Freehold|\s*\n\s*6|\s*$)',
                r'(H\.\s*No\.\s*\d+,\s*[A-Za-z\s,.-]+Vill\.[A-Za-z\s,.-]+Tehsil[A-Za-z\s,.-]+)',  # Full address format
                r'(\d+,\s*[A-Za-z\s,.-]+(?:Extension|Colony|Nagar|Road).*?)(?:\s*\n|$)',  # "106, Royal Extension ,Vill. Chajju Majra" format
                r'(?:Property\s*Address|Address\s*of\s*Property|Location)[:\s]*(.*?)(?:\n\n|\n[A-Z])',
            ],
            
            # Inspection Date patterns
            'inspection_date': [
                r'(?:Inspection\s*Date|Date\s*of\s*Inspection)[:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{4})',
                r'(?:Visited\s*on|Inspected\s*on)[:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{4})',
                r'Date[:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{4})',
            ],
            
            # Valuation Date patterns
            'valuation_date': [
                r'(?:Valuation\s*Date|Date\s*of\s*Valuation)[:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{4})',
                r'(?:Report\s*Date|Date\s*of\s*Report)[:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{4})',
                r'As\s*on[:\s]*(\d{1,2}[.-/]\d{1,2}[.-/]\d{4})',
            ],
            
            # Property Type patterns
            'property_type': [
                r'(?:Property\s*Type|Type\s*of\s*Property)[:\s]*([A-Za-z\s]+?)(?:\n|$)',
                r'(?:Category|Classification)[:\s]*([A-Za-z\s]+?)(?:\n|$)',
                r'(?:Land|Building|Flat|House|Commercial)',
            ],
            
            # Market Value patterns  
            'market_value': [
                r'(?:Market\s*Value|Fair\s*Market\s*Value)[:\s]*(?:Rs\.?\s*|INR\s*)?([0-9,]+(?:\.\d{2})?)',
                r'(?:Valuation|Value)[:\s]*(?:Rs\.?\s*|INR\s*)?([0-9,]+(?:\.\d{2})?)',
                r'(?:Amount|Total)[:\s]*(?:Rs\.?\s*|INR\s*)?([0-9,]+(?:\.\d{2})?)',
            ]
        }
        
        # Common field mappings for form pre-fill
        self.form_field_mappings = {
            'reference_number': 'reportReferenceNumber',
            'applicant_name': 'applicantName', 
            'property_address': 'propertyAddress',
            'inspection_date': 'inspectionDate',
            'valuation_date': 'valuationDate',
            'property_type': 'propertyType',
            'market_value': 'marketValue'
        }

    def extract_text_from_pdf(self, pdf_file: BytesIO) -> str:
        """Extract text from PDF using pdfplumber with fallback to PyPDF2"""
        try:
            # Primary method: pdfplumber (better for complex layouts)
            with pdfplumber.open(pdf_file) as pdf:
                text_pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_pages.append(text)
                
                if text_pages:
                    return '\n'.join(text_pages)
            
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}. Trying PyPDF2...")
            
        try:
            # Fallback method: PyPDF2
            pdf_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_pages = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_pages.append(text)
                    
            if text_pages:
                return '\n'.join(text_pages)
                
        except Exception as e:
            logger.error(f"PyPDF2 also failed: {e}")
            
        return ""

    def clean_extracted_value(self, value: str, field_type: str) -> str:
        """Clean and format extracted field values"""
        if not value:
            return ""
            
        value = value.strip()
        
        # Clean common artifacts
        value = re.sub(r'\s+', ' ', value)  # Multiple spaces to single
        value = re.sub(r'^[:\-\s]+', '', value)  # Leading punctuation
        value = re.sub(r'[:\-\s]+$', '', value)  # Trailing punctuation
        
        # Field-specific cleaning
        if field_type in ['applicant_name', 'property_address']:
            # Remove extra whitespace and line breaks
            value = re.sub(r'\n+', ' ', value)
            value = re.sub(r'\s+', ' ', value)
            
        elif field_type in ['inspection_date', 'valuation_date']:
            # Standardize date format to DD.MM.YYYY
            value = re.sub(r'[/-]', '.', value)
            
        elif field_type == 'reference_number':
            # Keep alphanumeric and common separators
            value = re.sub(r'[^A-Z0-9/_-]', '', value.upper())
            
        elif field_type == 'market_value':
            # Clean currency values
            value = re.sub(r'[^\d,.]', '', value)
            
        return value.strip()

    def extract_field_value(self, text: str, field_name: str) -> Optional[str]:
        """Extract a specific field value using multiple pattern attempts"""
        patterns = self.field_patterns.get(field_name, [])
        
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    cleaned_value = self.clean_extracted_value(value, field_name)
                    
                    if cleaned_value and len(cleaned_value) > 2:  # Minimum length check
                        logger.info(f"Extracted {field_name}: {cleaned_value}")
                        return cleaned_value
                        
            except Exception as e:
                logger.warning(f"Pattern failed for {field_name}: {e}")
                continue
                
        return None

    def extract_all_fields(self, pdf_file: BytesIO) -> Dict[str, Any]:
        """Extract all supported fields from PDF"""
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_file)
            
            if not text:
                logger.error("No text extracted from PDF")
                return {"error": "Could not extract text from PDF"}
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Extract each field
            extracted_fields = {}
            for field_name in self.field_patterns.keys():
                value = self.extract_field_value(text, field_name)
                extracted_fields[field_name] = value
                
            # Add metadata
            extracted_fields['extraction_timestamp'] = datetime.now().isoformat()
            extracted_fields['text_length'] = len(text)
            extracted_fields['success'] = True
            
            # Count successful extractions
            successful_fields = sum(1 for v in extracted_fields.values() 
                                  if v is not None and isinstance(v, str) and v.strip())
            extracted_fields['fields_extracted'] = successful_fields
            
            logger.info(f"Successfully extracted {successful_fields} fields")
            return extracted_fields
            
        except Exception as e:
            logger.error(f"PDF field extraction failed: {e}")
            return {
                "error": f"PDF processing failed: {str(e)}",
                "success": False,
                "extraction_timestamp": datetime.now().isoformat()
            }

    def get_form_field_mapping(self, extracted_fields: Dict[str, Any]) -> Dict[str, str]:
        """Convert extracted fields to form field names for pre-filling"""
        form_data = {}
        
        for pdf_field, form_field in self.form_field_mappings.items():
            value = extracted_fields.get(pdf_field)
            if value and isinstance(value, str) and value.strip():
                form_data[form_field] = value
                
        return form_data


class PDFProcessorService:
    """Main service class for PDF processing operations"""
    
    def __init__(self):
        self.extractor = PDFFieldExtractor()
        self.max_file_size = 15 * 1024 * 1024  # 15MB limit
        self.allowed_extensions = ['.pdf']
    
    def validate_pdf_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded PDF file"""
        errors = []
        
        # Check file extension
        if not any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
            errors.append(f"Invalid file type. Only PDF files are allowed.")
            
        # Check file size
        if file_size > self.max_file_size:
            errors.append(f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB.")
            
        # Check filename
        if not filename or len(filename.strip()) == 0:
            errors.append("Invalid filename.")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "filename": filename,
            "size_mb": round(file_size / (1024*1024), 2)
        }
    
    def process_pdf_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded PDF and extract field data"""
        try:
            # Validate file
            validation = self.validate_pdf_file(filename, len(file_content))
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "; ".join(validation["errors"]),
                    "validation": validation
                }
            
            # Create BytesIO object for processing
            pdf_file = BytesIO(file_content)
            
            # Extract fields
            extracted_data = self.extractor.extract_all_fields(pdf_file)
            
            if extracted_data.get("error"):
                return {
                    "success": False,
                    "error": extracted_data["error"],
                    "validation": validation
                }
            
            # Get form field mappings
            form_fields = self.extractor.get_form_field_mapping(extracted_data)
            
            return {
                "success": True,
                "filename": filename,
                "validation": validation,
                "extracted_fields": extracted_data,
                "form_fields": form_fields,
                "processing_info": {
                    "fields_found": extracted_data.get("fields_extracted", 0),
                    "text_length": extracted_data.get("text_length", 0),
                    "timestamp": extracted_data.get("extraction_timestamp")
                }
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "filename": filename
            }


# Convenience function for direct usage
def process_pdf_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Process a PDF file and return extracted field data"""
    processor = PDFProcessorService()
    return processor.process_pdf_upload(file_content, filename)


if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test with sample PDF
    sample_pdf_path = "/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend/data/VR_70.pdf"
    
    if os.path.exists(sample_pdf_path):
        with open(sample_pdf_path, 'rb') as f:
            content = f.read()
            result = process_pdf_file(content, "VR_70.pdf")
            print("PDF Processing Result:")
            print(f"Success: {result.get('success')}")
            
            if not result.get('success'):
                print(f"Error: {result.get('error')}")
            else:
                print(f"Fields extracted: {result.get('processing_info', {}).get('fields_found', 0)}")
                
                if result.get('extracted_fields'):
                    print("\nExtracted Fields:")
                    for field, value in result['extracted_fields'].items():
                        if isinstance(value, str) and value.strip():
                            print(f"  {field}: {value}")
                            
                if result.get('form_fields'):
                    print("\nForm Field Mappings:")
                    for form_field, value in result['form_fields'].items():
                        print(f"  {form_field}: {value}")
    else:
        print(f"Sample PDF not found at: {sample_pdf_path}")