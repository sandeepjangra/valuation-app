"""
FastAPI Backend Application for Valuation System
MongoDB Atlas integration with dynamic form templates
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bson import ObjectId
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Import our database manager (will be available after pip install)
from backend.database.multi_db_manager import MultiDatabaseSession

# Import field file manager
from backend.utils.field_file_manager import field_file_manager
from backend.utils.collection_file_manager import collection_file_manager

# Import admin API routes
from backend.admin_api import admin_router

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
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost").split(","),
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
from typing import Optional

# File-based field management
async def get_common_fields_from_file() -> List[Dict[str, Any]]:
    """Get common fields from local JSON file with database fallback"""
    
    # Try to read from local file first
    fields = field_file_manager.read_fields()
    
    if fields is not None:
        # Filter out inactive fields to match database behavior
        active_fields = [field for field in fields if field.get('isActive', True)]
        logger.info(f"📋 Loaded {len(active_fields)} active fields from local file (filtered from {len(fields)} total)")
        return active_fields
    
    # Fallback to database if file doesn't exist
    logger.warning("⚠️ Local fields file not found, falling back to database")
    return await fetch_fields_from_database()

async def fetch_fields_from_database() -> List[Dict[str, Any]]:
    """Fetch fields directly from database"""
    logger.info("🔄 Fetching fresh common fields from database")
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            async with MultiDatabaseSession() as db:
                fields = await db.find_many("admin", "common_form_fields", {"isActive": True}, sort=[("fieldGroup", 1), ("sortOrder", 1)])
                
                logger.info(f"✅ Fetched {len(fields)} common fields from database")
                return fields
                
        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt + 1} failed to fetch common fields: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
    
    # If all retries failed, return empty list
    logger.error("❌ Failed to fetch common fields after all retries")
    return []

async def refresh_fields_to_file() -> bool:
    """Refresh fields from database and save to local file"""
    try:
        logger.info("🔄 Refreshing fields from database to local file...")
        
        # Fetch fresh data from database
        fields = await fetch_fields_from_database()
        
        if not fields:
            logger.error("❌ No fields retrieved from database")
            return False
        
        # Save to local file
        success = field_file_manager.write_fields(fields)
        
        if success:
            logger.info(f"✅ Successfully refreshed {len(fields)} fields to local file")
            return True
        else:
            logger.error("❌ Failed to write fields to local file")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error refreshing fields to file: {e}")
        return False

# SBI Land Property fields management
async def get_sbi_land_fields_from_file() -> List[Dict[str, Any]]:
    """Get SBI land property fields from local JSON file"""
    try:
        import json
        import os
        
        file_path = os.path.join(os.path.dirname(__file__), "data", "sbi_land_property_details.json")
        
        if not os.path.exists(file_path):
            logger.error(f"❌ SBI land property fields file not found: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            fields = data.get('fields', [])
            logger.info(f"📋 Loaded {len(fields)} SBI land property fields from local file")
            return fields
            
    except Exception as e:
        logger.error(f"❌ Error reading SBI land property fields from file: {e}")
        return []

# ================================
# Common Form Fields API
# ================================

@app.get("/api/common-fields", response_model=List[Dict[str, Any]])
async def get_common_fields() -> JSONResponse:
    """Get all common form fields organized by groups from local file"""
    try:
        logger.info("📋 API call received for common fields")
        fields = await get_common_fields_from_file()
        logger.info(f"✅ Returning {len(fields)} fields to API clients")
        return JSONResponse(
            content=json.loads(json.dumps(fields, default=json_serializer))
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching common fields: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch common fields")

@app.post("/api/common-form-fields/refresh-collection")
async def refresh_common_fields_collection() -> JSONResponse:
    """Refresh the common fields collection from database to local file"""
    try:
        # Refresh fields from database to file
        success = await refresh_fields_to_file()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to refresh fields collection")
        
        # Get the updated fields and file info
        fields = await get_common_fields_from_file()
        file_info = field_file_manager.get_file_info()
        
        return JSONResponse(
            content={
                "message": "Collection refreshed successfully",
                "fields_count": len(fields),
                "file_info": file_info,
                "refreshed_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error refreshing common fields collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh fields collection")

@app.get("/api/admin/collections-status")
async def get_collections_status() -> JSONResponse:
    """Get status of all collection files for admin dashboard"""
    try:
        logger.info("📊 API call received for collections status")
        status = collection_file_manager.get_all_collections_status()
        logger.info(f"✅ Returning status for {len(status)} collections")
        return JSONResponse(
            content=json.loads(json.dumps(status, default=json_serializer))
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting collections status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collections status")

@app.post("/api/admin/refresh-collections")
async def refresh_all_collections() -> JSONResponse:
    """Refresh all collections from MongoDB to local files with individual error handling"""
    try:
        logger.info("🔄 API call received to refresh all collections")
        
        # Get all configured collections
        collections = list(collection_file_manager.COLLECTIONS_CONFIG.keys())
        results = {}
        successful_count = 0
        
        # Refresh each collection individually - failures don't stop the process
        for collection_name in collections:
            try:
                logger.info(f"🔄 Refreshing {collection_name}...")
                success = await collection_file_manager.refresh_collection_from_database(collection_name)
                results[collection_name] = success
                if success:
                    successful_count += 1
                    logger.info(f"✅ {collection_name} refreshed successfully")
                else:
                    logger.warning(f"⚠️ {collection_name} refresh failed")
            except Exception as e:
                logger.error(f"❌ Error refreshing {collection_name}: {e}")
                results[collection_name] = False
        
        # Determine overall status
        total_count = len(collections)
        if successful_count == total_count:
            message = f"All collections refreshed successfully: {successful_count}/{total_count}"
            logger.info(f"✅ {message}")
        elif successful_count > 0:
            message = f"Partial refresh completed: {successful_count}/{total_count} successful"
            logger.warning(f"⚠️ {message}")
        else:
            message = f"Refresh failed: 0/{total_count} successful"
            logger.error(f"❌ {message}")
        
        return JSONResponse(
            content={
                "message": message,
                "results": results,
                "successful_count": successful_count,
                "total_count": total_count,
                "refreshed_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Critical error during collection refresh: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh collections: {str(e)}")

@app.get("/api/admin/collection-data/{collection_name}")
async def get_collection_data(collection_name: str) -> JSONResponse:
    """Get data from a specific collection file"""
    try:
        logger.info(f"📋 API call received for collection data: {collection_name}")
        
        # Validate collection name
        if collection_name not in collection_file_manager.COLLECTIONS_CONFIG:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        documents = collection_file_manager.read_collection(collection_name)
        
        if documents is None:
            raise HTTPException(status_code=404, detail=f"Collection file '{collection_name}.json' not found")
        
        logger.info(f"✅ Returning {len(documents)} documents from {collection_name}")
        return JSONResponse(
            content={
                "collection": collection_name,
                "documents": json.loads(json.dumps(documents, default=json_serializer)),
                "total_count": len(documents)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting collection data for {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection data for {collection_name}")

@app.post("/api/admin/refresh-collection/{collection_name}")
async def refresh_single_collection(collection_name: str) -> JSONResponse:
    """Refresh a single collection from MongoDB to local file"""
    try:
        logger.info(f"🔄 API call received to refresh collection: {collection_name}")
        
        # Validate collection name
        if collection_name not in collection_file_manager.COLLECTIONS_CONFIG:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        success = await collection_file_manager.refresh_collection_from_database(collection_name)
        
        if success:
            # Get updated info
            info = collection_file_manager.get_collection_info(collection_name)
            return JSONResponse(
                content={
                    "message": f"Collection '{collection_name}' refreshed successfully",
                    "collection_info": info,
                    "refreshed_at": datetime.now(timezone.utc).isoformat()
                }
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to refresh collection '{collection_name}'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error refreshing collection {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh collection {collection_name}")

@app.get("/api/admin/collection-status")
async def get_collection_status() -> JSONResponse:
    """Get collection file status information for admin dashboard"""
    try:
        # Get file information
        file_info = field_file_manager.get_file_info()
        
        # Get field counts from file
        fields = await get_common_fields_from_file()
        total_count = len(fields) if fields else 0
        active_count = sum(1 for field in fields if field.get('isActive', True)) if fields else 0
        
        return JSONResponse(
            content={
                "fileExists": file_info.get("file_exists", False),
                "totalCount": total_count,
                "activeCount": active_count,
                "fileSize": file_info.get("file_size", 0),
                "lastModified": file_info.get("last_modified"),
                "generatedAt": file_info.get("generated_at"),
                "version": file_info.get("version"),
                "status": "available" if file_info.get("file_exists") else "missing"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting collection status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collection status")

@app.get("/api/common-form-fields")
async def get_all_common_fields(includeInactive: bool = False) -> JSONResponse:
    """Get all common form fields with option to include inactive fields for backup"""
    try:
        async with MultiDatabaseSession() as db:
            # Build query based on includeInactive parameter
            query = {} if includeInactive else {"isActive": True}
            
            fields = await db.find_many(
                "admin", 
                "common_form_fields", 
                query, 
                sort=[("fieldGroup", 1), ("sortOrder", 1)]
            )
            
            logger.info(f"📋 Retrieved {len(fields)} common fields (includeInactive: {includeInactive})")
            
            return JSONResponse(
                content=json.loads(json.dumps(fields, default=json_serializer))
            )
            
    except Exception as e:
        logger.error(f"Error fetching all common fields: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch common fields")

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

# ================================
# SBI Land Property Details API
# ================================

@app.get("/api/sbi/land-property-fields", response_model=List[Dict[str, Any]])
async def get_sbi_land_property_fields() -> JSONResponse:
    """Get all SBI land property form fields organized by groups from local file"""
    try:
        logger.info("📋 API call received for SBI land property fields")
        fields = await get_sbi_land_fields_from_file()
        logger.info(f"✅ Returning {len(fields)} SBI land fields to API clients")
        return JSONResponse(
            content=json.loads(json.dumps(fields, default=json_serializer))
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching SBI land property fields: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch SBI land property fields")

@app.get("/api/sbi/land-property-fields/group/{group_name}")
async def get_sbi_land_property_fields_by_group(group_name: str) -> JSONResponse:
    """Get SBI land property fields for a specific group"""
    try:
        logger.info(f"📋 API call received for SBI land property fields group: {group_name}")
        all_fields = await get_sbi_land_fields_from_file()
        group_fields = [field for field in all_fields if field.get('fieldGroup') == group_name]
        logger.info(f"✅ Returning {len(group_fields)} SBI land fields for group {group_name}")
        return JSONResponse(
            content=json.loads(json.dumps(group_fields, default=json_serializer))
        )
        
    except Exception as e:
        logger.error(f"Error fetching SBI land property fields for group {group_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch SBI land property fields for group")

@app.post("/api/sbi/land-property-fields/refresh-collection")
async def refresh_sbi_land_property_fields_collection() -> JSONResponse:
    """Refresh the SBI land property fields collection from MongoDB"""
    try:
        logger.info("🔄 API call received to refresh SBI land property fields collection")
        
        # Use collection_file_manager to refresh from MongoDB
        success = await collection_file_manager.refresh_collection_from_database("sbi_land_property_details")
        
        if success:
            # Get updated field count
            fields = await get_sbi_land_fields_from_file()
            logger.info(f"✅ SBI land property fields collection refreshed successfully with {len(fields)} fields")
            
            return JSONResponse(
                content={
                    "message": "SBI land property fields collection refreshed successfully",
                    "success": True,
                    "fields_count": len(fields),
                    "bank_code": "SBI",
                    "property_type": "Land",
                    "refreshed_at": datetime.now(timezone.utc).isoformat()
                }
            )
        else:
            logger.error("❌ Failed to refresh SBI land property fields collection")
            raise HTTPException(status_code=500, detail="Failed to refresh SBI land property fields collection")
        
    except Exception as e:
        logger.error(f"❌ Error refreshing SBI land property fields collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh SBI land property fields collection")

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
        # Mock response with detailed template structure for API clients
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