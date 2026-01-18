# Backend API Endpoints - Organization-Based Routing

## Overview
All organization-specific endpoints now follow the pattern: `/api/org/{orgShortName}/...`
Shared resources (Banks, Templates, Auth, Organizations management) remain at their traditional routes.

## Organization-Scoped Endpoints
These endpoints require a valid organization shortName in the route.

### Custom Templates
- **GET** `/api/org/{orgShortName}/custom-templates` - List all custom templates for the organization
- **GET** `/api/org/{orgShortName}/custom-templates/{id}` - Get a specific custom template
- **GET** `/api/org/{orgShortName}/custom-templates/fields` - Get available template fields
- **POST** `/api/org/{orgShortName}/custom-templates` - Create a new custom template
- **PUT** `/api/org/{orgShortName}/custom-templates/{id}` - Update a custom template
- **DELETE** `/api/org/{orgShortName}/custom-templates/{id}` - Delete a custom template

### Reports
- **GET** `/api/org/{orgShortName}/reports` - List all reports (with filtering and pagination)
  - Query params: `status`, `bankCode`, `page`, `pageSize`
- **GET** `/api/org/{orgShortName}/reports/{reportId}` - Get a specific report
- **POST** `/api/org/{orgShortName}/reports` - Create a new report
- **PUT** `/api/org/{orgShortName}/reports/{reportId}` - Update a report
- **DELETE** `/api/org/{orgShortName}/reports/{reportId}` - Delete a report
- **POST** `/api/org/{orgShortName}/reports/{reportId}/submit` - Submit a report for review
- **GET** `/api/org/{orgShortName}/reports/my-reports` - Get reports created by current user
  - Query params: `userEmail`, `page`, `pageSize`
- **GET** `/api/org/{orgShortName}/reports/assigned-to-me` - Get reports assigned to current user
  - Query params: `userEmail`, `page`, `pageSize`

### Organization Operations
- **GET** `/api/org/{orgShortName}/next-reference-number` - Get next report reference number

## Shared Endpoints (No Organization Context)

### Authentication
- **POST** `/api/auth/login` - User login
- **POST** `/api/auth/register` - User registration
- **POST** `/api/auth/logout` - User logout

### Banks (Shared Resource)
- **GET** `/api/banks` - List all banks
- **GET** `/api/banks/{bankCode}` - Get specific bank details

### Templates (Shared Bank Templates)
- **GET** `/api/templates` - List all bank templates
- **GET** `/api/templates/{bankCode}/{templateCode}/aggregated-fields` - Get template aggregated fields

### Organizations Management
- **GET** `/api/organizations` - List all active organizations
- **GET** `/api/organizations/{orgShortName}` - Get specific organization details
- **GET** `/api/organizations/health` - Health check for organizations API

## Organization Validation Middleware

The `OrganizationContextMiddleware` validates:
1. **Organization Existence**: Returns 404 if organization not found
2. **Organization Status**: Returns 403 if organization is inactive
3. **Context Injection**: Adds organization details to `HttpContext.Items`:
   - `Organization` - Full organization object
   - `OrganizationShortName` - Organization short name
   - `OrganizationId` - Organization MongoDB ObjectId

### Skipped Paths
The middleware skips validation for:
- `/health` and `/api/health`
- `/api/auth/*` (authentication endpoints)
- `/api/banks/*` (shared bank resources)
- `/api/templates/*` (shared bank templates)
- `/api/organizations/*` (organization management)
- `/swagger/*` (API documentation)
- `/_framework/*` and `/_content/*` (static resources)

## Examples

### Get Custom Templates (Valid Organization)
```bash
curl 'http://localhost:8000/api/org/system-administration/custom-templates'
```
Response:
```json
{
  "success": true,
  "data": [...],
  "message": "Custom templates retrieved successfully"
}
```

### Get Custom Templates (Invalid Organization)
```bash
curl 'http://localhost:8000/api/org/invalid-org/custom-templates'
```
Response:
```json
{
  "success": false,
  "message": "Organization 'invalid-org' not found",
  "errors": ["ORGANIZATION_NOT_FOUND"]
}
```

### Get Next Reference Number
```bash
curl 'http://localhost:8000/api/org/system-administration/next-reference-number'
```
Response:
```json
{
  "success": true,
  "message": "Reference number generated successfully",
  "data": {
    "reference_number": "SA-20260116-0002",
    "organization_short_name": "system-administration",
    "generated_at": "2026-01-16T21:50:46.016664Z"
  }
}
```

### List All Organizations (Shared)
```bash
curl 'http://localhost:8000/api/organizations'
```
Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "69618d3b1fd498a4ef610612",
      "shortName": "system-administration",
      "fullName": "System Administration",
      "isActive": true
    }
  ],
  "message": "Organizations retrieved successfully"
}
```

## Implementation Details

### Controllers Updated
1. ✅ **CustomTemplatesController** - `/api/org/{orgShortName}/custom-templates`
2. ✅ **OrganizationScopedController** - `/api/org/{orgShortName}/*`
3. ✅ **OrganizationsController** - `/api/organizations` (no org context)

### Controllers Remaining Shared
1. ✅ **AuthController** - `/api/auth/*` (pre-login)
2. ✅ **BanksController** - `/api/banks/*` (shared master data)
3. ✅ **TemplatesController** - `/api/templates/*` (shared bank templates)

## Next Steps

### Backend - Additional Endpoints Needed
- [✅] **Reports Management** - `/api/org/{orgShortName}/reports/*` - COMPLETE
  - POST `/api/org/{orgShortName}/reports` - Create report ✅
  - GET `/api/org/{orgShortName}/reports` - List reports ✅
  - GET `/api/org/{orgShortName}/reports/{id}` - Get report details ✅
  - PUT `/api/org/{orgShortName}/reports/{id}` - Update report ✅
  - DELETE `/api/org/{orgShortName}/reports/{id}` - Delete report ✅
  - POST `/api/org/{orgShortName}/reports/{id}/submit` - Submit report ✅
  
- [ ] **User Management** - `/api/org/{orgShortName}/users/*`
  - GET `/api/org/{orgShortName}/users` - List organization users
  - POST `/api/org/{orgShortName}/users` - Create user
  - GET `/api/org/{orgShortName}/users/{id}` - Get user details
  - PUT `/api/org/{orgShortName}/users/{id}` - Update user
  - DELETE `/api/org/{orgShortName}/users/{id}` - Delete/deactivate user

- [ ] **Dashboard/Statistics** - `/api/org/{orgShortName}/dashboard/*`
  - GET `/api/org/{orgShortName}/dashboard/stats` - Get dashboard statistics
  - GET `/api/org/{orgShortName}/dashboard/recent-activities` - Recent activities
  - GET `/api/org/{orgShortName}/dashboard/pending-reports` - Pending reports

### Backend - Current Status
✅ **All existing .NET backend controllers have been updated to organization-based routing**
- CustomTemplatesController - Organization-scoped ✅
- ReportsController - Organization-scoped ✅
- OrganizationScopedController - Organization-scoped operations ✅
- OrganizationsController - Shared (org management) ✅
- AuthController - Shared (pre-login) ✅
- BanksController - Shared (master data) ✅
- TemplatesController - Shared (bank templates) ✅

### Frontend
- [ ] Update all routes to include organization context: `/org/{orgShortName}/...`
- [ ] Update all HTTP services to use new API endpoints
- [ ] Create organization route guard to validate org before navigation
- [ ] Add organization selector for admin users
- [ ] Update navigation/menu items to use org-based routes
