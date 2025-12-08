"""
Enhanced Authentication Middleware with AWS Cognito Integration
Combines JWT validation, RBAC, and organization security
"""

import os
import jwt
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cachetools import TTLCache
import requests

from .cognito_service import cognito_service
from .rbac_models import RBACService, Permission, UserRole, SecurityContext
from database.multi_db_manager import MultiDatabaseManager

logger = logging.getLogger(__name__)

class EnhancedAuthMiddleware:
    """Enhanced authentication middleware with Cognito and RBAC"""
    
    def __init__(self):
        # AWS Cognito configuration
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        self.client_id = os.getenv("COGNITO_CLIENT_ID")
        
        # JWT validation cache (1 hour TTL)
        self.jwt_cache = TTLCache(maxsize=1000, ttl=3600)
        
        # JWK keys cache (24 hour TTL)
        self.jwk_cache = TTLCache(maxsize=1, ttl=86400)
        
        # Configure Cognito service
        if self.user_pool_id and self.client_id:
            cognito_service.configure(self.user_pool_id, self.client_id)
            self.cognito_enabled = True
            logger.info("🔐 Enhanced auth middleware initialized with Cognito")
        else:
            self.cognito_enabled = False
            logger.warning("⚠️ Cognito not configured - using development mode")
        
        # Build JWK URL for token validation
        if self.cognito_enabled:
            self.jwk_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
    
    async def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and extract claims"""
        
        # Check cache first
        if token in self.jwt_cache:
            return self.jwt_cache[token]
        
        if not self.cognito_enabled:
            # Development mode - parse development token
            claims = self._parse_development_token(token)
            self.jwt_cache[token] = claims
            return claims
        
        try:
            # Get JWK keys
            jwk_keys = await self._get_jwk_keys()
            
            # Decode token header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(status_code=401, detail="Invalid token format")
            
            # Find matching key
            key = None
            for jwk_key in jwk_keys.get("keys", []):
                if jwk_key.get("kid") == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk_key)
                    break
            
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token key")
            
            # Validate and decode token
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            # Cache valid token
            self.jwt_cache[token] = claims
            
            logger.debug(f"✅ JWT token validated for: {claims.get('email', 'unknown')}")
            return claims
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ Invalid JWT token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            raise HTTPException(status_code=500, detail="Token validation failed")
    
    async def _get_jwk_keys(self) -> Dict[str, Any]:
        """Fetch and cache JWK keys from Cognito"""
        
        if "jwk_keys" in self.jwk_cache:
            return self.jwk_cache["jwk_keys"]
        
        try:
            response = requests.get(self.jwk_url, timeout=10)
            response.raise_for_status()
            jwk_data = response.json()
            
            self.jwk_cache["jwk_keys"] = jwk_data
            logger.debug("🔄 JWK keys fetched and cached")
            
            return jwk_data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch JWK keys: {e}")
            raise HTTPException(status_code=500, detail="Unable to validate token")
    
    def _parse_development_token(self, token: str) -> Dict[str, Any]:
        """Parse development token for testing"""
        
        if token.startswith("dev_"):
            # Parse development token format: dev_username_domain_org_role
            parts = token.replace("dev_", "").split("_")
            
            if len(parts) >= 4:
                username = parts[0]
                domain = parts[1]
                
                # Handle roles with underscores (system_admin)
                known_roles = ["system_admin", "manager", "employee", "admin"]
                role = None
                org_end_index = len(parts)
                
                # Check for two-part role
                if len(parts) >= 2 and "_".join(parts[-2:]) in known_roles:
                    role = "_".join(parts[-2:])
                    org_end_index = -2
                elif parts[-1] in known_roles:
                    role = parts[-1]
                    org_end_index = -1
                else:
                    role = parts[-1]
                    org_end_index = -1
                
                # Extract organization
                if org_end_index == -1:
                    org_parts = parts[2:-1]
                else:
                    org_parts = parts[2:-2]
                
                org_token = "_".join(org_parts) if org_parts else "system_admin"
                org_short_name = org_token.replace("_", "-") if org_token != "system_admin" else "system_admin"
                
                email = f"{username}@{domain}"
                
                return {
                    "sub": f"dev_user_{username}",
                    "email": email,
                    "custom:org_short_name": org_short_name,
                    "custom:organization_id": org_short_name,
                    "cognito:groups": [role],
                    "iat": int(datetime.now(timezone.utc).timestamp()),
                    "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                    "dev_mode": True
                }
        
        # Default development claims
        return {
            "sub": "dev_user_test",
            "email": "test@example.com",
            "custom:org_short_name": "sk-tindwal",
            "custom:organization_id": "sk-tindwal",
            "cognito:groups": ["employee"],
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
            "dev_mode": True
        }
    
    async def create_security_context(self, jwt_claims: Dict[str, Any]) -> SecurityContext:
        """Create security context from JWT claims"""
        
        user_id = jwt_claims.get("sub")
        email = jwt_claims.get("email")
        org_short_name = jwt_claims.get("custom:org_short_name") or jwt_claims.get("custom:organization_id")
        roles = jwt_claims.get("cognito:groups", [])
        
        if not user_id or not email or not org_short_name:
            raise HTTPException(status_code=401, detail="Invalid token claims")
        
        # Validate organization exists and is active (except for system admins)
        if not RBACService.is_admin(roles):
            db_manager = MultiDatabaseManager()
            await db_manager.connect()
            
            try:
                org_exists = await db_manager.find_one(
                    "val_app_config", "organizations",
                    {"org_short_name": org_short_name, "is_active": True}
                )
                
                if not org_exists:
                    raise HTTPException(
                        status_code=403,
                        detail="Organization not found or inactive"
                    )
            finally:
                await db_manager.disconnect()
        
        return SecurityContext(
            user_id=user_id,
            email=email,
            organization_id=org_short_name,
            roles=roles,
            is_active=True
        )
    
    async def validate_organization_access(
        self, 
        security_context: SecurityContext, 
        target_org_id: str
    ) -> bool:
        """Validate user can access target organization"""
        
        try:
            security_context.require_organization_access(target_org_id)
            return True
        except PermissionError:
            return False
    
    async def validate_permission(
        self, 
        security_context: SecurityContext, 
        permission: Permission
    ) -> bool:
        """Validate user has required permission"""
        
        try:
            security_context.require_permission(permission)
            return True
        except PermissionError:
            return False

# Global middleware instance
auth_middleware = EnhancedAuthMiddleware()

# FastAPI security scheme
security = HTTPBearer()

async def get_security_context(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> SecurityContext:
    """FastAPI dependency to get security context from JWT token"""
    
    try:
        # Validate JWT token
        jwt_claims = await auth_middleware.validate_jwt_token(credentials.credentials)
        
        # Create security context
        security_context = await auth_middleware.create_security_context(jwt_claims)
        
        logger.debug(f"🔐 Security context created for: {security_context.email}")
        return security_context
        
    except Exception as e:
        logger.error(f"❌ Failed to create security context: {e}")
        raise

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find security context in arguments
            security_context = None
            for arg in args:
                if isinstance(arg, SecurityContext):
                    security_context = arg
                    break
            
            if not security_context:
                security_context = kwargs.get("security_context")
            
            if not security_context:
                raise HTTPException(status_code=500, detail="Security context not found")
            
            # Validate permission
            if not await auth_middleware.validate_permission(security_context, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_role(*required_roles: UserRole):
    """Decorator to require specific roles"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find security context in arguments
            security_context = None
            for arg in args:
                if isinstance(arg, SecurityContext):
                    security_context = arg
                    break
            
            if not security_context:
                security_context = kwargs.get("security_context")
            
            if not security_context:
                raise HTTPException(status_code=500, detail="Security context not found")
            
            # Check roles
            user_role_values = [role.lower() for role in security_context.roles]
            required_role_values = [role.value for role in required_roles]
            
            if not any(role in user_role_values for role in required_role_values):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient role. Required: {required_role_values}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_organization_access(org_id_param: str = "org_id"):
    """Decorator to require access to specific organization"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find security context
            security_context = None
            for arg in args:
                if isinstance(arg, SecurityContext):
                    security_context = arg
                    break
            
            if not security_context:
                security_context = kwargs.get("security_context")
            
            if not security_context:
                raise HTTPException(status_code=500, detail="Security context not found")
            
            # Get target organization ID from parameters
            target_org_id = kwargs.get(org_id_param)
            if not target_org_id:
                raise HTTPException(status_code=400, detail="Organization ID not provided")
            
            # Validate access
            if not await auth_middleware.validate_organization_access(security_context, target_org_id):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied to organization: {target_org_id}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator