"""
Organization Management API Endpoints
Handles CRUD operations for organizations and org-based access control
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from bson import ObjectId
import re
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

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
    report_reference_initials: Optional[str] = Field(None, min_length=1, max_length=50, description="Report reference initials (e.g., 'CEV/RVO')")
    
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
    report_reference_initials: Optional[str] = Field(None, min_length=1, max_length=50, description="Report reference initials (e.g., 'CEV/RVO')")
    
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
                "date_format": "DD/MM/YYYY",
                "report_reference_initials": org_data.report_reference_initials,  # NEW: Report reference initials
                "report_sequence_counter": 0  # NEW: Auto-increment counter (starts at 0, first report will be 0001)
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
        if org_data.report_reference_initials is not None:
            update_doc["$set"]["settings.report_reference_initials"] = org_data.report_reference_initials
        
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


# ================================
# Template Management for Organizations
# ================================

class CreateTemplateFromReportRequest(BaseModel):
    """Request model for creating a template from a filled report"""
    templateName: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    bankCode: str
    templateCode: str
    fieldValues: Dict[str, Any]


@router.post("/{org_short_name}/templates/from-report")
async def create_template_from_report(
    org_short_name: str,
    template_data: CreateTemplateFromReportRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a custom template from a filled report form.
    Only saves bank-specific fields with non-empty values.
    
    Business Rules:
    - Max 3 templates per organization + bank + property type
    - Only Manager and Admin can create templates
    - Only bank-specific fields are saved (common fields excluded)
    - Only non-empty field values are saved
    - Template name must be unique for the org + bank + property type combination
    """
    from database.multi_db_manager import MultiDatabaseManager
    from utils.auth_middleware import get_organization_context
    from utils.activity_logger import log_activity
    
    try:
        # Verify authentication and role
        org_context = await get_organization_context(credentials)
        
        # Debug logging
        logger.info(f"🔍 Template creation attempt - User: {org_context.email}, Org: {org_context.org_short_name}")
        logger.info(f"🔍 Roles: {org_context.roles}, is_manager: {org_context.is_manager}, is_system_admin: {org_context.is_system_admin}")
        logger.info(f"🔍 Target org from URL: {org_short_name}")
        
        # Check if user is Manager or System Admin
        if not org_context.is_manager and not org_context.is_system_admin:
            logger.error(f"❌ Permission denied - User {org_context.email} is neither manager nor system_admin")
            raise HTTPException(
                status_code=403,
                detail="Only Manager or Admin can create custom templates"
            )
        
        # Verify organization context matches URL parameter (except for system admins who can manage any org)
        if not org_context.is_system_admin and org_context.organization_short_name != org_short_name:
            logger.error(f"❌ Organization mismatch - User org: {org_context.organization_short_name}, URL org: {org_short_name}")
            raise HTTPException(
                status_code=403,
                detail="Organization mismatch"
            )
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # For system admin, get the target organization's database
        # For regular managers, use their own organization's database
        if org_context.is_system_admin:
            # System admin can create templates for any organization
            # Need to get the organization ID from the org_short_name
            admin_db = db_manager.get_database("admin")
            org_doc = await admin_db.organizations.find_one({"orgShortName": org_short_name})
            if not org_doc:
                raise HTTPException(status_code=404, detail=f"Organization {org_short_name} not found")
            target_org_id = str(org_doc["_id"])
            org_db = db_manager.get_org_database(target_org_id)
        else:
            # Regular manager/user - use their own organization
            org_db = db_manager.get_org_database(org_context.organization_id)
            target_org_id = org_context.organization_id
        
        admin_db = db_manager.get_database("admin")
        
        # Parse property type from template code (e.g., "land-property" -> "land")
        property_type = template_data.templateCode.split("-")[0] if "-" in template_data.templateCode else template_data.templateCode
        
        # Check template count limit (max 3 per bank+propertyType)
        existing_count = await org_db.custom_templates.count_documents({
            "bankCode": template_data.bankCode,
            "propertyType": property_type,
            "isActive": True
        })
        
        if existing_count >= 3:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum 3 templates allowed for {template_data.bankCode} - {property_type}. Please delete an existing template first."
            )
        
        # Check for duplicate template name
        duplicate = await org_db.custom_templates.find_one({
            "bankCode": template_data.bankCode,
            "propertyType": property_type,
            "templateName": template_data.templateName,
            "isActive": True
        })
        
        if duplicate:
            raise HTTPException(
                status_code=400,
                detail=f"Template name '{template_data.templateName}' already exists for {template_data.bankCode} - {property_type}"
            )
        
        # Get bank information
        banks_doc = await admin_db.banks.find_one({"_id": {"$regex": "all_banks_unified"}})
        if not banks_doc:
            raise HTTPException(status_code=404, detail="Banks configuration not found")
        
        bank_doc = None
        for bank in banks_doc.get("banks", []):
            if bank.get("bankCode", "").upper() == template_data.bankCode.upper():
                bank_doc = bank
                break
        
        if not bank_doc:
            raise HTTPException(status_code=404, detail=f"Bank {template_data.bankCode} not found")
        
        bank_name = bank_doc.get("bankName", "")
        
        # Get template configuration to identify bank-specific fields
        template_config = None
        for tmpl in bank_doc.get("templates", []):
            if tmpl.get("templateCode", "").upper() == template_data.templateCode.upper():
                template_config = tmpl
                break
        
        if not template_config:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_data.templateCode} not found for bank {template_data.bankCode}"
            )
        
        collection_ref = template_config.get("collectionRef")
        if not collection_ref:
            raise HTTPException(
                status_code=500,
                detail="Template collection reference not configured"
            )
        
        # Get common fields to filter them out
        common_fields_docs = await admin_db.common_form_fields.find({"isActive": True}).to_list(length=None)
        common_field_ids = set()
        
        for doc in common_fields_docs:
            for field in doc.get("fields", []):
                common_field_ids.add(field.get("fieldId"))
                # Also add subfield IDs if it's a group field
                if field.get("fieldType") == "group" and "subFields" in field:
                    for subfield in field["subFields"]:
                        common_field_ids.add(subfield.get("fieldId"))
        
        logger.info(f"🔍 Found {len(common_field_ids)} common field IDs to exclude")
        
        # Filter field values:
        # 1. Exclude common fields (only save bank-specific fields)
        # 2. Exclude empty values (null, "", [], {})
        filtered_field_values = {}
        
        for field_id, value in template_data.fieldValues.items():
            # Skip common fields
            if field_id in common_field_ids:
                continue
            
            # Skip empty values
            if value is None or value == "" or value == [] or value == {}:
                continue
            
            # Skip empty strings after stripping whitespace
            if isinstance(value, str) and not value.strip():
                continue
            
            filtered_field_values[field_id] = value
        
        logger.info(f"📊 Filtered from {len(template_data.fieldValues)} to {len(filtered_field_values)} bank-specific non-empty fields")
        
        if not filtered_field_values:
            raise HTTPException(
                status_code=400,
                detail="No bank-specific field values to save. Please fill in at least one bank-specific field."
            )
        
        # Create template document
        template_doc = {
            "templateName": template_data.templateName,
            "description": template_data.description or "",
            "bankCode": template_data.bankCode,
            "bankName": bank_name,
            "propertyType": property_type,
            "templateCode": template_data.templateCode,
            "fieldValues": filtered_field_values,
            "createdBy": org_context.user_id,
            "createdByName": org_context.email,
            "modifiedBy": org_context.user_id,
            "modifiedByName": org_context.email,
            "organizationId": target_org_id,
            "isActive": True,
            "version": 1,
            "createdFrom": "report_form",
            "createdAt": datetime.now(timezone.utc),
            "modifiedAt": datetime.now(timezone.utc)
        }
        
        # Insert template
        result = await org_db.custom_templates.insert_one(template_doc)
        template_id = str(result.inserted_id)
        
        # Log activity (log to the target organization's activity log)
        await log_activity(
            organization_id=target_org_id,
            user_id=org_context.user_id,
            user_email=org_context.email,
            action="custom_template_created_from_report",
            resource_type="custom_template",
            resource_id=template_id,
            details={
                "templateName": template_data.templateName,
                "bankCode": template_data.bankCode,
                "propertyType": property_type,
                "templateCode": template_data.templateCode,
                "fieldCount": len(filtered_field_values),
                "createdBySystemAdmin": org_context.is_system_admin
            },
            ip_address=None
        )
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Custom template created from report: {template_data.templateName} with {len(filtered_field_values)} fields")
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "data": {
                    "_id": template_id,
                    "templateName": template_data.templateName,
                    "bankCode": template_data.bankCode,
                    "propertyType": property_type,
                    "fieldCount": len(filtered_field_values)
                },
                "message": f"Custom template created successfully with {len(filtered_field_values)} field values"
            }
        )
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error creating custom template from report: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create template: {str(e)}"
        )
