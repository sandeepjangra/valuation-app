import { Routes } from '@angular/router';
// Import organization management guards as additional features
import { authGuard, managerGuard, systemAdminGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Main valuation app routes - redirect to system admin by default
  { path: '', redirectTo: '/org/system-administration/dashboard', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  
  // User profile route
  { 
    path: 'profile', 
    loadComponent: () => import('./components/user-profile/user-profile.component').then(m => m.UserProfileComponent),
    canActivate: [authGuard],
    title: 'User Profile - Valuation App'
  },
  
  // Organization-based routes (NEW!)
  {
    path: 'org/:orgShortName',
    canActivate: [authGuard()],
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./components/dashboard/dashboard').then(m => m.Dashboard),
        title: 'Dashboard'
      },
      {
        path: 'reports',
        children: [
          {
            path: '',
            loadComponent: () => import('./components/reports/reports').then(m => m.Reports),
            title: 'Reports'
          },
          {
            path: 'new',
            loadComponent: () => import('./components/new-report/new-report').then(m => m.NewReport),
            title: 'New Report'
          },
          {
            path: 'create',
            loadComponent: () => import('./components/report-form/report-form').then(m => m.ReportForm),
            title: 'Create Report'
          },
          {
            path: ':id',
            loadComponent: () => import('./components/report-form/report-form').then(m => m.ReportForm),
            title: 'Edit Report'
          }
        ]
      },
      {
        path: 'banks',
        children: [
          {
            path: '',
            loadComponent: () => import('./components/banks/banks').then(m => m.Banks),
            title: 'Banks'
          },
          {
            path: ':id',
            loadComponent: () => import('./components/bank-details/bank-details').then(m => m.BankDetails),
            title: 'Bank Details'
          }
        ]
      },
      {
        path: 'users',
        loadComponent: () =>
          import('./components/user-management/user-management.component')
            .then(m => m.UserManagementComponent),
        canActivate: [managerGuard],
        title: 'User Management'
      },
      {
        path: 'logs',
        loadComponent: () => import('./components/log-viewer.component').then(m => m.LogViewerComponent),
        canActivate: [managerGuard],
        title: 'Activity Logs'
      },
      {
        path: 'custom-templates',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./components/custom-templates/custom-templates-management.component')
                .then(m => m.CustomTemplatesManagementComponent),
            title: 'Custom Templates'
          },
          {
            path: 'create',
            loadComponent: () =>
              import('./components/custom-templates/custom-template-form.component')
                .then(m => m.CustomTemplateFormComponent),
            title: 'Create Template'
          },
          {
            path: 'edit/:id',
            loadComponent: () =>
              import('./components/custom-templates/custom-template-form.component')
                .then(m => m.CustomTemplateFormComponent),
            title: 'Edit Template'
          }
        ]
      }
    ]
  },

  // Admin routes for system administrators
  {
    path: 'admin',
    canActivate: [systemAdminGuard()],
    children: [
      {
        path: '',
        loadComponent: () => 
          import('./components/admin/admin-dashboard.component')
            .then(m => m.AdminDashboardComponent),
        title: 'Admin Dashboard',
        children: [
          {
            path: '',
            redirectTo: 'overview',
            pathMatch: 'full'
          },
          {
            path: 'overview',
            loadComponent: () => 
              import('./components/admin/overview/admin-overview.component')
                .then(m => m.AdminOverviewComponent),
            title: 'Admin Overview'
          },
          {
            path: 'health',
            loadComponent: () => 
              import('./components/admin/health-check/health-check.component')
                .then(m => m.HealthCheckComponent),
            title: 'Health Check - Admin'
          },
          {
            path: 'activity',
            loadComponent: () => 
              import('./components/admin/activity-logs/activity-logs.component')
                .then(m => m.ActivityLogsComponent),
            title: 'Activity Logs - Admin'
          },
          {
            path: 'server-logs',
            loadComponent: () => 
              import('./components/admin/server-logs/server-logs.component')
                .then(m => m.ServerLogsComponent),
            title: 'Server Logs - Admin'
          },
          {
            path: 'organizations',
            loadComponent: () => 
              import('./components/admin/organizations/organizations-list.component')
                .then(m => m.OrganizationsListComponent),
            title: 'Organizations - System Admin'
          },
          {
            path: 'organizations/:orgId',
            loadComponent: () => 
              import('./components/admin/organizations/organization-details.component')
                .then(m => m.OrganizationDetailsComponent),
            title: 'Organization Details - System Admin'
          },
          {
            path: 'organizations/:orgId/users',
            loadComponent: () => 
              import('./components/admin/users/manage-users.component')
                .then(m => m.ManageUsersComponent),
            title: 'Manage Users - System Admin'
          }
        ]
      }
    ]
  },
  
  // Organization management routes (legacy, kept for backward compatibility)
  {
    path: 'organization',
    canActivate: [authGuard],
    children: [
      {
        path: 'users',
        loadComponent: () =>
          import('./components/user-management/user-management.component')
            .then(m => m.UserManagementComponent),
        canActivate: [managerGuard],
        title: 'User Management - Valuation App'
      }
    ]
  },

  // Custom Templates Management (legacy)
  {
    path: 'custom-templates',
    canActivate: [authGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./components/custom-templates/custom-templates-management.component')
            .then(m => m.CustomTemplatesManagementComponent),
        title: 'Custom Templates - Valuation App'
      },
      {
        path: 'create',
        loadComponent: () =>
          import('./components/custom-templates/custom-template-form.component')
            .then(m => m.CustomTemplateFormComponent),
        title: 'Create Template - Valuation App'
      },
      {
        path: 'edit/:id',
        loadComponent: () =>
          import('./components/custom-templates/custom-template-form.component')
            .then(m => m.CustomTemplateFormComponent),
        title: 'Edit Template - Valuation App'
      }
    ]
  }
];

