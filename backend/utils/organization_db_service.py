"""
Organization-Aware Database Service
Provides database operations with automatic organization filtering and security
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Literal
from database.multi_db_manager import MultiDatabaseManager, DatabaseType
from utils.auth_middleware import OrganizationContext, OrganizationMiddleware
from database.organization_models import FILTERED_COLLECTIONS, UserRole

logger = logging.getLogger(__name__)

class OrganizationDatabaseService:
    """
    Database service with automatic organization filtering and audit logging
    """
    
    def __init__(self, db_manager: MultiDatabaseManager, org_middleware: OrganizationMiddleware):
        self.db_manager = db_manager
        self.org_middleware = org_middleware
    
    async def find_one(
        self,
        org_context: OrganizationContext,
        collection_name: str,
        filter_dict: Dict[str, Any],
        db_type: DatabaseType = "admin",
        include_inactive: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Find single document with organization filtering"""
        
        # Apply organization filter
        filtered_query = self.org_middleware.apply_organization_filter(
            collection_name, filter_dict.copy(), org_context
        )
        
        # Execute query
        result = await self.db_manager.find_one(
            db_type, collection_name, filtered_query, include_inactive
        )
        
        # Log access
        if result:
            await self.org_middleware.log_database_operation(
                org_context=org_context,
                action="read",
                collection=collection_name,
                resource_id=str(result.get("_id", "unknown"))
            )
        
        return result
    
    async def find_many(
        self,
        org_context: OrganizationContext,
        collection_name: str,
        filter_dict: Optional[Dict[str, Any]] = None,
        db_type: DatabaseType = "admin",
        sort: Optional[List[Tuple[str, int]]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """Find multiple documents with organization filtering"""
        
        if filter_dict is None:
            filter_dict = {}
        
        # Apply organization filter
        filtered_query = self.org_middleware.apply_organization_filter(
            collection_name, filter_dict.copy(), org_context
        )
        
        # Execute query
        results = await self.db_manager.find_many(
            db_type, collection_name, filtered_query, sort, skip, limit, include_inactive
        )
        
        # Log access
        await self.org_middleware.log_database_operation(
            org_context=org_context,
            action="read",
            collection=collection_name,
            details={"count": len(results), "filter": str(filtered_query)}
        )
        
        return results
    
    async def insert_one(
        self,
        org_context: OrganizationContext,
        collection_name: str,
        document: Dict[str, Any],
        db_type: DatabaseType = "admin"
    ) -> str:
        """Insert document with organization context"""
        
        # Inject organization_id for filtered collections
        if collection_name in FILTERED_COLLECTIONS and not org_context.is_system_admin:
            document["organization_id"] = org_context.organization_id
        
        # Add audit fields
        document["created_by"] = org_context.user_id
        
        # Execute insert
        result_id = await self.db_manager.insert_one(db_type, collection_name, document)
        
        # Log creation
        await self.org_middleware.log_database_operation(
            org_context=org_context,
            action="create",
            collection=collection_name,
            resource_id=str(result_id)
        )
        
        return str(result_id)
    
    async def update_one(
        self,
        org_context: OrganizationContext,
        collection_name: str,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        db_type: DatabaseType = "admin"
    ) -> bool:
        """Update document with organization filtering and versioning"""
        
        # Apply organization filter to find query
        filtered_query = self.org_middleware.apply_organization_filter(
            collection_name, filter_dict.copy(), org_context
        )
        
        # Add audit fields to update
        update_dict["modified_by"] = org_context.user_id
        
        # Execute update with versioning
        success = await self.db_manager.update_one(
            db_type, collection_name, filtered_query, update_dict, org_context.user_id
        )
        
        # Log update
        if success:
            await self.org_middleware.log_database_operation(
                org_context=org_context,
                action="update",
                collection=collection_name,
                details={"filter": str(filtered_query), "updates": list(update_dict.keys())}
            )
        
        return success
    
    async def delete_one(
        self,
        org_context: OrganizationContext,
        collection_name: str,
        filter_dict: Dict[str, Any],
        db_type: DatabaseType = "admin"
    ) -> bool:
        """Soft delete document with organization filtering"""
        
        # Apply organization filter
        filtered_query = self.org_middleware.apply_organization_filter(
            collection_name, filter_dict.copy(), org_context
        )
        
        # Execute soft delete
        success = await self.db_manager.delete_one(
            db_type, collection_name, filtered_query, org_context.user_id
        )
        
        # Log deletion
        if success:
            await self.org_middleware.log_database_operation(
                org_context=org_context,
                action="delete",
                collection=collection_name,
                details={"filter": str(filtered_query)}
            )
        
        return success
    
    async def aggregate(
        self,
        org_context: OrganizationContext,
        collection_name: str,
        pipeline: List[Dict[str, Any]],
        db_type: DatabaseType = "admin"
    ) -> List[Dict[str, Any]]:
        """Execute aggregation with organization filtering"""
        
        # Inject organization filter at the beginning of pipeline if needed
        if collection_name in FILTERED_COLLECTIONS and not org_context.is_system_admin:
            org_filter_stage = {"$match": {"organization_id": org_context.organization_id}}
            
            # Check if first stage is already a match, merge if possible
            if pipeline and "$match" in pipeline[0]:
                pipeline[0]["$match"]["organization_id"] = org_context.organization_id
            else:
                pipeline.insert(0, org_filter_stage)
        
        # Execute aggregation
        results = await self.db_manager.aggregate(db_type, collection_name, pipeline)
        
        # Log access
        await self.org_middleware.log_database_operation(
            org_context=org_context,
            action="read",
            collection=collection_name,
            details={"aggregation": True, "result_count": len(results)}
        )
        
        return results
    
    async def count_documents(
        self,
        org_context: OrganizationContext,
        collection_name: str,
        filter_dict: Optional[Dict[str, Any]] = None,
        db_type: DatabaseType = "admin"
    ) -> int:
        """Count documents with organization filtering"""
        
        if filter_dict is None:
            filter_dict = {}
        
        # Apply organization filter
        filtered_query = self.org_middleware.apply_organization_filter(
            collection_name, filter_dict.copy(), org_context
        )
        
        # Execute count
        count = await self.db_manager.count_documents(db_type, collection_name, filtered_query)
        
        return count
    
    async def create_organization_report(
        self,
        org_context: OrganizationContext,
        report_name: str,
        template_used: str,
        report_data: Dict[str, Any],
        property_details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new organization report"""
        
        from database.organization_models import ReportSchema
        
        # Validate required context
        if not org_context.organization_id or not org_context.user_id:
            raise ValueError("Missing organization or user context")
        
        # Create report document
        report_doc = ReportSchema.create_document(
            organization_id=org_context.organization_id,
            report_name=report_name,
            template_used=template_used,
            created_by=org_context.user_id,
            report_data=report_data,
            property_details=property_details
        )
        
        # Insert report
        report_id = await self.insert_one(org_context, "reports", report_doc)
        
        logger.info(f"📄 Created report {report_name} for organization {org_context.organization_id}")
        
        return report_id
    
    async def get_organization_reports(
        self,
        org_context: OrganizationContext,
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get reports for organization"""
        
        filter_dict: Dict[str, Any] = {}
        if status_filter:
            filter_dict["workflow.status"] = status_filter
        
        reports = await self.find_many(
            org_context=org_context,
            collection_name="reports",
            filter_dict=filter_dict,
            sort=[("created_at", -1)],
            limit=limit
        )
        
        return reports
    
    async def get_organization_users(
        self,
        org_context: OrganizationContext,
        role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get users in organization (manager+ required)"""
        
        if not org_context.is_manager:
            raise PermissionError("Manager role required to view organization users")
        
        filter_dict: Dict[str, Any] = {}
        if role_filter:
            filter_dict["role"] = role_filter
        
        users = await self.find_many(
            org_context=org_context,
            collection_name="users",
            filter_dict=filter_dict,
            sort=[("created_at", -1)]
        )
        
        # Remove sensitive information
        for user in users:
            user.pop("cognito_user_id", None)
            user.pop("session_info", None)
        
        return users
    
    async def get_organization_audit_logs(
        self,
        org_context: OrganizationContext,
        action_filter: Optional[str] = None,
        user_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs for organization (manager+ required)"""
        
        if not org_context.is_manager:
            raise PermissionError("Manager role required to view audit logs")
        
        filter_dict: Dict[str, Any] = {}
        if action_filter:
            filter_dict["action"] = action_filter
        if user_filter:
            filter_dict["user_id"] = user_filter
        
        logs = await self.find_many(
            org_context=org_context,
            collection_name="audit_logs",
            filter_dict=filter_dict,
            sort=[("created_at", -1)],
            limit=limit
        )
        
        return logs
    
    async def create_organization_user(
        self,
        org_context: OrganizationContext,
        cognito_user_id: str,
        email: str,
        role: str,
        profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new user in organization (manager+ required)"""
        
        if not org_context.is_manager:
            raise PermissionError("Manager role required to create users")
        
        from database.organization_models import UserSchema, validate_email, validate_user_role
        
        # Validate required context
        if not org_context.organization_id or not org_context.user_id:
            raise ValueError("Missing organization or user context")
        
        # Validate inputs
        if not validate_email(email):
            raise ValueError("Invalid email format")
        
        if not validate_user_role(role):
            raise ValueError("Invalid user role")
        
        # Cast role to proper type
        user_role: UserRole = role  # type: ignore
        
        # Check if user already exists
        existing_user = await self.find_one(
            org_context=org_context,
            collection_name="users",
            filter_dict={"email": email},
            include_inactive=True
        )
        
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user document
        user_doc = UserSchema.create_document(
            cognito_user_id=cognito_user_id,
            email=email,
            organization_id=org_context.organization_id,
            role=user_role,
            created_by=org_context.user_id,
            profile=profile
        )
        
        # Insert user
        user_id = await self.insert_one(org_context, "users", user_doc)
        
        logger.info(f"👤 Created user {email} with role {role} in organization {org_context.organization_id}")
        
        return user_id
    
    async def get_user_by_email(
        self,
        org_context: OrganizationContext,
        email: str
    ) -> Optional[Dict[str, Any]]:
        """Get user by email within organization context"""
        
        return await self.find_one(
            org_context=org_context,
            collection_name="users",
            filter_dict={"email": email}
        )
    
    async def get_user_by_cognito_id(
        self,
        org_context: OrganizationContext,
        cognito_user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user by Cognito ID within organization context"""
        
        return await self.find_one(
            org_context=org_context,
            collection_name="users",
            filter_dict={"cognito_user_id": cognito_user_id}
        )
    
    # Utility methods for system admin operations
    async def get_all_organizations(
        self,
        org_context: OrganizationContext
    ) -> List[Dict[str, Any]]:
        """Get all organizations (system admin only)"""
        
        if not org_context.is_system_admin:
            raise PermissionError("System admin role required")
        
        return await self.db_manager.find_many(
            "admin", "organizations", {}, 
            sort=[("created_at", -1)]
        )
    
    async def create_organization(
        self,
        org_context: OrganizationContext,
        organization_id: str,
        name: str,
        contact_email: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new organization (system admin only)"""
        
        if not org_context.is_system_admin:
            raise PermissionError("System admin role required")
        
        from database.organization_models import OrganizationSchema, validate_organization_id, validate_email
        
        # Validate inputs
        if not validate_organization_id(organization_id):
            raise ValueError("Invalid organization ID format")
        
        if not validate_email(contact_email):
            raise ValueError("Invalid contact email format")
        
        # Check if organization already exists
        existing_org = await self.db_manager.find_one(
            "admin", "organizations",
            {"organization_id": organization_id},
            include_inactive=True
        )
        
        if existing_org:
            raise ValueError("Organization with this ID already exists")
        
        # Create organization document
        org_doc = OrganizationSchema.create_document(
            organization_id=organization_id,
            name=name,
            contact_email=contact_email,
            created_by=org_context.user_id,
            settings=settings
        )
        
        # Insert organization
        org_id = await self.db_manager.insert_one("admin", "organizations", org_doc)
        
        logger.info(f"🏢 Created organization {name} ({organization_id})")
        
        return str(org_id)

def create_org_db_service(db_manager: MultiDatabaseManager, org_middleware: OrganizationMiddleware) -> OrganizationDatabaseService:
    """Factory function to create organization database service"""
    return OrganizationDatabaseService(db_manager, org_middleware)