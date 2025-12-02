# API Endpoints Documentation

Base URL: `http://localhost:8000`

## Authentication Endpoints

### POST /api/auth/login
- **Purpose**: User login
- **Example**: `curl -X POST "http://localhost:8000/api/auth/login"`

### POST /api/auth/dev-login
- **Purpose**: Development login (for testing)
- **Example**: `curl -X POST "http://localhost:8000/api/auth/dev-login"`

### POST /api/auth/logout
- **Purpose**: User logout
- **Example**: `curl -X POST "http://localhost:8000/api/auth/logout"`

### GET /api/auth/me
- **Purpose**: Get current user information
- **Example**: `curl -X GET "http://localhost:8000/api/auth/me"`

## Health & Status Endpoints

### GET /api/health
- **Purpose**: Check API health status
- **Example**: `curl -s http://localhost:8000/api/health`
- **Response**: `{"status":"healthy","timestamp":"2025-11-29T20:12:04.860559+00:00"}`

### GET /api/admin/dashboard/health
- **Purpose**: Admin dashboard health check
- **Example**: `curl -s http://localhost:8000/api/admin/dashboard/health`

## Admin Dashboard Endpoints

### GET /api/admin/dashboard/activity-logs
- **Purpose**: Get activity logs for admin dashboard
- **Example**: `curl -s http://localhost:8000/api/admin/dashboard/activity-logs`

### GET /api/admin/dashboard/activity-stats
- **Purpose**: Get activity statistics for admin dashboard
- **Example**: `curl -s http://localhost:8000/api/admin/dashboard/activity-stats`

## Organization Management Endpoints

### GET /api/admin/organizations
- **Purpose**: Get all organizations
- **Parameters**: 
  - `include_system=true` - Include system admin organization (defaults to false)
- **Example**: `curl -s "http://localhost:8000/api/admin/organizations?include_system=true"`
- **Response**: Returns array with system-administration, sk-tindwal, and yogesh-jangra organizations

### POST /api/admin/organizations
- **Purpose**: Create a new organization
- **Example**: `curl -X POST "http://localhost:8000/api/admin/organizations"`

### GET /api/admin/organizations/{org_id}
- **Purpose**: Get specific organization details
- **Example**: `curl -s "http://localhost:8000/api/admin/organizations/sk_tindwal_001"`

### DELETE /api/admin/organizations/{org_id}
- **Purpose**: Delete an organization
- **Example**: `curl -X DELETE "http://localhost:8000/api/admin/organizations/org_id"`

## User Management Endpoints

### POST /api/admin/organizations/{org_id}/users
- **Purpose**: Add user to organization
- **Example**: `curl -X POST "http://localhost:8000/api/admin/organizations/sk_tindwal_001/users"`

### GET /api/admin/organizations/{org_id}/users
- **Purpose**: Get users in organization
- **Example**: `curl -s "http://localhost:8000/api/admin/organizations/sk_tindwal_001/users"`

### PUT /api/admin/organizations/{org_id}/users/{user_id}
- **Purpose**: Update user in organization
- **Example**: `curl -X PUT "http://localhost:8000/api/admin/organizations/sk_tindwal_001/users/user_123"`

### PUT /api/admin/organizations/{org_id}/users/{user_id}/status
- **Purpose**: Update user status
- **Example**: `curl -X PUT "http://localhost:8000/api/admin/organizations/sk_tindwal_001/users/user_123/status"`

### DELETE /api/admin/organizations/{org_id}/users/{user_id}
- **Purpose**: Remove user from organization
- **Example**: `curl -X DELETE "http://localhost:8000/api/admin/organizations/sk_tindwal_001/users/user_123"`

### PUT /api/admin/users/{user_id}/role
- **Purpose**: Update user role
- **Example**: `curl -X PUT "http://localhost:8000/api/admin/users/user_123/role"`

## Banks & Templates Endpoints

### GET /api/banks
- **Purpose**: Get all available banks
- **Example**: `curl -s "http://localhost:8000/api/banks"`

### GET /api/templates/{bank_code}/{template_id}/aggregated-fields
- **Purpose**: Get template fields for specific bank and template
- **Example**: `curl -s "http://localhost:8000/api/templates/sbi/land/aggregated-fields"`

## Calculation Endpoints

### POST /api/calculate
- **Purpose**: Perform valuation calculations
- **Example**: `curl -X POST "http://localhost:8000/api/calculate"`

## Report Management Endpoints

### POST /api/reports
- **Purpose**: Create a new report
- **Example**: `curl -X POST "http://localhost:8000/api/reports"`

### PUT /api/reports/{report_id}
- **Purpose**: Update an existing report
- **Example**: `curl -X PUT "http://localhost:8000/api/reports/report_123"`

### POST /api/reports/{report_id}/submit
- **Purpose**: Submit a report
- **Example**: `curl -X POST "http://localhost:8000/api/reports/report_123/submit"`

### GET /api/reports/{report_id}/activity
- **Purpose**: Get report activity/history
- **Example**: `curl -s "http://localhost:8000/api/reports/report_123/activity"`

## Custom Templates Endpoints

### GET /api/custom-templates/fields
- **Purpose**: Get available fields for custom templates
- **Example**: `curl -s "http://localhost:8000/api/custom-templates/fields"`

### GET /api/custom-templates
- **Purpose**: Get all custom templates
- **Example**: `curl -s "http://localhost:8000/api/custom-templates"`

### GET /api/custom-templates/{template_id}
- **Purpose**: Get specific custom template
- **Example**: `curl -s "http://localhost:8000/api/custom-templates/template_123"`

### POST /api/custom-templates
- **Purpose**: Create a new custom template
- **Example**: `curl -X POST "http://localhost:8000/api/custom-templates"`

### PUT /api/custom-templates/{template_id}
- **Purpose**: Update custom template
- **Example**: `curl -X PUT "http://localhost:8000/api/custom-templates/template_123"`

### DELETE /api/custom-templates/{template_id}
- **Purpose**: Delete custom template
- **Example**: `curl -X DELETE "http://localhost:8000/api/custom-templates/template_123"`

### POST /api/custom-templates/{template_id}/clone
- **Purpose**: Clone an existing custom template
- **Example**: `curl -X POST "http://localhost:8000/api/custom-templates/template_123/clone"`

## Frontend Organization Routing

The frontend uses organization-based routing:
- **System Admin Dashboard**: `http://localhost:4200/org/system-administration/dashboard`
- **Organization Dashboard**: `http://localhost:4200/org/{org-short-name}/dashboard`
- **Organization Reports**: `http://localhost:4200/org/{org-short-name}/reports`
- **Organization New Report**: `http://localhost:4200/org/{org-short-name}/new-report`

## Notes

1. All API endpoints require proper authentication headers
2. Organization endpoints use `org-short-name` in URLs (e.g., "sk-tindwal", "yogesh-jangra")
3. The `include_system=true` parameter is needed to get the system administration organization
4. Base URL for all API calls is `http://localhost:8000`
5. Frontend runs on `http://localhost:4200`
6. **Frontend Integration**: Angular OrganizationService now uses `/api/admin/organizations` endpoint
7. **Admin Switching**: System admin users see organization switcher when `isSystemAdmin=true`

## Current Organizations

Based on the current database:
1. **sk-tindwal** (Surinder Kumar Tindwal)
2. **yogesh-jangra** (Yogesh Jangra)  
3. **system-administration** (System Admin Org - created for admin users)