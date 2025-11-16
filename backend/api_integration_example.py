"""
FastAPI Integration Example for Organization Middleware
Shows how to integrate JWT authentication and organization filtering with API endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from database.multi_db_manager import MultiDatabaseManager
from utils.auth_middleware import (
    OrganizationContext, CognitoJWTValidator, 
    create_organization_middleware, require_role
)
from utils.organization_db_service import OrganizationDatabaseService, create_org_db_service

# Create FastAPI app
app = FastAPI(
    title="Valuation App API",
    description="Multi-tenant valuation application with organization-based access control",
    version="1.0.0"
)

# Global instances
db_manager = None
jwt_validator = None
org_middleware = None
org_db_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and middleware on startup"""
    global db_manager, jwt_validator, org_middleware, org_db_service
    
    # Initialize database manager
    db_manager = MultiDatabaseManager()
    await db_manager.connect()
    
    # Initialize JWT validator
    jwt_validator = CognitoJWTValidator()
    
    # Initialize organization middleware
    org_middleware = create_organization_middleware(db_manager)
    
    # Initialize organization database service
    org_db_service = create_org_db_service(db_manager, org_middleware)
    
    print("🚀 API server startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    global db_manager
    if db_manager:
        await db_manager.disconnect()
    print("🛑 API server shutdown complete!")

# Dependency for extracting organization context from JWT token
async def get_organization_context(request: Request) -> OrganizationContext:
    """
    Extract and validate organization context from JWT token
    Use as a FastAPI dependency for protected endpoints
    """
    # Extract token from Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Validate JWT token
        jwt_claims = await jwt_validator.validate_token(token)
        
        # Create organization context
        org_context = OrganizationContext(jwt_claims)
        
        return org_context
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# API Endpoints with organization-based access control

@app.get("/api/health")
async def health_check():
    """Public health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/organization", response_model=Dict[str, Any])
async def get_organization_info(
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Get current user's organization information
    Accessible by: all authenticated users
    """
    try:
        org_info = await org_db_service.get_organization_by_id(
            org_context.organization_id, 
            org_context
        )
        
        if not org_info:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return {
            "organization_id": org_info["_id"],
            "name": org_info["name"],
            "user_email": org_context.email,
            "user_roles": org_context.roles,
            "is_active": org_info.get("is_active", True)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get organization info: {str(e)}")

@app.get("/api/users", response_model=List[Dict[str, Any]])
@require_role("system_admin", "manager")
async def get_organization_users(
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Get all users in the organization
    Accessible by: system_admin, manager
    """
    try:
        users = await org_db_service.get_organization_users(org_context)
        
        # Remove sensitive information
        safe_users = []
        for user in users:
            safe_user = {
                "user_id": user["_id"],
                "email": user["email"],
                "roles": user["roles"],
                "is_active": user.get("is_active", True),
                "created_at": user.get("created_at")
            }
            safe_users.append(safe_user)
        
        return safe_users
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@app.post("/api/users", response_model=Dict[str, str])
@require_role("system_admin", "manager")
async def create_organization_user(
    user_data: Dict[str, Any],
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Create a new user in the organization
    Accessible by: system_admin, manager
    """
    try:
        # Validate required fields
        required_fields = ["email", "roles"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create user document
        new_user = {
            "organization_id": org_context.organization_id,
            "email": user_data["email"],
            "roles": user_data["roles"],
            "is_active": user_data.get("is_active", True),
            "created_by": org_context.user_id,
            "created_at": datetime.utcnow()
        }
        
        user_id = await org_db_service.create_organization_user(new_user, org_context)
        
        return {"user_id": str(user_id), "message": "User created successfully"}
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.get("/api/reports", response_model=List[Dict[str, Any]])
async def get_organization_reports(
    limit: int = 10,
    offset: int = 0,
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Get reports for the organization
    Accessible by: all authenticated users (filtered by organization)
    """
    try:
        reports = await org_db_service.get_organization_reports(
            org_context, 
            limit=limit, 
            offset=offset
        )
        
        return reports
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reports: {str(e)}")

@app.post("/api/reports", response_model=Dict[str, str])
async def create_report(
    report_data: Dict[str, Any],
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Create a new report
    Accessible by: all authenticated users
    """
    try:
        # Add organization context to report
        new_report = {
            **report_data,
            "organization_id": org_context.organization_id,
            "created_by": org_context.user_id,
            "created_at": datetime.utcnow()
        }
        
        report_id = await org_db_service.create_organization_report(new_report, org_context)
        
        return {"report_id": str(report_id), "message": "Report created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

@app.delete("/api/reports/{report_id}")
@require_role("system_admin", "manager")
async def delete_report(
    report_id: str,
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Delete a report
    Accessible by: system_admin, manager
    """
    try:
        success = await org_db_service.delete_organization_report(report_id, org_context)
        
        if not success:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {"message": "Report deleted successfully"}
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

@app.get("/api/audit-logs", response_model=List[Dict[str, Any]])
@require_role("system_admin", "manager")
async def get_audit_logs(
    limit: int = 50,
    offset: int = 0,
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Get audit logs for the organization
    Accessible by: system_admin, manager
    """
    try:
        logs = await org_db_service.get_organization_audit_logs(
            org_context, 
            limit=limit, 
            offset=offset
        )
        
        return logs
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")

@app.get("/api/system/organizations", response_model=List[Dict[str, Any]])
@require_role("system_admin")
async def get_all_organizations(
    org_context: OrganizationContext = Depends(get_organization_context)
):
    """
    Get all organizations (system admin only)
    Accessible by: system_admin only
    """
    try:
        organizations = await org_db_service.get_all_organizations(org_context)
        
        return organizations
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get organizations: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    return {
        "error": True,
        "status_code": exc.status_code,
        "message": exc.detail,
        "timestamp": datetime.utcnow()
    }

# Development endpoint for creating test tokens
if __name__ == "__main__":
    from utils.auth_middleware import create_dev_token
    
    print("\n🧪 Development Test Tokens:")
    print(f"Manager: Bearer {create_dev_token('manager@demo.com', 'demo_org_001', 'manager')}")
    print(f"Employee: Bearer {create_dev_token('employee@demo.com', 'demo_org_001', 'employee')}")
    print(f"System Admin: Bearer {create_dev_token('admin@system.com', 'system_admin', 'system_admin')}")
    
    print("\n📋 Example API Usage:")
    print("curl -H 'Authorization: Bearer dev_manager_demo.com_demo_org_001_manager' http://localhost:8000/api/organization")
    print("curl -H 'Authorization: Bearer dev_employee_demo.com_demo_org_001_employee' http://localhost:8000/api/reports")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)