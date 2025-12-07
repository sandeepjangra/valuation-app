"""
JWT Authentication and Organization Security Middleware
Handles AWS Cognito JWT token validation and organization-based access control
"""

import os
import json
import jwt
import requests
import logging
from typing import Optional, Dict, Any, List, Union, Callable
from functools import wraps
from datetime import datetime, timezone
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cachetools import TTLCache
import asyncio
from database.multi_db_manager import MultiDatabaseManager
from database.organization_models import AuditLogSchema, FILTERED_COLLECTIONS

logger = logging.getLogger(__name__)

# Security configuration
security = HTTPBearer()

class CognitoJWTValidator:
    """
    AWS Cognito JWT token validator with caching
    """
    
    def __init__(self):
        # Cognito configuration from environment
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        self.client_id = os.getenv("COGNITO_CLIENT_ID")
        
        if not self.user_pool_id or not self.client_id:
            logger.warning("⚠️ Cognito configuration not found in environment variables")
            self.enabled = False
        else:
            self.enabled = True
            
        # JWK cache (24-hour TTL)
        self.jwk_cache = TTLCache(maxsize=1, ttl=86400)  # 24 hours
        
        # Build JWK URL
        if self.enabled:
            self.jwk_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
            logger.info(f"🔐 Cognito JWT validator initialized for region: {self.region}")
    
    async def get_jwk_keys(self) -> Dict[str, Any]:
        """Fetch and cache JWK keys from Cognito"""
        if "jwk_keys" in self.jwk_cache:
            return self.jwk_cache["jwk_keys"]
        
        try:
            # Fetch JWK keys from Cognito
            response = requests.get(self.jwk_url, timeout=10)
            response.raise_for_status()
            jwk_data = response.json()
            
            # Cache the keys
            self.jwk_cache["jwk_keys"] = jwk_data
            logger.debug("🔄 JWK keys fetched and cached")
            
            return jwk_data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch JWK keys: {e}")
            raise HTTPException(status_code=500, detail="Unable to validate token")
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and extract claims"""
        if not self.enabled:
            # Development mode - return mock claims
            logger.warning("🚧 JWT validation disabled - using development mode")
            return self._get_development_claims(token)
        
        try:
            # Get JWK keys
            jwk_data = await self.get_jwk_keys()
            
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(status_code=401, detail="Invalid token format")
            
            # Find matching key
            key = None
            for jwk_key in jwk_data.get("keys", []):
                if jwk_key.get("kid") == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk_key)
                    break
            
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token key")
            
            # Validate and decode token
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            logger.debug(f"✅ JWT token validated for user: {payload.get('email', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ Invalid JWT token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            raise HTTPException(status_code=500, detail="Token validation failed")
    
    def _get_development_claims(self, token: str) -> Dict[str, Any]:
        """Generate development claims for testing (DO NOT USE IN PRODUCTION)"""
        
        # Token format: "dev_username_domain_org_short_name_role"
        # Example: "dev_manager_test.com_sk_tindwal_manager"
        # Hyphens in org_short_name are replaced with underscores in token
        # Known roles: system_admin, manager, employee
        
        if token.startswith("dev_"):
            parts = token.replace("dev_", "").split("_")
            if len(parts) >= 4:
                username = parts[0]
                domain = parts[1]
                
                # Known roles (including those with underscores)
                known_roles = ["system_admin", "manager", "employee", "admin"]
                
                # Find role by checking from the end
                role = None
                org_end_index = len(parts)
                
                # Check for two-part role (system_admin)
                if len(parts) >= 2 and "_".join(parts[-2:]) in known_roles:
                    role = "_".join(parts[-2:])
                    org_end_index = -2
                # Check for single-part role
                elif parts[-1] in known_roles:
                    role = parts[-1]
                    org_end_index = -1
                else:
                    # Default to last part
                    role = parts[-1]
                    org_end_index = -1
                
                # Everything between domain and role is org_short_name
                if org_end_index == -1:
                    org_token_parts = parts[2:-1]
                else:  # org_end_index == -2
                    org_token_parts = parts[2:-2]
                    
                org_token = "_".join(org_token_parts) if org_token_parts else "system_admin"
                
                # Convert underscores back to hyphens for org_short_name
                # Special case: "system_admin" stays as-is
                if org_token == "system_admin":
                    org_short_name = "system_admin"
                else:
                    org_short_name = org_token.replace("_", "-")
                    
                email = f"{username}@{domain}"
                
                return {
                    "sub": f"dev_user_{username}",
                    "email": email,
                    "custom:org_short_name": org_short_name,
                    "custom:organization_id": org_short_name,  # Backward compatibility
                    "cognito:groups": [role],
                    "iat": int(datetime.now(timezone.utc).timestamp()),
                    "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,  # 1 hour
                    "dev_mode": True
                }
        
        # Default development user
        return {
            "sub": "dev_user_test",
            "email": "test@example.com",
            "custom:org_short_name": "sk-tindwal",
            "custom:organization_id": "sk-tindwal",  # Backward compatibility
            "cognito:groups": ["employee"],
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
            "dev_mode": True
        }

# Global JWT validator instance
jwt_validator = CognitoJWTValidator()

class OrganizationContext:
    """
    Organization context extracted from JWT token
    """
    
    def __init__(self, jwt_claims: Dict[str, Any]):
        self.user_id = jwt_claims.get("sub")
        self.email = jwt_claims.get("email")
        self.org_short_name = jwt_claims.get("custom:org_short_name")
        # Backward compatibility: fallback to organization_id if org_short_name not found
        if not self.org_short_name:
            self.org_short_name = jwt_claims.get("custom:organization_id")
        
        self.organization_id = self.org_short_name  # Alias for backward compatibility
        self.roles = jwt_claims.get("cognito:groups", [])
        self.is_system_admin = "system_admin" in self.roles
        self.is_manager = "manager" in self.roles or self.is_system_admin
        self.is_employee = "employee" in self.roles
        self.dev_mode = jwt_claims.get("dev_mode", False)
        
        # Validate required fields
        if not self.org_short_name:
            raise HTTPException(status_code=401, detail="Organization short name not found in token")
        
        if not self.roles:
            raise HTTPException(status_code=401, detail="User roles not found in token")
    
    def can_access_organization(self, target_org_short_name: str) -> bool:
        """Check if user can access the target organization"""
        if self.is_system_admin:
            return True  # System admin can access all organizations
        
        return self.org_short_name == target_org_short_name
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission for specific resource and action"""
        if self.is_system_admin:
            return True  # System admin has all permissions
        
        # Define role-based permissions
        # Manager: Full access including report submission
        # Employee: Can create/edit/save reports but CANNOT submit them
        permissions = {
            "manager": {
                "organization": ["read", "update"],
                "users": ["read", "update"], # Managers can only read and update users, not create
                "reports": ["create", "read", "update", "delete", "submit"],  # Can submit reports
                "templates": ["read", "update"],
                "audit_logs": ["read"],
                "files": ["create", "read", "update", "delete"]
            },
            "employee": {
                "organization": ["read"],
                "reports": ["create", "read", "update"],  # CANNOT submit (no "submit" permission)
                "templates": ["read"],
                "files": ["create", "read", "update"]
            }
        }
        
        user_role = "manager" if self.is_manager else "employee"
        user_perms = permissions.get(user_role, {})
        resource_perms = user_perms.get(resource, [])
        
        return action in resource_perms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "org_short_name": self.org_short_name,
            "organization_id": self.organization_id,  # Backward compatibility
            "roles": self.roles,
            "is_system_admin": self.is_system_admin,
            "is_manager": self.is_manager,
            "dev_mode": self.dev_mode
        }

