"""
Organization Management API Endpoints
Handles CRUD operations for organizations and org-based access control
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from bson import ObjectId
import re
import logging

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/organizations", tags=["organizations"])

# ================================
# Pydantic Models
# ================================

class OrganizationCreate(BaseModel):
    """Model for creating a new organization"""
    org_name: str = Field(..., min_length=3, max_length=100, description="Organization name")
    org_short_name: str = Field(..., min_length=3, max_length=50, description="URL-safe short name")
    contact_email: str = Field(..., description="Contact email")
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    
    @validator('org_short_name')
    def validate_short_name(cls, v):
        """Validate org_short_name is URL-safe"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('org_short_name must be lowercase alphanumeric with hyphens only')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('org_short_name cannot start or end with hyphen')
        if '--' in v:
            raise ValueError('org_short_name cannot contain consecutive hyphens')
        return v
    
    @validator('contact_email')
    def validate_email(cls, v):
        """Basic email validation"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v

class OrganizationUpdate(BaseModel):
    """Model for updating an organization"""
    org_name: Optional[str] = Field(None, min_length=3, max_length=100)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('contact_email')
    def validate_email(cls, v):
        """Basic email validation"""
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v

class OrganizationResponse(BaseModel):
    """Model for organization response"""
    id: str
    org_name: str
    org_short_name: str
    org_display_name: str
    is_system_org: bool
    is_active: bool
    contact_info: Dict[str, Any]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ================================
# Helper Functions
# ================================

def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

async def get_org_collection(db_manager):
    """Get organizations collection from val_app_config database"""
    config_db = db_manager.client.val_app_config
    return config_db.organizations

def serialize_org(org: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize organization document for API response"""
    return {
        "id": str(org["_id"]),
        "org_name": org.get("org_name", ""),
        "org_short_name": org.get("org_short_name", ""),
        "org_display_name": org.get("org_display_name", org.get("org_name", "")),
        "is_system_org": org.get("is_system_org", False),
        "is_active": org.get("is_active", True),
        "contact_info": org.get("contact_info", {}),
        "settings": org.get("settings", {}),
        "created_at": org.get("created_at"),
        "updated_at": org.get("updated_at"),
    }

# ================================
# API Endpoints
# ================================

@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    active_only: bool = True,
    include_system: bool = False
):
    """
    List all organizations
    - active_only: Filter only active organizations
    - include_system: Include System Administration org in results
    """
    try:
        from database.mongodb_manager import MongoDBManager
        
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        orgs_collection = await get_org_collection(db_manager)
        
        # Build query
        query = {}
        if active_only:
            query["is_active"] = True
        if not include_system:
            query["is_system_org"] = {"$ne": True}
        
        # Find organizations
        orgs_cursor = orgs_collection.find(query).sort("org_name", 1)
        orgs = await orgs_cursor.to_list(length=None)
        
        await db_manager.disconnect()
        
        # Serialize and return
        return [serialize_org(org) for org in orgs]
        
    except Exception as e:
        logger.error(f"Error listing organizations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list organizations: {str(e)}"
        )

