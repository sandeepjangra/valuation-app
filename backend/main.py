"""
FastAPI Backend Application for Valuation System
MongoDB Atlas integration with dynamic form templates
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bson import ObjectId
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Import our database manager (will be available after pip install)
from database.multi_db_manager import MultiDatabaseSession

# Import admin API routes
from admin_api import admin_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Security
security = HTTPBearer()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    
    # Startup
    logger.info("🚀 Starting Valuation Application...")
    
    # Connect to MongoDB Atlas
    # try:
    #     await db_manager.connect()
    #     logger.info("✅ Connected to MongoDB Atlas")
    # except Exception as e:
    #     logger.error(f"❌ Failed to connect to MongoDB: {e}")
    #     raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Valuation Application...")
    # await db_manager.disconnect()

# Create FastAPI application
app = FastAPI(
    title="Valuation Application API",
    description="Property Valuation System for Indian Banks",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:4200").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include admin router
app.include_router(admin_router)

# ================================
# Utility Functions
# ================================

def json_serializer(obj: Any) -> str:
    """JSON serializer for MongoDB ObjectId and datetime"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user (placeholder)"""
    # TODO: Implement JWT token validation
    # For now, return a mock user
    return {
        "_id": ObjectId(),
        "userId": "EMP001",
        "email": "test@example.com",
        "role": "EMPLOYEE"
    }

# ================================
# Health Check Endpoint
# ================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # db_health = await db_manager.health_check()
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "valuation-api",
            "version": "1.0.0",
            # "database": db_health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

import asyncio
from datetime import timedelta
from typing import Optional

# Add caching for common fields
COMMON_FIELDS_CACHE: Optional[List[Dict[str, Any]]] = None
CACHE_TIMESTAMP: Optional[datetime] = None
CACHE_DURATION = timedelta(minutes=15)  # Cache for 15 minutes

async def get_cached_common_fields() -> List[Dict[str, Any]]:
    """Get common fields with caching"""
    global COMMON_FIELDS_CACHE, CACHE_TIMESTAMP
    
    # Check if cache is valid
    if (COMMON_FIELDS_CACHE is not None and 
        CACHE_TIMESTAMP is not None and 
        datetime.now(timezone.utc) - CACHE_TIMESTAMP < CACHE_DURATION):
        logger.info("📋 Returning cached common fields")
        return COMMON_FIELDS_CACHE
    
    # Cache miss or expired, fetch from database
    logger.info("🔄 Fetching fresh common fields from database")
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            async with MultiDatabaseSession() as db:
                fields = await db.find_many("admin", "common_form_fields", {"isActive": True}, sort=[("fieldGroup", 1), ("sortOrder", 1)])
                
                # Update cache
                COMMON_FIELDS_CACHE = fields
                CACHE_TIMESTAMP = datetime.now(timezone.utc)
                
                logger.info(f"✅ Cached {len(fields)} common fields")
                return fields
                
        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt + 1} failed to fetch common fields: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
    
    # If all retries failed, return empty list
    logger.error("❌ Failed to fetch common fields after all retries")
    return []

# ================================
# Common Form Fields API
# ================================

@app.get("/api/common-fields", response_model=List[Dict[str, Any]])
async def get_common_fields() -> JSONResponse:
    """Get all common form fields organized by groups with caching"""
    try:
        fields = await get_cached_common_fields()
        return JSONResponse(
            content=json.loads(json.dumps(fields, default=json_serializer))
        )
        
    except Exception as e:
        logger.error(f"Error fetching common fields: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch common fields")

