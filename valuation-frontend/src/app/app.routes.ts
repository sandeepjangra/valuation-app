import { Routes } from '@angular/router';
// Import organization management guards as additional features
import { authGuard, managerGuard, systemAdminGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Main valuation app routes
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  { 
    path: 'dashboard', 
    loadComponent: () => import('./components/dashboard/dashboard').then(m => m.Dashboard),
    canActivate: [authGuard()]
  },
  { 
    path: 'new-report', 
    loadComponent: () => import('./components/new-report/new-report').then(m => m.NewReport),
    canActivate: [authGuard()]
  },
  { 
    path: 'report-form', 
    loadComponent: () => import('./components/report-form/report-form').then(m => m.ReportForm),
    canActivate: [authGuard()]
  },
  // Admin routes for system administrators
  {
    path: 'admin',
    canActivate: [systemAdminGuard()],
    children: [
      {
        path: '',
        redirectTo: 'organizations',
        pathMatch: 'full'
      },
      {
        path: 'organizations',
        loadComponent: () => 
          import('./components/admin/organizations/organizations-list.component')
            .then(m => m.OrganizationsListComponent),
        title: 'Organizations - System Admin'
      },
      {
        path: 'organizations/:orgId/users',
        loadComponent: () => 
          import('./components/admin/users/manage-users.component')
            .then(m => m.ManageUsersComponent),
        title: 'Manage Users - System Admin'
      }
    ]
  },
  { 
    path: 'reports', 
    loadComponent: () => import('./components/reports/reports').then(m => m.Reports),
    canActivate: [authGuard()]
  },
  { 
    path: 'banks', 
    loadComponent: () => import('./components/banks/banks').then(m => m.Banks),
    canActivate: [authGuard()]
  },
  { 
    path: 'bank-details/:id', 
    loadComponent: () => import('./components/bank-details/bank-details').then(m => m.BankDetails),
    canActivate: [authGuard()]
  },
  { 
    path: 'logs', 
    loadComponent: () => import('./components/log-viewer.component').then(m => m.LogViewerComponent),
    canActivate: [authGuard()]
  },
  
  // User profile route
  { 
    path: 'profile', 
    loadComponent: () => import('./components/user-profile/user-profile.component').then(m => m.UserProfileComponent),
    canActivate: [authGuard],
    title: 'User Profile - Valuation App'
  },
  
  // Organization management routes (additional functionality)
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

  // Custom Templates Management
  {
    path: 'custom-templates',
    canActivate: [authGuard, managerGuard],
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
