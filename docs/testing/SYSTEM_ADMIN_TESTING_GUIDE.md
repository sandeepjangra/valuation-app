# System Admin Testing Guide

## Overview
This guide demonstrates the complete role-based organization management system with:
- System Admin creates organizations
- System Admin adds users with roles (Manager/Employee)
- Manager can submit reports and view activity logs
- Employee can only create/edit reports (no submit, no logs)

## Prerequisites
- Backend running on http://localhost:8000
- Frontend running on http://localhost:4200
- MongoDB Atlas connected

## Test Flow

### 1. System Admin Login
Login as system administrator to access organization management.

**Login Credentials:**
```
Email: admin@system.com
Password: admin123
Role: system_admin
```

After login:
- Navigate to http://localhost:4200/admin/organizations
- You should see "Organization Management" page
- Admin link should be visible in header

### 2. View Existing Organizations
Current organizations in the system:
- **demo_org_001**: Demo Organization (3 users)
- **acme_real_estate_002**: Acme Real Estate (0 users, newly created)

### 3. Create New Organization

Click "➕ Create Organization" button.

**Example Organization:**
```
Organization Name: Tech Valuations LLC
Contact Email: contact@techvaluations.com
Contact Phone: +1-555-8888
Address: 456 Innovation Drive, Tech City, CA 94000
Max Users: 15
Plan: professional
```

**What Happens:**
- POST request to `/api/admin/organizations`
- System creates new database: `tech_valuations_llc_xxx`
- Collections auto-created: reports, custom_templates, users_settings, activity_logs, files_metadata
- Returns organization_id (e.g., `tech_valuations_llc_003`)

### 4. Add Manager User

Click "👥 Manage Users" on the new organization.

**Add Manager:**
```
Full Name: Sarah Johnson
Email Address: sarah.johnson@techvaluations.com
Password: manager123
Role: 👔 Manager (Can submit reports & view logs)
```

**What Happens:**
- POST request to `/api/admin/organizations/{org_id}/users`
- User created in valuation_admin.users collection
- User gets permissions: create, read, update, delete, submit
- User can view activity logs

### 5. Add Employee User

Click "➕ Add User" again.

**Add Employee:**
```
Full Name: Mike Davis
Email Address: mike.davis@techvaluations.com
Password: employee123
Role: 👤 Employee (Can create/edit reports only)
```

**What Happens:**
- POST request to `/api/admin/organizations/{org_id}/users`
- User created with employee role
- User gets permissions: create, read, update (NO submit, NO logs access)

### 6. Test Manager Login

Logout and login as Manager:
```
Email: sarah.johnson@techvaluations.com
Password: manager123
```

**Manager Can:**
- Create reports: POST `/api/reports`
- Update reports: PUT `/api/reports/{id}`
- **Submit reports**: POST `/api/reports/{id}/submit` ✅
- **View activity logs**: GET `/api/reports/{id}/activity` ✅

**Test Commands:**
```bash
# Login as Manager
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah.johnson@techvaluations.com",
    "password": "manager123"
  }'

# Create Report
curl -X POST http://localhost:8000/api/reports \
  -H "Authorization: Bearer <manager_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Property Valuation Report",
    "property_address": "123 Main St",
    "valuation_amount": 450000
  }'

# Submit Report (Manager ONLY)
curl -X POST http://localhost:8000/api/reports/<report_id>/submit \
  -H "Authorization: Bearer <manager_token>"

# View Activity Logs (Manager ONLY)
curl http://localhost:8000/api/reports/<report_id>/activity \
  -H "Authorization: Bearer <manager_token>"
```

### 7. Test Employee Login

Logout and login as Employee:
```
Email: mike.davis@techvaluations.com
Password: employee123
```

**Employee Can:**
- Create reports: POST `/api/reports` ✅
- Update reports: PUT `/api/reports/{id}` ✅

**Employee CANNOT:**
- Submit reports: POST `/api/reports/{id}/submit` ❌ (403 Forbidden)
- View activity logs: GET `/api/reports/{id}/activity` ❌ (403 Forbidden)

**Test Commands:**
```bash
# Login as Employee
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mike.davis@techvaluations.com",
    "password": "employee123"
  }'

# Create Report (Works)
curl -X POST http://localhost:8000/api/reports \
  -H "Authorization: Bearer <employee_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Employee Report",
    "property_address": "789 Oak Ave",
    "valuation_amount": 350000
  }'

# Try to Submit Report (FAILS with 403)
curl -X POST http://localhost:8000/api/reports/<report_id>/submit \
  -H "Authorization: Bearer <employee_token>"

# Expected Response:
# {
#   "detail": "Only Managers can submit reports"
# }

# Try to View Logs (FAILS with 403)
curl http://localhost:8000/api/reports/<report_id>/activity \
  -H "Authorization: Bearer <employee_token>"

# Expected Response:
# {
#   "detail": "Only Managers can view activity logs"
# }
```

