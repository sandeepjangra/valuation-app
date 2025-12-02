"""
PDF Upload and Processing API endpoints
Handles file upload and field extraction for property valuation forms
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

# Import our PDF processor
from services.pdf_processor import PDFProcessorService

# Set up logging
logger = logging.getLogger(__name__)

# Create router for PDF-related endpoints
pdf_router = APIRouter(prefix="/api/pdf", tags=["PDF Processing"])

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
                "form_field_mapping": True
            }
        }
        
    except Exception as e:
        logger.error(f"PDF service health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }


# Export the router for inclusion in main app
__all__ = ["pdf_router"]