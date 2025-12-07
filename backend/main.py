from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from passlib.context import CryptContext
import json
import logging
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from utils.logger import RequestResponseLogger
from utils.activity_logger import ActivityLogger, ActivityAction, get_client_ip, get_user_agent

# System databases that must NEVER be deleted
PROTECTED_DATABASES = [
    'val_app_config',      # Main configuration database
    'valuation_admin',     # Admin database
    'shared_resources',    # Shared resources across all orgs
    'admin',               # MongoDB admin database
    'local',               # MongoDB local database
    'config'               # MongoDB config database
]

from utils.auth_middleware import (
    get_organization_context, 
    OrganizationContext, 
    require_permission,
    require_role
)

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # If python-dotenv is not installed, try to read .env manually
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to convert datetime objects to ISO format strings
def convert_datetimes_to_iso(obj):
    """Recursively convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetimes_to_iso(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes_to_iso(item) for item in obj]
    else:
        return obj

# Activity logging helper function
async def log_activity(
    organization_id: str,
    user_id: str,
    user_email: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    """
    Log user activity to organization's activity_logs collection
    
    Args:
        organization_id: Organization ID
        user_id: User ID performing the action
        user_email: User email for readability
        action: Action performed (e.g., "report_created", "report_submitted", "report_updated")
        resource_type: Type of resource (e.g., "report", "template", "user")
        resource_id: ID of the resource affected
        details: Additional details about the action
        ip_address: IP address of the request
    """
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organization database
        org_db = db_manager.get_org_database(organization_id)
        
        # Create activity log document
        activity_log = {
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }
        
        # Insert into activity_logs collection
        await org_db.activity_logs.insert_one(activity_log)
        
        await db_manager.disconnect()
        
        logger.debug(f"📝 Activity logged: {action} by {user_email} in org {organization_id}")
        
    except Exception as e:
        # Don't fail the main operation if activity logging fails
        logger.error(f"❌ Failed to log activity: {str(e)}")

app = FastAPI(title="Valuation App API", version="1.0.0")

# Initialize request/response logger
api_logger = RequestResponseLogger()

# Global activity logger instance (initialized on startup)
activity_logger: Optional[ActivityLogger] = None

# Import and include routers
from organization_api import router as organization_router
from admin_api import admin_router
from api.pdf_endpoints import pdf_router

app.include_router(organization_router)
app.include_router(admin_router)
app.include_router(pdf_router)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Pydantic models for authentication
class LoginRequest(BaseModel):
    email: str
    password: str
    rememberMe: Optional[bool] = False

class LoginResponse(BaseModel):
    access_token: str
    expires_in: int
    user: Dict[str, Any]
    organization: Dict[str, Any]

class DevLoginRequest(BaseModel):
    email: str
    organizationId: str
    role: str

# Organization Management Models
class CreateOrganizationRequest(BaseModel):
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    max_users: Optional[int] = 25
    plan: Optional[str] = "basic"

class OrganizationResponse(BaseModel):
    organization_id: str
    name: str
    status: str
    contact_info: Dict[str, Any]
    settings: Dict[str, Any]
    subscription: Dict[str, Any]
    created_at: str

# User Management Models
class AddUserToOrgRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str  # "manager" or "employee"
    phone: Optional[str] = None

class UpdateUserRoleRequest(BaseModel):
    role: str  # "manager" or "employee"

class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    organization_id: str
    role: str
    status: str
    created_at: str

# Custom Template Models
class CreateCustomTemplateRequest(BaseModel):
    templateName: str
    description: Optional[str] = None
    bankCode: str
    propertyType: str  # "land" or "apartment"
    fieldValues: Dict[str, Any]  # Only field values, not structure

class UpdateCustomTemplateRequest(BaseModel):
    templateName: Optional[str] = None
    description: Optional[str] = None
    fieldValues: Optional[Dict[str, Any]] = None

class CloneCustomTemplateRequest(BaseModel):
    newTemplateName: str

class CreateTemplateFromReportRequest(BaseModel):
    templateName: str
    description: Optional[str] = None
    bankCode: str
    templateCode: str  # e.g., "land-property"
    fieldValues: Dict[str, Any]  # All field values from the report form

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def json_serializer(obj):
    """JSON serializer for objects not serializable by default"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

# Authentication helper functions
def create_dev_token(email: str, org_short_name: str, role: str) -> Dict[str, Any]:
    """Create a development JWT token"""
    import time
    
    # Create a simple token payload for development
    payload = {
        "sub": f"dev_user_{email.split('@')[0]}",
        "email": email,
        "custom:org_short_name": org_short_name,
        "custom:organization_id": org_short_name,  # Backward compatibility
        "cognito:groups": [role],
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour
        "dev_mode": True
    }
    
    # For development, we'll use a simple token (in production, use proper JWT)
    # Replace hyphens with underscores for token format
    org_token = org_short_name.replace("-", "_")
    dev_token = f"dev_{email.split('@')[0]}_{email.split('@')[1]}_{org_token}_{role}"
    
    return {
        "access_token": dev_token,
        "expires_in": 3600,
        "user": {
            "_id": payload["sub"],
            "org_short_name": org_short_name,
            "organization_id": org_short_name,  # Backward compatibility
            "email": email,
            "first_name": email.split('@')[0].title(),
            "roles": [role],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        "organization": {
            "org_short_name": org_short_name,
            "id": org_short_name,  # Backward compatibility
            "name": "System Administration" if org_short_name == "system_admin" else "Demo Organization 001",
            "type": "system" if org_short_name == "system_admin" else "valuation_company"
        }
    }

# Authentication endpoints
@app.post("/api/auth/login")
async def login(login_request: LoginRequest, request: Request):
    """Traditional login endpoint - fetches user from database and returns role"""
    global activity_logger
    
    logger.info(f"🔐 Login attempt for: {login_request.email}")
    
    # Import login logger
    from utils.login_logger import login_logger
    
    # Get client info
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        admin_db = db_manager.get_database("admin")
        
        # Check if this is system admin (admin@system.com)
        if login_request.email == "admin@system.com":
            # Look for System Administration org in val_app_config
            config_db = db_manager.client["val_app_config"]
            sys_org = await config_db.organizations.find_one({
                "org_name": "System Administration", 
                "is_system_org": True
            })
            
            if sys_org:
                # Check system-administration database
                sys_db = db_manager.client["system-administration"]
                user = await sys_db.users.find_one({"email": login_request.email})
                
                if user and pwd_context.verify(login_request.password, user['password_hash']):
                    # Create system admin token with proper organization context
                    org_short_name = "system-administration"
                    token_data = create_dev_token(login_request.email, org_short_name, "admin")
                    
                    # Add system admin user information
                    token_data["user"] = {
                        "user_id": str(user["_id"]),
                        "email": user["email"],
                        "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                        "org_short_name": org_short_name,
                        "organization_id": str(sys_org["_id"]),
                        "organization_name": sys_org["org_name"],
                        "role": "admin",
                        "is_system_admin": True
                    }
                    
                    # Log successful login
                    login_logger.log_login_attempt(
                        email=login_request.email,
                        success=True,
                        ip_address=client_ip,
                        user_agent=user_agent,
                        jwt_token=token_data["access_token"],
                        organization_id=org_short_name,
                        role="admin",
                        login_type="traditional"
                    )
                    
                    logger.info(f"✅ System admin login successful for {login_request.email}")
                    
                    await db_manager.disconnect()
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "data": token_data
                        }
                    )
        
        # Find user by email in admin database
        user = await admin_db.users.find_one({
            "email": login_request.email,
            "isActive": True
        })
        
        # If not found in admin db, check valuation_admin for legacy users
        if not user:
            valuation_admin_db = db_manager.client["valuation_admin"]
            user = await valuation_admin_db.users.find_one({
                "email": login_request.email,
                "isActive": True
            })
        
        if not user:
            logger.warning(f"❌ User not found: {login_request.email}")
            
            # Log failed login attempt
            login_logger.log_login_attempt(
                email=login_request.email,
                success=False,
                ip_address=client_ip,
                user_agent=user_agent,
                error_message="User not found",
                login_type="traditional"
            )
            
            # Log failed login attempt to activity logger
            if activity_logger is None:
                activity_logger = ActivityLogger(db_manager)
                await activity_logger.initialize()
            
            await activity_logger.log_activity(
                action=ActivityAction.LOGIN,
                user_id="unknown",
                user_email=login_request.email,
                organization_id="unknown",
                organization_name="Unknown",
                status="failed",
                error_message="User not found",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
            
            await db_manager.disconnect()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Validate password if password_hash exists
        if user.get("password_hash"):
            if not pwd_context.verify(login_request.password, user["password_hash"]):
                logger.warning(f"❌ Invalid password for: {login_request.email}")
                
                # Log failed login attempt
                login_logger.log_login_attempt(
                    email=login_request.email,
                    success=False,
                    ip_address=client_ip,
                    user_agent=user_agent,
                    error_message="Invalid password",
                    login_type="traditional"
                )
                
                await db_manager.disconnect()
                raise HTTPException(status_code=401, detail="Invalid email or password")
        else:
            # In development, accept any password if no password_hash (legacy users)
            logger.info(f"🧪 Development mode: accepting any password for {login_request.email}")
        
        # Get user details
        user_id = user.get("user_id") or user.get("cognito_user_id")
        email = user.get("email")
        full_name = user.get("full_name") or user.get("profile", {}).get("display_name", "")
        organization_id = user.get("organization_id")  # Legacy field
        role = user.get("role")  # Get actual role from database
        
        # Get organization details to fetch org_short_name
        # Try val_app_config first (new schema), fallback to admin database
        config_db = db_manager.client["val_app_config"]
        org = await config_db.organizations.find_one({
            "metadata.original_organization_id": organization_id
        })
        
        # Fallback to admin database for legacy orgs
        if not org:
            admin_db = db_manager.client["valuation_admin"]
            org = await admin_db.organizations.find_one({
                "organization_id": organization_id,
                "isActive": True
            })
        
        if not org:
            logger.error(f"❌ Organization not found for user: {organization_id}")
            await db_manager.disconnect()
            raise HTTPException(status_code=500, detail="Organization not found")
        
        # Get org_short_name (new schema) or fallback to organization_id
        org_short_name = org.get("org_short_name", organization_id)
        org_name = org.get("org_name") or org.get("name", "Unknown Organization")
        
        # Update last_login timestamp
        val_admin_db = db_manager.client["valuation_admin"]
        await val_admin_db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "last_login": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Log successful login activity
        if activity_logger is None:
            activity_logger = ActivityLogger(db_manager)
            await activity_logger.initialize()
        
        await activity_logger.log_activity(
            action=ActivityAction.LOGIN,
            user_id=user_id,
            user_email=email,
            organization_id=org_short_name,
            organization_name=org_name,
            details={
                "full_name": full_name,
                "role": role
            },
            status="success",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        await db_manager.disconnect()
        
        # Create development token with org_short_name
        token_data = create_dev_token(email, org_short_name, role)
        
        # Log successful login attempt
        login_logger.log_login_attempt(
            email=email,
            success=True,
            ip_address=client_ip,
            user_agent=user_agent,
            jwt_token=token_data["access_token"],
            organization_id=org_short_name,
            role=role,
            login_type="traditional"
        )
        
        # Add user information to response
        token_data["user"] = {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "org_short_name": org_short_name,
            "organization_id": organization_id,  # Backward compatibility
            "organization_name": org_name,
            "role": role
        }
        
        logger.info(f"✅ Login successful for {email} with role {role} in org {org_short_name}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": token_data
            }
        )
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}")
        
        # Log system error
        login_logger.log_login_attempt(
            email=login_request.email,
            success=False,
            ip_address=client_ip,
            user_agent=user_agent,
            error_message=f"System error: {str(e)}",
            login_type="traditional"
        )
        
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/auth/dev-login")
async def dev_login(dev_request: DevLoginRequest, request: Request = None):
    """Development login endpoint with predefined roles"""
    logger.info(f"🧪 Development login for: {dev_request.email} as {dev_request.role}")
    
    # Import login logger
    from utils.login_logger import login_logger
    
    # Get client info
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        # organizationId in dev_request is now org_short_name
        org_short_name = dev_request.organizationId
        
        # Create development token with org_short_name
        token_data = create_dev_token(dev_request.email, org_short_name, dev_request.role)
        
        # Log successful dev login
        login_logger.log_login_attempt(
            email=dev_request.email,
            success=True,
            ip_address=client_ip,
            user_agent=user_agent,
            jwt_token=token_data["access_token"],
            organization_id=org_short_name,
            role=dev_request.role,
            login_type="dev_login"
        )
        
        logger.info(f"✅ Development login successful for {dev_request.email} in org {org_short_name}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": token_data
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Development login failed: {str(e)}")
        
        # Log dev login failure
        login_logger.log_login_attempt(
            email=dev_request.email,
            success=False,
            ip_address=client_ip,
            user_agent=user_agent,
            error_message=f"Dev login error: {str(e)}",
            organization_id=dev_request.organizationId,
            role=dev_request.role,
            login_type="dev_login"
        )
        
        raise HTTPException(
            status_code=500,
            detail="Development login failed"
        )

@app.post("/api/auth/logout")
async def logout(request: Request = None):
    """Logout endpoint"""
    logger.info("🔓 User logout")
    
    # Log logout activity
    try:
        from utils.login_logger import login_logger
        
        # Try to get user info from token if available
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Could extract user info from token, but for now just log generic logout
            pass
        
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Note: We don't have user email in logout, so we'll log it as a system event
        # In a real implementation, you'd extract user info from the JWT token
        
    except Exception as e:
        logger.warning(f"Failed to log logout activity: {e}")
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Logged out successfully"
        }
    )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/admin/login-activities")
