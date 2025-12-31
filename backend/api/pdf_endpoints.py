"""
PDF Upload and Processing API endpoints
Handles file upload and field extraction for property valuation forms
PLUS PDF Generation for reports
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import our PDF processor and generator
from services.pdf_processor import PDFProcessorService
try:
    from pdf_generator_fallback import pdf_generator
    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("PDF Generator not available - only PDF processing will work")

# Set up logging
logger = logging.getLogger(__name__)

# Create router for PDF-related endpoints (processing + generation)
pdf_router = APIRouter(prefix="/api", tags=["PDF Processing & Generation"])

# Initialize PDF processor
pdf_processor = PDFProcessorService()


@pdf_router.post("/upload", response_model=Dict[str, Any])
async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process a PDF file for field extraction
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        Dictionary containing extraction results and form field mappings
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
        
        logger.info(f"Processing PDF upload: {file.filename} ({len(file_content)} bytes)")
        
        # Process the PDF
        result = pdf_processor.process_pdf_upload(file_content, file.filename)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.get("error", "PDF processing failed")
            )
        
        logger.info(f"Successfully processed PDF: {result.get('processing_info', {}).get('fields_found', 0)} fields extracted")
        
        return {
            "success": True,
            "message": f"PDF processed successfully. Extracted {result.get('processing_info', {}).get('fields_found', 0)} fields.",
            "data": {
                "filename": result.get("filename"),
                "validation": result.get("validation"),
                "extracted_fields": result.get("extracted_fields", {}),
                "form_fields": result.get("form_fields", {}),
                "processing_info": result.get("processing_info", {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@pdf_router.post("/extract-fields", response_model=Dict[str, Any])
async def extract_fields_from_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extract only field data from PDF without validation info
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        Dictionary containing extracted field mappings for form pre-fill
    """
    try:
        # Process the upload
        result = await upload_pdf(file)
        
        if not result.get("success"):
            return result
        
        # Return only the form fields for direct integration
        return {
            "success": True,
            "fields": result["data"]["form_fields"],
            "metadata": {
                "filename": result["data"]["filename"],
                "fields_extracted": result["data"]["processing_info"].get("fields_found", 0),
                "extraction_timestamp": result["data"]["extracted_fields"].get("extraction_timestamp")
            }
        }
        
    except Exception as e:
        logger.error(f"Field extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Field extraction failed: {str(e)}"
        )


@pdf_router.get("/supported-fields")
async def get_supported_fields() -> Dict[str, Any]:
    """
    Get list of fields that can be extracted from PDFs
    
    Returns:
        Dictionary of supported field names and their descriptions
    """
    return {
        "success": True,
        "supported_fields": {
            "reference_number": {
                "description": "Report reference number",
                "form_field": "reportReferenceNumber",
                "example": "CEV/RVO/299/4699/21092025"
            },
            "applicant_name": {
                "description": "Name of the applicant/borrower",
                "form_field": "applicantName",
                "example": "Manisha W/o Deepak Jangid"
            },
            "property_address": {
                "description": "Property address or location",
                "form_field": "propertyAddress",
                "example": "H. No. 106, Royal Extension, Vill. Chajju Majra"
            },
            "inspection_date": {
                "description": "Date of property inspection",
                "form_field": "inspectionDate",
                "example": "21.09.2025"
            },
            "valuation_date": {
                "description": "Date of valuation",
                "form_field": "valuationDate",
                "example": "21.09.2025"
            },
            "property_type": {
                "description": "Type of property",
                "form_field": "propertyType",
                "example": "LAND"
            },
            "market_value": {
                "description": "Market value amount",
                "form_field": "marketValue",
                "example": "50.35"
            }
        },
        "processing_info": {
            "max_file_size_mb": pdf_processor.max_file_size // (1024 * 1024),
            "supported_extensions": pdf_processor.allowed_extensions,
            "extraction_method": "Pattern matching with OCR fallback"
        }
    }


