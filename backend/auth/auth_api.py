"""
Authentication API Endpoints
Handles login, registration, user management with AWS Cognito integration
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from .cognito_service import cognito_service
from .enhanced_auth_middleware import get_security_context, require_permission, require_role
from .rbac_models import Permission, UserRole, SecurityContext
from database.multi_db_manager import MultiDatabaseManager

logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_id: str
    role: str
    phone: Optional[str] = None

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UpdateUserRoleRequest(BaseModel):
    role: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@auth_router.post("/login")
async def login(login_request: LoginRequest, request: Request):
    """Authenticate user with AWS Cognito"""
    
    logger.info(f"🔐 Login attempt for: {login_request.email}")
    
    try:
        # Authenticate with Cognito
        auth_result = await cognito_service.authenticate_user(
            login_request.email, 
            login_request.password
        )
        
        # Get user info from MongoDB for additional details
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            # Find user in organization database
            user_org_id = auth_result["user_info"]["organization_id"]
            org_db = db_manager.get_org_database(user_org_id)
            
            user_profile = await org_db.users.find_one({
                "email": login_request.email,
                "is_active": True
            })
            
            if user_profile:
                # Update last login
                await org_db.users.update_one(
                    {"email": login_request.email},
                    {
                        "$set": {
                            "last_login": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                # Merge Cognito and MongoDB user data
                auth_result["user_info"].update({
                    "profile": user_profile,
                    "preferences": user_profile.get("preferences", {}),
                    "settings": user_profile.get("settings", {})
                })
        
        finally:
            await db_manager.disconnect()
        
        logger.info(f"✅ Login successful: {login_request.email}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Login successful",
                "data": {
                    "access_token": auth_result["access_token"],
                    "id_token": auth_result["id_token"],
                    "refresh_token": auth_result["refresh_token"],
                    "expires_in": auth_result["expires_in"],
                    "user": auth_result["user_info"]
                }
            }
        )
        
    except HTTPException as e:
        logger.warning(f"❌ Login failed for {login_request.email}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@auth_router.post("/register")
@require_permission(Permission.USER_CREATE)
async def register_user(
    user_request: RegisterUserRequest,
    request: Request,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Register new user (Admin/Manager only)"""
    
    logger.info(f"👤 User registration request: {user_request.email}")
    
    try:
        # Validate role
        valid_roles = ["admin", "manager", "employee"]
        if user_request.role not in valid_roles:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid role. Must be one of: {valid_roles}"
            )
        
        # Validate organization access
        if not security_context.is_manager_or_admin():
            raise HTTPException(
                status_code=403,
                detail="Only managers and admins can register users"
            )
        
        # Create user in Cognito
        cognito_result = await cognito_service.create_user(
            email=user_request.email,
            password=user_request.password,
            full_name=user_request.full_name,
            organization_id=user_request.organization_id,
            role=user_request.role,
            phone=user_request.phone
        )
        
        # Create user profile in MongoDB
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            org_db = db_manager.get_org_database(user_request.organization_id)
            
            user_profile = {
                "user_id": cognito_result["user_id"],
                "email": user_request.email,
                "full_name": user_request.full_name,
                "phone": user_request.phone or "",
                "organization_id": user_request.organization_id,
                "role": user_request.role,
                "is_active": True,
                "created_by": security_context.user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_login": None,
                "preferences": {
                    "theme": "light",
                    "language": "en",
                    "notifications": True
                },
                "settings": {
                    "dashboard_layout": "grid",
                    "default_bank": None,
                    "timezone": "UTC"
                }
            }
            
            await org_db.users.insert_one(user_profile)
            
            # Log activity
            activity_log = {
                "user_id": security_context.user_id,
                "action": "user_created",
                "resource_type": "user",
                "resource_id": cognito_result["user_id"],
                "details": {
                    "email": user_request.email,
                    "role": user_request.role,
                    "full_name": user_request.full_name
                },
                "timestamp": datetime.now(timezone.utc),
                "ip_address": request.client.host if request.client else None
            }
            await org_db.activity_logs.insert_one(activity_log)
        
        finally:
            await db_manager.disconnect()
        
        logger.info(f"✅ User registered: {user_request.email}")
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "User registered successfully",
                "data": {
                    "user_id": cognito_result["user_id"],
                    "email": user_request.email,
                    "role": user_request.role,
                    "status": cognito_result["status"]
                }
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ User registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="User registration failed")

@auth_router.get("/me")
async def get_current_user(
    security_context: SecurityContext = Depends(get_security_context)
):
    """Get current user information"""
    
    try:
        # Get user info from Cognito
        user_info = await cognito_service.get_user_info(security_context.email)
        
        # Get additional profile data from MongoDB
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            org_db = db_manager.get_org_database(security_context.organization_id)
            user_profile = await org_db.users.find_one({
                "email": security_context.email,
                "is_active": True
            })
            
            if user_profile:
                user_info.update({
                    "profile": user_profile,
                    "preferences": user_profile.get("preferences", {}),
                    "settings": user_profile.get("settings", {})
                })
        
        finally:
            await db_manager.disconnect()
        
        # Add security context information
        user_info.update({
            "security_context": security_context.to_dict(),
            "permissions": {
                "can_submit_reports": security_context.can_submit_reports(),
                "can_manage_users": security_context.rbac.can_manage_users(security_context.roles),
                "is_manager": security_context.is_manager_or_admin(),
                "is_admin": security_context.rbac.is_admin(security_context.roles)
            }
        })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": user_info
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting user info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