@app.post("/api/common-fields/refresh")
async def refresh_common_fields_cache() -> JSONResponse:
    """Refresh the common fields cache (admin only)"""
    global COMMON_FIELDS_CACHE, CACHE_TIMESTAMP
    try:
        # Clear cache
        COMMON_FIELDS_CACHE = None
        CACHE_TIMESTAMP = None
        
        # Fetch fresh data
        fields = await get_cached_common_fields()
        
        return JSONResponse(
            content={
                "message": "Cache refreshed successfully",
                "fields_count": len(fields),
                "refreshed_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error refreshing common fields cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh cache")

@app.get("/api/common-fields/group/{group_name}", response_model=List[Dict[str, Any]])
async def get_common_fields_by_group(group_name: str) -> List[Dict[str, Any]]:
    """Get common fields for a specific group"""
    try:
        # async with DatabaseSession() as db:
        #     fields = await db.find_many(
        #         "common_form_fields", 
        #         {"fieldGroup": group_name, "isActive": True},
        #         sort_by={"sortOrder": 1}
        #     )
        #     return JSONResponse(
        #         content=json.loads(json.dumps(fields, default=json_serializer))
        #     )
        
        # Mock response based on group
        if group_name == "basic_info":
            return [
                {
                    "_id": "672345678901234567890201",
                    "fieldId": "valuation_date",
                    "fieldGroup": "basic_info",
                    "technicalName": "valuation_date",
                    "uiDisplayName": "Date of Valuation",
                    "fieldType": "date",
                    "isRequired": True,
                    "gridSize": 6,
                    "sortOrder": 1
                },
                {
                    "_id": "672345678901234567890202",
                    "fieldId": "report_reference_number",
                    "fieldGroup": "basic_info",
                    "technicalName": "report_reference_number",
                    "uiDisplayName": "Report Reference Number",
                    "fieldType": "text",
                    "isRequired": True,
                    "gridSize": 6,
                    "sortOrder": 2
                }
            ]
        else:
            return []
        
    except Exception as e:
        logger.error(f"Error fetching fields for group {group_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch fields for group")

@app.get("/api/banks/{bank_code}/branches", response_model=List[Dict[str, Any]])
async def get_bank_branches(bank_code: str) -> List[Dict[str, Any]]:
    """Get all branches for a specific bank"""
    try:
        # async with DatabaseSession() as db:
        #     bank = await db.get_bank_by_code(bank_code.upper())
        #     if not bank:
        #         raise HTTPException(status_code=404, detail="Bank not found")
        #     
        #     branches = bank.get("branches", [])
        #     active_branches = [branch for branch in branches if branch.get("isActive", True)]
        #     return JSONResponse(
        #         content=json.loads(json.dumps(active_branches, default=json_serializer))
        #     )
        
        # Mock response based on bank code
        if bank_code.upper() == "SBI":
            return [
                {
                    "branchId": "SBI_DEL_CP_001",
                    "branchName": "Connaught Place",
                    "branchCode": "SBIN0000001",
                    "ifscCode": "SBIN0000001",
                    "address": {
                        "street": "Janpath Road, Connaught Place",
                        "city": "New Delhi",
                        "state": "Delhi",
                        "pincode": "110001"
                    },
                    "contact": {
                        "phone": "+91-11-23417930",
                        "email": "sbi.cp.delhi@sbi.co.in"
                    },
                    "isActive": True
                },
                {
                    "branchId": "SBI_MUM_BKC_002",
                    "branchName": "Bandra Kurla Complex",
                    "branchCode": "SBIN0000002",
                    "ifscCode": "SBIN0000002",
                    "address": {
                        "street": "G Block, Bandra Kurla Complex",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400051"
                    },
                    "contact": {
                        "phone": "+91-22-26542100",
                        "email": "sbi.bkc.mumbai@sbi.co.in"
                    },
                    "isActive": True
                }
            ]
        elif bank_code.upper() == "HDFC":
            return [
                {
                    "branchId": "HDFC_MUM_BND_001",
                    "branchName": "Bandra West",
                    "branchCode": "HDFC0000001",
                    "ifscCode": "HDFC0000001",
                    "address": {
                        "street": "Turner Road, Bandra West",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400050"
                    },
                    "contact": {
                        "phone": "+91-22-26420000",
                        "email": "hdfc.bandra.mumbai@hdfcbank.com"
                    },
                    "isActive": True
                }
            ]
        else:
            return []
        
    except Exception as e:
        logger.error(f"Error fetching branches for bank {bank_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bank branches")

# ================================
# Banks API Endpoints
# ================================

@app.get("/api/banks", response_model=List[Dict[str, Any]])
async def get_banks():
    """Get all active banks"""
    try:
        async with MultiDatabaseSession() as db:
            banks = await db.find_many("admin", "banks", {"isActive": True})
            return JSONResponse(
                content=json.loads(json.dumps(banks, default=json_serializer))
            )
        
    except Exception as e:
        logger.error(f"Error fetching banks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch banks")

@app.get("/api/banks/{bank_code}", response_model=Dict[str, Any])
async def get_bank(bank_code: str) -> Dict[str, Any]:
    """Get bank details by bank code"""
    try:
        # async with DatabaseSession() as db:
        #     bank = await db.get_bank_by_code(bank_code.upper())
        #     if not bank:
        #         raise HTTPException(status_code=404, detail="Bank not found")
        #     
        #     return JSONResponse(
        #         content=json.loads(json.dumps(bank, default=json_serializer))
        #     )
        
        # Mock response
        if bank_code.upper() == "SBI":
            return {
                "_id": "672345678901234567890123",
                "bankCode": "SBI",
                "bankName": "State Bank of India",
                "bankType": "PUBLIC_SECTOR",
                "submissionMode": "HARDCOPY",
                "contactInfo": {
                    "address": "Corporate Centre, Nariman Point, Mumbai",
                    "email": "valuations@sbi.co.in",
                    "phone": "+91-22-22740000"
                },
                "isActive": True
            }
        else:
            raise HTTPException(status_code=404, detail="Bank not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bank {bank_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bank details")

# ================================
# Templates API Endpoints
# ================================

@app.get("/api/templates/bank/{bank_code}", response_model=List[Dict[str, Any]])
async def get_templates_for_bank(bank_code: str) -> List[Dict[str, Any]]:
    """Get all templates for a specific bank"""
    try:
        async with MultiDatabaseSession() as db:
            # Find bank by code and get its templates
            bank = await db.find_one("admin", "banks", {"code": bank_code.upper(), "isActive": True})
            if not bank:
                return []
            
            templates = bank.get("templates", [])
            return templates
    except Exception as e:
        logger.error(f"Error fetching templates for bank {bank_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch templates")

@app.get("/api/templates/{template_id}", response_model=Dict[str, Any])
async def get_template(template_id: str) -> Dict[str, Any]:
    """Get complete template with form fields"""
    try:
        # Mock response with detailed template structure matching Angular models
        if template_id == "property-description-v1":
            return {
                "id": "property-description-v1",
                "name": "Property Description Template",
                "description": "Standard template for property valuation report - Property Description section",
                "version": "1.0",
                "category": "general",
                "sections": [
                    {
                        "id": "basic-details",
                        "title": "Basic Report Details",
                        "description": "Essential information about the valuation report",
                        "order": 1,
                        "collapsible": True,
                        "expanded": True,
                        "visible": True,
                        "fields": [
                            {
                                "id": "reportDate",
                                "name": "reportDate",
                                "label": "Report Date",
                                "type": "date",
                                "required": True,
                                "gridSize": 6,
                                "order": 1,
                                "visible": True,
                                "defaultValue": datetime.now(timezone.utc).strftime('%Y-%m-%d')
                            },
                            {
                                "id": "inspectionDate",
                                "name": "inspectionDate",
                                "label": "Inspection Date",
                                "type": "date",
                                "required": True,
                                "gridSize": 6,
                                "order": 2,
                                "visible": True
                            },
                            {
                                "id": "purpose",
                                "name": "purpose",
                                "label": "Purpose of Valuation",
                                "type": "select",
                                "required": True,
                                "gridSize": 12,
                                "order": 3,
                                "visible": True,
                                "options": [
                                    {"value": "mortgage", "label": "Mortgage/Loan"},
                                    {"value": "sale", "label": "Sale Transaction"},
                                    {"value": "insurance", "label": "Insurance"},
                                    {"value": "taxation", "label": "Taxation"},
                                    {"value": "investment", "label": "Investment Analysis"}
                                ]
                            }
                        ]
                    },
                    {
                        "id": "bank-details",
                        "title": "Bank Details",
                        "description": "Information about the bank and loan",
                        "order": 2,
                        "collapsible": True,
                        "expanded": False,
                        "visible": True,
                        "fields": [
                            {
                                "id": "bankName",
                                "name": "bankName",
                                "label": "Bank Name",
                                "type": "text",
                                "required": True,
                                "gridSize": 6,
                                "order": 1,
                                "visible": True
                            },
                            {
                                "id": "branchName",
                                "name": "branchName",
                                "label": "Branch Name",
                                "type": "text",
                                "required": True,
                                "gridSize": 6,
                                "order": 2,
                                "visible": True
                            },
                            {
                                "id": "loanAmount",
                                "name": "loanAmount",
                                "label": "Loan Amount (₹)",
                                "type": "number",
                                "required": True,
                                "gridSize": 6,
                                "order": 3,
                                "visible": True,
                                "validation": {"min": 100000, "max": 100000000}
                            },
                            {
                                "id": "loanType",
                                "name": "loanType",
                                "label": "Loan Type",
                                "type": "select",
                                "required": True,
                                "gridSize": 6,
                                "order": 4,
                                "visible": True,
                                "options": [
                                    {"value": "home-loan", "label": "Home Loan"},
                                    {"value": "plot-loan", "label": "Plot Loan"},
                                    {"value": "construction-loan", "label": "Construction Loan"},
                                    {"value": "commercial-loan", "label": "Commercial Loan"}
                                ]
                            }
                        ]
                    },
                    {
                        "id": "valuer-details",
                        "title": "Valuer Details",
                        "description": "Information about the valuation professional",
                        "order": 3,
                        "collapsible": True,
                        "expanded": False,
                        "visible": True,
                        "fields": [
                            {
                                "id": "valuerName",
                                "name": "valuerName",
                                "label": "Valuer Name",
                                "type": "text",
                                "required": True,
                                "gridSize": 6,
                                "order": 1,
                                "visible": True
                            },
                            {
                                "id": "valuerLicense",
                                "name": "valuerLicense",
                                "label": "License Number",
                                "type": "text",
                                "required": True,
                                "gridSize": 6,
                                "order": 2,
                                "visible": True
                            },
                            {
                                "id": "valuerContact",
                                "name": "valuerContact",
                                "label": "Contact Number",
                                "type": "tel",
                                "required": True,
                                "gridSize": 6,
                                "order": 3,
                                "visible": True
                            },
                            {
                                "id": "valuerEmail",
                                "name": "valuerEmail",
                                "label": "Email Address",
                                "type": "email",
                                "required": True,
                                "gridSize": 6,
                                "order": 4,
                                "visible": True
                            }
                        ]
                    },
                    {
                        "id": "borrower-details",
                        "title": "Borrower/Owner Details",
                        "description": "Information about the property owner or borrower",
                        "order": 4,
                        "collapsible": True,
                        "expanded": False,
                        "visible": True,
                        "fields": [
                            {
                                "id": "ownerName",
                                "name": "ownerName",
                                "label": "Owner/Borrower Name",
                                "type": "text",
                                "required": True,
                                "gridSize": 6,
                                "order": 1,
                                "visible": True
                            },
                            {
                                "id": "ownerContact",
                                "name": "ownerContact",
                                "label": "Contact Number",
                                "type": "tel",
                                "required": True,
                                "gridSize": 6,
                                "order": 2,
                                "visible": True
                            },
                            {
                                "id": "ownerEmail",
                                "name": "ownerEmail",
                                "label": "Email Address",
                                "type": "email",
                                "required": False,
                                "gridSize": 6,
                                "order": 3,
                                "visible": True
                            },
                            {
                                "id": "ownerOccupation",
                                "name": "ownerOccupation",
                                "label": "Occupation",
                                "type": "text",
                                "required": False,
                                "gridSize": 6,
                                "order": 4,
                                "visible": True
                            }
                        ]
                    },
                    {
                        "id": "property-details",
                        "title": "Property Details",
                        "description": "Comprehensive property information",
                        "order": 5,
                        "collapsible": True,
                        "expanded": False,
                        "visible": True,
                        "fields": [
                            {
                                "id": "propertyType",
                                "name": "propertyType",
                                "label": "Property Type",
                                "type": "select",
                                "required": True,
                                "gridSize": 6,
                                "order": 1,
                                "visible": True,
                                "options": [
                                    {"value": "residential-flat", "label": "Residential Flat"},
                                    {"value": "independent-house", "label": "Independent House"},
                                    {"value": "villa", "label": "Villa"},
                                    {"value": "plot", "label": "Plot/Land"},
                                    {"value": "commercial", "label": "Commercial"}
                                ]
                            },
                            {
                                "id": "constructionType",
                                "name": "constructionType",
                                "label": "Construction Type",
                                "type": "select",
                                "required": True,
                                "gridSize": 6,
                                "order": 2,
                                "visible": True,
                                "options": [
                                    {"value": "rcc", "label": "RCC Structure"},
                                    {"value": "load-bearing", "label": "Load Bearing"},
                                    {"value": "steel-frame", "label": "Steel Frame"},
                                    {"value": "mixed", "label": "Mixed Construction"}
                                ]
                            },
                            {
                                "id": "totalArea",
                                "name": "totalArea",
                                "label": "Total Area (sq ft)",
                                "type": "number",
                                "required": True,
                                "gridSize": 6,
                                "order": 3,
                                "visible": True,
                                "validation": {"min": 100, "max": 50000}
                            },
                            {
                                "id": "carpetArea",
                                "name": "carpetArea",
                                "label": "Carpet Area (sq ft)",
                                "type": "number",
                                "required": True,
                                "gridSize": 6,
                                "order": 4,
                                "visible": True,
                                "validation": {"min": 50, "max": 40000}
                            },
                            {
                                "id": "propertyAge",
                                "name": "propertyAge",
                                "label": "Property Age (years)",
                                "type": "number",
                                "required": True,
                                "gridSize": 6,
                                "order": 5,
                                "visible": True,
                                "validation": {"min": 0, "max": 100}
                            },
                            {
                                "id": "bedrooms",
                                "name": "bedrooms",
                                "label": "Number of Bedrooms",
                                "type": "select",
                                "required": True,
                                "gridSize": 6,
                                "order": 6,
                                "visible": True,
                                "options": [
                                    {"value": "1", "label": "1 BHK"},
                                    {"value": "2", "label": "2 BHK"},
                                    {"value": "3", "label": "3 BHK"},
                                    {"value": "4", "label": "4 BHK"},
                                    {"value": "5+", "label": "5+ BHK"}
                                ]
                            }
                        ]
                    },
                    {
                        "id": "location-details",
                        "title": "Location Details",
                        "description": "Property location and accessibility information",
                        "order": 6,
                        "collapsible": True,
                        "expanded": False,
                        "visible": True,
                        "fields": [
                            {
                                "id": "propertyAddress",
                                "name": "propertyAddress",
                                "label": "Complete Property Address",
                                "type": "textarea",
                                "required": True,
                                "gridSize": 12,
                                "order": 1,
                                "visible": True,
                                "placeholder": "Enter complete address with landmarks"
                            },
                            {
                                "id": "pincode",
                                "name": "pincode",
                                "label": "PIN Code",
                                "type": "text",
                                "required": True,
                                "gridSize": 6,
                                "order": 2,
                                "visible": True
                            },
                            {
                                "id": "city",
                                "name": "city",
                                "label": "City",
                                "type": "text",
                                "required": True,
                                "gridSize": 6,
                                "order": 3,
                                "visible": True
                            },
                            {
                                "id": "propertyLatitude",
                                "name": "propertyLatitude",
                                "label": "Latitude",
                                "type": "number",
                                "required": False,
                                "gridSize": 6,
                                "order": 4,
                                "visible": True,
                                "placeholder": "Click location button to auto-fill"
                            },
                            {
                                "id": "propertyLongitude",
                                "name": "propertyLongitude",
                                "label": "Longitude",
                                "type": "number",
                                "required": False,
                                "gridSize": 6,
                                "order": 5,
                                "visible": True,
                                "placeholder": "Click location button to auto-fill"
                            }
                        ]
                    }
                ],
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "isActive": True
            }
        elif template_id == "SBI_RES_FLAT_V2025":
            return {
                "_id": "672345678901234567890125",
                "templateId": "SBI_RES_FLAT_V2025",
                "templateName": "SBI Residential Flat Valuation Form",
                "bankCode": "SBI",
                "version": "2.0",
                "tabs": [
                    {
                        "tabId": "borrower_details",
                        "tabName": "Borrower Information",
                        "order": 1,
                        "fields": [
                            {
                                "fieldId": "borrower_name",
                                "displayName": "Borrower Full Name",
                                "fieldType": "TEXT",
                                "isRequired": True,
                                "placeholder": "Enter borrower's full name",
                                "order": 1
                            },
                            {
                                "fieldId": "loan_amount",
                                "displayName": "Loan Amount (₹)",
                                "fieldType": "CURRENCY",
                                "isRequired": True,
                                "minValue": 100000,
                                "maxValue": 100000000,
                                "order": 2
                            }
                        ]
                    },
                    {
                        "tabId": "property_details",
                        "tabName": "Property Information",
                        "order": 2,
                        "fields": [
                            {
                                "fieldId": "property_address",
                                "displayName": "Complete Property Address",
                                "fieldType": "TEXTAREA",
                                "isRequired": True,
                                "rows": 3,
                                "order": 1
                            },
                            {
                                "fieldId": "carpet_area",
                                "displayName": "Carpet Area (sq ft)",
                                "fieldType": "NUMBER",
                                "isRequired": True,
                                "minValue": 100,
                                "maxValue": 10000,
                                "order": 2
                            }
                        ]
                    }
                ],
                "isActive": True
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch template")

# ================================
# Valuation Reports API Endpoints
# ================================

@app.post("/api/reports", response_model=Dict[str, Any])
async def create_report(
    report_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new valuation report"""
    try:
        # Validate required fields
        required_fields = ["templateId", "bankCode", "borrowerInfo"]
        for field in required_fields:
            if field not in report_data:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required field: {field}"
                )
        
        # Add creator information
        report_data["createdBy"] = current_user["_id"]
        report_data["createdAt"] = datetime.now(timezone.utc)
        report_data["status"] = "DRAFT"
        
        async with MultiDatabaseSession() as db:
            report_id = await db.insert_one("reports", "valuation_reports", report_data)
            return {"reportId": str(report_id), "status": "created"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to create report")

@app.get("/api/reports/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_reports(
    user_id: str,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get reports created by a user"""
    try:
        # Authorization check
        if str(current_user["_id"]) != user_id and current_user["role"] not in ["MANAGER", "ADMIN"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        async with MultiDatabaseSession() as db:
            query = {"createdBy": user_id}
            if status:
                query["status"] = status
            
            reports = await db.find_many("reports", "valuation_reports", query)
            return reports
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reports")

# ================================
# File Upload API Endpoints
# ================================

@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    report_id: Optional[str] = None,
    category: str = "GENERAL",
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Upload file to GridFS"""
    try:
        # Validate file type
        allowed_types = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,pdf").split(",")
        if file.filename is None:
            raise HTTPException(status_code=400, detail="No filename provided")
        file_extension = file.filename.split(".")[-1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Check file size
        max_size = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
        file_content = await file.read()
        
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size / 1024 / 1024:.1f}MB"
            )
        
        # Upload to GridFS
        # async with DatabaseSession() as db:
        #     file_id = await db.upload_file(
        #         file_content,
        #         file.filename,
        #         file.content_type,
        #         metadata={
        #             "reportId": report_id,
        #             "category": category,
        #             "uploadedBy": current_user["_id"]
        #         }
        #     )
        
        # Mock response
        file_id = "672345678901234567890127"
        
        return {
            "fileId": file_id,
            "filename": file.filename,
            "size": len(file_content),
            "contentType": file.content_type,
            "category": category,
            "uploadedAt": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

# ================================
# Application Entry Point
# ================================

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )