# Activity Logging System - Phase 3 Implementation

## Overview
Complete activity logging system to track all user actions across the valuation application.

## Backend Implementation ✅

### 1. ActivityLogEntry Entity
**File:** `backend-dotnet/ValuationApp.Core/Entities/ActivityLogEntry.cs`
- Standalone entity for activity_logs collection
- Properties:
  - `UserId`, `OrgShortName` - User and organization identifiers
  - `Action`, `ActionType` - What action and category
  - `Description` - Human-readable description
  - `EntityType`, `EntityId` - What entity was affected (optional)
  - `Metadata` - Additional context (JSON dictionary)
  - `IpAddress`, `UserAgent` - Request metadata (auto-captured)
  - `Timestamp`, `CreatedAt` - When action occurred

### 2. Activity Logging Service
**File:** `backend-dotnet/ValuationApp.Infrastructure/Services/ActivityLoggingService.cs`

**Key Methods:**
- `LogActivityAsync()` - Create new activity log entry
- `GetUserActivityAsync()` - Get activities for specific user
- `GetOrgActivityAsync()` - Get activities for organization
- `GetAllActivityAsync()` - Get all activities (system admin)
- `GetActivitiesByTypeAsync()` - Filter by action type
- `GetEntityActivityAsync()` - Get all activities on an entity (e.g., report)
- `GetActivitiesByDateRangeAsync()` - Filter by date range
- `GetActivityCountsByTypeAsync()` - Analytics data

**Features:**
- Pagination support (limit, skip)
- Flexible filtering (user, org, type, entity, date range)
- Error handling and logging
- Indexes for performance (on user_id, org_short_name, timestamp)

### 3. Activity Logs Controller
**File:** `backend-dotnet/ValuationApp.API/Controllers/ActivityLogsController.cs`

**Endpoints:**
```
POST   /api/activity-logs                        - Log new activity
GET    /api/activity-logs/user/{userId}          - Get user activity
GET    /api/activity-logs/org/{orgShortName}     - Get org activity
GET    /api/activity-logs/all                    - Get all activity
GET    /api/activity-logs/type/{actionType}      - Get by action type
GET    /api/activity-logs/entity/{type}/{id}     - Get entity activity
GET    /api/activity-logs/date-range             - Get by date range
GET    /api/activity-logs/analytics/counts       - Get activity counts
```

**Security Note:** All endpoints should be protected with permission checks in production.

### 4. MongoDB Integration
**File:** `backend-dotnet/ValuationApp.Infrastructure/Data/MongoDbContext.cs`
- Added `ActivityLogs` collection property
- Collection: `activity_logs` in admin database

### 5. Service Registration
**File:** `backend-dotnet/ValuationApp.API/Program.cs`
- Registered `IActivityLoggingService` → `ActivityLoggingService` as scoped service

### Backend Testing ✅
```bash
# Test: Log activity
curl -X POST http://localhost:8000/api/activity-logs \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-123",
    "orgShortName": "TEST",
    "action": "login",
    "actionType": "authentication",
    "description": "User logged in"
  }'
# Response: {"success":true,"data":{"id":"696ceb1c3a47202f2ba56e92"}}

# Test: Get user activity
curl http://localhost:8000/api/activity-logs/user/test-user-123
# Response: Activity logs array with IP address, user agent, timestamps
```

## Frontend Implementation ✅

### 1. Activity Log Models
**File:** `valuation-frontend/src/app/models/activity-log.model.ts`

**Interfaces:**
- `ActivityLogEntry` - Matches backend entity
- `LogActivityRequest` - Request payload
- `ActivityLogResponse` - API response wrapper

**Enums & Constants:**
- `ActionType` enum - 8 action categories
- `CommonActions` object - Pre-defined action names for each category:
  ```typescript
  CommonActions.AUTHENTICATION.LOGIN
  CommonActions.USER.CREATE
  CommonActions.REPORT.SUBMIT
  CommonActions.TEMPLATE.UPDATE
  // etc...
  ```

### 2. Activity Logging Service
**File:** `valuation-frontend/src/app/services/activity-logging.service.ts`