### 8. Update User Role

System Admin can change user roles:

1. Navigate to organization's user management
2. Click "✏️ Edit Role" on Employee user
3. Change role to Manager
4. User now has submit and view logs permissions

**API Call:**
```bash
curl -X PUT http://localhost:8000/api/admin/users/<user_id>/role \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "manager"
  }'
```

## Activity Logging

All actions are logged in `{org_id}.activity_logs` collection:

**Example Activity Log Entry:**
```json
{
  "_id": ObjectId("..."),
  "user_id": "usr_abc123",
  "user_name": "Sarah Johnson",
  "user_email": "sarah.johnson@techvaluations.com",
  "user_role": "manager",
  "action": "report_submitted",
  "resource_type": "report",
  "resource_id": "rpt_xyz789",
  "details": {
    "message": "Report submitted successfully by Manager",
    "report_title": "Property Valuation Report"
  },
  "ip_address": "127.0.0.1",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Log Actions:**
- `report_created`: When any user creates a report
- `report_updated`: When any user updates a report
- `report_submitted`: When Manager submits a report
- `user_created`: When System Admin adds a user
- `role_updated`: When System Admin changes user role

## Permission Matrix

| Action | System Admin | Manager | Employee |
|--------|-------------|---------|----------|
| Create Organizations | ✅ | ❌ | ❌ |
| Add Users | ✅ | ❌ | ❌ |
| Update User Roles | ✅ | ❌ | ❌ |
| Create Reports | ✅ | ✅ | ✅ |
| Update Reports | ✅ | ✅ | ✅ |
| Submit Reports | ✅ | ✅ | ❌ |
| View Activity Logs | ✅ | ✅ | ❌ |
| Delete Reports | ✅ | ✅ | ❌ |

## Frontend Role Helpers

Auth service provides role checking methods:

```typescript
// Check if user can submit reports
const canSubmit = authService.canSubmitReports(); // true for Manager, false for Employee

// Check if user can view activity logs
const canViewLogs = authService.canViewActivityLogs(); // true for Manager, false for Employee

// Get fresh user data from backend
authService.getCurrentUserFromBackend().subscribe(user => {
  console.log('User permissions:', user.permissions);
});
```

## Troubleshooting

### Issue: "User not found in database"
**Solution:** Ensure user exists in `valuation_admin.users` collection. System Admin must add users via the admin UI.

### Issue: "403 Forbidden" when Employee tries to submit
**Expected Behavior:** This is correct. Only Managers can submit reports.

### Issue: Organization database not created
**Solution:** Check backend logs. Database creation happens in `create_organization()` endpoint.

### Issue: Activity logs not showing
**Solution:** 
1. Ensure `log_activity()` is being called in endpoints
2. Check `{org_id}.activity_logs` collection exists
3. Verify user context is being passed correctly

## Verification Checklist

- [ ] System Admin can login and see Admin link in header
- [ ] System Admin can view list of organizations
- [ ] System Admin can create new organization
- [ ] Database auto-created with correct collections
- [ ] System Admin can add Manager user to organization
- [ ] System Admin can add Employee user to organization
- [ ] Manager can login and create reports
- [ ] Manager can submit reports successfully
- [ ] Manager can view activity logs
- [ ] Employee can login and create reports
- [ ] Employee CANNOT submit reports (403 error)
- [ ] Employee CANNOT view activity logs (403 error)
- [ ] Activity logs capture all actions correctly
- [ ] System Admin can update user roles
- [ ] Role change takes effect immediately

## Success Criteria

✅ **Backend:**
- Organization CRUD APIs working
- User management APIs working
- Role-based permission enforcement
- Activity logging on all report actions
- Database auto-creation

✅ **Frontend:**
- Organizations list component displays all orgs
- Create organization dialog works
- User management interface functional
- Role assignment UI working
- Auth service role helpers available
- Admin routes protected by systemAdminGuard

✅ **Integration:**
- End-to-end flow from org creation to role-based report access
- Manager can submit, Employee cannot
- Manager can view logs, Employee cannot
- Activity logs show complete audit trail
- Multi-tenant isolation (each org has own database)