async def get_login_activities(
    request: Request,
    limit: int = 50,
    hours: int = 24
):
    """Get recent login activities (Admin only)"""
    try:
        from utils.login_logger import login_logger
        
        # Get recent activities
        activities = login_logger.get_recent_login_activities(limit=limit)
        
        # Get statistics
        stats = login_logger.get_login_stats(hours=hours)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "activities": activities,
                    "statistics": stats,
                    "total_returned": len(activities)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching login activities: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )



# ================================
# ADMIN DASHBOARD - HEALTH CHECK
# ================================

@app.get("/api/admin/dashboard/health")
async def admin_health_check(request: Request):
    """
    Comprehensive system health check for admin dashboard
    Monitors: Backend API, MongoDB, Storage, System Resources
    """
    request_data = await api_logger.log_request(request)
    
    logger.info("🏥 Running comprehensive health check")
    
    try:
        import psutil
        import time
        from database.multi_db_manager import MultiDatabaseManager
        
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {},
            "system_resources": {},
            "performance_metrics": {}
        }
        
        # 1. Backend API Health
        health_status["services"]["backend_api"] = {
            "status": "up",
            "response_time_ms": 0,
            "message": "FastAPI running"
        }
        
        # 2. MongoDB Health
        mongo_start = time.time()
        try:
            db_manager = MultiDatabaseManager()
            await db_manager.connect()
            
            # Test connection with a simple query
            config_db = db_manager.client.val_app_config
            org_count = await config_db.organizations.count_documents({})
            
            mongo_response_time = round((time.time() - mongo_start) * 1000, 2)
            
            # Get database count
            db_names = await db_manager.client.list_database_names()
            
            health_status["services"]["mongodb"] = {
                "status": "up",
                "response_time_ms": mongo_response_time,
                "message": "Connected",
                "details": {
                    "databases_count": len(db_names),
                    "organizations_count": org_count
                }
            }
            
            await db_manager.disconnect()
            
        except Exception as e:
            health_status["services"]["mongodb"] = {
                "status": "down",
                "response_time_ms": round((time.time() - mongo_start) * 1000, 2),
                "message": f"Connection failed: {str(e)}",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # 3. Storage Health (Check disk space)
        try:
            disk_usage = psutil.disk_usage('/')
            
            storage_status = "up"
            if disk_usage.percent > 90:
                storage_status = "critical"
                health_status["overall_status"] = "degraded"
            elif disk_usage.percent > 80:
                storage_status = "warning"
            
            health_status["services"]["storage"] = {
                "status": storage_status,
                "response_time_ms": 0,
                "message": f"{disk_usage.percent}% used",
                "details": {
                    "total_gb": round(disk_usage.total / (1024**3), 2),
                    "used_gb": round(disk_usage.used / (1024**3), 2),
                    "free_gb": round(disk_usage.free / (1024**3), 2),
                    "percent_used": disk_usage.percent
                }
            }
        except Exception as e:
            health_status["services"]["storage"] = {
                "status": "unknown",
                "response_time_ms": 0,
                "message": f"Could not check storage: {str(e)}"
            }
        
        # 4. System Resources
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status["system_resources"] = {
                "cpu": {
                    "percent": round(cpu_percent, 1),
                    "status": "normal" if cpu_percent < 80 else "high"
                },
                "memory": {
                    "percent": round(memory.percent, 1),
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "status": "normal" if memory.percent < 80 else "high"
                },
                "disk": {
                    "percent": round(disk.percent, 1),
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "status": "normal" if disk.percent < 80 else "high"
                }
            }
            
            # Update overall status based on resources
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                health_status["overall_status"] = "degraded"
                
        except Exception as e:
            logger.warning(f"Could not get system resources: {e}")
            health_status["system_resources"] = {
                "error": "Could not retrieve system resources"
            }
        
        # 5. Performance Metrics (placeholder for now)
        health_status["performance_metrics"] = {
            "uptime_seconds": round(time.time() - psutil.boot_time(), 0) if hasattr(psutil, 'boot_time') else 0,
            "requests_per_minute": 0,  # TODO: Implement request counter
            "avg_response_time_ms": 0,  # TODO: Implement from logs
            "error_rate_percent": 0     # TODO: Implement from logs
        }
        
        logger.info(f"✅ Health check completed: {health_status['overall_status']}")
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": health_status
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "overall_status": "down"
            }
        )
        
        api_logger.log_response(error_response, request_data)
        return error_response


# ================================
# ADMIN - ACTIVITY LOGS ENDPOINTS
# ================================

@app.get("/api/admin/dashboard/activity-logs")
async def get_activity_logs(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    organization_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Get activity logs with filtering and pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    - organization_id: Filter by organization
    - user_id: Filter by user
    - action: Filter by action type (LOGIN, CREATE_REPORT, etc.)
    - status: Filter by status (success, failed)
    - start_date: Filter by start date (ISO format)
    - end_date: Filter by end date (ISO format)
    - search: Search in user email, organization name, or details
    """
    global activity_logger
    request_data = await api_logger.log_request(request)
    
    try:
        # Initialize activity logger if not already done
        if activity_logger is None:
            from database.multi_db_manager import MultiDatabaseManager
            db_manager = MultiDatabaseManager()
            await db_manager.connect()
            activity_logger = ActivityLogger(db_manager)
            await activity_logger.initialize()
        
        # Validate and limit page size
        page_size = min(page_size, 100)
        skip = (page - 1) * page_size
        
        # Parse date filters
        start_datetime = None
        end_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format.")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format.")
        
        # Get activities from activity logger
        result = await activity_logger.get_activities(
            skip=skip,
            limit=page_size,
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            status=status,
            start_date=start_datetime,
            end_date=end_datetime,
            search=search
        )
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Failed to fetch activity logs: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
        
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/admin/dashboard/activity-stats")
async def get_activity_stats(
    request: Request,
    organization_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get activity statistics
    
    Query Parameters:
    - organization_id: Filter by organization
    - start_date: Filter by start date (ISO format)
    - end_date: Filter by end date (ISO format)
    """
    global activity_logger
    request_data = await api_logger.log_request(request)
    
    try:
        # Initialize activity logger if not already done
        if activity_logger is None:
            from database.multi_db_manager import MultiDatabaseManager
            db_manager = MultiDatabaseManager()
            await db_manager.connect()
            activity_logger = ActivityLogger(db_manager)
            await activity_logger.initialize()
        
        # Parse date filters
        start_datetime = None
        end_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format.")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format.")
        
        # Get statistics
        stats = await activity_logger.get_activity_stats(
            organization_id=organization_id,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": stats
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Failed to fetch activity stats: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
        
        api_logger.log_response(error_response, request_data)
        return error_response


# ================================
# ROLE-BASED ACCESS CONTROL HELPERS
# ================================

@app.get("/api/auth/me")
async def get_current_user(request: Request):
    """Get current user information from token"""
    try:
        from utils.auth_middleware import get_organization_context
        from fastapi.security import HTTPBearer
        
        security = HTTPBearer()
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.replace("Bearer ", "")
        
        # Create credentials object
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Get organization context
        org_context = await get_organization_context(credentials)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "user_id": org_context.user_id,
                    "email": org_context.email,
                    "organization_id": org_context.organization_id,
                    "roles": org_context.roles,
                    "is_system_admin": org_context.is_system_admin,
                    "is_manager": org_context.is_manager,
                    "is_employee": org_context.is_employee,
                    "permissions": {
                        "can_submit_reports": org_context.has_permission("reports", "submit"),
                        "can_create_reports": org_context.has_permission("reports", "create"),
                        "can_read_reports": org_context.has_permission("reports", "read"),
                        "can_update_reports": org_context.has_permission("reports", "update"),
                        "can_view_audit_logs": org_context.has_permission("audit_logs", "read")
                    }
                }
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error getting current user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

@app.get("/api/banks")
async def get_all_banks(request: Request):
    """Get all active banks with their templates from shared_resources"""
    # Log the request
    request_data = await api_logger.log_request(request)
    
    logger.info("🏦 Fetching all banks from shared_resources...")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get shared resources database
        shared_db = db_manager.get_database("shared")
        
        # Fetch all active banks
        banks_cursor = shared_db.banks.find({"isActive": True})
        banks = await banks_cursor.to_list(length=None)
        
        logger.info(f"📦 Found {len(banks)} active banks")
        
        # For each bank, fetch its templates
        for bank in banks:
            bank_code = bank.get("bankCode")
            
            # Fetch templates for this bank
            templates_cursor = shared_db.bank_templates.find({
                "bankCode": bank_code,
                "isActive": True
            })
            templates = await templates_cursor.to_list(length=None)
            
            # Clean up template documents (remove migration metadata)
            cleaned_templates = []
            for template in templates:
                # Remove migration-specific fields
                template.pop("migratedAt", None)
                template.pop("migrationSource", None)
                template.pop("bankCode", None)  # Already in parent bank
                template.pop("bankName", None)  # Already in parent bank
                cleaned_templates.append(template)
            
            # Add templates array to bank
            bank["templates"] = cleaned_templates
            
            # Clean up bank document
            bank.pop("migratedAt", None)
            bank.pop("migrationSource", None)
            
            logger.debug(f"  ✅ {bank_code}: {len(cleaned_templates)} templates")
        
        logger.info(f"✅ Successfully aggregated banks with templates")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content=json.loads(json.dumps(banks, default=json_serializer))
        )
        
        # Log the response
        api_logger.log_response(response, request_data)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching banks: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "details": str(e)}
        )
        
        # Log the error response
        api_logger.log_response(error_response, request_data)
        
        return error_response

