"""
Role-Based Access Control (RBAC) Models and Permissions
Defines roles, permissions, and access control logic
"""

from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

class UserRole(Enum):
    """User roles in the system"""
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class Permission(Enum):
    """System permissions"""
    # Organization management
    ORG_CREATE = "org:create"
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_ROLE_UPDATE = "user:role_update"
    
    # Report management
    REPORT_CREATE = "report:create"
    REPORT_READ = "report:read"
    REPORT_UPDATE = "report:update"
    REPORT_DELETE = "report:delete"
    REPORT_SUBMIT = "report:submit"
    REPORT_APPROVE = "report:approve"
    
    # Template management
    TEMPLATE_CREATE = "template:create"
    TEMPLATE_READ = "template:read"
    TEMPLATE_UPDATE = "template:update"
    TEMPLATE_DELETE = "template:delete"
    
    # Audit and monitoring
    AUDIT_READ = "audit:read"
    SYSTEM_MONITOR = "system:monitor"
    
    # File management
    FILE_UPLOAD = "file:upload"
    FILE_READ = "file:read"
    FILE_DELETE = "file:delete"

@dataclass
class RolePermissions:
    """Role permissions mapping"""
    role: UserRole
    permissions: Set[Permission]
    description: str

# Define role-based permissions
ROLE_PERMISSIONS: Dict[UserRole, RolePermissions] = {
    UserRole.ADMIN: RolePermissions(
        role=UserRole.ADMIN,
        permissions={
            # Full system access
            Permission.ORG_CREATE,
            Permission.ORG_READ,
            Permission.ORG_UPDATE,
            Permission.ORG_DELETE,
            Permission.USER_CREATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.USER_DELETE,
            Permission.USER_ROLE_UPDATE,
            Permission.REPORT_CREATE,
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            Permission.REPORT_DELETE,
            Permission.REPORT_SUBMIT,
            Permission.REPORT_APPROVE,
            Permission.TEMPLATE_CREATE,
            Permission.TEMPLATE_READ,
            Permission.TEMPLATE_UPDATE,
            Permission.TEMPLATE_DELETE,
            Permission.AUDIT_READ,
            Permission.SYSTEM_MONITOR,
            Permission.FILE_UPLOAD,
            Permission.FILE_READ,
            Permission.FILE_DELETE,
        },
        description="System administrators with full access to all features"
    ),
    
    UserRole.MANAGER: RolePermissions(
        role=UserRole.MANAGER,
        permissions={
            # Organization management (read/update only)
            Permission.ORG_READ,
            Permission.ORG_UPDATE,
            
            # User management (within organization)
            Permission.USER_READ,
            Permission.USER_UPDATE,
            
            # Full report management including submission
            Permission.REPORT_CREATE,
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            Permission.REPORT_DELETE,
            Permission.REPORT_SUBMIT,  # Key difference: can submit reports
            
            # Template management
            Permission.TEMPLATE_CREATE,
            Permission.TEMPLATE_READ,
            Permission.TEMPLATE_UPDATE,
            Permission.TEMPLATE_DELETE,
            
            # Audit access
            Permission.AUDIT_READ,
            
            # File management
            Permission.FILE_UPLOAD,
            Permission.FILE_READ,
            Permission.FILE_DELETE,
        },
        description="Managers with report submission rights and team management"
    ),
    
    UserRole.EMPLOYEE: RolePermissions(
        role=UserRole.EMPLOYEE,
        permissions={
            # Basic organization access
            Permission.ORG_READ,
            
            # Report management (NO SUBMIT permission)
            Permission.REPORT_CREATE,
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            # Note: No REPORT_SUBMIT - employees cannot submit reports
            
            # Template read access
            Permission.TEMPLATE_READ,
            
            # File management
            Permission.FILE_UPLOAD,
            Permission.FILE_READ,
        },
        description="Employees with report creation and editing rights (cannot submit)"
    )
}

