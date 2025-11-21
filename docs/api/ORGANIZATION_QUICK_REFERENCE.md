# Organization Security Middleware - Quick Reference Guide

## 🚀 Quick Start

### 1. Import Required Components

```python
from utils.auth_middleware import (
    OrganizationContext, 
    create_organization_middleware, 
    require_role
)
from utils.organization_db_service import create_org_db_service
```

### 2. Initialize in FastAPI

```python
# On startup
db_manager = MultiDatabaseManager()
await db_manager.connect()

org_middleware = create_organization_middleware(db_manager)
org_db_service = create_org_db_service(db_manager, org_middleware)

# Dependency for JWT validation
async def get_org_context(request: Request) -> OrganizationContext:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    jwt_claims = await CognitoJWTValidator().validate_token(token)
    return OrganizationContext(jwt_claims)
```

### 3. Protect API Endpoints

```python
# Basic organization filtering (all authenticated users)
@app.get("/api/reports")
async def get_reports(org_context: OrganizationContext = Depends(get_org_context)):
    return await org_db_service.get_organization_reports(org_context)

# Role-based protection
@app.post("/api/users")
@require_role("manager", "system_admin")
async def create_user(
    user_data: dict,
    org_context: OrganizationContext = Depends(get_org_context)
):
    return await org_db_service.create_organization_user(user_data, org_context)
```

## 🔐 Development Tokens

### Generate Test Tokens

```python
from utils.auth_middleware import create_dev_token

# Create tokens for testing
manager_token = create_dev_token("manager@demo.com", "demo_org_001", "manager")
employee_token = create_dev_token("employee@demo.com", "demo_org_001", "employee")  
admin_token = create_dev_token("admin@system.com", "system_admin", "system_admin")
```

### Use in API Calls

```bash
# Manager accessing organization users
curl -H "Authorization: Bearer dev_manager_demo.com_demo_org_001_manager" \
     http://localhost:8000/api/users

# Employee accessing reports (allowed)
curl -H "Authorization: Bearer dev_employee_demo.com_demo_org_001_employee" \
     http://localhost:8000/api/reports

# Employee trying to access users (denied)
curl -H "Authorization: Bearer dev_employee_demo.com_demo_org_001_employee" \
     http://localhost:8000/api/users
```

## 📊 Database Operations

### Organization-Filtered Queries

```python
# All these are automatically filtered by organization_id
reports = await org_db_service.get_organization_reports(org_context)
users = await org_db_service.get_organization_users(org_context)  
audit_logs = await org_db_service.get_organization_audit_logs(org_context)
```

### Creating Documents

```python
# Documents automatically get organization_id added
new_report = {
    "title": "Property Valuation Report",
    "property_id": "PROP001",
    "value": 500000
    # organization_id will be added automatically
}

report_id = await org_db_service.create_organization_report(new_report, org_context)
```

### Role-Based Operations

```python
# Only managers and system_admins can do this
if org_context.has_permission("users", "create"):
    user_id = await org_db_service.create_organization_user(user_data, org_context)

# Check specific roles
if "manager" in org_context.roles:
    # Manager-specific logic
    pass
```

## 🔍 Permission Checks

### Available Permissions

```python
# Resource permissions
org_context.has_permission("reports", "create")    # True for all roles
org_context.has_permission("reports", "delete")    # True for manager, system_admin
org_context.has_permission("users", "read")        # True for manager, system_admin
org_context.has_permission("audit_logs", "read")   # True for manager, system_admin

# Role checks
org_context.is_system_admin()  # True only for system_admin role
org_context.is_manager()       # True for manager and system_admin
```

### Role Hierarchy

```
system_admin
    ├── Can access all organizations
    ├── Full CRUD on all resources
    └── System management functions

manager  
    ├── Organization management
    ├── User creation and management
    ├── Report management
    └── Audit log access

employee
    ├── Report creation and viewing
    ├── Own profile management
    └── Basic organization info access
```

## 🔧 Troubleshooting

### Common Issues

1. **Token Validation Fails**
   ```python
   # Check if Cognito environment variables are set for production
   # For development, ensure token format: dev_username_domain_org_role
   ```

2. **Permission Denied Errors**
   ```python
   # Verify user has required role
   print(f"User roles: {org_context.roles}")
   print(f"Required permission: {org_context.has_permission('resource', 'action')}")
   ```

3. **Organization Filtering Not Working**
   ```python
   # Ensure organization_id is in JWT claims
   print(f"Organization ID: {org_context.organization_id}")
   ```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.getLogger("utils.auth_middleware").setLevel(logging.DEBUG)
logging.getLogger("utils.organization_db_service").setLevel(logging.DEBUG)
```

## 🧪 Testing

### Run Test Suite

```bash
cd backend
python test_organization_security.py
```

### Manual API Testing

```bash
# Start the example API server
python api_integration_example.py

# Test different endpoints with different roles
curl -H "Authorization: Bearer dev_manager_demo.com_demo_org_001_manager" \
     http://localhost:8000/api/organization

curl -H "Authorization: Bearer dev_admin_system.com_system_admin_system_admin" \
     http://localhost:8000/api/system/organizations
```

## 📋 Environment Setup

### Development Mode (No AWS Cognito)

```bash
# No environment variables needed
# Uses development tokens automatically
python api_integration_example.py
```

### Production Mode (AWS Cognito)

```bash
export AWS_REGION=us-east-1
export COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
export COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
export MONGODB_URI=mongodb+srv://...

python api_integration_example.py
```

## 📈 Performance Tips

1. **Use Indexes**: All organization_id queries use indexed fields
2. **Limit Results**: Use limit/offset parameters for large datasets
3. **Cache Contexts**: Cache OrganizationContext for multiple operations
4. **Batch Operations**: Group multiple database operations when possible

## 🔐 Security Best Practices

1. **Always Use Dependencies**: Never bypass the JWT validation dependency
2. **Check Permissions**: Use `@require_role` decorators for sensitive operations
3. **Audit Everything**: All operations are automatically logged
4. **Validate Input**: Always validate user input before database operations
5. **Rotate Secrets**: Regularly rotate JWT secrets and database credentials

---

This middleware system provides enterprise-grade security with minimal integration effort! 🛡️