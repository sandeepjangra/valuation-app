# Authentication System Guide

## Overview

This document describes the comprehensive authentication system implemented for the Valuation App, which integrates AWS Cognito with MongoDB for secure, role-based user management.

## Architecture

### Components

1. **AWS Cognito** - Primary authentication provider
2. **MongoDB** - User profiles and organization data
3. **JWT Tokens** - Secure API access
4. **Role-Based Access Control (RBAC)** - Permission management
5. **Multi-tenant Security** - Organization isolation

### Authentication Flow

```
User Login → AWS Cognito → JWT Token → API Access → MongoDB Profile
```

## User Roles and Permissions

### Admin
- **Full system access**
- Create/manage organizations
- Create/manage users across all organizations
- Full report management
- System monitoring and audit logs
- Template management

### Manager
- **Organization-level management**
- Read/update organization settings
- Manage users within organization
- Full report management including submission
- Template creation and management
- Audit log access

### Employee
- **Basic operational access**
- Create and edit reports (cannot submit)
- Read templates
- File upload/management
- Basic organization information

## Setup Instructions

### 1. AWS Cognito Configuration

#### Create User Pool
```bash
# Using AWS CLI
aws cognito-idp create-user-pool \
    --pool-name "ValuationApp-UserPool" \
    --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
    --auto-verified-attributes email \
    --username-attributes email
```

#### Create User Pool Client
```bash
aws cognito-idp create-user-pool-client \
    --user-pool-id us-east-1_XXXXXXXXX \
    --client-name "ValuationApp-Client" \
    --generate-secret \
    --explicit-auth-flows ADMIN_NO_SRP_AUTH
```

### 2. Environment Configuration

Create `.env` file in backend directory:

```env
# AWS Cognito Configuration
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_REGION=us-east-1

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# Application Configuration
ENVIRONMENT=development
DEBUG=true
```

### 3. Run Setup Script

```bash
cd scripts
python setup_auth_system.py
```

This script will:
- Create Cognito user groups (admin, manager, employee)
- Initialize system administration organization
- Create system admin user
- Set up demo organization and users

### 4. Frontend Configuration

Update `src/aws-exports.ts`:

```typescript
const awsmobile = {
  "aws_project_region": "us-east-1",
  "aws_user_pools_id": "us-east-1_XXXXXXXXX",
  "aws_user_pools_web_client_id": "XXXXXXXXXXXXXXXXXXXXXXXXXX",
  // ... other configuration
};
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| POST | `/api/auth/login` | User login | Public |
| POST | `/api/auth/logout` | User logout | Authenticated |
| GET | `/api/auth/me` | Get current user | Authenticated |
| PUT | `/api/auth/me` | Update profile | Authenticated |

### User Management Endpoints

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| POST | `/api/auth/register` | Create user | Admin, Manager |
| PUT | `/api/auth/users/{id}/role` | Update user role | Admin |
| POST | `/api/auth/users/{id}/disable` | Disable user | Admin, Manager |
| POST | `/api/auth/users/{id}/enable` | Enable user | Admin, Manager |

## Frontend Integration

### Authentication Service

```typescript
import { AuthService } from './services/auth.service';

// Login
this.authService.login({
  email: 'user@example.com',
  password: 'password123'
}).subscribe(response => {
  // Handle successful login
});

// Check permissions
if (this.authService.canSubmitReports()) {
  // Show submit button
}
```

### Route Guards

```typescript
// Protect routes with authentication
{
  path: 'dashboard',
  component: DashboardComponent,
  canActivate: [AuthGuard]
}

// Protect routes with role requirements
{
  path: 'admin',
  component: AdminComponent,
  canActivate: [AdminGuard]
}
```

### HTTP Interceptor

Automatically adds JWT tokens to API requests:

```typescript
// Configured in app.module.ts
providers: [
  {
    provide: HTTP_INTERCEPTORS,
    useClass: AuthInterceptor,
    multi: true
  }
]
```

## Security Features

### JWT Token Validation
- Validates tokens against AWS Cognito JWK
- Automatic token refresh
- Secure token storage

### Organization Isolation
- Users can only access their organization's data
- System admins can access all organizations
- Database-level isolation

### Permission-Based Access Control
- Fine-grained permissions for each role
- Decorator-based endpoint protection
- Frontend permission checks

### Audit Logging
- All user actions logged
- IP address and user agent tracking
- Searchable audit trail

## Development Mode

For development, the system supports mock authentication:

```typescript
// Development login buttons
loginAsAdmin() {
  // Uses development token format
}
```

Development tokens format: `dev_username_domain_org_role`

## Production Deployment

### Security Checklist

1. **Environment Variables**
   - Set production Cognito pool IDs
   - Use secure MongoDB connection strings
   - Configure proper CORS origins

2. **Password Policies**
   - Enforce strong passwords in Cognito
   - Enable MFA for admin accounts
   - Regular password rotation

3. **Token Security**
   - Short token expiration times
   - Secure token storage
   - Token blacklisting for logout

4. **Network Security**
   - HTTPS only
   - API rate limiting
   - IP whitelisting for admin access

### Monitoring

- CloudWatch logs for Cognito events
- MongoDB audit logs
- Application performance monitoring
- Security event alerting

## Troubleshooting

### Common Issues

1. **Token Validation Errors**
   ```
   Error: Invalid token key
   ```
   - Check Cognito User Pool ID
   - Verify JWK endpoint accessibility

2. **Permission Denied**
   ```
   Error: Insufficient permissions
   ```
   - Check user role assignments
   - Verify Cognito groups

3. **Organization Access Denied**
   ```
   Error: Access denied to organization
   ```
   - Verify user's organization assignment
   - Check organization active status

### Debug Commands

```bash
# Check Cognito user
aws cognito-idp admin-get-user \
    --user-pool-id us-east-1_XXXXXXXXX \
    --username user@example.com

# List user groups
aws cognito-idp admin-list-groups-for-user \
    --user-pool-id us-east-1_XXXXXXXXX \
    --username user@example.com
```

## API Testing

### Using cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@system.com","password":"Admin123!"}'

# Access protected endpoint
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Postman

1. Create environment variables for tokens
2. Set up authentication collection
3. Use pre-request scripts for token refresh

## Best Practices

### Backend Development
- Always use security context dependency injection
- Validate permissions at endpoint level
- Log security-relevant actions
- Handle token expiration gracefully

### Frontend Development
- Store tokens securely
- Implement automatic token refresh
- Show/hide UI based on permissions
- Handle authentication errors gracefully

### Database Security
- Use organization-specific databases
- Implement proper indexing
- Regular backup and recovery testing
- Monitor for suspicious activity

## Support and Maintenance

### Regular Tasks
- Monitor Cognito usage and costs
- Review audit logs for security events
- Update user roles as needed
- Clean up inactive users

### Updates and Patches
- Keep AWS SDK updated
- Monitor Cognito service updates
- Test authentication flow after updates
- Update frontend dependencies regularly

## Contact

For questions or issues with the authentication system:
- Check the troubleshooting section
- Review audit logs for errors
- Contact system administrator