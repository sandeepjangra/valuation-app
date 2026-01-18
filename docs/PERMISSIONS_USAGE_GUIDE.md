# Permission System Usage Guide

## Overview
The RBAC (Role-Based Access Control) system is now fully integrated into the Angular frontend.

## Quick Start

### 1. In Templates (Show/Hide Elements)

```typescript
<!-- Show button only if user can create reports -->
<button *hasPermission="'reports.create'">
  Create Report
</button>

<!-- Show section only if user can manage users -->
<div *hasPermission="'users.create'">
  <h2>User Management</h2>
  <!-- User management UI -->
</div>

<!-- Multiple permissions (ALL must be true) -->
<button *hasPermission="['reports.create', 'reports.submit']" hasPermissionMode="all">
  Create & Submit Report
</button>

<!-- Multiple permissions (ANY can be true) -->
<div *hasPermission="['analytics.viewOrgActivity', 'analytics.viewAllActivity']" hasPermissionMode="any">
  <h2>Analytics Dashboard</h2>
</div>
```

### 2. In Component Code

```typescript
import { PermissionsService } from './services/permissions.service';

export class MyComponent {
  private permissionsService = inject(PermissionsService);

  ngOnInit() {
    // Check single permission
    if (this.permissionsService.hasPermission('reports.create')) {
      console.log('User can create reports');
    }

    // Check multiple permissions (AND)
    if (this.permissionsService.hasAllPermissions(['users.create', 'users.editAny'])) {
      console.log('User can fully manage users');
    }

    // Check multiple permissions (OR)
    if (this.permissionsService.hasAnyPermission(['reports.submit', 'reports.editOthers'])) {
      console.log('User has some report management permissions');
    }

    // Helper methods
    if (this.permissionsService.canManageUsers()) {
      this.loadUserManagementTools();
    }

    if (this.permissionsService.canSubmitReports()) {
      this.showSubmitButton = true;
    }

    // Get user role
    const role = this.permissionsService.getUserRole();
    console.log('User role:', role); // 'system_admin' | 'org_admin' | 'employee'

    // Check if system admin
    if (this.permissionsService.isUserSystemAdmin()) {
      this.showAdminPanel = true;
    }
  }
}
```

### 3. In Route Guards

```typescript
// app.routes.ts
import { PermissionGuard, RoleGuard } from './guards/permission.guard';

export const routes: Routes = [
  {
    path: 'admin/organizations',
    component: OrganizationsComponent,
    canActivate: [PermissionGuard],
    data: {
      permissions: ['organizations.viewAll'],
      mode: 'all'
    }
  },
  {
    path: 'admin/users',
    component: UsersComponent,
    canActivate: [PermissionGuard],
    data: {
      permissions: ['users.create', 'users.editAny'],
      mode: 'any' // User needs at least one of these
    }
  },
  {
    path: 'reports/submit',
    component: SubmitReportComponent,
    canActivate: [RoleGuard],
    data: {
      roles: ['system_admin', 'org_admin'] // Only these roles can access
    }
  }
];
```

## Available Permissions

### Organizations
- `organizations.viewAll` - View all organizations (system admin)
- `organizations.create` - Create new organizations
- `organizations.editAny` - Edit any organization
- `organizations.delete` - Delete organizations
- `organizations.manageSettings` - Manage org settings

### Users
- `users.viewAllOrgs` - View users across all orgs
- `users.viewOwnOrg` - View users in own org
- `users.create` - Create new users
- `users.editAny` - Edit any user
- `users.deleteAny` - Delete users
- `users.viewActivity` - View user activity logs
- `users.manageRoles` - Assign/change user roles

### Reports
- `reports.create` - Create new reports
- `reports.editOwn` - Edit own reports
- `reports.editOthers` - Edit others' reports
- `reports.deleteOwn` - Delete own reports
- `reports.deleteOthers` - Delete others' reports
- `reports.viewDrafts` - View draft reports
- `reports.saveDraft` - Save reports as drafts
- `reports.submit` - Submit reports (approval)
- `reports.viewAllOrg` - View all reports in org
- `reports.viewAllOrgs` - View reports across all orgs
- `reports.export` - Export reports