**Core Methods:**
- `logActivity()` - Generic logging (fire-and-forget, doesn't block UI)
- `logAuthActivity()` - Authentication actions
- `logOrgActivity()` - Organization actions
- `logUserActivity()` - User management actions
- `logReportActivity()` - Report actions
- `logTemplateActivity()` - Template actions
- `logDraftActivity()` - Draft actions
- `logSettingsActivity()` - Settings changes

**Query Methods (return Observables):**
- `getUserActivity()` - Get user's activity history
- `getOrgActivity()` - Get organization activity
- `getAllActivity()` - Get all activities (system admin)
- `getActivitiesByType()` - Filter by action type
- `getEntityActivity()` - Get entity's activity
- `getActivitiesByDateRange()` - Filter by date
- `getActivityCountsByType()` - Analytics data

**Features:**
- Fire-and-forget logging (doesn't block UI or cause failures)
- Error handling with fallback
- Convenient helper methods for each activity type
- Observable-based for retrieving logs

### 3. Auth Service Integration ✅
**File:** `valuation-frontend/src/app/services/auth.service.ts`

**Integrated Activity Logging:**
1. **Login Success:**
   - Logs authentication activity with user email, role
   - Fires after permissions are loaded

2. **Logout:**
   - Logs logout activity before clearing auth
   - Includes user context in metadata

**Usage Example:**
```typescript
// Login activity (automatic)
this.activityLoggingService.logAuthActivity(
  userId,
  orgShortName,
  CommonActions.AUTHENTICATION.LOGIN,
  'User logged in successfully',
  { role, email }
);

// Logout activity (automatic)
this.activityLoggingService.logAuthActivity(
  userId,
  orgShortName,
  CommonActions.AUTHENTICATION.LOGOUT,
  'User logged out',
  { role, email }
);
```

## Action Types & Categories

### 1. Authentication
- `login` - User login
- `logout` - User logout
- `token_refresh` - Token refresh
- `password_change` - Password change

### 2. Organization
- `create_organization` - New organization created
- `update_organization` - Organization updated
- `delete_organization` - Organization deleted
- `view_organization` - Organization details viewed

### 3. User Management
- `create_user` - New user created
- `update_user` - User updated
- `delete_user` - User deleted
- `activate_user` - User activated
- `deactivate_user` - User deactivated
- `change_user_role` - User role changed
- `view_user` - User profile viewed

### 4. Reports
- `create_report` - Report created
- `update_report` - Report updated
- `delete_report` - Report deleted
- `submit_report` - Report submitted for approval
- `export_report` - Report exported
- `view_report` - Report viewed

### 5. Templates
- `create_template` - Custom template created
- `update_template` - Template updated
- `delete_template` - Template deleted
- `view_template` - Template viewed

### 6. Drafts
- `create_draft` - Draft created
- `update_draft` - Draft updated
- `delete_draft` - Draft deleted
- `view_draft` - Draft viewed

### 7. Settings
- `update_org_settings` - Organization settings changed
- `update_system_settings` - System settings changed
- `view_settings` - Settings page viewed

### 8. Analytics
- `view_analytics_dashboard` - Analytics dashboard viewed
- `export_analytics_report` - Analytics report exported

## Usage Examples

### In Components

```typescript
import { ActivityLoggingService } from '../services/activity-logging.service';
import { CommonActions } from '../models/activity-log.model';

export class ReportFormComponent {
  constructor(
    private authService: AuthService,
    private activityLoggingService: ActivityLoggingService
  ) {}

  saveReport() {
    const user = this.authService.getCurrentUser();
    
    // Save report...
    
    // Log activity
    this.activityLoggingService.logReportActivity(
      user.user_id,
      user.org_short_name,
      CommonActions.REPORT.CREATE,
      `Created report: ${reportName}`,
      reportId,
      { reportType, propertyType }
    );
  }

  submitReport() {
    const user = this.authService.getCurrentUser();
    
    // Submit report...
    
    // Log activity
    this.activityLoggingService.logReportActivity(
      user.user_id,
      user.org_short_name,
      CommonActions.REPORT.SUBMIT,
      `Submitted report ${reportId} for approval`,
      reportId,
      { status: 'submitted', submittedBy: user.email }
    );
  }
}
```

### Viewing Activity Logs

```typescript
// Get user's own activity
this.activityLoggingService.getUserActivity(userId, 50)
  .subscribe(response => {
    if (response.success) {
      this.activities = response.data as ActivityLogEntry[];
    }
  });

// Get organization activity (for managers/admins)
this.activityLoggingService.getOrgActivity(orgShortName, 100)
  .subscribe(response => {
    if (response.success) {
      this.orgActivities = response.data as ActivityLogEntry[];
    }
  });

// Get activity for specific report
this.activityLoggingService.getEntityActivity('report', reportId)
  .subscribe(response => {
    if (response.success) {
      this.reportHistory = response.data as ActivityLogEntry[];
    }
  });
```

## Next Steps (Remaining Work)

### 1. Activity Viewer UI Component
**Priority:** HIGH
**Time Estimate:** 2-3 hours

Create components for viewing activity logs:
- `ActivityLogComponent` - List view with filtering
- `ActivityDetailComponent` - Detailed view of single activity
- `ActivityDashboardComponent` - Analytics/charts for managers

**Features:**
- Filter by user, action type, date range, entity
- Search functionality
- Pagination
- Export to CSV
- Real-time updates (optional)

**Permissions:**
- Employees: View own activity only
- Managers: View organization activity
- System Admin: View all activity

### 2. Integrate Logging Throughout Application
**Priority:** MEDIUM
**Time Estimate:** 3-4 hours

Add activity logging to:
- ✅ **Authentication:** login, logout (COMPLETED)
- ⏳ **Organization Management:** create, update, delete
- ⏳ **User Management:** create, update, delete, role changes
- ⏳ **Reports:** create, edit, delete, submit, export, view
- ⏳ **Templates:** create, edit, delete
- ⏳ **Drafts:** create, edit, delete
- ⏳ **Settings:** organization settings, system settings

### 3. Add Permission Checks to Activity Log Endpoints
**Priority:** MEDIUM
**Time Estimate:** 1 hour

Protect endpoints with permission middleware:
- `/user/{userId}` - Only owner or managers/admins
- `/org/{orgShortName}` - Only org members with analytics permission
- `/all` - System admins only
- Other endpoints - Based on analytics permissions

### 4. Create Database Indexes
**Priority:** LOW
**Time Estimate:** 30 minutes

Create MongoDB indexes for performance:
```javascript
db.activity_logs.createIndex({ user_id: 1, timestamp: -1 });
db.activity_logs.createIndex({ org_short_name: 1, timestamp: -1 });
db.activity_logs.createIndex({ action_type: 1, timestamp: -1 });
db.activity_logs.createIndex({ entity_type: 1, entity_id: 1, timestamp: -1 });
db.activity_logs.createIndex({ timestamp: -1 });
```

### 5. Testing
**Priority:** LOW
**Time Estimate:** 1-2 hours

Test scenarios:
- Login/logout logging works
- All action types log correctly
- Filtering/pagination works
- Permissions enforced
- Performance with large log volumes
- Activity viewer UI displays correctly

## Files Created

### Backend
1. `ValuationApp.Core/Entities/ActivityLogEntry.cs` - Activity log entity
2. `ValuationApp.Core/Interfaces/IActivityLoggingService.cs` - Service interface
3. `ValuationApp.Infrastructure/Services/ActivityLoggingService.cs` - Service implementation
4. `ValuationApp.API/Controllers/ActivityLogsController.cs` - API endpoints

### Frontend
1. `models/activity-log.model.ts` - TypeScript interfaces and constants
2. `services/activity-logging.service.ts` - Frontend logging service

### Updated Files
- `ValuationApp.Infrastructure/Data/MongoDbContext.cs` - Added ActivityLogs collection
- `ValuationApp.API/Program.cs` - Registered ActivityLoggingService
- `valuation-frontend/src/app/services/auth.service.ts` - Integrated login/logout logging

## Status

**Phase 3 Progress:** 60% Complete

✅ **Completed:**
- Backend activity logging service
- Backend API endpoints
- Frontend activity logging service
- Integration with auth service (login/logout)
- Data models and interfaces
- Testing (basic)

⏳ **Remaining:**
- Activity viewer UI components
- Integrate logging throughout application
- Permission checks on endpoints
- Database indexes
- Comprehensive testing
- Activity dashboard/analytics UI

## Summary

Phase 3 provides a solid foundation for activity logging:
- **Fire-and-forget logging** doesn't block UI operations
- **Flexible filtering** by user, org, type, entity, date
- **Analytics support** with aggregated counts
- **Auto-capture** of IP address and user agent
- **Structured metadata** for rich context
- **Type-safe** with enums and constants

The system is ready for integration throughout the application. Next priority is creating the activity viewer UI and adding logging calls to all user actions.
