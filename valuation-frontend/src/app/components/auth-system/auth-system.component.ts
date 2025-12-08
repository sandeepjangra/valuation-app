import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

interface AuthTest {
  email: string;
  password: string;
  expectedOrg: string;
  expectedRole: string;
  status: 'pending' | 'success' | 'failed';
  result?: any;
  error?: string;
}

@Component({
  selector: 'app-auth-system',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth-system.component.html',
  styleUrls: ['./auth-system.component.css']
})
export class AuthSystemComponent implements OnInit {
  readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  readonly isLoading = signal<boolean>(false);
  readonly activeTab = signal<string>('overview');
  readonly testResults = signal<AuthTest[]>([]);

  readonly currentAuth = computed(() => ({
    isAuthenticated: this.authService.isAuthenticated(),
    user: this.authService.currentUser(),
    orgContext: this.authService.getOrganizationContext(),
    isSystemAdmin: this.authService.isSystemAdmin(),
    isManager: this.authService.isManager(),
    isEmployee: this.authService.isEmployee()
  }));

  readonly testUsers: AuthTest[] = [
    {
      email: 'admin@system.com',
      password: 'admin',
      expectedOrg: 'system-administration',
      expectedRole: 'system_admin',
      status: 'pending'
    },
    {
      email: 'sk.tindwal@gmail.com',
      password: 'admin',
      expectedOrg: 'sk-tindwal',
      expectedRole: 'manager',
      status: 'pending'
    },
    {
      email: 'sanjeev.jangra@gmail.com',
      password: 'admin',
      expectedOrg: 'sk-tindwal',
      expectedRole: 'employee',
      status: 'pending'
    },
    {
      email: 'yjangra007@gmail.com',
      password: 'admin',
      expectedOrg: 'yogesh-jangra',
      expectedRole: 'manager',
      status: 'pending'
    },
    {
      email: 'lucky.jangra@gmail.com',
      password: 'admin',
      expectedOrg: 'yogesh-jangra',
      expectedRole: 'employee',
      status: 'pending'
    }
  ];

  ngOnInit() {
    this.testResults.set([...this.testUsers]);
  }

  setActiveTab(tab: string) {
    this.activeTab.set(tab);
  }

  async testSingleUser(test: AuthTest) {
    this.isLoading.set(true);
    
    try {
      if (this.authService.isAuthenticated()) {
        await this.authService.logout().toPromise();
      }

      const result = await this.authService.login({
        email: test.email,
        password: test.password
      }).toPromise();

      if (result && this.authService.isAuthenticated()) {
        const orgContext = this.authService.getOrganizationContext();
        
        const orgMatch = orgContext?.orgShortName === test.expectedOrg;
        const roleMatch = orgContext?.roles.includes(test.expectedRole as any);
        
        if (orgMatch && roleMatch) {
          test.status = 'success';
          test.result = {
            organization: orgContext.orgShortName,
            roles: orgContext.roles,
            isSystemAdmin: orgContext.isSystemAdmin,
            isManager: orgContext.isManager
          };
        } else {
          test.status = 'failed';
          test.error = `Expected org: ${test.expectedOrg}, got: ${orgContext?.orgShortName}. Expected role: ${test.expectedRole}, got: ${orgContext?.roles.join(', ')}`;
        }
      } else {
        test.status = 'failed';
        test.error = 'Login failed - no authentication result';
      }
    } catch (error: any) {
      test.status = 'failed';
      test.error = error.message || 'Login failed';
    }

    this.isLoading.set(false);
    this.updateTestResults();
  }

  async testAllUsers() {
    this.isLoading.set(true);
    
    for (const test of this.testResults()) {
      await this.testSingleUser(test);
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    this.isLoading.set(false);
  }

  async loginAsUser(email: string, password: string) {
    this.isLoading.set(true);
    
    try {
      await this.authService.login({ email, password }).toPromise();
      
      if (this.authService.isAuthenticated()) {
        const orgContext = this.authService.getOrganizationContext();
        if (orgContext?.isSystemAdmin) {
          this.router.navigate(['/admin']);
        } else {
          this.router.navigate(['/org', orgContext?.orgShortName, 'dashboard']);
        }
      }
    } catch (error: any) {
      console.error('Login failed:', error);
    }
    
    this.isLoading.set(false);
  }

  async logout() {
    await this.authService.logout().toPromise();
  }

  resetTests() {
    this.testResults.set([...this.testUsers]);
  }

  private updateTestResults() {
    this.testResults.set([...this.testResults()]);
  }

  getPermissionsList(): string[] {
    const orgContext = this.authService.getOrganizationContext();
    if (!orgContext) return [];

    const permissions: string[] = [];
    
    const permissionChecks = [
      { resource: 'reports', action: 'create', label: 'Create Reports' },
      { resource: 'reports', action: 'read', label: 'Read Reports' },
      { resource: 'reports', action: 'update', label: 'Update Reports' },
      { resource: 'reports', action: 'delete', label: 'Delete Reports' },
      { resource: 'reports', action: 'submit', label: 'Submit Reports' },
      { resource: 'users', action: 'create', label: 'Create Users' },
      { resource: 'users', action: 'read', label: 'Read Users' },
      { resource: 'users', action: 'update', label: 'Update Users' },
      { resource: 'users', action: 'delete', label: 'Delete Users' },
      { resource: 'audit_logs', action: 'read', label: 'View Audit Logs' },
      { resource: 'organizations', action: 'read', label: 'Read Organizations' },
      { resource: 'organizations', action: 'create', label: 'Create Organizations' },
      { resource: 'organizations', action: 'update', label: 'Update Organizations' },
      { resource: 'organizations', action: 'delete', label: 'Delete Organizations' }
    ];

    for (const check of permissionChecks) {
      if (this.authService.hasPermission(check.resource, check.action)) {
        permissions.push(check.label);
      }
    }

    return permissions;
  }
}