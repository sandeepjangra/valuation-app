"""
Organization Management Models and Schemas
Defines database schemas for multi-tenant organization structure
"""

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime, timezone
from bson import ObjectId
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

# Type definitions for roles and statuses
UserRole = Literal["manager", "employee", "system_admin"]
OrganizationStatus = Literal["active", "suspended", "inactive"]
UserStatus = Literal["active", "inactive", "pending"]
AuditAction = Literal["create", "read", "update", "delete", "login", "logout", "access_denied"]

class OrganizationSchema:
    """
    Organization collection schema and validation
    Collection: organizations (in valuation_admin database)
    """
    
    @staticmethod
    def create_document(
        organization_id: str,
        name: str,
        contact_email: str,
        created_by: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new organization document"""
        now = datetime.now(timezone.utc)
        
        return {
            "organization_id": organization_id,  # Unique identifier for JWT claims
            "name": name,
            "status": "active",
            "contact_info": {
                "email": contact_email,
                "phone": None,
                "address": None
            },
            "settings": {
                "max_users": 50,  # Default limit
                "features_enabled": ["reports", "templates", "file_upload"],
                "s3_prefix": organization_id,  # For S3 folder structure
                "timezone": "UTC",
                "date_format": "YYYY-MM-DD",
                **(settings or {})
            },
            "subscription": {
                "plan": "basic",
                "max_reports_per_month": 100,
                "storage_limit_gb": 10,
                "expires_at": None
            },
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "isActive": True,
            "version": 1
        }
    
    @staticmethod
    def get_indexes() -> List[Dict[str, Any]]:
        """Get required indexes for organizations collection"""
        return [
            {"keys": [("organization_id", 1)], "unique": True, "name": "idx_organization_id"},
            {"keys": [("status", 1)], "name": "idx_status"},
            {"keys": [("created_at", -1)], "name": "idx_created_at"},
            {"keys": [("isActive", 1)], "name": "idx_active"}
        ]

class UserSchema:
    """
    User collection schema and validation
    Collection: users (in valuation_admin database)
    """
    
    @staticmethod
    def create_document(
        cognito_user_id: str,
        email: str,
        organization_id: str,
        role: UserRole,
        created_by: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new user document"""
        now = datetime.now(timezone.utc)
        
        return {
            "cognito_user_id": cognito_user_id,  # From AWS Cognito
            "email": email,
            "organization_id": organization_id,  # Links user to organization
            "role": role,  # manager, employee, system_admin
            "status": "active",
            "profile": {
                "first_name": None,
                "last_name": None,
                "display_name": email.split("@")[0],  # Default display name
                "avatar_url": None,
                "department": None,
                "phone": None,
                **(profile or {})
            },
            "permissions": UserSchema._get_role_permissions(role),
            "session_info": {
                "last_login": None,
                "last_activity": None,
                "active_sessions": [],  # Track active sessions for single session enforcement
                "login_count": 0
            },
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "isActive": True,
            "version": 1
        }
    
    @staticmethod
    def _get_role_permissions(role: UserRole) -> Dict[str, List[str]]:
        """Get permissions based on user role"""
        if role == "system_admin":
            return {
                "organizations": ["create", "read", "update", "delete"],
                "users": ["create", "read", "update", "delete"],
                "reports": ["create", "read", "update", "delete"],
                "templates": ["create", "read", "update", "delete"],
                "audit_logs": ["read"],
                "system_settings": ["create", "read", "update", "delete"]
            }
        elif role == "manager":
            return {
                "organization": ["read", "update"],  # Own org only
                "users": ["create", "read", "update"],  # Own org only
                "reports": ["create", "read", "update", "delete"],  # Own org only
                "templates": ["read", "update"],  # Read all, update own org
                "audit_logs": ["read"],  # Own org only
                "files": ["create", "read", "update", "delete"]  # Own org only
            }
        else:  # employee
            return {
                "organization": ["read"],  # Own org only, read-only
                "reports": ["create", "read", "update"],  # Own org only, no delete
                "templates": ["read"],  # Read-only
                "files": ["create", "read", "update"]  # Own org only, no delete
            }
    
    @staticmethod
    def get_indexes() -> List[Dict[str, Any]]:
        """Get required indexes for users collection"""
        return [
            {"keys": [("cognito_user_id", 1)], "unique": True, "name": "idx_cognito_user_id"},
            {"keys": [("email", 1)], "unique": True, "name": "idx_email"},
            {"keys": [("organization_id", 1)], "name": "idx_organization_id"},
            {"keys": [("role", 1)], "name": "idx_role"},
            {"keys": [("status", 1)], "name": "idx_status"},
            {"keys": [("organization_id", 1), ("role", 1)], "name": "idx_org_role"},
            {"keys": [("isActive", 1)], "name": "idx_active"}
        ]

class ReportSchema:
    """
    Organization-filtered reports collection schema
    Collection: reports (in valuation_admin database)
    """
    
    @staticmethod
    def create_document(
        organization_id: str,
        report_name: str,
        template_used: str,
        created_by: str,
        report_data: Dict[str, Any],
        property_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new report document"""
        now = datetime.now(timezone.utc)
        
        return {
            "organization_id": organization_id,  # 🔒 Security filter field
            "report_name": report_name,
            "report_id": f"RPT_{organization_id}_{int(now.timestamp())}",  # Unique report ID
            "template_used": template_used,  # Reference to template collection
            "property_details": property_details or {},
            "report_data": report_data,
            "workflow": {
                "status": "draft",  # draft, submitted, reviewed, approved, rejected
                "submitted_by": None,
                "submitted_at": None,
                "reviewed_by": None,
                "reviewed_at": None,
                "approved_by": None,
                "approved_at": None,
                "comments": []
            },
            "file_attachments": [],  # S3 file references
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "isActive": True,
            "version": 1
        }
    
    @staticmethod
    def get_indexes() -> List[Dict[str, Any]]:
        """Get required indexes for reports collection"""
        return [
            {"keys": [("organization_id", 1)], "name": "idx_organization_id"},
            {"keys": [("report_id", 1)], "unique": True, "name": "idx_report_id"},
            {"keys": [("created_by", 1)], "name": "idx_created_by"},
            {"keys": [("template_used", 1)], "name": "idx_template_used"},
            {"keys": [("workflow.status", 1)], "name": "idx_workflow_status"},
            {"keys": [("organization_id", 1), ("created_by", 1)], "name": "idx_org_user"},
            {"keys": [("organization_id", 1), ("workflow.status", 1)], "name": "idx_org_status"},
            {"keys": [("created_at", -1)], "name": "idx_created_at_desc"},
            {"keys": [("isActive", 1)], "name": "idx_active"}
        ]

class AuditLogSchema:
    """
    Audit logging collection schema for security monitoring
    Collection: audit_logs (in valuation_admin database)
    """
    
    @staticmethod
    def create_document(
        organization_id: str,
        user_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new audit log document"""
        now = datetime.now(timezone.utc)
        
        return {
            "organization_id": organization_id,  # 🔒 Security filter field
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,  # e.g., "report", "template", "user"
            "resource_id": resource_id,
            "details": details or {},
            "request_info": {
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": now,
                "session_id": None  # Can be added later if needed
            },
            "created_at": now,
            "isActive": True
        }
    
    @staticmethod
    def get_indexes() -> List[Dict[str, Any]]:
        """Get required indexes for audit_logs collection"""
        return [
            {"keys": [("organization_id", 1)], "name": "idx_organization_id"},
            {"keys": [("user_id", 1)], "name": "idx_user_id"},
            {"keys": [("action", 1)], "name": "idx_action"},
            {"keys": [("resource_type", 1)], "name": "idx_resource_type"},
            {"keys": [("created_at", -1)], "name": "idx_created_at_desc"},
            {"keys": [("organization_id", 1), ("user_id", 1)], "name": "idx_org_user"},
            {"keys": [("organization_id", 1), ("action", 1)], "name": "idx_org_action"},
            {"keys": [("organization_id", 1), ("created_at", -1)], "name": "idx_org_time"},
            # TTL index to auto-delete old audit logs (optional)
            {"keys": [("created_at", 1)], "expireAfterSeconds": 31536000, "name": "idx_ttl_audit_logs"}  # 1 year
        ]

class OrganizationSettingsSchema:
    """
    Organization-specific settings collection schema
    Collection: organization_settings (in valuation_admin database)
    """
    
    @staticmethod
    def create_document(
        organization_id: str,
        settings_type: str,
        settings_data: Dict[str, Any],
        created_by: str
    ) -> Dict[str, Any]:
        """Create organization settings document"""
        now = datetime.now(timezone.utc)
        
        return {
            "organization_id": organization_id,  # 🔒 Security filter field
            "settings_type": settings_type,  # e.g., "ui_preferences", "notifications", "integrations"
            "settings_data": settings_data,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "isActive": True,
            "version": 1
        }
    
    @staticmethod
    def get_indexes() -> List[Dict[str, Any]]:
        """Get required indexes for organization_settings collection"""
        return [
            {"keys": [("organization_id", 1)], "name": "idx_organization_id"},
            {"keys": [("settings_type", 1)], "name": "idx_settings_type"},
            {"keys": [("organization_id", 1), ("settings_type", 1)], "unique": True, "name": "idx_org_settings_type"},
            {"keys": [("isActive", 1)], "name": "idx_active"}
        ]

class FileMetadataSchema:
    """
    File metadata collection for S3 file references
    Collection: file_metadata (in valuation_admin database)
    """
    
    @staticmethod
    def create_document(
        organization_id: str,
        s3_key: str,
        original_filename: str,
        file_type: str,
        file_size: int,
        uploaded_by: str,
        report_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create file metadata document"""
        now = datetime.now(timezone.utc)
        
        return {
            "organization_id": organization_id,  # 🔒 Security filter field
            "s3_key": s3_key,  # Full S3 path: org_12345/reports/file.pdf
            "original_filename": original_filename,
            "file_type": file_type,
            "file_size": file_size,
            "mime_type": None,  # Can be detected during upload
            "report_id": report_id,  # Link to report if applicable
            "description": description,
            "access_level": "organization",  # organization, public, restricted
            "download_count": 0,
            "uploaded_by": uploaded_by,
            "created_at": now,
            "updated_at": now,
            "isActive": True,
            "version": 1
        }
    
    @staticmethod
    def get_indexes() -> List[Dict[str, Any]]:
        """Get required indexes for file_metadata collection"""
        return [
            {"keys": [("organization_id", 1)], "name": "idx_organization_id"},
            {"keys": [("s3_key", 1)], "unique": True, "name": "idx_s3_key"},
            {"keys": [("report_id", 1)], "name": "idx_report_id"},
            {"keys": [("uploaded_by", 1)], "name": "idx_uploaded_by"},
            {"keys": [("file_type", 1)], "name": "idx_file_type"},
            {"keys": [("organization_id", 1), ("report_id", 1)], "name": "idx_org_report"},
            {"keys": [("created_at", -1)], "name": "idx_created_at_desc"},
            {"keys": [("isActive", 1)], "name": "idx_active"}
        ]

# Collection name mapping
ORGANIZATION_COLLECTIONS = {
    "organizations": OrganizationSchema,
    "users": UserSchema,
    "reports": ReportSchema,
    "audit_logs": AuditLogSchema,
    "organization_settings": OrganizationSettingsSchema,
    "file_metadata": FileMetadataSchema
}

# Collections that require organization_id filtering (security-critical)
FILTERED_COLLECTIONS = [
    "users", "reports", "audit_logs", "organization_settings", "file_metadata"
]

# Collections that are shared across organizations (no filtering needed)
SHARED_COLLECTIONS = [
    "common_fields", "sbi_land_property_details", "uco_land_property_details", 
    "organizations"  # Organizations collection itself doesn't need filtering
]

async def create_organization_indexes(db_manager, logger=None):
    """
    Create all required indexes for organization collections
    Should be called during application startup
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        for collection_name, schema_class in ORGANIZATION_COLLECTIONS.items():
            collection = db_manager.get_collection("admin", collection_name)
            indexes = schema_class.get_indexes()
            
            for index_spec in indexes:
                try:
                    await collection.create_index(
                        index_spec["keys"],
                        unique=index_spec.get("unique", False),
                        name=index_spec["name"],
                        background=True,
                        expireAfterSeconds=index_spec.get("expireAfterSeconds")
                    )
                    logger.info(f"✅ Created index {index_spec['name']} on {collection_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Index {index_spec['name']} on {collection_name} may already exist: {e}")
        
        logger.info("🎯 Organization database indexes creation completed")
        
    except Exception as e:
        logger.error(f"❌ Failed to create organization indexes: {e}")
        raise

def validate_organization_id(organization_id: str) -> bool:
    """Validate organization ID format"""
    if not organization_id or not isinstance(organization_id, str):
        return False
    
    # Must be 3-50 characters, alphanumeric + underscores
    import re
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, organization_id))

def validate_user_role(role: str) -> bool:
    """Validate user role"""
    return role in ["manager", "employee", "system_admin"]

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))