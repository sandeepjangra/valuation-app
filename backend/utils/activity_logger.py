"""
Activity Logger Utility
Tracks user actions across all organizations for admin monitoring
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ActivityAction(str, Enum):
    """Enumeration of trackable user actions"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE_REPORT = "CREATE_REPORT"
    UPDATE_REPORT = "UPDATE_REPORT"
    DELETE_REPORT = "DELETE_REPORT"
    VIEW_REPORT = "VIEW_REPORT"
    DOWNLOAD_REPORT = "DOWNLOAD_REPORT"
    ADD_USER = "ADD_USER"
    EDIT_USER = "EDIT_USER"
    DELETE_USER = "DELETE_USER"
    UPLOAD_FILE = "UPLOAD_FILE"
    DELETE_FILE = "DELETE_FILE"
    EDIT_ORG = "EDIT_ORG"
    CREATE_ORG = "CREATE_ORG"
    DELETE_ORG = "DELETE_ORG"
    UPDATE_TEMPLATE = "UPDATE_TEMPLATE"
    UPLOAD_TEMPLATE = "UPLOAD_TEMPLATE"
    

class ActivityLogger:
    """
    Centralized activity logging for admin monitoring
    Logs all user actions to val_app_config.activity_logs collection
    """
    
    def __init__(self, db_manager):
        """
        Initialize activity logger
        
        Args:
            db_manager: MultiDatabaseManager instance
        """
        self.db_manager = db_manager
        self.config_db = None
        self.collection_name = "activity_logs"
        
    async def initialize(self):
        """Initialize connection to config database"""
        try:
            self.config_db = await self.db_manager.get_config_db()
            logger.info("Activity logger initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize activity logger: {str(e)}")
            raise
    
    async def log_activity(
        self,
        action: ActivityAction,
        user_id: str,
        user_email: str,
        organization_id: str,
        organization_name: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> bool:
        """
        Log a user activity
        
        Args:
            action: The action performed (from ActivityAction enum)
            user_id: ID of the user performing the action
            user_email: Email of the user
            organization_id: ID of the organization
            organization_name: Name of the organization
            details: Additional details about the action (e.g., report_id, file_name)
            ip_address: IP address of the user
            user_agent: User agent string
            status: Status of the action (success, failed, partial)
            error_message: Error message if action failed
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            if not self.config_db:
                await self.initialize()
            
            activity_log = {
                "timestamp": datetime.now(timezone.utc),
                "action": action.value,
                "user_id": user_id,
                "user_email": user_email,
                "organization_id": organization_id,
                "organization_name": organization_name,
                "status": status,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "error_message": error_message
            }
            
            await self.config_db[self.collection_name].insert_one(activity_log)
            logger.debug(f"Activity logged: {action.value} by {user_email} in {organization_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
            # Don't fail the main operation if logging fails
            return False
    
    async def get_activities(
        self,
        skip: int = 0,
        limit: int = 50,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve activity logs with filters and pagination
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            organization_id: Filter by organization
            user_id: Filter by user
            action: Filter by action type
            status: Filter by status (success, failed)
            start_date: Filter by start date
            end_date: Filter by end date
            search: Search in user_email, organization_name, or details
            
        Returns:
            Dict with 'activities' list and 'total_count'
        """
        try:
            if not self.config_db:
                await self.initialize()
            
            # Build filter query
            filter_query = {}
            
            if organization_id:
                filter_query["organization_id"] = organization_id
            
            if user_id:
                filter_query["user_id"] = user_id
            
            if action:
                filter_query["action"] = action
            
            if status:
                filter_query["status"] = status
            
            # Date range filter
            if start_date or end_date:
                filter_query["timestamp"] = {}
                if start_date:
                    filter_query["timestamp"]["$gte"] = start_date
                if end_date:
                    filter_query["timestamp"]["$lte"] = end_date
            
            # Search filter
            if search:
                filter_query["$or"] = [
                    {"user_email": {"$regex": search, "$options": "i"}},
                    {"organization_name": {"$regex": search, "$options": "i"}},
                    {"details.report_id": {"$regex": search, "$options": "i"}},
                    {"details.file_name": {"$regex": search, "$options": "i"}}
                ]
            
            # Get total count
            total_count = await self.config_db[self.collection_name].count_documents(filter_query)
            
            # Get paginated activities
            activities_cursor = self.config_db[self.collection_name].find(filter_query).sort(
                "timestamp", -1
            ).skip(skip).limit(limit)
            
            activities = await activities_cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for activity in activities:
                activity["_id"] = str(activity["_id"])
            
            return {
                "activities": activities,
                "total_count": total_count,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "page_size": limit,
                "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve activities: {str(e)}")
            raise
    
    async def get_activity_stats(
        self,
        organization_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get activity statistics
        
        Args:
            organization_id: Filter by organization
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Dict with activity statistics
        """
        try:
            if not self.config_db:
                await self.initialize()
            
            # Build filter query
            filter_query = {}
            
            if organization_id:
                filter_query["organization_id"] = organization_id
            
            if start_date or end_date:
                filter_query["timestamp"] = {}
                if start_date:
                    filter_query["timestamp"]["$gte"] = start_date
                if end_date:
                    filter_query["timestamp"]["$lte"] = end_date
            
            # Get action counts
            action_pipeline = [
                {"$match": filter_query},
                {"$group": {
                    "_id": "$action",
                    "count": {"$sum": 1}
                }}
            ]
            
            action_counts = await self.config_db[self.collection_name].aggregate(action_pipeline).to_list(None)
            
            # Get organization counts
            org_pipeline = [
                {"$match": filter_query},
                {"$group": {
                    "_id": "$organization_id",
                    "organization_name": {"$first": "$organization_name"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            org_counts = await self.config_db[self.collection_name].aggregate(org_pipeline).to_list(None)
            
            # Get total activities
            total_activities = await self.config_db[self.collection_name].count_documents(filter_query)
            
            # Get success/failure counts
            success_count = await self.config_db[self.collection_name].count_documents({**filter_query, "status": "success"})
            failed_count = await self.config_db[self.collection_name].count_documents({**filter_query, "status": "failed"})
            
            return {
                "total_activities": total_activities,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": (success_count / total_activities * 100) if total_activities > 0 else 0,
                "actions_breakdown": {item["_id"]: item["count"] for item in action_counts},
                "top_organizations": [
                    {
                        "organization_id": item["_id"],
                        "organization_name": item["organization_name"],
                        "activity_count": item["count"]
                    }
                    for item in org_counts
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get activity stats: {str(e)}")
            raise


# Helper function to extract IP address from request
def get_client_ip(request) -> Optional[str]:
    """Extract client IP address from request headers"""
    try:
        # Check X-Forwarded-For header (for proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return None
    except Exception:
        return None


# Helper function to extract user agent
def get_user_agent(request) -> Optional[str]:
    """Extract user agent from request headers"""
    try:
        return request.headers.get("User-Agent")
    except Exception:
        return None