@app.get("/api/templates/{bank_code}/{template_id}/aggregated-fields")
async def get_aggregated_template_fields(bank_code: str, template_id: str, request: Request) -> JSONResponse:
    """Get template fields using multi-collection aggregation: common_form_fields + bank-specific template collection"""
    # Log the request
    request_data = await api_logger.log_request(request)
    
    try:
        logger.info(f"🔄 Multi-Collection Aggregation API call for template: {bank_code}/{template_id}")
        
        # Ensure environment variable is set before importing database modules
        if not os.getenv('MONGODB_URI'):
            raise HTTPException(status_code=500, detail="MongoDB connection not configured")
        
        from database.multi_db_manager import MultiDatabaseManager
        
        logger.info(f"🔄 Starting Multi-Collection Aggregation API call for template: {bank_code}/{template_id}")
        
        # Use MultiDatabaseManager directly (same as working debug endpoints)
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            admin_db = db_manager.get_database("admin")
            
            # Debug: Check what documents exist in the admin.banks collection
            admin_banks_count = await admin_db.banks.count_documents({})
            logger.info(f"🔍 Found {admin_banks_count} documents in admin.banks collection")
            
            # Find the comprehensive document
            unified_doc = await admin_db.banks.find_one({"_id": "all_banks_comprehensive_v4"})
            
            if unified_doc:
                logger.info(f"✅ Found comprehensive document: {unified_doc.get('_id')}")
            else:
                logger.error(f"❌ Comprehensive document not found!")
                # Try to find any document
                any_doc = await admin_db.banks.find_one({})
                if any_doc:
                    logger.info(f"   But found other document: {any_doc.get('_id')}")
                    # Use it if it seems to be banks data
                    if "banks" in any_doc:
                        unified_doc = any_doc
                        logger.info(f"✅ Using found document as it contains banks data")
                
            if not unified_doc:
                raise HTTPException(status_code=404, detail="Banks configuration not found")

            
            # Find the specific bank in the banks array
            bank_doc = None
            all_banks = unified_doc.get("banks", [])
            
            for bank in all_banks:
                if bank.get("bankCode", "").upper() == bank_code.upper():
                    bank_doc = bank
                    break
            
            if not bank_doc:
                logger.warning(f"❌ Bank not found: {bank_code}")
                raise HTTPException(status_code=404, detail=f"Bank {bank_code} not found")
            
            if not bank_doc.get("isActive", True):
                logger.warning(f"❌ Bank is inactive: {bank_code}")
                raise HTTPException(status_code=404, detail=f"Bank {bank_code} is inactive")
            
            # Step 2: Find the specific template within the bank
            target_template = None
            templates = bank_doc.get("templates", [])
            
            for template in templates:
                if (template.get("templateCode", "").upper() == template_id.upper() or 
                    template.get("templateId", "").upper() == template_id.upper()):
                    target_template = template
                    break
            
            if not target_template:
                logger.warning(f"❌ Template not found: {template_id} for bank {bank_code}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Template {template_id} not found for bank {bank_code}"
                )
                
            collection_ref = target_template.get("collectionRef")
            if not collection_ref:
                logger.error(f"❌ No collection reference found for template: {bank_code}/{template_id}")
                raise HTTPException(
                    status_code=500, 
                    detail="Template collection reference not configured"
                )
            
            logger.info(f"📋 Using collection: {collection_ref}")
            
            # Step 3: Get common form fields (all active fields)
            common_fields_collection = admin_db["common_form_fields"]
            common_fields_docs = await common_fields_collection.find({"isActive": True}).to_list(length=None)
            
            # Get common fields (already in correct format)
            common_fields = []
            for doc in common_fields_docs:
                doc_fields = doc.get("fields", [])
                for field in doc_fields:
                    # Fields are already in correct frontend format
                    common_fields.append(field)
            
            logger.info(f"📄 Fetched {len(common_fields)} common fields")
            
            # Step 4: Get bank-specific template fields from the collection
            template_collection = admin_db[collection_ref]
            template_collection_docs = await template_collection.find({}).to_list(length=None)
            
            if not template_collection_docs:
                logger.warning(f"❌ No template data found in collection: {collection_ref}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Template data not found for {bank_code}/{template_id}"
                )
            
            # Process bank-specific fields from collection documents
            bank_specific_tabs = []
            
            for doc in template_collection_docs:
                template_metadata = doc.get("templateMetadata", {})
                
                # Build tabs structure based on template metadata
                tabs_config = template_metadata.get("tabs", [])
                
                if not tabs_config:
                    # Fallback: create a single tab from document fields
                    doc_fields = doc.get("fields", [])
                    if doc_fields:
                        bank_specific_tabs.append({
                            "tabId": "property_details",
                            "tabName": "property_details",
                            "tabTitle": "Property Details",
                            "tabOrder": 1,
                            "hasSections": False,
                            "description": "Property valuation details",
                            "fields": doc_fields,
                            "sections": []
                        })
                    continue
                
                # Process each tab from metadata
                for tab_config in sorted(tabs_config, key=lambda x: x.get("sortOrder", 0)):
                    tab_id = tab_config.get("tabId", "default_tab")
                    
                    # Build tab structure
                    tab = {
                        "tabId": tab_id,
                        "tabName": tab_config.get("tabName", tab_id),
                        "tabTitle": tab_config.get("tabName", tab_id).replace("_", " ").title(),
                        "tabOrder": tab_config.get("sortOrder", 1),
                        "hasSections": tab_config.get("hasSections", False),
                        "description": tab_config.get("description", ""),
                        "fields": [],
                        "sections": []
                    }
                    
                    # Handle tabs with sections
                    if tab_config.get("hasSections"):
                        sections_config = tab_config.get("sections", [])
                        print(f"DEBUG: Tab {tab_config.get('tabName')} has {len(sections_config)} sections")
                        
                        for section_config in sorted(sections_config, key=lambda x: x.get("sortOrder", 0)):
                            section_id = section_config.get("sectionId")
                            
                            # Find the corresponding section in documents array
                            document_section = None
                            for document in doc.get("documents", []):
                                for doc_section in document.get("sections", []):
                                    if doc_section.get("sectionId") == section_id:
                                        document_section = doc_section
                                        break
                                if document_section:
                                    break
                            
                            if document_section:
                                section_fields = document_section.get("fields", [])
                                
                                # Check if this is a documents section - integrate document types
                                section_name = section_config.get("sectionName", "").lower()
                                print(f"DEBUG: Processing section: '{section_name}' - checking for document keyword")
                                logger.info(f"🔍 Processing section: '{section_name}' - checking for document keyword")
                                if "document" in section_name:
                                    logger.info(f"📄 Found documents section: {section_name}")
                                    try:
                                        from services.document_types_integrator import DocumentTypesIntegrator
                                        
                                        logger.info(f"📄 Calling DocumentTypesIntegrator with bank_code='{bank_code}', property_type='{template_id}'")
                                        # Get document types for this bank and property type (template_id = property type)
                                        doc_type_fields = await DocumentTypesIntegrator.get_document_fields(
                                            db_manager, property_type=template_id, bank_code=bank_code
                                        )
                                        if doc_type_fields:
                                            logger.info(f"📄 Adding {len(doc_type_fields)} document type fields to section")
                                            section_fields.extend(doc_type_fields)
                                        else:
                                            logger.warning(f"📄 No document type fields found for {bank_code}/{template_id}")
                                    except Exception as e:
                                        logger.error(f"❌ Error integrating document types: {e}")
                                        import traceback
                                        traceback.print_exc()
                                else:
                                    logger.info(f"🔍 Section '{section_name}' does not contain 'document' keyword")
                                
                                section = {
                                    "sectionId": section_config.get("sectionId"),
                                    "sectionName": section_config.get("sectionName"),
                                    "sortOrder": section_config.get("sortOrder"),
                                    "description": section_config.get("description", ""),
                                    "fields": section_fields
                                }
                                tab["sections"].append(section)
                                # Also add fields to tab level for backward compatibility
                                tab["fields"].extend(section_fields)
                    
                    # Handle tabs without sections (normal field structure)
                    else:
                        # Get fields from the specific document that matches this tab's documentSource
                        document_source = tab_config.get("documentSource")
                        if document_source:
                            # Find the document with matching templateId
                            for document in doc.get("documents", []):
                                if document.get("templateId") == document_source:
                                    tab["fields"] = document.get("fields", [])
                                    break
                        else:
                            # Fallback: get all fields if no documentSource specified
                            all_doc_fields = []
                            for document in doc.get("documents", []):
                                doc_fields = document.get("fields", [])
                                all_doc_fields.extend(doc_fields)
                            tab["fields"] = all_doc_fields
                    
                    bank_specific_tabs.append(tab)
            
            logger.info(f"🎯 Created {len(bank_specific_tabs)} bank-specific tabs")
            
            # Step 4.5: Process fields to enhance calculation metadata
            # Common fields are already transformed, no need for additional processing
            processed_common_fields = common_fields
            processed_bank_tabs = []
            for tab in bank_specific_tabs:
                processed_tab = dict(tab)
                processed_tab["fields"] = process_template_fields(tab.get("fields", []))
                
                # Also process section fields if they exist
                if tab.get("sections"):
                    processed_sections = []
                    for section in tab["sections"]:
                        processed_section = dict(section)
                        processed_section["fields"] = process_template_fields(section.get("fields", []))
                        processed_sections.append(processed_section)
                    processed_tab["sections"] = processed_sections
                
                processed_bank_tabs.append(processed_tab)
            
            logger.info(f"✅ Processed calculation metadata for all fields")
            
            # Step 5: Build comprehensive response (matching expected frontend format)
            response_data = {
                "templateInfo": {
                    "templateId": target_template.get("templateId", ""),
                    "templateName": target_template.get("templateName", ""),
                    "templateCode": target_template.get("templateCode", ""),
                    "templateType": target_template.get("templateType", ""),
                    "propertyType": target_template.get("propertyType", ""),
                    "description": target_template.get("description", ""),
                    "version": target_template.get("version", "1.0"),
                    "bankCode": bank_doc.get("bankCode", ""),
                    "bankName": bank_doc.get("bankName", "")
                },
                "commonFields": processed_common_fields,
                "bankSpecificTabs": processed_bank_tabs,
                "aggregatedAt": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "architecture": "multi_collection",
                    "commonFieldsSource": "common_form_fields",
                    "bankSpecificSource": collection_ref,
                    "totalCommonFields": len(common_fields),
                    "totalBankTabs": len(bank_specific_tabs),
                    "source": "multi_collection_aggregation"
                }
            }
            
            total_bank_fields = sum(len(tab.get("fields", [])) for tab in bank_specific_tabs)
            logger.info(f"✅ Successfully aggregated {len(common_fields)} common + {total_bank_fields} bank-specific fields for {bank_code}/{template_id}")
            
            response = JSONResponse(
                content=json.loads(json.dumps(response_data, default=json_serializer))
            )
            
            # Log the response
            api_logger.log_response(response, request_data)
            
            return response
            
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"❌ Unexpected error in aggregated fields: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            await db_manager.disconnect()
            
    except HTTPException as http_exc:
        error_response = JSONResponse(
            status_code=http_exc.status_code,
            content={"error": http_exc.detail}
        )
        api_logger.log_response(error_response, request_data)
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error in multi-collection aggregation: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"error": f"Failed to aggregate template fields: {str(e)}"}
        )
        api_logger.log_response(error_response, request_data)
        raise HTTPException(status_code=500, detail=f"Failed to aggregate template fields: {str(e)}")

# ================================
# FIELD PROCESSING UTILITIES
# ================================

def transform_common_field_to_frontend_format(field: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB common field structure to frontend expected format"""
    # Map MongoDB field structure to frontend format - NEW INTERFACE
    transformed = {
        # NEW: Use frontend interface field names
        "fieldId": field.get("fieldId", field.get("id", "")),
        "uiDisplayName": field.get("uiDisplayName", field.get("label", "")),
        "fieldType": field.get("fieldType", field.get("type", "text")),
        "isRequired": field.get("isRequired", field.get("required", False)),
        "placeholder": field.get("placeholder", ""),
        "helpText": field.get("helpText", ""),
        "validation": field.get("validation", {}),
        "sortOrder": field.get("sortOrder", 0),
        "gridSize": field.get("gridSize", 6),
        "fieldGroup": field.get("fieldGroup", "Common"),  # Use existing or default to "Common"
        
        # Add missing required fields for frontend interface
        "_id": field.get("_id", field.get("id", "")),
        "technicalName": field.get("technicalName", field.get("fieldId", field.get("id", ""))),
        "isActive": field.get("isActive", True),
        "isReadonly": field.get("isReadonly", False)
    }
    
    # Handle special field types
    if transformed["type"] == "select" and "options" in field:
        transformed["options"] = field["options"]
    elif transformed["type"] == "select_dynamic":
        transformed["type"] = "select"
        if "dataSourceConfig" in field:
            transformed["dataSourceConfig"] = field["dataSourceConfig"]
    
    # Add other MongoDB properties if they exist
    for key in ["defaultValue", "dynamic", "dataSource", "dataSourceConfig", "technicalName"]:
        if key in field:
            transformed[key] = field[key]
    
    # Add technical name for backend compatibility
    transformed["technicalName"] = field.get("technicalName", field.get("fieldId", transformed["id"]))
    
    return transformed

async def get_transformed_common_fields(db) -> List[Dict[str, Any]]:
    """Get and transform common fields for frontend consumption"""
    try:
        # Get common form fields (all active fields)
        common_fields_docs = await db.find_many(
            "admin",
            "common_form_fields", 
            {"isActive": True}
        )
        
        # Process common fields and transform them
        common_fields = []
        for doc in common_fields_docs:
            doc_fields = doc.get("fields", [])
            for field in doc_fields:
                transformed_field = transform_common_field_to_frontend_format(field)
                common_fields.append(transformed_field)
        
        logger.info(f"📄 Fetched and transformed {len(common_fields)} common fields")
        return common_fields
    
    except Exception as e:
        logger.error(f"❌ Error fetching common fields: {e}")
        return []

def process_template_fields(fields_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process template fields to enhance calculation metadata and ensure proper structure"""
    processed_fields = []
    
    for field in fields_list:
        processed_field = dict(field)  # Create a copy
        
        # Check if field has calculation metadata
        calc_metadata = field.get('calculationMetadata', {})
        
        if calc_metadata:
            logger.debug(f"Processing calculation field: {field.get('fieldId', 'unknown')}")
            
            # Ensure calculation metadata is properly structured
            if calc_metadata.get('isCalculatedField'):
                # This is a calculated field (result field)
                processed_field['isReadonly'] = True  # Calculated fields are always readonly
                processed_field['isCalculated'] = True
                
                # Ensure formula exists
                if not processed_field.get('formula') and calc_metadata.get('formula'):
                    processed_field['formula'] = calc_metadata['formula']
                
                # Ensure formatting is applied
                if calc_metadata.get('formatting', {}).get('currency'):
                    if processed_field.get('fieldType') != 'currency':
                        processed_field['fieldType'] = 'currency'
                        processed_field['displayFormat'] = 'currency'
                
            elif calc_metadata.get('isCalculationInput'):
                # This is an input field for calculations
                processed_field['isCalculationInput'] = True
                
        # Process subFields if they exist (for group fields)
        if 'subFields' in field:
            processed_field['subFields'] = process_template_fields(field['subFields'])
        
        processed_fields.append(processed_field)
    
    return processed_fields

# ================================
# CALCULATION ENGINE APIs
# ================================

from pydantic import BaseModel
from typing import Dict, Any, List, Union

class CalculationRequest(BaseModel):
    formula: str
    dependencies: Dict[str, Union[float, int, str]]
    fieldId: str
    templateId: str
    formatting: Dict[str, Any] = {}

@app.post("/api/calculate")
async def calculate_field_value(calc_request: CalculationRequest, request: Request) -> JSONResponse:
    """Calculate field value based on formula and dependencies"""
    request_data = await api_logger.log_request(request)
    
    try:
        logger.info(f"🧮 Processing calculation for field: {calc_request.fieldId}")
        logger.debug(f"Formula: {calc_request.formula}")
        logger.debug(f"Dependencies: {calc_request.dependencies}")
        
        # Clean and validate input values
        cleaned_deps = {}
        for key, value in calc_request.dependencies.items():
            if value is None or value == "":
                cleaned_deps[key] = 0
            elif isinstance(value, str):
                # Remove currency symbols and commas, extract numeric value
                cleaned_value = str(value).replace('₹', '').replace(',', '').replace(' ', '').strip()
                try:
                    cleaned_deps[key] = float(cleaned_value) if cleaned_value else 0
                except ValueError:
                    logger.warning(f"Could not convert '{value}' to number, using 0")
                    cleaned_deps[key] = 0
            else:
                cleaned_deps[key] = float(value)
        
        logger.debug(f"Cleaned dependencies: {cleaned_deps}")
        
        # Simple formula evaluation for basic arithmetic
        # Support: addition (+), subtraction (-), multiplication (*), division (/)
        formula = calc_request.formula.strip()
        
        # Replace field names in formula with actual values
        evaluation_formula = formula
        for field_name, field_value in cleaned_deps.items():
            evaluation_formula = evaluation_formula.replace(field_name, str(field_value))
        
        logger.debug(f"Evaluation formula: {evaluation_formula}")
        
        # Safely evaluate the formula (only allow basic arithmetic operations)
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in evaluation_formula):
            raise ValueError("Formula contains invalid characters")
        
        # Calculate result
        try:
            result = eval(evaluation_formula)
            logger.info(f"✅ Calculation result: {result}")
        except Exception as eval_error:
            logger.error(f"❌ Formula evaluation error: {eval_error}")
            result = 0
        
        # Apply simple numeric formatting
        formatting = calc_request.formatting or {}
        decimal_places = formatting.get('decimalPlaces', 2)
        formatted_result = round(result, decimal_places)
        
        logger.info(f"Simple formatting - Field ID: {calc_request.fieldId}, Result: {result}, Formatted: {formatted_result}")
        
        response_data = {
            "success": True,
            "result": result,
            "formattedResult": formatted_result,
            "formula": calc_request.formula,
            "evaluatedFormula": evaluation_formula,
            "fieldId": calc_request.fieldId
        }
        
        response = JSONResponse(
            status_code=200,
            content=response_data
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Calculation error: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Calculation failed: {str(e)}",
                "result": 0,
                "formattedResult": "0"
            }
        )
        api_logger.log_response(error_response, request_data)
        return error_response


        
    except Exception as e:
        logger.error(f"Currency formatting error: {e}")
        return f"₹{amount:,.2f}"

# ================================
# ORGANIZATION MANAGEMENT APIs
# ================================

@app.post("/api/admin/organizations")
async def create_organization(org_request: CreateOrganizationRequest, request: Request):
    """Create a new organization (System Admin only)"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"🏢 Creating new organization: {org_request.name}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        import re
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Generate org_short_name (URL-safe identifier) from name
        def slugify(text: str) -> str:
            """Convert text to URL-safe slug"""
            text = text.lower().strip()
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[-\s]+', '-', text)
            return text
        
        org_short_name_base = slugify(org_request.name)[:30]  # Limit to 30 chars
        
        # Get val_app_config database
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Check if org_short_name exists, add number suffix if needed
        org_short_name = org_short_name_base
        counter = 1
        
        while await orgs_collection.find_one({"org_short_name": org_short_name}):
            counter += 1
            org_short_name = f"{org_short_name_base}-{counter}"
        
        logger.info(f"📝 Generated org_short_name: {org_short_name}")
        
        # Generate legacy organization_id for backward compatibility
        org_id_base = re.sub(r'[^a-z0-9]+', '_', org_request.name.lower())[:20]
        org_id = f"{org_id_base}_{counter:03d}"
        
        # Determine max reports based on plan
        max_reports_map = {
            "basic": 100,
            "premium": 500,
            "enterprise": -1  # Unlimited
        }
        max_reports = max_reports_map.get(org_request.plan, 100)
        
        # Determine storage limit based on plan
        storage_map = {
            "basic": 10,
            "premium": 50,
            "enterprise": -1  # Unlimited
        }
        storage_gb = storage_map.get(org_request.plan, 10)
        
        # Create organization document with NEW unified schema
        org_document = {
            # Core identity
            "org_name": org_request.name,
            "org_short_name": org_short_name,  # URL-safe unique identifier
            "org_display_name": org_request.name,
            "organization_type": org_request.type if hasattr(org_request, 'type') else "valuation_company",
            "description": org_request.description if hasattr(org_request, 'description') else None,
            
            # System flags
            "is_system_org": False,
            "is_active": True,
            
            # Contact information
            "contact_info": {
                "email": org_request.contact_email,
                "phone": org_request.contact_phone if hasattr(org_request, 'contact_phone') else None,
                "address": org_request.address if hasattr(org_request, 'address') else None
            },
            
            # Settings & Limits
            "settings": {
                "s3_prefix": org_id,  # Use legacy org_id for S3 compatibility
                "subscription_plan": org_request.plan,
                "max_users": org_request.max_users,
                "max_reports_per_month": max_reports,
                "max_storage_gb": storage_gb,
                "features_enabled": ["reports", "templates", "file_upload"],
                "timezone": "UTC",
                "date_format": "DD/MM/YYYY"
            },
            
            # Backward compatibility metadata
            "metadata": {
                "original_organization_id": org_id,
                "database_name": org_short_name,
                "created_from": "admin_ui",
                "migration_date": None
            },
            
            # Audit fields
            "created_by": "system_admin",  # TODO: Get from JWT
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Insert into val_app_config.organizations
        result = await orgs_collection.insert_one(org_document)
        logger.info(f"✅ Created organization in val_app_config: {result.inserted_id}")
        
        # Initialize organization database structure using org_short_name
        success = await db_manager.ensure_org_database_structure(org_short_name)
        
        if not success:
            logger.error(f"❌ Failed to initialize database for {org_short_name}")
            # Rollback - delete org document
            await orgs_collection.delete_one({"_id": result.inserted_id})
            raise HTTPException(status_code=500, detail="Failed to initialize organization database")
        
        logger.info(f"✅ Organization database initialized: {org_short_name}")
        
        await db_manager.disconnect()
        
        # Return organization data (convert to API format)
        org_response = {
            "_id": str(result.inserted_id),
            "organization_id": org_id,  # Legacy field for backward compat
            "org_short_name": org_short_name,
            "name": org_request.name,
            "status": "active",
            "contact_info": org_document["contact_info"],
            "settings": org_document["settings"],
            "created_at": org_document["created_at"].isoformat(),
            "updated_at": org_document["updated_at"].isoformat(),
            "isActive": True
        }
        
        response = JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": f"Organization '{org_request.name}' created successfully",
                "data": org_response
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error creating organization: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/admin/organizations")
async def list_organizations(request: Request, include_system: bool = False):
    """List all organizations (System Admin only)"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"📋 Fetching all organizations (include_system: {include_system})")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organizations from val_app_config
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Build query filter
        query_filter = {"is_active": True}
        if not include_system:
            query_filter["is_system_org"] = {"$ne": True}
            
        # Get organizations based on filter
        orgs_cursor = orgs_collection.find(query_filter)
        organizations = await orgs_cursor.to_list(length=None)
        
        # Transform to match UI expectations (backward compatible format)
        formatted_orgs = []
        for org in organizations:
            # Get user count from org-specific database
            org_short_name = org.get("org_short_name")
            user_count = 0
            
            if org_short_name:
                try:
                    org_db = db_manager.client[org_short_name]
                    user_count = await org_db.users.count_documents({"is_active": True}) if hasattr(org_db, 'users') else 0
                except:
                    user_count = 0
            
            formatted_org = {
                "_id": str(org["_id"]),
                "organization_id": org.get("metadata", {}).get("original_organization_id", org_short_name),
                "org_short_name": org_short_name,
                "name": org.get("org_name"),
                "status": "active" if org.get("is_active") else "inactive",
                "contact_info": org.get("contact_info", {}),
                "settings": org.get("settings", {}),
                "user_count": user_count,
                "created_at": org.get("created_at").isoformat() if org.get("created_at") else None,
                "updated_at": org.get("updated_at").isoformat() if org.get("updated_at") else None,
                "isActive": org.get("is_active", True)
            }
            formatted_orgs.append(formatted_org)
        
        logger.info(f"✅ Found {len(formatted_orgs)} organizations from val_app_config")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": formatted_orgs,
                "total": len(formatted_orgs)
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching organizations: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/admin/organizations/{org_id}")
async def get_organization(org_id: str, request: Request):
    """Get organization details (System Admin only)"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"🔍 Fetching organization: {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organizations from val_app_config
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Try to find by org_short_name first, then by ObjectId, then by legacy organization_id
        org = None
        if ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        
        if not org:
            org = await orgs_collection.find_one({"org_short_name": org_id})
        
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_short_name = org.get("org_short_name")
        
        # Get users from org-specific database
        users = []
        if org_short_name:
            try:
                org_db = db_manager.client[org_short_name]
                if hasattr(org_db, 'users'):
                    users_cursor = org_db.users.find({"is_active": True})
                    users = await users_cursor.to_list(length=None)
                    
                    # Clean up user data
                    for user in users:
                        user["_id"] = str(user["_id"])
                        if user.get("created_at"):
                            user["created_at"] = user["created_at"].isoformat()
                        if user.get("updated_at"):
                            user["updated_at"] = user["updated_at"].isoformat()
                        if user.get("last_login"):
                            user["last_login"] = user["last_login"].isoformat()
            except Exception as e:
                logger.warning(f"Could not fetch users for org {org_short_name}: {e}")
                users = []
        
        # Format response (backward compatible)
        org_response = {
            "_id": str(org["_id"]),
            "organization_id": org.get("metadata", {}).get("original_organization_id", org_short_name),
            "org_short_name": org_short_name,
            "name": org.get("org_name"),
            "status": "active" if org.get("is_active") else "inactive",
            "contact_info": org.get("contact_info", {}),
            "settings": org.get("settings", {}),
            "subscription": {
                "plan": org.get("settings", {}).get("subscription_plan"),
                "max_reports_per_month": org.get("settings", {}).get("max_reports_per_month"),
                "storage_limit_gb": org.get("settings", {}).get("max_storage_gb"),
                "expires_at": None
            },
            "created_at": org.get("created_at").isoformat() if org.get("created_at") else None,
            "updated_at": org.get("updated_at").isoformat() if org.get("updated_at") else None,
            "isActive": org.get("is_active", True),
            "users": users,
            "user_count": len(users)
        }
        
        logger.info(f"✅ Found organization {org_id} with {len(users)} users")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={"success": True, "data": org_response}
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error fetching organization: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/organizations/{org_short_name}/next-reference-number")
async def get_next_reference_number(org_short_name: str, request: Request):
    """
    Get preview of next report reference number WITHOUT incrementing counter
    Used when loading report form to show what the reference number will be
    
    Returns:
        {
            "reference_number": "CEV/RVO/0001/02122025",
            "initials": "CEV/RVO",
            "sequence": 1,
            "formatted_sequence": "0001",
            "date": "02122025",
            "preview": true
        }
    """
    request_data = await api_logger.log_request(request)
    
    logger.info(f"📋 Fetching next reference number preview for: {org_short_name}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from services.reference_number_service import ReferenceNumberService
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Initialize reference number service
        ref_service = ReferenceNumberService(db_manager)
        
        # Get preview (does not increment counter)
        preview_data = await ref_service.get_next_reference_number_preview(org_short_name)
        
        logger.info(f"✅ Preview reference number: {preview_data['reference_number']}")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={"success": True, "data": preview_data}
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except ValueError as ve:
        # Organization not found or missing initials configuration
        logger.error(f"❌ Configuration error: {str(ve)}")
        error_response = JSONResponse(
            status_code=400,
            content={
                "success": False, 
                "error": str(ve),
                "message": "Please configure report reference initials in organization settings"
            }
        )
        api_logger.log_response(error_response, request_data)
        return error_response
    except Exception as e:
        logger.error(f"❌ Error getting reference number preview: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.delete("/api/admin/organizations/{org_id}")
async def delete_organization(org_id: str, hard_delete: bool = False, request: Request = None):
    """
    Delete organization and optionally its database (System Admin only)
    
    Parameters:
    - org_id: Organization short name, _id, or legacy organization_id
    - hard_delete: If true, also drops the organization database (default: false)
    
    WARNING: Hard delete will permanently remove all data!
    """
    request_data = await api_logger.log_request(request)
    
    logger.info(f"🗑️ Deleting organization: {org_id} (hard_delete={hard_delete})")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get val_app_config database
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Find organization by org_short_name or _id
        org = None
        
        # Try org_short_name first
        org = await orgs_collection.find_one({"org_short_name": org_id})
        
        # Try ObjectId if not found
        if not org and ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        
        # Try legacy organization_id
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_name = org.get("org_name", org_id)
        org_short_name = org.get("org_short_name")
        is_system_org = org.get("is_system_org", False)
        
        # PROTECTION: Prevent deletion of system organization
        if is_system_org:
            raise HTTPException(
                status_code=403, 
                detail="Cannot delete system organization"
            )
        
        # PROTECTION: Prevent deletion of protected databases
        if org_short_name in PROTECTED_DATABASES:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot delete organization with protected database: {org_short_name}"
            )
        
        # Soft delete - set is_active to False
        await orgs_collection.update_one(
            {"_id": org["_id"]},
            {
                "$set": {
                    "is_active": False,
                    "deleted_at": datetime.now(timezone.utc),
                    "deleted_by": "system_admin"  # TODO: Get from JWT
                }
            }
        )
        logger.info(f"✅ Organization soft-deleted: {org_name}")
        
        users_deactivated = 0
        database_dropped = False
        
        # Deactivate all users belonging to this organization
        try:
            org_db = db_manager.client[org_short_name]
            users_result = await org_db.users.update_many(
                {"is_active": True},
                {"$set": {"is_active": False, "deleted_at": datetime.now(timezone.utc)}}
            )
            users_deactivated = users_result.modified_count
            logger.info(f"✅ Deactivated {users_deactivated} users from organization")
        except Exception as e:
            logger.warning(f"⚠️ Could not deactivate users: {e}")
        
        # Hard delete: Drop the organization database
        if hard_delete:
            # Double-check it's not a protected database
            if org_short_name not in PROTECTED_DATABASES:
                logger.warning(f"⚠️ HARD DELETE: Dropping database: {org_short_name}")
                await db_manager.client.drop_database(org_short_name)
                database_dropped = True
                logger.info(f"✅ Database permanently deleted: {org_short_name}")
            else:
                logger.error(f"❌ Attempted to drop protected database: {org_short_name}")
        
        await db_manager.disconnect()
        
        delete_type = "permanently deleted (hard delete)" if hard_delete else "deactivated (soft delete)"
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Organization '{org_name}' has been {delete_type}",
                "data": {
                    "organization": org_short_name,
                    "org_name": org_name,
                    "delete_type": "hard" if hard_delete else "soft",
                    "database_dropped": database_dropped,
                    "users_deactivated": users_deactivated
                }
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error deleting organization: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.patch("/api/admin/organizations/{org_id}")
async def update_organization(org_id: str, request: Request):
    """
    Update organization details with change tracking (System Admin only)
    
    Tracks all changes in organization_changes collection for audit trail.
    Only non-immutable fields can be updated.
    
    Immutable fields: _id, org_short_name, created_at, created_by
    """
    request_data = await api_logger.log_request(request)
    
    logger.info(f"✏️ Updating organization: {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        from utils.change_tracker import (
            compute_changes,
            validate_editable_fields,
            build_update_document,
            create_change_record
        )
        
        # Parse request body
        body = await request.json()
        
        # Validate that only editable fields are being updated
        is_valid, error_msg = validate_editable_fields(body)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get collections
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        changes_collection = config_db.organization_changes
        
        # Find organization by org_short_name, _id, or legacy organization_id
        org = None
        
        # Try org_short_name first
        org = await orgs_collection.find_one({"org_short_name": org_id})
        
        # Try ObjectId if not found
        if not org and ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        
        # Try legacy organization_id
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_name = org.get("org_name", org_id)
        current_version = org.get("current_version", 0)
        
        # Compute what changed (delta)
        changes = compute_changes(org, body)
        
        if not changes:
            # No changes detected
            await db_manager.disconnect()
            response = JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "No changes detected",
                    "data": {
                        "_id": str(org["_id"]),
                        "org_short_name": org.get("org_short_name"),
                        "org_name": org_name
                    }
                }
            )
            api_logger.log_response(response, request_data)
            return response
        
        # Create change history record
        new_version = await create_change_record(
            changes_collection=changes_collection,
            org_id=org["_id"],
            changes=changes,
            changed_by="system_admin",  # TODO: Get from JWT token
            change_type="update",
            current_version=current_version
        )
        
        logger.info(f"📝 Created change record version {new_version} with {len(changes)} changes")
        
        # Build update document
        update_fields = build_update_document(changes)
        update_fields["current_version"] = new_version
        update_fields["updated_at"] = datetime.now(timezone.utc)
        update_fields["updated_by"] = "system_admin"  # TODO: Get from JWT token
        
        # Update organization with new values
        await orgs_collection.update_one(
            {"_id": org["_id"]},
            {"$set": update_fields}
        )
        
        logger.info(f"✅ Updated organization: {org_name} (version {new_version})")
        
        # Get updated organization
        updated_org = await orgs_collection.find_one({"_id": org["_id"]})
        
        await db_manager.disconnect()
        
        # Format response
        org_response = {
            "_id": str(updated_org["_id"]),
            "org_short_name": updated_org.get("org_short_name"),
            "org_name": updated_org.get("org_name"),
            "org_display_name": updated_org.get("org_display_name"),
            "contact_info": updated_org.get("contact_info", {}),
            "settings": updated_org.get("settings", {}),
            "is_active": updated_org.get("is_active", True),
            "current_version": new_version,
            "updated_at": updated_org.get("updated_at").isoformat() if updated_org.get("updated_at") else None,
            "changes_applied": len(changes)
        }
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Organization '{org_name}' updated successfully",
                "data": org_response,
                "changes": changes  # Include what changed for transparency
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error updating organization: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.patch("/api/admin/organizations/{org_id}/status")
async def update_organization_status(org_id: str, request: Request):
    """
    Toggle organization active/inactive status (System Admin only)
    This deactivates the organization without deleting data
    """
    request_data = await api_logger.log_request(request)
    
    logger.info(f"🔄 Toggling status for organization: {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        from utils.change_tracker import create_change_record
        
        # Parse request body to get new status
        body = await request.json()
        new_status = body.get("status")
        
        if new_status not in ["active", "inactive"]:
            raise HTTPException(
                status_code=400, 
                detail="Status must be 'active' or 'inactive'"
            )
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get collections
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        changes_collection = config_db.organization_changes
        
        # Find organization by org_short_name or _id
        org = None
        
        # Try org_short_name first
        org = await orgs_collection.find_one({"org_short_name": org_id})
        
        # Try ObjectId if not found
        if not org and ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        
        # Try legacy organization_id
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_name = org.get("org_name", org_id)
        org_short_name = org.get("org_short_name")
        current_status = "active" if org.get("is_active", True) else "inactive"
        current_version = org.get("current_version", 0)
        
        # Skip if status is already set to desired value
        if current_status == new_status:
            await db_manager.disconnect()
            response = JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Organization is already {new_status}",
                    "data": {
                        "org_short_name": org_short_name,
                        "org_name": org_name,
                        "status": current_status
                    }
                }
            )
            api_logger.log_response(response, request_data)
            return response
        
        # Create change record for status change
        is_active = (new_status == "active")
        change_type = "deactivate" if new_status == "inactive" else "activate"
        
        changes = [{
            "field": "is_active",
            "old_value": org.get("is_active", True),
            "new_value": is_active
        }]
        
        new_version = await create_change_record(
            changes_collection=changes_collection,
            org_id=org["_id"],
            changes=changes,
            changed_by="system_admin",  # TODO: Get from JWT token
            change_type=change_type,
            current_version=current_version
        )
        
        # Update organization status
        update_result = await orgs_collection.update_one(
            {"_id": org["_id"]},
            {
                "$set": {
                    "is_active": is_active,
                    "status": new_status,
                    "current_version": new_version,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": "system_admin"  # TODO: Get from JWT token
                }
            }
        )
        
        # Also update all users in this organization's database
        org_db = db_manager.client[org_short_name]
        users_result = await org_db.users.update_many(
            {},  # All users in this org
            {
                "$set": {
                    "is_active": is_active,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"✅ Updated organization status: {current_status} → {new_status}")
        logger.info(f"✅ Updated {users_result.modified_count} users")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Organization '{org_name}' status changed to {new_status}",
                "data": {
                    "org_short_name": org_short_name,
                    "org_name": org_name,
                    "previous_status": current_status,
                    "new_status": new_status,
                    "users_updated": users_result.modified_count
                }
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error updating organization status: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


# ================================
# USER MANAGEMENT APIs
# ================================

@app.post("/api/admin/organizations/{org_id}/users")
async def add_user_to_organization(org_id: str, user_request: AddUserToOrgRequest, request: Request):
    """Add a new user to an organization (System Admin only)"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"👤 Adding user {user_request.email} to organization {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        from utils.user_change_tracker import create_user_creation_record
        
        # Validate role
        if user_request.role not in ["manager", "employee"]:
            raise HTTPException(status_code=400, detail="Role must be 'manager' or 'employee'")
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organization from val_app_config database
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Try to find organization by org_short_name, ObjectId, or legacy organization_id
        org = None
        if ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        
        if not org:
            org = await orgs_collection.find_one({"org_short_name": org_id})
        
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        if not org.get("is_active", False):
            await db_manager.disconnect()
            raise HTTPException(status_code=400, detail=f"Organization {org_id} is not active")
        
        org_short_name = org.get("org_short_name")
        if not org_short_name:
            await db_manager.disconnect()
            raise HTTPException(status_code=500, detail="Organization missing org_short_name")
        
        # Get organization-specific database
        org_db = db_manager.client[org_short_name]
        
        # Check if user already exists in organization database
        existing_user = await org_db.users.find_one({"email": user_request.email})
        
        if existing_user:
            await db_manager.disconnect()
            raise HTTPException(status_code=400, detail=f"User with email {user_request.email} already exists in this organization")
        
        # Generate user ID
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        # Hash password
        hashed_password = pwd_context.hash(user_request.password)
        
        # Create user document for organization database
        user_document = {
            "_id": user_id,
            "email": user_request.email,
            "full_name": user_request.full_name,
            "phone": user_request.phone or "",
            "password_hash": hashed_password,
            "org_id": str(org["_id"]),
            "org_short_name": org_short_name,
            "role": user_request.role,
            "is_active": True,
            "created_by": "system_admin",  # TODO: Get from JWT
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_login": None,
            "current_version": 1  # Start version tracking
        }
        
        # Insert into organization database users collection
        result = await org_db.users.insert_one(user_document)
        logger.info(f"✅ Created user in {org_short_name}.users: {user_id}")
        
        # Create user settings
        user_settings = {
            "_id": user_id,
            "user_email": user_request.email,
            "dashboard_layout": "grid",
            "theme": "light",
            "notifications_enabled": True,
            "default_bank": None,
            "favorite_templates": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await org_db.users_settings.insert_one(user_settings)
        logger.info(f"✅ Created user settings in {org_short_name}.users_settings")
        
        # Create user change tracking record
        user_changes_collection = org_db.user_changes
        await create_user_creation_record(
            changes_collection=user_changes_collection,
            user_id=user_id,
            user_data=user_document,
            created_by="system_admin"  # TODO: Get from JWT
        )
        logger.info(f"📝 Created user change record for {user_id} (version 1)")
        
        # Log activity
        activity_log = {
            "user_id": "system_admin",
            "action": "user_created",
            "resource_type": "user",
            "resource_id": user_id,
            "details": {
                "email": user_request.email,
                "role": user_request.role,
                "full_name": user_request.full_name
            },
            "timestamp": datetime.now(timezone.utc)
        }
        await org_db.activity_logs.insert_one(activity_log)
        
        await db_manager.disconnect()
        
        # Return user data (remove sensitive fields)
        user_response = {
            "_id": user_id,
            "email": user_request.email,
            "full_name": user_request.full_name,
            "phone": user_request.phone or "",
            "org_id": str(org["_id"]),
            "org_short_name": org_short_name,
            "role": user_request.role,
            "is_active": True,
            "created_at": user_document["created_at"].isoformat(),
            "updated_at": user_document["updated_at"].isoformat(),
            "current_version": 1
        }
        
        response = JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": f"User '{user_request.email}' added to organization successfully",
                "data": user_response
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error adding user: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/admin/organizations/{org_id}/users")
async def list_organization_users(org_id: str, request: Request):
    """List all users in an organization"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"📋 Fetching users for organization: {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organization from val_app_config database
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        # Try to find organization by org_short_name, ObjectId, or legacy organization_id
        org = None
        if ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        
        if not org:
            org = await orgs_collection.find_one({"org_short_name": org_id})
        
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_short_name = org.get("org_short_name")
        if not org_short_name:
            await db_manager.disconnect()
            raise HTTPException(status_code=500, detail="Organization missing org_short_name")
        
        # Get users from organization-specific database
        org_db = db_manager.client[org_short_name]
        users_cursor = org_db.users.find({"is_active": True})
        users = await users_cursor.to_list(length=None)
        
        # Format user data for frontend
        formatted_users = []
        for user in users:
            formatted_user = {
                "_id": str(user["_id"]),
                "user_id": user.get("_id"),  # For compatibility
                "name": user.get("full_name", ""),
                "email": user.get("email", ""),
                "phone": user.get("phone", ""),  # Include phone number
                "role": user.get("role", "employee"),
                "status": "active" if user.get("is_active", True) else "inactive",
                "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
                "current_version": user.get("current_version", 0)  # Include version for tracking
            }
            formatted_users.append(formatted_user)
        
        logger.info(f"✅ Found {len(formatted_users)} users in {org_short_name}")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": formatted_users,
                "total": len(formatted_users)
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error fetching users: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.put("/api/admin/organizations/{org_id}/users/{user_id}")
async def update_organization_user(org_id: str, user_id: str, update_data: dict, request: Request):
    """Update user details in an organization"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"🔄 Updating user {user_id} in organization {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        from utils.user_change_tracker import (
            compute_user_changes,
            create_user_change_record
        )
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organization
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        org = None
        if ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        if not org:
            org = await orgs_collection.find_one({"org_short_name": org_id})
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_short_name = org.get("org_short_name")
        org_db = db_manager.client[org_short_name]
        
        # Find user
        user = await org_db.users.find_one({"_id": user_id})
        if not user:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        current_version = user.get("current_version", 0)
        
        # Prepare update fields (only allow phone and role)
        update_fields = {}
        if "phone" in update_data:
            update_fields["phone"] = update_data["phone"]
        if "role" in update_data:
            if update_data["role"] not in ["manager", "employee"]:
                raise HTTPException(status_code=400, detail="Role must be 'manager' or 'employee'")
            update_fields["role"] = update_data["role"]
        
        if not update_fields:
            await db_manager.disconnect()
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Compute changes
        changes = compute_user_changes(user, update_fields)
        
        if not changes:
            # No changes detected
            await db_manager.disconnect()
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "No changes detected",
                    "data": {"user_id": user_id}
                }
            )
        
        # Create change record
        user_changes_collection = org_db.user_changes
        new_version = await create_user_change_record(
            changes_collection=user_changes_collection,
            user_id=user_id,
            changes=changes,
            changed_by="system_admin",  # TODO: Get from JWT
            change_type="update",
            current_version=current_version
        )
        
        logger.info(f"📝 Created user change record version {new_version} with {len(changes)} changes")
        
        # Update user with new values
        update_fields["updated_at"] = datetime.now(timezone.utc)
        update_fields["current_version"] = new_version
        
        result = await org_db.users.update_one(
            {"_id": user_id},
            {"$set": update_fields}
        )
        
        logger.info(f"✅ Updated user {user_id} (version {new_version})")
        
        # Log activity
        activity_log = {
            "user_id": "system_admin",
            "action": "user_updated",
            "resource_type": "user",
            "resource_id": user_id,
            "details": {
                "email": user.get("email"),
                "updated_fields": list(update_fields.keys()),
                "version": new_version
            },
            "timestamp": datetime.now(timezone.utc)
        }
        await org_db.activity_logs.insert_one(activity_log)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"User {user.get('email')} updated successfully",
                "data": {
                    "user_id": user_id,
                    "updated_fields": [c["field"] for c in changes],
                    "version": new_version
                }
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error updating user: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.put("/api/admin/organizations/{org_id}/users/{user_id}/status")
async def toggle_user_status(org_id: str, user_id: str, status_data: dict, request: Request):
    """Activate or deactivate a user"""
    request_data = await api_logger.log_request(request)
    
    is_active = status_data.get("is_active", True)
    action = "activate" if is_active else "deactivate"
    logger.info(f"🔄 {action.capitalize()}ing user {user_id} in organization {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        from utils.user_change_tracker import create_status_change_record
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organization
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        org = None
        if ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        if not org:
            org = await orgs_collection.find_one({"org_short_name": org_id})
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_short_name = org.get("org_short_name")
        org_db = db_manager.client[org_short_name]
        
        # Find user
        user = await org_db.users.find_one({"_id": user_id})
        if not user:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        current_version = user.get("current_version", 0)
        old_status = user.get("is_active", True)
        
        # Check if status actually changed
        if old_status == is_active:
            await db_manager.disconnect()
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"User already {action}d",
                    "data": {"user_id": user_id, "is_active": is_active}
                }
            )
        
        # Create status change record
        user_changes_collection = org_db.user_changes
        new_version = await create_status_change_record(
            changes_collection=user_changes_collection,
            user_id=user_id,
            old_status=old_status,
            new_status=is_active,
            changed_by="system_admin",  # TODO: Get from JWT
            current_version=current_version
        )
        
        logger.info(f"📝 Created status change record version {new_version}")
        
        # Update status
        result = await org_db.users.update_one(
            {"_id": user_id},
            {"$set": {
                "is_active": is_active,
                "updated_at": datetime.now(timezone.utc),
                "current_version": new_version
            }}
        )
        
        logger.info(f"✅ {action.capitalize()}d user {user_id} (version {new_version})")
        
        # Log activity
        activity_log = {
            "user_id": "system_admin",
            "action": f"user_{action}d",
            "resource_type": "user",
            "resource_id": user_id,
            "details": {
                "email": user.get("email"),
                "is_active": is_active,
                "version": new_version
            },
            "timestamp": datetime.now(timezone.utc)
        }
        await org_db.activity_logs.insert_one(activity_log)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"User {user.get('email')} {action}d successfully",
                "data": {
                    "user_id": user_id,
                    "is_active": is_active,
                    "version": new_version
                }
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error {action}ing user: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.delete("/api/admin/organizations/{org_id}/users/{user_id}")
async def delete_organization_user(org_id: str, user_id: str, request: Request):
    """Delete a user from an organization (hard delete)"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"🗑️ Deleting user {user_id} from organization {org_id}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        from utils.user_change_tracker import create_deletion_record
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get organization
        config_db = db_manager.client.val_app_config
        orgs_collection = config_db.organizations
        
        org = None
        if ObjectId.is_valid(org_id):
            org = await orgs_collection.find_one({"_id": ObjectId(org_id)})
        if not org:
            org = await orgs_collection.find_one({"org_short_name": org_id})
        if not org:
            org = await orgs_collection.find_one({"metadata.original_organization_id": org_id})
        
        if not org:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")
        
        org_short_name = org.get("org_short_name")
        org_db = db_manager.client[org_short_name]
        
        # Find user
        user = await org_db.users.find_one({"_id": user_id})
        if not user:
            await db_manager.disconnect()
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        user_email = user.get("email")
        current_version = user.get("current_version", 0)
        
        # Create deletion record BEFORE deleting
        user_changes_collection = org_db.user_changes
        final_version = await create_deletion_record(
            changes_collection=user_changes_collection,
            user_id=user_id,
            user_data=user,
            deleted_by="system_admin",  # TODO: Get from JWT
            current_version=current_version
        )
        
        logger.info(f"📝 Created deletion record version {final_version}")
        
        # Delete user
        await org_db.users.delete_one({"_id": user_id})
        
        # Delete user settings if exists
        await org_db.users_settings.delete_one({"_id": user_id})
        
        logger.info(f"✅ Deleted user {user_id} ({user_email})")
        
        # Log activity
        activity_log = {
            "user_id": "system_admin",
            "action": "user_deleted",
            "resource_type": "user",
            "resource_id": user_id,
            "details": {
                "email": user_email,
                "full_name": user.get("full_name"),
                "final_version": final_version
            },
            "timestamp": datetime.now(timezone.utc)
        }
        await org_db.activity_logs.insert_one(activity_log)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"User {user_email} deleted successfully",
                "data": {
                    "user_id": user_id,
                    "final_version": final_version
                }
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error deleting user: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.put("/api/admin/users/{user_id}/role")
async def update_user_role(user_id: str, role_request: UpdateUserRoleRequest, request: Request):
    """Update user role (System Admin only)"""
    request_data = await api_logger.log_request(request)
    
    logger.info(f"🔄 Updating role for user {user_id} to {role_request.role}")
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        # Validate role
        if role_request.role not in ["manager", "employee"]:
            raise HTTPException(status_code=400, detail="Role must be 'manager' or 'employee'")
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        admin_db = db_manager.get_database("admin")
        
        # Find user
        user = await admin_db.users.find_one({
            "user_id": user_id,
            "isActive": True
        })
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Update role
        result = await admin_db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "role": role_request.role,
                    "updated_at": datetime.now(timezone.utc),
                    "version": user.get("version", 1) + 1
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update user role")
        
        logger.info(f"✅ Updated role for user {user_id}")
        
        # Log activity
        org_db = db_manager.get_org_database(user["organization_id"])
        activity_log = {
            "user_id": "system_admin",
            "action": "user_role_updated",
            "resource_type": "user",
            "resource_id": user_id,
            "details": {
                "old_role": user.get("role"),
                "new_role": role_request.role,
                "user_email": user.get("email")
            },
            "timestamp": datetime.now(timezone.utc)
        }
        await org_db.activity_logs.insert_one(activity_log)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"User role updated to '{role_request.role}'"
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error updating user role: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


# ================================
# REPORT MANAGEMENT APIs (with Activity Logging)
# ================================

class ReportCreateRequest(BaseModel):
    bank_code: str
    template_id: str
    property_address: str
    report_data: Dict[str, Any]

class ReportUpdateRequest(BaseModel):
    report_data: Dict[str, Any]
    status: Optional[str] = None

@app.post("/api/reports")
async def create_report(
    report_request: ReportCreateRequest, 
    request: Request,
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """Create a new report (Manager and Employee can create)"""
    request_data = await api_logger.log_request(request)
    
    try:
        # Check permission
        if not org_context.has_permission("reports", "create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions to create reports")
        
        from database.multi_db_manager import MultiDatabaseManager
        from services.reference_number_service import ReferenceNumberService
        import uuid
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Initialize reference number service
        ref_service = ReferenceNumberService(db_manager)
        
        # Generate unique reference number with retry logic for race conditions
        try:
            reference_number = await ref_service.generate_with_retry(
                org_context.org_short_name,
                max_retries=3
            )
            logger.info(f"📋 Generated reference number: {reference_number}")
        except Exception as ref_error:
            logger.error(f"❌ Failed to generate reference number: {ref_error}")
            await db_manager.disconnect()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate reference number. Please ensure organization has configured report reference initials. Error: {str(ref_error)}"
            )
        
        # Use org_short_name for database lookup
        org_db = db_manager.get_org_database(org_context.org_short_name)
        
        # Generate report ID
        report_id = f"rpt_{uuid.uuid4().hex[:12]}"
        
        # Create report document
        report = {
            "report_id": report_id,
            "reference_number": reference_number,  # NEW: Unique reference number
            "bank_code": report_request.bank_code,
            "template_id": report_request.template_id,
            "property_address": report_request.property_address,
            "report_data": report_request.report_data,
            "status": "draft",  # Initial status is always draft
            "created_by": org_context.user_id,
            "created_by_email": org_context.email,
            "organization_id": org_context.organization_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "submitted_at": None,
            "version": 1
        }
        
        # Insert report
        result = await org_db.reports.insert_one(report)
        
        logger.info(f"✅ Report created: {report_id} by {org_context.email}")
        
        # Log activity
        await log_activity(
            organization_id=org_context.organization_id,
            user_id=org_context.user_id,
            user_email=org_context.email,
            action="report_created",
            resource_type="report",
            resource_id=report_id,
            details={
                "reference_number": reference_number,  # NEW: Include reference number in activity log
                "bank_code": report_request.bank_code,
                "template_id": report_request.template_id,
                "property_address": report_request.property_address,
                "status": "draft"
            },
            ip_address=request.client.host
        )
        
        await db_manager.disconnect()
        
        report["_id"] = str(result.inserted_id)
        report["created_at"] = report["created_at"].isoformat()
        report["updated_at"] = report["updated_at"].isoformat()
        
        response = JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Report created successfully",
                "data": report
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error creating report: {str(e)}")
        import traceback
        traceback.print_exc()
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.put("/api/reports/{report_id}")
async def update_report(
    report_id: str, 
    update_request: ReportUpdateRequest, 
    request: Request,
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """Update a report (Manager and Employee can update)"""
    request_data = await api_logger.log_request(request)
    
    try:
        # Check permission
        if not org_context.has_permission("reports", "update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions to update reports")
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Use org_short_name for database lookup
        org_db = db_manager.get_org_database(org_context.org_short_name)
        
        # Find existing report (filter by org for security)
        report = await org_db.reports.find_one({
            "report_id": report_id
        })
        
        if not report:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
        
        # Prepare update data
        update_data = {
            "report_data": update_request.report_data,
            "updated_at": datetime.now(timezone.utc),
            "updated_by": org_context.user_id,
            "updated_by_email": org_context.email,
            "version": report.get("version", 1) + 1
        }
        
        # Only allow status update if explicitly provided
        if update_request.status:
            update_data["status"] = update_request.status
        
        # Update report
        result = await org_db.reports.update_one(
            {"report_id": report_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update report")
        
        logger.info(f"✅ Report updated: {report_id} by {org_context.email}")
        
        # Log activity
        await log_activity(
            organization_id=org_context.org_short_name,
            user_id=org_context.user_id,
            user_email=org_context.email,
            action="report_updated",
            resource_type="report",
            resource_id=report_id,
            details={
                "previous_status": report.get("status"),
                "new_status": update_request.status or report.get("status"),
                "version": update_data["version"]
            },
            ip_address=request.client.host
        )
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Report updated successfully"
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error updating report: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.post("/api/reports/{report_id}/submit")
async def submit_report(
    report_id: str, 
    request: Request,
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """Submit a report for review (Manager ONLY - Employees cannot submit)"""
    request_data = await api_logger.log_request(request)
    
    try:
        # Check permission - ONLY Manager can submit
        if not org_context.has_permission("reports", "submit"):
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions. Only Managers can submit reports."
            )
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Use org_short_name for database lookup
        org_db = db_manager.get_org_database(org_context.org_short_name)
        
        # Find existing report (auto-filtered by org database)
        report = await org_db.reports.find_one({
            "report_id": report_id
        })
        
        if not report:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
        
        # Check if already submitted
        if report.get("status") == "submitted":
            raise HTTPException(status_code=400, detail="Report already submitted")
        
        # Update report status to submitted
        result = await org_db.reports.update_one(
            {"report_id": report_id},
            {
                "$set": {
                    "status": "submitted",
                    "submitted_at": datetime.now(timezone.utc),
                    "submitted_by": org_context.user_id,
                    "submitted_by_email": org_context.email,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to submit report")
        
        logger.info(f"✅ Report submitted: {report_id} by Manager {org_context.email}")
        
        # Log activity - IMPORTANT: This shows Manager submitted the report
        await log_activity(
            organization_id=org_context.org_short_name,
            user_id=org_context.user_id,
            user_email=org_context.email,
            action="report_submitted",
            resource_type="report",
            resource_id=report_id,
            details={
                "previous_status": report.get("status", "draft"),
                "new_status": "submitted",
                "bank_code": report.get("bank_code"),
                "property_address": report.get("property_address"),
                "role": "manager"  # Explicitly log that a manager submitted this
            },
            ip_address=request.client.host
        )
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Report submitted successfully by Manager"
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error submitting report: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/reports/{report_id}/activity")
async def get_report_activity(report_id: str, request: Request):
    """Get activity logs for a specific report"""
    request_data = await api_logger.log_request(request)
    
    try:
        from utils.auth_middleware import get_organization_context
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Get auth token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        token = auth_header.replace("Bearer ", "")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Get organization context from token
        org_context = await get_organization_context(credentials)
        
        # Check permission - Only Manager can view activity logs
        if not org_context.has_permission("audit_logs", "read"):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions. Only Managers can view activity logs."
            )
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Get all activity logs for this report
        activities_cursor = org_db.activity_logs.find({
            "resource_type": "report",
            "resource_id": report_id
        }).sort("timestamp", -1)  # Most recent first
        
        activities = await activities_cursor.to_list(length=None)
        
        # Convert datetime objects
        for activity in activities:
            activity["_id"] = str(activity["_id"])
            if activity.get("timestamp"):
                activity["timestamp"] = activity["timestamp"].isoformat()
            if activity.get("created_at"):
                activity["created_at"] = activity["created_at"].isoformat()
        
        logger.info(f"📋 Retrieved {len(activities)} activity logs for report {report_id}")
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": activities,
                "total": len(activities)
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error fetching activity logs: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


# =============================================================================
# CUSTOM TEMPLATES API ENDPOINTS
# =============================================================================

@app.get("/api/custom-templates/banks")
async def get_custom_template_banks(request: Request):
    """
    Get list of banks available for custom templates
    """
    request_data = api_logger.log_request(request)
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        admin_db = db_manager.client["valuation_admin"]
        
        # Get template config
        template_config = await admin_db.bank_custom_template.find_one({"isActive": True})
        
        if not template_config:
            raise HTTPException(status_code=404, detail="Custom template configuration not found")
        
        # Format response
        bank_list = []
        for bank in template_config.get("banks", []):
            if bank.get("isActive", True):
                property_types = []
                for prop_type, config in bank.get("propertyTypes", {}).items():
                    if config.get("isActive", True):
                        property_types.append(prop_type)
                
                bank_list.append({
                    "bankCode": bank["bankCode"],
                    "bankName": bank.get("bankName", bank["bankCode"]),
                    "propertyTypes": property_types
                })
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": bank_list
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching custom template banks: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response

@app.get("/api/custom-templates/fields")
async def get_template_fields(
    bank_code: str,
    property_type: str,
    request: Request
):
    """
    Get field structure for a specific bank and property type.
    This is used when creating/editing custom templates.
    PUBLIC ENDPOINT - No authentication required (returns shared bank template structure)
    """
    request_data = api_logger.log_request(request)
    
    try:
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        admin_db = db_manager.client["valuation_admin"]
        
        # Get bank custom template config
        template_config = await admin_db.bank_custom_template.find_one({"isActive": True})
        
        if not template_config:
            raise HTTPException(status_code=404, detail="Custom template configuration not found")
        
        # Find bank in banks array (case insensitive)
        bank_config = None
        for bank in template_config.get("banks", []):
            if bank.get("bankCode", "").upper() == bank_code.upper() and bank.get("isActive", True):
                bank_config = bank
                break
        
        if not bank_config:
            raise HTTPException(status_code=404, detail=f"Bank {bank_code} not found or inactive")
        
        # Get fields for specific property type
        property_config = bank_config.get("propertyTypes", {}).get(property_type)
        if not property_config or not property_config.get("isActive", True):
            raise HTTPException(status_code=404, detail=f"Property type {property_type} not configured for {bank_code}")
        
        await db_manager.disconnect()
        
        # Filter only active fields
        active_fields = [field for field in property_config["fields"] if field.get("isActive", True)]
        
        response_content = {
            "success": True,
            "bankCode": bank_config.get("bankCode"),
            "bankName": bank_config.get("bankName", bank_code),
            "propertyType": property_type,
            "commonFields": [],
            "bankSpecificTabs": [{
                "tabId": "custom_fields",
                "tabName": "Custom Template Fields",
                "sortOrder": 1,
                "hasSections": False,
                "fields": active_fields,
                "sections": []
            }]
        }
        
        response = JSONResponse(
            status_code=200,
            content=response_content
        )
        
        api_logger.log_response(response, request_data)
        return response

    except Exception as e:
        logger.error(f"❌ Error fetching custom template banks: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/custom-templates")
async def list_custom_templates(
    request: Request,
    bankCode: Optional[str] = None,
    propertyType: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    List all custom templates for the organization.
    Optionally filter by bankCode and/or propertyType.
    """
    request_data = api_logger.log_request(request)
    
    try:
        # Verify authentication
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Build query filter
        query_filter = {"isActive": True}
        if bankCode:
            query_filter["bankCode"] = bankCode
        if propertyType:
            query_filter["propertyType"] = propertyType
        
        # Fetch templates (exclude fieldValues for list view)
        templates_cursor = org_db.custom_templates.find(
            query_filter,
            {
                "fieldValues": 0  # Exclude large fieldValues from list
            }
        ).sort("createdAt", -1)
        
        templates = await templates_cursor.to_list(length=None)
        
        # Convert ObjectId and datetime
        for template in templates:
            template["_id"] = str(template["_id"])
            if template.get("createdAt"):
                template["createdAt"] = template["createdAt"].isoformat()
            if template.get("updatedAt"):
                template["updatedAt"] = template["updatedAt"].isoformat()
        
        # Count templates per bank+propertyType if filtering
        count_info = {}
        if bankCode and propertyType:
            count = await org_db.custom_templates.count_documents({
                "bankCode": bankCode,
                "propertyType": propertyType,
                "isActive": True
            })
            count_info = {
                "current": count,
                "max": 3,
                "canCreateMore": count < 3
            }
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": templates,
                "total": len(templates),
                "countInfo": count_info
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error listing custom templates: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/custom-templates/{template_id}")
async def get_custom_template(
    template_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get a specific custom template with full fieldValues.
    """
    request_data = api_logger.log_request(request)
    
    try:
        # Verify authentication
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Fetch template
        template = await org_db.custom_templates.find_one({
            "_id": ObjectId(template_id),
            "isActive": True
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Convert ObjectId and datetime
        template["_id"] = str(template["_id"])
        if template.get("createdAt"):
            template["createdAt"] = template["createdAt"].isoformat()
        if template.get("updatedAt"):
            template["updatedAt"] = template["updatedAt"].isoformat()
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": template
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error fetching custom template: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.post("/api/custom-templates")
async def create_custom_template(
    template_data: CreateCustomTemplateRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a new custom template.
    Only Manager and Admin can create templates.
    Max 3 templates per bankCode+propertyType combination.
    """
    request_data = api_logger.log_request(request)
    
    try:
        # Verify authentication and role
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        # Debug logging
        logger.info(f"🔍 Template creation attempt - User: {org_context.email}, Org: {org_context.org_short_name}")
        logger.info(f"🔍 Roles: {org_context.roles}, is_manager: {org_context.is_manager}, is_system_admin: {org_context.is_system_admin}")
        
        # Check if user is Manager or Admin (case-insensitive)
        user_roles = [role.lower() for role in org_context.roles]
        if not any(role in ["manager", "admin", "system_admin"] for role in user_roles):
            logger.error(f"❌ Permission denied - User roles: {org_context.roles}, Required: manager/admin/system_admin")
            raise HTTPException(
                status_code=403,
                detail="Only Manager or Admin can create custom templates"
            )
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Check template count limit (max 3 per bank+propertyType)
        existing_count = await org_db.custom_templates.count_documents({
            "bankCode": template_data.bankCode,
            "propertyType": template_data.propertyType,
            "isActive": True
        })
        
        if existing_count >= 3:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum 3 templates allowed for {template_data.bankCode} - {template_data.propertyType}"
            )
        
        # Get bank name from shared resources
        shared_db = db_manager.get_shared_database()
        bank = await shared_db.banks.find_one({"bankCode": template_data.bankCode})
        bank_name = bank.get("bankName", "") if bank else ""
        
        # Create template document
        template_doc = {
            "templateName": template_data.templateName,
            "description": template_data.description or "",
            "bankCode": template_data.bankCode,
            "bankName": bank_name,
            "propertyType": template_data.propertyType,
            "fieldValues": template_data.fieldValues,
            "createdBy": org_context.user_id,
            "createdByName": org_context.email,  # Use email since user_name may not exist
            "organizationId": org_context.organization_id,
            "isActive": True,
            "version": 1,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        
        # Insert template
        result = await org_db.custom_templates.insert_one(template_doc)
        template_doc["_id"] = str(result.inserted_id)
        
        # Log activity
        await log_activity(
            organization_id=org_context.organization_id,
            user_id=org_context.user_id,
            user_email=org_context.email,  # Use email property
            action="custom_template_created",
            resource_type="custom_template",
            resource_id=str(result.inserted_id),
            details={
                "templateName": template_data.templateName,
                "bankCode": template_data.bankCode,
                "propertyType": template_data.propertyType
            },
            ip_address=request.client.host if request.client else None
        )
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Custom template created: {template_data.templateName}")
        
        response = JSONResponse(
            status_code=201,
            content={
                "success": True,
                "data": {
                    "_id": template_doc["_id"],
                    "templateName": template_doc["templateName"],
                    "bankCode": template_doc["bankCode"],
                    "propertyType": template_doc["propertyType"]
                },
                "message": "Custom template created successfully"
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error creating custom template: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.put("/api/custom-templates/{template_id}")
async def update_custom_template(
    template_id: str,
    template_data: UpdateCustomTemplateRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update an existing custom template.
    Only Manager and Admin can update templates.
    """
    request_data = api_logger.log_request(request)
    
    try:
        # Verify authentication and role
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        # Check if user is Manager or Admin (case-insensitive)
        user_roles = [role.lower() for role in org_context.roles]
        if not any(role in ["manager", "admin", "system_admin"] for role in user_roles):
            logger.error(f"❌ Permission denied - User roles: {org_context.roles}, Required: manager/admin/system_admin")
            raise HTTPException(
                status_code=403,
                detail="Only Manager or Admin can update custom templates"
            )
        
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Check if template exists
        existing_template = await org_db.custom_templates.find_one({
            "_id": ObjectId(template_id),
            "isActive": True
        })
        
        if not existing_template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Build update document
        update_doc = {"updatedAt": datetime.now(timezone.utc)}
        if template_data.templateName is not None:
            update_doc["templateName"] = template_data.templateName
        if template_data.description is not None:
            update_doc["description"] = template_data.description
        if template_data.fieldValues is not None:
            update_doc["fieldValues"] = template_data.fieldValues
        
        # Update template
        await org_db.custom_templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_doc}
        )
        
        # Log activity
        await log_activity(
            organization_id=org_context.organization_id,
            user_id=org_context.user_id,
            user_email=org_context.email,  # Use email property
            action="custom_template_updated",
            resource_type="custom_template",
            resource_id=template_id,
            details={
                "templateName": template_data.templateName or existing_template.get("templateName"),
                "bankCode": existing_template.get("bankCode"),
                "propertyType": existing_template.get("propertyType")
            },
            ip_address=request.client.host if request.client else None
        )
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Custom template updated: {template_id}")
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Custom template updated successfully"
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error updating custom template: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.delete("/api/custom-templates/{template_id}")
async def delete_custom_template(
    template_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete a custom template (soft delete).
    Only Manager and Admin can delete templates.
    """
    request_data = api_logger.log_request(request)
    
    try:
        # Verify authentication and role
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        # Check if user is Manager or Admin (case-insensitive)
        user_roles = [role.lower() for role in org_context.roles]
        if not any(role in ["manager", "admin", "system_admin"] for role in user_roles):
            logger.error(f"❌ Permission denied - User roles: {org_context.roles}, Required: manager/admin/system_admin")
            raise HTTPException(
                status_code=403,
                detail="Only Manager or Admin can delete custom templates"
            )
        
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Check if template exists
        existing_template = await org_db.custom_templates.find_one({
            "_id": ObjectId(template_id),
            "isActive": True
        })
        
        if not existing_template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Soft delete
        await org_db.custom_templates.update_one(
            {"_id": ObjectId(template_id)},
            {
                "$set": {
                    "isActive": False,
                    "deletedAt": datetime.now(timezone.utc),
                    "deletedBy": org_context.user_id
                }
            }
        )
        
        # Log activity
        await log_activity(
            organization_id=org_context.organization_id,
            user_id=org_context.user_id,
            user_email=org_context.email,  # Use email property
            action="custom_template_deleted",
            resource_type="custom_template",
            resource_id=template_id,
            details={
                "templateName": existing_template.get("templateName"),
                "bankCode": existing_template.get("bankCode"),
                "propertyType": existing_template.get("propertyType")
            },
            ip_address=request.client.host if request.client else None
        )
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Custom template deleted: {template_id}")
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Custom template deleted successfully"
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error deleting custom template: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.post("/api/custom-templates/{template_id}/clone")
async def clone_custom_template(
    template_id: str,
    clone_data: CloneCustomTemplateRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Clone an existing custom template with a new name.
    Only Manager and Admin can clone templates.
    Validates max 3 templates limit.
    """
    request_data = api_logger.log_request(request)
    
    try:
        # Verify authentication and role
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        # Check if user is Manager or Admin (case-insensitive)
        user_roles = [role.lower() for role in org_context.roles]
        if not any(role in ["manager", "admin", "system_admin"] for role in user_roles):
            logger.error(f"❌ Permission denied - User roles: {org_context.roles}, Required: manager/admin/system_admin")
            raise HTTPException(
                status_code=403,
                detail="Only Manager or Admin can clone custom templates"
            )
        
        from database.multi_db_manager import MultiDatabaseManager
        from bson import ObjectId
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Get original template
        original_template = await org_db.custom_templates.find_one({
            "_id": ObjectId(template_id),
            "isActive": True
        })
        
        if not original_template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check template count limit
        existing_count = await org_db.custom_templates.count_documents({
            "bankCode": original_template["bankCode"],
            "propertyType": original_template["propertyType"],
            "isActive": True
        })
        
        if existing_count >= 3:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum 3 templates allowed for {original_template['bankCode']} - {original_template['propertyType']}"
            )
        
        # Create cloned template
        cloned_template = {
            "templateName": clone_data.newTemplateName,
            "description": original_template.get("description", "") + " (Cloned)",
            "bankCode": original_template["bankCode"],
            "bankName": original_template.get("bankName", ""),
            "propertyType": original_template["propertyType"],
            "fieldValues": original_template["fieldValues"],  # Copy all field values
            "createdBy": org_context.user_id,
            "createdByName": org_context.email,  # Use email since user_name may not exist
            "organizationId": org_context.organization_id,
            "isActive": True,
            "version": 1,
            "clonedFrom": template_id,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        
        # Insert cloned template
        result = await org_db.custom_templates.insert_one(cloned_template)
        
        # Log activity
        await log_activity(
            organization_id=org_context.organization_id,
            user_id=org_context.user_id,
            user_email=org_context.email,  # Use email property
            action="custom_template_cloned",
            resource_type="custom_template",
            resource_id=str(result.inserted_id),
            details={
                "newTemplateName": clone_data.newTemplateName,
                "originalTemplateId": template_id,
                "originalTemplateName": original_template.get("templateName"),
                "bankCode": original_template["bankCode"],
                "propertyType": original_template["propertyType"]
            },
            ip_address=request.client.host if request.client else None
        )
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Custom template cloned: {clone_data.newTemplateName}")
        
        response = JSONResponse(
            status_code=201,
            content={
                "success": True,
                "data": {
                    "_id": str(result.inserted_id),
                    "templateName": clone_data.newTemplateName,
                    "bankCode": original_template["bankCode"],
                    "propertyType": original_template["propertyType"]
                },
                "message": "Custom template cloned successfully"
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error cloning custom template: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.post("/api/organizations/{org_short_name}/templates/from-report")
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
    request_data = await api_logger.log_request(request)
    
    try:
        # Verify authentication and role
        from utils.auth_middleware import get_organization_context
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
        
        from database.multi_db_manager import MultiDatabaseManager
        
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
        
        logger.info(f"🔍 Processing {len(template_data.fieldValues)} total field values from request")
        
        for field_id, value in template_data.fieldValues.items():
            # Skip common fields
            if field_id in common_field_ids:
                logger.debug(f"  ⏭️  Skipping common field: {field_id}")
                continue
            
            # Skip empty values
            if value is None or value == "" or value == [] or value == {}:
                logger.debug(f"  ⏭️  Skipping empty field: {field_id}")
                continue
            
            # Skip empty strings after stripping whitespace
            if isinstance(value, str) and not value.strip():
                logger.debug(f"  ⏭️  Skipping whitespace-only field: {field_id}")
                continue
            
            logger.info(f"  ✅ Including bank-specific field: {field_id} = {str(value)[:50]}...")
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
            "createdByName": org_context.email,  # Use email as name (no user_name in org_context)
            "modifiedBy": org_context.user_id,
            "modifiedByName": org_context.email,  # Use email as name (no user_name in org_context)
            "organizationId": target_org_id,  # Use target org ID (supports system admin)
            "isActive": True,
            "version": 1,
            "createdFrom": "report_form",  # Track that this was created from report
            "createdAt": datetime.now(timezone.utc),
            "modifiedAt": datetime.now(timezone.utc)
        }
        
        # Insert template
        result = await org_db.custom_templates.insert_one(template_doc)
        template_id = str(result.inserted_id)
        
        # Log activity (log to the target organization's activity log)
        await log_activity(
            organization_id=target_org_id,  # Use target org ID for activity log
            user_id=org_context.user_id,
            user_email=org_context.email,  # Use email property
            action="custom_template_created_from_report",
            resource_type="custom_template",
            resource_id=template_id,
            details={
                "templateName": template_data.templateName,
                "bankCode": template_data.bankCode,
                "propertyType": property_type,
                "templateCode": template_data.templateCode,
                "fieldCount": len(filtered_field_values),
                "createdBySystemAdmin": org_context.is_system_admin  # Track if created by system admin
            },
            ip_address=request.client.host if request.client else None
        )
        
        await db_manager.disconnect()
        
        logger.info(f"✅ Custom template created from report: {template_data.templateName} with {len(filtered_field_values)} fields")
        
        response = JSONResponse(
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
        
        api_logger.log_response(response, request_data)
        return response
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error creating custom template from report: {str(e)}")
        logger.exception(e)  # Log full traceback
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


# ================================
# DASHBOARD COMPONENT APIs
# ================================

@app.get("/api/dashboard/pending-reports")
async def get_pending_reports(
    request: Request,
    limit: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get pending reports for dashboard component"""
    request_data = await api_logger.log_request(request)
    
    try:
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Get reports with status 'draft' or 'in_progress' (pending completion)
        pending_reports_cursor = org_db.reports.find({
            "status": {"$in": ["draft", "in_progress"]}
        }).sort("updated_at", -1).limit(limit)
        
        pending_reports = await pending_reports_cursor.to_list(length=None)
        
        # Format reports for dashboard display
        formatted_reports = []
        for report in pending_reports:
            formatted_report = {
                "_id": str(report["_id"]),
                "report_id": report.get("report_id"),
                "property_address": report.get("property_address", "N/A"),
                "bank_code": report.get("bank_code", ""),
                "template_id": report.get("template_id", ""),
                "status": report.get("status", "draft"),
                "created_by_email": report.get("created_by_email", ""),
                "created_at": report.get("created_at").isoformat() if report.get("created_at") else None,
                "updated_at": report.get("updated_at").isoformat() if report.get("updated_at") else None
            }
            formatted_reports.append(formatted_report)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": formatted_reports,
                "total": len(formatted_reports)
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching pending reports: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/dashboard/created-reports")
async def get_created_reports(
    request: Request,
    limit: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get recently created reports for dashboard component"""
    request_data = await api_logger.log_request(request)
    
    try:
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Get recently created reports (all statuses)
        created_reports_cursor = org_db.reports.find({}).sort("created_at", -1).limit(limit)
        
        created_reports = await created_reports_cursor.to_list(length=None)
        
        # Format reports for dashboard display
        formatted_reports = []
        for report in created_reports:
            formatted_report = {
                "_id": str(report["_id"]),
                "report_id": report.get("report_id"),
                "property_address": report.get("property_address", "N/A"),
                "bank_code": report.get("bank_code", ""),
                "template_id": report.get("template_id", ""),
                "status": report.get("status", "draft"),
                "created_by_email": report.get("created_by_email", ""),
                "created_at": report.get("created_at").isoformat() if report.get("created_at") else None,
                "updated_at": report.get("updated_at").isoformat() if report.get("updated_at") else None
            }
            formatted_reports.append(formatted_report)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": formatted_reports,
                "total": len(formatted_reports)
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching created reports: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/dashboard/banks")
async def get_dashboard_banks(
    request: Request,
    limit: int = 8,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get banks summary for dashboard component"""
    request_data = await api_logger.log_request(request)
    
    try:
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        # Get banks from shared resources
        shared_db = db_manager.get_database("shared")
        
        # Fetch active banks with template counts
        banks_cursor = shared_db.banks.find({"isActive": True}).limit(limit)
        banks = await banks_cursor.to_list(length=None)
        
        # Format banks for dashboard display
        formatted_banks = []
        for bank in banks:
            bank_code = bank.get("bankCode")
            
            # Count templates for this bank
            template_count = await shared_db.bank_templates.count_documents({
                "bankCode": bank_code,
                "isActive": True
            })
            
            formatted_bank = {
                "_id": str(bank["_id"]),
                "bankCode": bank_code,
                "bankName": bank.get("bankName", ""),
                "description": bank.get("description", ""),
                "template_count": template_count,
                "isActive": bank.get("isActive", True)
            }
            formatted_banks.append(formatted_bank)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": formatted_banks,
                "total": len(formatted_banks)
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching dashboard banks: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/dashboard/recent-activities")
async def get_recent_activities(
    request: Request,
    limit: int = 10,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get recent activities for dashboard component"""
    request_data = await api_logger.log_request(request)
    
    try:
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Get recent activities from activity logs
        activities_cursor = org_db.activity_logs.find({}).sort("timestamp", -1).limit(limit)
        
        activities = await activities_cursor.to_list(length=None)
        
        # Format activities for dashboard display
        formatted_activities = []
        for activity in activities:
            formatted_activity = {
                "_id": str(activity["_id"]),
                "user_email": activity.get("user_email", ""),
                "action": activity.get("action", ""),
                "resource_type": activity.get("resource_type", ""),
                "resource_id": activity.get("resource_id", ""),
                "details": activity.get("details", {}),
                "timestamp": activity.get("timestamp").isoformat() if activity.get("timestamp") else None,
                "ip_address": activity.get("ip_address", "")
            }
            formatted_activities.append(formatted_activity)
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": formatted_activities,
                "total": len(formatted_activities)
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching recent activities: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


@app.get("/api/dashboard/stats")
async def get_dashboard_stats(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get dashboard statistics summary"""
    request_data = await api_logger.log_request(request)
    
    try:
        from utils.auth_middleware import get_organization_context
        org_context = await get_organization_context(credentials)
        
        from database.multi_db_manager import MultiDatabaseManager
        
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        org_db = db_manager.get_org_database(org_context.organization_id)
        
        # Get various counts for dashboard stats
        stats = {}
        
        # Reports statistics
        stats["total_reports"] = await org_db.reports.count_documents({})
        stats["pending_reports"] = await org_db.reports.count_documents({
            "status": {"$in": ["draft", "in_progress"]}
        })
        stats["submitted_reports"] = await org_db.reports.count_documents({
            "status": "submitted"
        })
        
        # Custom templates count
        stats["custom_templates"] = await org_db.custom_templates.count_documents({
            "isActive": True
        })
        
        # Recent activity count (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        stats["recent_activities"] = await org_db.activity_logs.count_documents({
            "timestamp": {"$gte": week_ago}
        })
        
        # User count (if users collection exists)
        try:
            stats["total_users"] = await org_db.users.count_documents({"is_active": True})
        except:
            stats["total_users"] = 0
        
        await db_manager.disconnect()
        
        response = JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": stats
            }
        )
        
        api_logger.log_response(response, request_data)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching dashboard stats: {str(e)}")
        error_response = JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
        api_logger.log_response(error_response, request_data)
        return error_response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
