import { Routes } from '@angular/router';
// Import organization management guards as additional features
import { authGuard, managerGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Main valuation app routes
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./components/login/login').then(m => m.Login)
  },
  { 
    path: 'dashboard', 
    loadComponent: () => import('./components/dashboard/dashboard').then(m => m.Dashboard)
  },
  { 
    path: 'new-report', 
    loadComponent: () => import('./components/new-report/new-report').then(m => m.NewReport)
  },
  { 
    path: 'report-form', 
    loadComponent: () => import('./components/report-form/report-form').then(m => m.ReportForm)
  },
  { 
    path: 'admin', 
    loadComponent: () => import('./components/admin/admin').then(m => m.Admin)
  },
  { 
    path: 'reports', 
    loadComponent: () => import('./components/reports/reports').then(m => m.Reports)
  },
  { 
    path: 'banks', 
    loadComponent: () => import('./components/banks/banks').then(m => m.Banks)
  },
  { 
    path: 'bank-details/:id', 
    loadComponent: () => import('./components/bank-details/bank-details').then(m => m.BankDetails)
  },
  { 
    path: 'logs', 
    loadComponent: () => import('./components/log-viewer.component').then(m => m.LogViewerComponent)
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
  }
];