### Templates
- `templates.view` - View templates
- `templates.viewBankTemplates` - View bank templates
- `templates.createCustom` - Create custom templates
- `templates.editCustom` - Edit custom templates
- `templates.deleteCustom` - Delete custom templates
- `templates.manageBankTemplates` - Manage bank templates
- `templates.shareAcrossOrgs` - Share templates across orgs

### Drafts
- `drafts.create` - Create drafts
- `drafts.editOwn` - Edit own drafts
- `drafts.editOthers` - Edit others' drafts
- `drafts.viewOwn` - View own drafts
- `drafts.viewOthers` - View others' drafts
- `drafts.deleteOwn` - Delete own drafts
- `drafts.deleteOthers` - Delete others' drafts

### Analytics
- `analytics.viewOwnActivity` - View own activity
- `analytics.viewOrgActivity` - View org-wide activity
- `analytics.viewAllActivity` - View all activity (system-wide)
- `analytics.exportReports` - Export analytics reports

### Settings
- `settings.editOrgSettings` - Edit organization settings
- `settings.editSystemSettings` - Edit system-wide settings
- `settings.manageIntegrations` - Manage integrations
- `settings.viewLogs` - View system logs

## Helper Methods

```typescript
permissionsService.canManageOrganizations()  // Can create/edit orgs
permissionsService.canManageUsers()          // Can create/edit users
permissionsService.canSubmitReports()        // Can submit (approve) reports
permissionsService.canCreateCustomTemplates() // Can create templates
permissionsService.canViewAnalytics()        // Can view analytics
permissionsService.canManageSettings()       // Can manage settings
```

## Example: Navigation Menu with Permissions

```typescript
@Component({
  template: `
    <nav>
      <a routerLink="/dashboard">Dashboard</a>
      
      <a routerLink="/reports" *hasPermission="'reports.create'">
        Reports
      </a>
      
      <a routerLink="/templates" *hasPermission="'templates.view'">
        Templates
      </a>
      
      <a routerLink="/admin/users" *hasPermission="'users.viewOwnOrg'">
        Users
      </a>
      
      <a routerLink="/admin/organizations" *hasPermission="'organizations.viewAll'">
        Organizations
      </a>
      
      <a routerLink="/analytics" *hasPermission="['analytics.viewOrgActivity', 'analytics.viewAllActivity']" hasPermissionMode="any">
        Analytics
      </a>
      
      <a routerLink="/settings" *hasPermission="'settings.editOrgSettings'">
        Settings
      </a>
    </nav>
  `
})
export class NavigationComponent {
  // Navigation items will automatically show/hide based on permissions
}
```

## Role Comparison

| Permission | System Admin | Org Admin | Employee |
|-----------|--------------|-----------|----------|
| View all orgs | ✅ | ❌ | ❌ |
| Manage own org | ✅ | ✅ | ❌ |
| Create users | ✅ | ✅ (own org) | ❌ |
| Create reports | ✅ | ✅ | ✅ |
| Edit any report | ✅ | ✅ (own org) | ✅ (own org) |
| Submit reports | ✅ | ✅ | ❌ |
| Create templates | ✅ | ✅ (custom) | ❌ |
| View analytics | ✅ (all) | ✅ (own org) | ✅ (own only) |
| Manage settings | ✅ (all) | ✅ (own org) | ❌ |

## Testing Permissions

1. **Login as different roles** to see different UI elements
2. **Check browser console** for permission loading logs
3. **Try accessing protected routes** - should redirect to /unauthorized
4. **Check API calls** - permissions should be enforced on backend too

## Notes

- Permissions are loaded automatically on login
- Permissions are cached in memory
- Permissions are cleared on logout
- Backend should also enforce permissions (don't rely on frontend only!)
- The `*hasPermission` directive is reactive - it updates when permissions change