@router.get("/{org_identifier}", response_model=OrganizationResponse)
async def get_organization(org_identifier: str):
    """
    Get organization by ID or short name
    """
    try:
        from database.mongodb_manager import MongoDBManager
        
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        orgs_collection = await get_org_collection(db_manager)
        
        # Try to find by ObjectId first, then by short name
        query = {}
        if ObjectId.is_valid(org_identifier):
            query["_id"] = ObjectId(org_identifier)
        else:
            query["org_short_name"] = org_identifier
        
        org = await orgs_collection.find_one(query)
        
        await db_manager.disconnect()
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization not found: {org_identifier}"
            )
        
        return serialize_org(org)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get organization: {str(e)}"
        )

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(org_data: OrganizationCreate):
    """
    Create a new organization
    """
    try:
        from database.mongodb_manager import MongoDBManager
        
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        orgs_collection = await get_org_collection(db_manager)
        
        # Check if org_name already exists
        existing_name = await orgs_collection.find_one({"org_name": org_data.org_name})
        if existing_name:
            await db_manager.disconnect()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization name already exists: {org_data.org_name}"
            )
        
        # Check if org_short_name already exists
        existing_short = await orgs_collection.find_one({"org_short_name": org_data.org_short_name})
        if existing_short:
            await db_manager.disconnect()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization short name already exists: {org_data.org_short_name}"
            )
        
        # Create organization document
        now = datetime.now(timezone.utc)
        org_doc = {
            "org_name": org_data.org_name,
            "org_short_name": org_data.org_short_name,
            "org_display_name": org_data.org_name,
            "is_system_org": False,
            "is_active": True,
            "contact_info": {
                "email": org_data.contact_email,
                "phone": org_data.contact_phone,
                "address": org_data.contact_address
            },
            "settings": {
                "max_users": 50,
                "features_enabled": ["reports", "templates", "file_upload"],
                "timezone": "UTC",
                "date_format": "DD/MM/YYYY"
            },
            "subscription": {
                "plan": "basic",
                "max_reports_per_month": 100,
                "storage_limit_gb": 10,
                "expires_at": None
            },
            "created_by": "system",  # TODO: Get from JWT token
            "created_at": now,
            "updated_at": now,
            "version": 1
        }
        
        # Insert organization
        result = await orgs_collection.insert_one(org_doc)
        org_doc["_id"] = result.inserted_id
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Created organization: {org_data.org_name} ({org_data.org_short_name})")
        
        return serialize_org(org_doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )

@router.put("/{org_identifier}", response_model=OrganizationResponse)
async def update_organization(org_identifier: str, org_data: OrganizationUpdate):
    """
    Update an organization
    Note: org_short_name cannot be changed after creation
    """
    try:
        from database.mongodb_manager import MongoDBManager
        
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        orgs_collection = await get_org_collection(db_manager)
        
        # Find organization
        query = {}
        if ObjectId.is_valid(org_identifier):
            query["_id"] = ObjectId(org_identifier)
        else:
            query["org_short_name"] = org_identifier
        
        org = await orgs_collection.find_one(query)
        
        if not org:
            await db_manager.disconnect()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization not found: {org_identifier}"
            )
        
        # Prevent updating system org
        if org.get("is_system_org", False):
            await db_manager.disconnect()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update System Administration organization"
            )
        
        # Build update document
        update_doc = {"$set": {"updated_at": datetime.now(timezone.utc)}}
        
        if org_data.org_name:
            # Check if new name already exists
            existing = await orgs_collection.find_one({
                "org_name": org_data.org_name,
                "_id": {"$ne": org["_id"]}
            })
            if existing:
                await db_manager.disconnect()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Organization name already exists: {org_data.org_name}"
                )
            update_doc["$set"]["org_name"] = org_data.org_name
            update_doc["$set"]["org_display_name"] = org_data.org_name
        
        if org_data.contact_email:
            update_doc["$set"]["contact_info.email"] = org_data.contact_email
        if org_data.contact_phone:
            update_doc["$set"]["contact_info.phone"] = org_data.contact_phone
        if org_data.contact_address:
            update_doc["$set"]["contact_info.address"] = org_data.contact_address
        if org_data.is_active is not None:
            update_doc["$set"]["is_active"] = org_data.is_active
        
        # Update organization
        await orgs_collection.update_one(query, update_doc)
        
        # Get updated organization
        updated_org = await orgs_collection.find_one(query)
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Updated organization: {org_identifier}")
        
        return serialize_org(updated_org)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )

@router.delete("/{org_identifier}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(org_identifier: str):
    """
    Delete an organization (soft delete by setting is_active=False)
    System Administration org cannot be deleted
    """
    try:
        from database.mongodb_manager import MongoDBManager
        
        db_manager = MongoDBManager()
        await db_manager.connect()
        
        orgs_collection = await get_org_collection(db_manager)
        
        # Find organization
        query = {}
        if ObjectId.is_valid(org_identifier):
            query["_id"] = ObjectId(org_identifier)
        else:
            query["org_short_name"] = org_identifier
        
        org = await orgs_collection.find_one(query)
        
        if not org:
            await db_manager.disconnect()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization not found: {org_identifier}"
            )
        
        # Prevent deleting system org
        if org.get("is_system_org", False):
            await db_manager.disconnect()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete System Administration organization"
            )
        
        # Soft delete (set is_active=False)
        await orgs_collection.update_one(
            query,
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Deleted organization: {org_identifier}")
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete organization: {str(e)}"
        )