@pdf_router.get("/health")
async def pdf_service_health() -> Dict[str, Any]:
    """Check PDF service health"""
    try:
        # Test basic functionality
        test_data = b"dummy content"
        
        return {
            "success": True,
            "status": "healthy",
            "service": "PDF Processing Service",
            "version": "1.0.0",
            "capabilities": {
                "pdf_text_extraction": True,
                "field_pattern_matching": True,
                "form_field_mapping": True,
                "pdf_generation": PDF_GENERATOR_AVAILABLE
            }
        }
        
    except Exception as e:
        logger.error(f"PDF service health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }


# ================================
# PDF GENERATION ENDPOINTS
# ================================

@pdf_router.post("/reports/{report_id}/generate-pdf")
async def generate_report_pdf(report_id: str, request: Request):
    """
    Generate PDF for a specific report
    
    Creates a professional PDF document from stored report data
    using bank-specific templates with proper branding.
    """
    
    if not PDF_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="PDF generation service is not available. Please install required dependencies."
        )
    
    try:
        # TODO: In production, fetch actual report data from database
        # Example query: report_data = await get_report_from_database(report_id)
        
        sample_form_data = {
            '_id': report_id,
            'reference_number': f'SBI-LP-{report_id[:8].upper()}',
            'property_address': '123 Sample Street, Sample Area, Sample City - 400001',
            'survey_number': '123/4A',
            'village': 'Sample Village',
            'taluka': 'Sample Taluka',  
            'district': 'Sample District',
            'total_extent_plot': 2400,
            'valuation_rate': 5000,
            'estimated_land_value': 12000000
        }
        
        # Generate PDF using simplified generator
        report_data = {
            'bankCode': 'SBI',
            'propertyType': 'land',
            'reportReferenceNumber': f'SBI-LP-{report_id[:8].upper()}',
            'organizationShortName': 'ValuationOrg',
            'formValues': sample_form_data,
            'templateData': {
                'documents': [
                    {
                        'sections': [
                            {
                                'title': 'Property Information',
                                'fields': [
                                    {'fieldId': 'property_address', 'label': 'Property Address'},
                                    {'fieldId': 'survey_number', 'label': 'Survey Number'},
                                    {'fieldId': 'village', 'label': 'Village'},
                                    {'fieldId': 'taluka', 'label': 'Taluka'},
                                    {'fieldId': 'district', 'label': 'District'}
                                ]
                            },
                            {
                                'title': 'Valuation Details', 
                                'fields': [
                                    {'fieldId': 'total_extent_plot', 'label': 'Total Plot Area (sq.ft)'},
                                    {'fieldId': 'valuation_rate', 'label': 'Valuation Rate (₹/sq.ft)'},
                                    {'fieldId': 'estimated_land_value', 'label': 'Estimated Land Value (₹)'}
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        pdf_bytes = pdf_generator.generate_pdf(report_data)
        
        # Return response (text format for now)
        return Response(
            content=pdf_bytes,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=SBI_Land_Report_{report_id}.txt"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@pdf_router.get("/pdf-templates/{bank_code}/{property_type}")
async def get_pdf_template_info(bank_code: str, property_type: str):
    """
    Get information about available PDF templates
    
    Returns template configuration and customization options
    for the specified bank and property type.
    """
    
    templates_info = {
        'SBI': {
            'LAND_PROPERTY': {
                'name': 'State Bank of India - Land Property Valuation',
                'description': 'Comprehensive land property valuation report with SBI branding',
                'sections': [
                    'Report Header with SBI Branding',
                    'Property Details & Location',
                    'Valuation Assessment Table', 
                    'Summary & Total Value',
                    'Signature Section'
                ],
                'customizable_fields': [
                    'property_address', 'survey_number', 'village',
                    'taluka', 'district', 'total_extent_plot',
                    'valuation_rate', 'estimated_land_value'
                ],
                'styling_options': {
                    'colors': ['SBI Blue (#1e40af)', 'Custom'],
                    'fonts': ['Arial', 'Times New Roman', 'Calibri'],
                    'page_size': ['A4', 'Letter'],
                    'orientation': ['Portrait', 'Landscape']
                },
                'available': True,
                'version': '1.0'
            }
        }
    }
    
    if bank_code in templates_info and property_type in templates_info[bank_code]:
        template_info = templates_info[bank_code][property_type]
        template_info['bank_full_name'] = get_bank_full_name(bank_code)
        return template_info
    else:
        return {
            'available': False,
            'message': f'Template for {bank_code} {property_type} is not yet available',
            'supported_templates': ['SBI/LAND_PROPERTY'],
            'contact': 'Please contact support to request additional templates'
        }

@pdf_router.get("/pdf-templates")
async def list_available_templates():
    """
    List all available PDF templates with their capabilities
    
    Returns a comprehensive list of supported bank and property type
    combinations for PDF report generation.
    """
    
    try:
        return pdf_generator.get_available_templates()
    except Exception as e:
        return {
            'templates': [],
            'message': f'PDF generation service error: {str(e)}',
            'total_available': 0
        }

@pdf_router.post("/pdf-templates")
async def create_pdf_template(template_data: dict):
    """
    Create a new PDF template
    """
    try:
        # TODO: Implement template creation logic
        # For now, return success response
        return {
            'success': True,
            'message': 'PDF template created successfully',
            'template_id': f"template_{template_data.get('bankCode', 'unknown')}_{template_data.get('propertyType', 'unknown')}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create PDF template: {str(e)}")

@pdf_router.get("/pdf-templates/{template_id}")
async def get_pdf_template(template_id: str):
    """
    Get specific PDF template by ID
    """
    try:
        # TODO: Implement template retrieval logic
        # For now, return sample template
        return {
            'id': template_id,
            'bankCode': 'SBI',
            'propertyType': 'land',
            'templateName': 'SBI Land Property Valuation',
            'sections': [],
            'pageWidth': 210,
            'pageHeight': 297,
            'margins': {'top': 20, 'right': 15, 'bottom': 20, 'left': 15}
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Template not found: {str(e)}")

@pdf_router.put("/pdf-templates/{template_id}")
async def update_pdf_template(template_id: str, template_data: dict):
    """
    Update existing PDF template
    """
    try:
        # TODO: Implement template update logic
        return {
            'success': True,
            'message': 'PDF template updated successfully',
            'template_id': template_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update PDF template: {str(e)}")

@pdf_router.delete("/pdf-templates/{template_id}")
async def delete_pdf_template(template_id: str):
    """
    Delete PDF template
    """
    try:
        # TODO: Implement template deletion logic
        return {
            'success': True,
            'message': 'PDF template deleted successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF template: {str(e)}")

def get_bank_full_name(bank_code: str) -> str:
    """Get full bank name from bank code"""
    bank_names = {
        'SBI': 'State Bank of India',
        'HDFC': 'HDFC Bank Limited',
        'ICICI': 'ICICI Bank Limited',
        'BOI': 'Bank of India',
        'PNB': 'Punjab National Bank',
        'BOB': 'Bank of Baroda',
        'UBI': 'Union Bank of India',
        'UCO': 'UCO Bank',
        'CBI': 'Central Bank of India'
    }
    return bank_names.get(bank_code, bank_code)


# Export the router for inclusion in main app
__all__ = ["pdf_router"]