class RBACService:
    """Role-Based Access Control service"""
    
    @staticmethod
    def get_role_permissions(role: UserRole) -> Set[Permission]:
        """Get permissions for a role"""
        return ROLE_PERMISSIONS.get(role, RolePermissions(role, set(), "")).permissions
    
    @staticmethod
    def has_permission(user_roles: List[str], required_permission: Permission) -> bool:
        """Check if user has required permission"""
        for role_str in user_roles:
            try:
                role = UserRole(role_str.lower())
                role_perms = RBACService.get_role_permissions(role)
                if required_permission in role_perms:
                    return True
            except ValueError:
                continue
        return False
    
    @staticmethod
    def has_any_permission(user_roles: List[str], required_permissions: List[Permission]) -> bool:
        """Check if user has any of the required permissions"""
        return any(
            RBACService.has_permission(user_roles, perm) 
            for perm in required_permissions
        )
    
    @staticmethod
    def has_all_permissions(user_roles: List[str], required_permissions: List[Permission]) -> bool:
        """Check if user has all required permissions"""
        return all(
            RBACService.has_permission(user_roles, perm) 
            for perm in required_permissions
        )
    
    @staticmethod
    def is_admin(user_roles: List[str]) -> bool:
        """Check if user is admin"""
        return UserRole.ADMIN.value in [role.lower() for role in user_roles]
    
    @staticmethod
    def is_manager(user_roles: List[str]) -> bool:
        """Check if user is manager or admin"""
        role_values = [role.lower() for role in user_roles]
        return (UserRole.MANAGER.value in role_values or 
                UserRole.ADMIN.value in role_values)
    
    @staticmethod
    def can_submit_reports(user_roles: List[str]) -> bool:
        """Check if user can submit reports (managers and admins only)"""
        return RBACService.has_permission(user_roles, Permission.REPORT_SUBMIT)
    
    @staticmethod
    def can_manage_users(user_roles: List[str]) -> bool:
        """Check if user can manage other users"""
        return RBACService.has_permission(user_roles, Permission.USER_UPDATE)
    
    @staticmethod
    def get_accessible_resources(user_roles: List[str]) -> Dict[str, List[str]]:
        """Get list of resources user can access"""
        all_permissions = set()
        
        for role_str in user_roles:
            try:
                role = UserRole(role_str.lower())
                role_perms = RBACService.get_role_permissions(role)
                all_permissions.update(role_perms)
            except ValueError:
                continue
        
        # Group permissions by resource type
        resources = {}
        for perm in all_permissions:
            resource, action = perm.value.split(":", 1)
            if resource not in resources:
                resources[resource] = []
            resources[resource].append(action)
        
        return resources

@dataclass
class OrganizationAccess:
    """Organization access control"""
    user_id: str
    organization_id: str
    roles: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    def can_access_organization(self, target_org_id: str) -> bool:
        """Check if user can access target organization"""
        # System admins can access all organizations
        if RBACService.is_admin(self.roles):
            return True
        
        # Users can only access their own organization
        return self.organization_id == target_org_id
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "roles": self.roles,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "permissions": RBACService.get_accessible_resources(self.roles)
        }

class SecurityContext:
    """Security context for request processing"""
    
    def __init__(
        self, 
        user_id: str, 
        email: str, 
        organization_id: str, 
        roles: List[str],
        is_active: bool = True
    ):
        self.user_id = user_id
        self.email = email
        self.organization_id = organization_id
        self.roles = roles
        self.is_active = is_active
        self.rbac = RBACService()
    
    def require_permission(self, permission: Permission) -> bool:
        """Require specific permission (raises exception if not authorized)"""
        if not self.is_active:
            raise PermissionError("User account is inactive")
        
        if not self.rbac.has_permission(self.roles, permission):
            raise PermissionError(f"Insufficient permissions: {permission.value}")
        
        return True
    
    def require_organization_access(self, target_org_id: str) -> bool:
        """Require access to specific organization"""
        if not self.is_active:
            raise PermissionError("User account is inactive")
        
        # System admins can access all organizations
        if self.rbac.is_admin(self.roles):
            return True
        
        if self.organization_id != target_org_id:
            raise PermissionError(f"Access denied to organization: {target_org_id}")
        
        return True
    
    def can_submit_reports(self) -> bool:
        """Check if user can submit reports"""
        return self.rbac.can_submit_reports(self.roles)
    
    def is_manager_or_admin(self) -> bool:
        """Check if user is manager or admin"""
        return self.rbac.is_manager(self.roles)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "organization_id": self.organization_id,
            "roles": self.roles,
            "is_active": self.is_active,
            "permissions": self.rbac.get_accessible_resources(self.roles)
        }