async def get_organization_context(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> OrganizationContext:
    """
    FastAPI dependency to extract and validate organization context from JWT token
    """
    try:
        # Debug: Log the token being processed
        logger.info(f"🔍 Processing token: {credentials.credentials[:50]}...")
        
        # Validate JWT token
        jwt_claims = await jwt_validator.validate_token(credentials.credentials)
        
        # Debug: Log the JWT claims
        logger.info(f"🔍 JWT Claims: {jwt_claims}")
        
        # Create organization context
        org_context = OrganizationContext(jwt_claims)
        
        # Debug: Log the organization context
        logger.info(f"🏢 Organization context created: {org_context.org_short_name} ({org_context.email})")
        logger.info(f"🏢 Roles: {org_context.roles}, is_manager: {org_context.is_manager}")
        
        return org_context
        
    except Exception as e:
        logger.error(f"❌ Failed to create organization context: {e}")
        raise

class OrganizationMiddleware:
    """
    Middleware for automatic organization filtering and security
    """
    
    def __init__(self, db_manager: MultiDatabaseManager):
        self.db_manager = db_manager
    
    async def validate_organization_access(
        self, 
        org_context: OrganizationContext, 
        request: Request
    ) -> None:
        """Validate that user can access the organization specified in URL"""
        
        # Extract organization short name from URL path
        url_org_short_name = None
        path_parts = request.url.path.split("/")
        
        # Look for /org/{org_short_name}/ pattern in URL
        try:
            if "org" in path_parts:
                org_index = path_parts.index("org")
                if org_index + 1 < len(path_parts):
                    url_org_short_name = path_parts[org_index + 1]
        except (ValueError, IndexError):
            pass
        
        if url_org_short_name:
            # Validate access to URL organization
            if not org_context.can_access_organization(url_org_short_name):
                await self._log_access_violation(
                    org_context, 
                    f"Attempted access to organization: {url_org_short_name}",
                    request
                )
                raise HTTPException(
                    status_code=403, 
                    detail=f"Access denied to organization: {url_org_short_name}"
                )
        
        # Verify organization exists and is active
        if not org_context.is_system_admin:
            # Check in val_app_config database
            org_exists = await self.db_manager.find_one(
                "val_app_config", "organizations",
                {"org_short_name": org_context.org_short_name, "is_active": True}
            )
            
            if not org_exists:
                raise HTTPException(
                    status_code=403,
                    detail="Organization not found or inactive"
                )
    
    def apply_organization_filter(
        self, 
        collection_name: str, 
        query_filter: Dict[str, Any], 
        org_context: OrganizationContext
    ) -> Dict[str, Any]:
        """Apply automatic organization filtering to database queries"""
        
        if collection_name in FILTERED_COLLECTIONS and not org_context.is_system_admin:
            # Add org_short_name filter for security-critical collections
            query_filter["org_short_name"] = org_context.org_short_name
            
            logger.debug(f"🔒 Applied organization filter: {collection_name} -> {org_context.org_short_name}")
        
        return query_filter
    
    async def log_database_operation(
        self,
        org_context: OrganizationContext,
        action: str,
        collection: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> None:
        """Log database operations for audit trail"""
        try:
            audit_log = AuditLogSchema.create_document(
                organization_id=org_context.organization_id,
                user_id=org_context.user_id,
                action=action,
                resource_type=collection,
                resource_id=resource_id,
                details=details,
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
            
            await self.db_manager.insert_one("admin", "audit_logs", audit_log)
            
        except Exception as e:
            logger.error(f"❌ Failed to log audit trail: {e}")
            # Don't fail the main operation if audit logging fails
    
    async def _log_access_violation(
        self, 
        org_context: OrganizationContext, 
        details: str, 
        request: Request
    ) -> None:
        """Log security violations"""
        try:
            await self.log_database_operation(
                org_context=org_context,
                action="access_denied",
                collection="organization_access",
                details={"violation": details, "url": str(request.url)},
                request=request
            )
        except Exception as e:
            logger.error(f"❌ Failed to log access violation: {e}")

def require_role(*required_roles: str) -> Callable:
    """
    Decorator to require specific roles for endpoint access
    Usage: @require_role("manager", "system_admin")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find org_context in function arguments
            org_context = None
            for arg in args:
                if isinstance(arg, OrganizationContext):
                    org_context = arg
                    break
            
            # Check kwargs as well
            if not org_context:
                org_context = kwargs.get("org_context")
            
            if not org_context:
                raise HTTPException(status_code=500, detail="Organization context not found")
            
            # Check if user has required role
            user_roles = set(org_context.roles)
            required_roles_set = set(required_roles)
            
            if not user_roles.intersection(required_roles_set):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Insufficient permissions. Required roles: {required_roles}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_permission(resource: str, action: str) -> Callable:
    """
    Decorator to require specific permission for endpoint access
    Usage: @require_permission("reports", "create")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find org_context in function arguments
            org_context = None
            for arg in args:
                if isinstance(arg, OrganizationContext):
                    org_context = arg
                    break
            
            if not org_context:
                org_context = kwargs.get("org_context")
            
            if not org_context:
                raise HTTPException(status_code=500, detail="Organization context not found")
            
            # Check permission
            if not org_context.has_permission(resource, action):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Insufficient permissions for {action} on {resource}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Helper function to create organization middleware instance
def create_organization_middleware(db_manager: MultiDatabaseManager) -> OrganizationMiddleware:
    """Create organization middleware instance with database manager"""
    return OrganizationMiddleware(db_manager)

# Development helper for testing
def create_dev_token(email: str, org_short_name: str, role: str) -> str:
    """Create a development token for testing"""
    # Format: dev_email_domain_org-short-name_role
    # Example: dev_manager_test.com_sk-tindwal_manager
    email_parts = email.split('@')
    if len(email_parts) == 2:
        username, domain = email_parts
        # Replace hyphens with underscores in org_short_name for token format
        org_token = org_short_name.replace("-", "_")
        return f"dev_{username}_{domain}_{org_token}_{role}"
    else:
        # Fallback format
        org_token = org_short_name.replace("-", "_")
        return f"dev_{email.replace('@', '_')}_{org_token}_{role}"

# Environment validation
def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = ["AWS_REGION", "COGNITO_USER_POOL_ID", "COGNITO_CLIENT_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars and os.getenv("ENVIRONMENT") == "production":
        logger.error(f"❌ Missing required environment variables for production: {missing_vars}")
        raise RuntimeError(f"Missing required environment variables: {missing_vars}")
    elif missing_vars:
        logger.warning(f"⚠️ Missing environment variables (development mode): {missing_vars}")

# Initialize environment validation
validate_environment()