@auth_router.put("/me")
async def update_current_user(
    update_request: UpdateUserRequest,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Update current user profile"""
    
    try:
        # Update in Cognito if needed
        if update_request.full_name or update_request.phone:
            # Note: Cognito updates would go here
            pass
        
        # Update in MongoDB
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            org_db = db_manager.get_org_database(security_context.organization_id)
            
            update_data = {"updated_at": datetime.now(timezone.utc)}
            if update_request.full_name:
                update_data["full_name"] = update_request.full_name
            if update_request.phone:
                update_data["phone"] = update_request.phone
            
            result = await org_db.users.update_one(
                {"email": security_context.email},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
        
        finally:
            await db_manager.disconnect()
        
        logger.info(f"✅ User profile updated: {security_context.email}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Profile updated successfully"
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Profile update failed")

@auth_router.put("/users/{user_id}/role")
@require_permission(Permission.USER_ROLE_UPDATE)
async def update_user_role(
    user_id: str,
    role_request: UpdateUserRoleRequest,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Update user role (Admin only)"""
    
    logger.info(f"🔄 Role update request for user {user_id} to {role_request.role}")
    
    try:
        # Validate role
        valid_roles = ["admin", "manager", "employee"]
        if role_request.role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {valid_roles}"
            )
        
        # Get user email from MongoDB
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            org_db = db_manager.get_org_database(security_context.organization_id)
            user = await org_db.users.find_one({"user_id": user_id})
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_email = user["email"]
            
            # Update role in Cognito
            success = await cognito_service.update_user_role(user_email, role_request.role)
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update role in Cognito")
            
            # Update role in MongoDB
            await org_db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "role": role_request.role,
                        "updated_at": datetime.now(timezone.utc),
                        "updated_by": security_context.user_id
                    }
                }
            )
            
            # Log activity
            activity_log = {
                "user_id": security_context.user_id,
                "action": "user_role_updated",
                "resource_type": "user",
                "resource_id": user_id,
                "details": {
                    "email": user_email,
                    "old_role": user.get("role"),
                    "new_role": role_request.role
                },
                "timestamp": datetime.now(timezone.utc)
            }
            await org_db.activity_logs.insert_one(activity_log)
        
        finally:
            await db_manager.disconnect()
        
        logger.info(f"✅ User role updated: {user_id} -> {role_request.role}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"User role updated to {role_request.role}"
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Role update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Role update failed")

@auth_router.post("/users/{user_id}/disable")
@require_permission(Permission.USER_UPDATE)
async def disable_user(
    user_id: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Disable user account (Admin/Manager only)"""
    
    logger.info(f"🚫 Disabling user: {user_id}")
    
    try:
        # Get user from MongoDB
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            org_db = db_manager.get_org_database(security_context.organization_id)
            user = await org_db.users.find_one({"user_id": user_id})
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_email = user["email"]
            
            # Disable in Cognito
            success = await cognito_service.disable_user(user_email)
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to disable user in Cognito")
            
            # Update in MongoDB
            await org_db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_active": False,
                        "disabled_at": datetime.now(timezone.utc),
                        "disabled_by": security_context.user_id,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Log activity
            activity_log = {
                "user_id": security_context.user_id,
                "action": "user_disabled",
                "resource_type": "user",
                "resource_id": user_id,
                "details": {"email": user_email},
                "timestamp": datetime.now(timezone.utc)
            }
            await org_db.activity_logs.insert_one(activity_log)
        
        finally:
            await db_manager.disconnect()
        
        logger.info(f"✅ User disabled: {user_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User disabled successfully"
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ User disable error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disable user")

@auth_router.post("/users/{user_id}/enable")
@require_permission(Permission.USER_UPDATE)
async def enable_user(
    user_id: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Enable user account (Admin/Manager only)"""
    
    logger.info(f"✅ Enabling user: {user_id}")
    
    try:
        # Get user from MongoDB
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            org_db = db_manager.get_org_database(security_context.organization_id)
            user = await org_db.users.find_one({"user_id": user_id})
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_email = user["email"]
            
            # Enable in Cognito
            success = await cognito_service.enable_user(user_email)
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to enable user in Cognito")
            
            # Update in MongoDB
            await org_db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_active": True,
                        "enabled_at": datetime.now(timezone.utc),
                        "enabled_by": security_context.user_id,
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$unset": {
                        "disabled_at": "",
                        "disabled_by": ""
                    }
                }
            )
            
            # Log activity
            activity_log = {
                "user_id": security_context.user_id,
                "action": "user_enabled",
                "resource_type": "user",
                "resource_id": user_id,
                "details": {"email": user_email},
                "timestamp": datetime.now(timezone.utc)
            }
            await org_db.activity_logs.insert_one(activity_log)
        
        finally:
            await db_manager.disconnect()
        
        logger.info(f"✅ User enabled: {user_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User enabled successfully"
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ User enable error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enable user")

@auth_router.post("/logout")
async def logout(security_context: SecurityContext = Depends(get_security_context)):
    """Logout user (invalidate session)"""
    
    logger.info(f"🔓 User logout: {security_context.email}")
    
    try:
        # Log logout activity
        db_manager = MultiDatabaseManager()
        await db_manager.connect()
        
        try:
            org_db = db_manager.get_org_database(security_context.organization_id)
            
            activity_log = {
                "user_id": security_context.user_id,
                "action": "user_logout",
                "resource_type": "session",
                "resource_id": security_context.user_id,
                "details": {"email": security_context.email},
                "timestamp": datetime.now(timezone.utc)
            }
            await org_db.activity_logs.insert_one(activity_log)
        
        finally:
            await db_manager.disconnect()
        
        # Note: In a full implementation, you would invalidate the JWT token
        # This could be done by maintaining a blacklist or using short-lived tokens
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Logged out successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")