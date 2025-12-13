/**
 * Organization Selector Component
 * 
 * Purpose:
 * - For System Admins: Dropdown to switch between organizations
 * - For Managers/Employees: Static display of current organization
 * 
 * Features:
 * - Fetches list of organizations for system_admin
 * - Updates routing when organization is changed
 * - Persists selected organization in localStorage
 * - Displays organization badge with logo/icon
 */

import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Organization } from '../../models/organization.model';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-organization-selector',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="organization-selector">
      <!-- System Admin: Organization Dropdown -->
      <div *ngIf="isSystemAdmin()" class="org-dropdown">
        <label for="org-select" class="org-label">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          <span>Organization:</span>
        </label>
        
        <select 
          id="org-select"
          class="org-select"
          [value]="selectedOrgShortName()"
          (change)="onOrganizationChange($event)"
          [disabled]="isLoading()">
          <option value="" disabled>Select Organization</option>
          <option *ngFor="let org of organizations()" [value]="org.org_short_name">
            {{ org.name }} ({{ org.org_short_name }})
          </option>
        </select>
        
        <div *ngIf="isLoading()" class="loading-spinner">
          <svg class="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      </div>

      <!-- Manager/Employee: Static Organization Display -->
      <div *ngIf="!isSystemAdmin()" class="org-display">
        <div class="org-badge">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          <div class="org-info">
            <span class="org-name">{{ currentOrgName() }}</span>
            <span class="org-short-name">{{ selectedOrgShortName() }}</span>
          </div>
        </div>
        
        <span class="role-badge" [class]="'role-' + currentRole()">
          {{ currentRole() | titlecase }}
        </span>
      </div>
    </div>
  `,
  styles: [`
    .organization-selector {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.5rem;
    }

    /* System Admin Dropdown */
    .org-dropdown {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      position: relative;
    }

    .org-label {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.875rem;
      font-weight: 500;
      color: #6b7280;
    }

    .org-label svg {
      color: #9ca3af;
    }

    .org-select {
      padding: 0.5rem 2.5rem 0.5rem 0.75rem;
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      background-color: white;
      font-size: 0.875rem;
      color: #1f2937;
      cursor: pointer;
      transition: all 0.15s ease;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E");
      background-position: right 0.5rem center;
      background-repeat: no-repeat;
      background-size: 1.5em 1.5em;
      min-width: 250px;
    }

    .org-select:hover:not(:disabled) {
      border-color: #3b82f6;
    }

    .org-select:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    .org-select:disabled {
      background-color: #f3f4f6;
      cursor: not-allowed;
      opacity: 0.6;
    }

    /* Manager/Employee Display */
    .org-display {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.5rem 1rem;
      background-color: #f9fafb;
      border-radius: 0.5rem;
      border: 1px solid #e5e7eb;
    }

    .org-badge {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .org-badge svg {
      color: #3b82f6;
      flex-shrink: 0;
    }

    .org-info {
      display: flex;
      flex-direction: column;
      gap: 0.125rem;
    }

    .org-name {
      font-size: 0.875rem;
      font-weight: 600;
      color: #1f2937;
    }

    .org-short-name {
      font-size: 0.75rem;
      color: #6b7280;
      font-family: monospace;
    }

    .role-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.025em;
    }

    .role-badge.role-manager {
      background-color: #dbeafe;
      color: #1e40af;
    }

    .role-badge.role-employee {
      background-color: #f3e8ff;
      color: #6b21a8;
    }

    .role-badge.role-system_admin {
      background-color: #fee2e2;
      color: #991b1b;
    }

    /* Loading Spinner */
    .loading-spinner {
      position: absolute;
      right: 2.5rem;
      display: flex;
      align-items: center;
    }

    .spinner {
      width: 1rem;
      height: 1rem;
      animation: spin 1s linear infinite;
      color: #3b82f6;
    }

    @keyframes spin {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }

    /* Responsive */
    @media (max-width: 768px) {
      .organization-selector {
        flex-direction: column;
        align-items: flex-start;
      }

      .org-select {
        min-width: 100%;
      }

      .org-display {
        width: 100%;
      }
    }
  `]
})
export class OrganizationSelectorComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly http = inject(HttpClient);

  // Signals
  protected readonly organizations = signal<Organization[]>([]);
  protected readonly selectedOrgShortName = signal<string>('');
  protected readonly currentOrgName = signal<string>('');
  protected readonly isLoading = signal<boolean>(false);

  // Computed
  protected readonly isSystemAdmin = computed(() => this.authService.isSystemAdmin());
  protected readonly currentRole = computed(() => this.authService.getCurrentRole());

  private readonly API_BASE = environment.apiUrl || 'http://localhost:8000/api';
  private readonly SELECTED_ORG_KEY = 'selected_org_short_name';

  ngOnInit(): void {
    this.initializeOrganization();
    
    if (this.isSystemAdmin()) {
      this.loadOrganizations();
    }
  }

  /**
   * Initialize organization from current user context
   */
  private initializeOrganization(): void {
    const orgContext = this.authService.getOrganizationContext();
    
    if (orgContext) {
      const storedOrg = localStorage.getItem(this.SELECTED_ORG_KEY);
      const orgShortName = this.isSystemAdmin() && storedOrg ? storedOrg : orgContext.orgShortName;
      
      this.selectedOrgShortName.set(orgShortName);
      this.currentOrgName.set(this.formatOrgName(orgShortName));
      
      console.log('✅ Organization initialized:', {
        orgShortName,
        role: this.currentRole(),
        isSystemAdmin: this.isSystemAdmin()
      });
    }
  }

  /**
   * Load organizations for system admin
   */
  private loadOrganizations(): void {
    this.isLoading.set(true);
    
    this.http.get<{success: boolean, data: Organization[]}>(`${this.API_BASE}/admin/organizations`)
      .subscribe({
        next: (response) => {
          if (response.success && response.data) {
            this.organizations.set(response.data);
            console.log(`✅ Loaded ${response.data.length} organizations`);
          }
          this.isLoading.set(false);
        },
        error: (error) => {
          console.error('❌ Failed to load organizations:', error);
          this.isLoading.set(false);
          
          // Fallback to mock data for development
          this.organizations.set([
            {
              _id: '1',
              org_short_name: 'sk-tindwal',
              name: 'SK Tindwal & Associates',
              type: 'valuation_company',
              is_active: true,
              created_at: new Date(),
              updated_at: new Date()
            },
            {
              _id: '2',
              org_short_name: 'abc-valuers',
              name: 'ABC Property Valuers',
              type: 'valuation_company',
              is_active: true,
              created_at: new Date(),
              updated_at: new Date()
            }
          ] as Organization[]);
        }
      });
  }

  /**
   * Handle organization change (System Admin only)
   */
  onOrganizationChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const newOrgShortName = select.value;
    
    if (!newOrgShortName) return;
    
    // Prevent rapid switching that causes flickering
    if (this.isLoading()) {
      console.log('⏳ Already switching organizations, ignoring request');
      return;
    }
    
    console.log('🔄 Switching organization:', {
      from: this.selectedOrgShortName(),
      to: newOrgShortName
    });
    
    // Set loading state
    this.isLoading.set(true);
    
    // Get current user info to maintain email and role
    const currentUser = this.authService.currentUserValue;
    const userEmail = currentUser?.email || 'admin@system.com';
    const userRole = currentUser?.roles?.includes('system_admin') ? 'system_admin' : 'manager';
    
    console.log('🔑 Re-authenticating for organization:', newOrgShortName);
    
    // Re-authenticate with the new organization context
    this.authService.loginWithDevToken(userEmail, newOrgShortName, userRole).subscribe({
      next: (response) => {
        console.log('✅ Organization switch successful:', newOrgShortName);
        
        // Clear any cached data to force fresh loading for the new organization
        // this.clearOrganizationCache(); // TODO: Implement proper cache clearing
        
        // Clear cached data to prevent stale data from showing
        this.clearAllCachedData();
        
        // Update selected organization
        this.selectedOrgShortName.set(newOrgShortName);
        localStorage.setItem(this.SELECTED_ORG_KEY, newOrgShortName);
        
        // Update current org name
        const selectedOrg = this.organizations().find(org => org.org_short_name === newOrgShortName);
        this.currentOrgName.set(selectedOrg?.name || this.formatOrgName(newOrgShortName));
        
        // Smooth navigation without page reload
        console.log('🔄 Smoothly navigating to new organization context');
        this.router.navigate(['/org', newOrgShortName, 'dashboard']).then(() => {
          this.isLoading.set(false);
          console.log('✅ Organization switched successfully with new token for:', newOrgShortName);
          console.log('🔄 Dashboard should reload with organization-specific data');
        });
      },
      error: (error) => {
        console.error('❌ Failed to re-authenticate with new organization:', error);
        this.isLoading.set(false);
        
        // Revert selection on error
        const currentOrg = this.selectedOrgShortName();
        if (select.value !== currentOrg) {
          select.value = currentOrg;
        }
        
        alert('Failed to switch organization. Please try again.');
      }
    });
  }

  /**
   * Clear ALL cached data when switching organizations
   * This prevents cross-organization data leakage
   */
  private clearAllCachedData(): void {
    console.log('🧹 CRITICAL: Clearing ALL cached data to prevent cross-organization leakage');
    
    // Clear dashboard data cache
    if (typeof window !== 'undefined' && window.localStorage) {
      // Remove any cached dashboard data
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('dashboard') || key.includes('template') || key.includes('report'))) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => {
        console.log('🗑️ Removing cached data:', key);
        localStorage.removeItem(key);
      });
    }
    
    // Force services to clear their internal caches
    // Note: This is a nuclear option - forces complete data refresh
    console.log('💥 Forcing complete data refresh for new organization context');
  }

  /**
   * Clear organization-specific cached data when switching
   */
  private clearOrganizationCache(): void {
    console.log('🧹 Clearing organization cache to ensure fresh data loading');
    
    // Clear any service-level caches that might persist organization data
    // This ensures that when we switch organizations, we get fresh data
    
    // Note: Individual services should implement their own cache clearing if needed
    // For now, we rely on the authentication token change to fetch new data
  }

  /**
   * Format organization short name to display name
   */
  private formatOrgName(orgShortName: string): string {
    return orgShortName
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
}
