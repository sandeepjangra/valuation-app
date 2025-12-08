/**
 * User Profile Component
 * Displays detailed user information and organization context
 */

import { Component, inject, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { User, Organization } from '../../models/organization.model';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="profile-container">
      <!-- Header Section -->
      <div class="profile-header">
        <div class="header-content">
          <button class="back-btn" (click)="goBack()">
            ← Back
          </button>
          <h1>User Profile</h1>
        </div>
      </div>

            <!-- Loading State -->
      @if (isLoading()) {
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p>Loading profile...</p>
        </div>
      }

      <!-- Error State -->
      @if (error()) {
        <div class="error-container">
          <div class="error-icon">⚠️</div>
          <h3>Unable to Load Profile</h3>
          <p>{{ error() }}</p>
          <button class="retry-button" (click)="loadProfile()">Retry</button>
        </div>
      }

      <!-- Profile Content -->
            <!-- Main Content -->
      @if (!isLoading() && !error()) {
        <div class="profile-content">
        
        <!-- User Information Card -->
        <div class="info-card">
          <div class="card-header">
            <div class="user-avatar">
              {{ getUserInitials() }}
            </div>
            <div class="user-basic-info">
              <h2>{{ currentUser()?.full_name }}</h2>
              <p class="user-email">{{ currentUser()?.email }}</p>
              <div class="user-roles">
                                @for (role of currentUser()?.roles; track role) {
                  <span class="role-badge" [class]="'role-' + role">
                    {{ role | titlecase }}
                  </span>
                }
              </div>
            </div>
          </div>
        </div>

        <!-- Organization Information -->
        <div class="info-card">
          <div class="card-title">
            <h3>🏢 Organization Details</h3>
          </div>
          <div class="card-content">
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Organization ID:</span>
                <span class="detail-value">{{ orgContext()?.organizationId }}</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">Organization Type:</span>
                <span class="detail-value">Valuation Company</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Account Information -->
        <div class="info-card">
          <div class="card-title">
            <h3>👤 Account Information</h3>
          </div>
          <div class="card-content">
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">User ID:</span>
                <span class="detail-value">{{ currentUser()?.user_id }}</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">Account Status:</span>
                <span class="detail-value status-active">
                  Active
                </span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">Member Since:</span>
                <span class="detail-value">Not available</span>
              </div>
              

            </div>
          </div>
        </div>

        <!-- Permissions & Access -->
        <div class="info-card">
          <div class="card-title">
            <h3>🔐 Permissions & Access</h3>
          </div>
          <div class="card-content">
            <div class="permissions-grid">
              <div class="permission-item">
                <span class="permission-label">System Administrator:</span>
                <span class="permission-value" [class]="orgContext()?.isSystemAdmin ? 'permission-granted' : 'permission-denied'">
                  {{ orgContext()?.isSystemAdmin ? '✅ Yes' : '❌ No' }}
                </span>
              </div>
              
              <div class="permission-item">
                <span class="permission-label">Manager Access:</span>
                <span class="permission-value" [class]="orgContext()?.isManager ? 'permission-granted' : 'permission-denied'">
                  {{ orgContext()?.isManager ? '✅ Yes' : '❌ No' }}
                </span>
              </div>
              
              <div class="permission-item">
                <span class="permission-label">Employee Access:</span>
                <span class="permission-value" [class]="orgContext()?.isEmployee ? 'permission-granted' : 'permission-denied'">
                  {{ orgContext()?.isEmployee ? '✅ Yes' : '❌ No' }}
                </span>
              </div>
            </div>
            
            <div class="access-note">
              <p><strong>Note:</strong> Your access level determines which features and data you can view and modify within the application.</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="profile-actions">
          <button class="btn btn-outline" (click)="goBack()">
            Back to Application
          </button>
          <button class="btn btn-danger" (click)="logout()">
            Logout from Account
          </button>
        </div>
      </div>
      }
    </div>
  `,
  styles: [`
    .profile-container {
      padding: 30px;
      max-width: 1000px;
      margin: 0 auto;
      background: linear-gradient(135deg, #faf9ff 0%, #f3f0ff 100%);
      min-height: 100vh;
    }

    .profile-header {
      margin-bottom: 30px;
    }

    .header-content {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .back-btn {
      background: #6c757d;
      color: white;
      border: none;
      padding: 10px 16px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s ease;
    }

    .back-btn:hover {
      background: #5a6268;
      transform: translateY(-1px);
    }

    .profile-header h1 {
      margin: 0;
      font-size: 2.5rem;
      font-weight: 700;
      color: #4a148c;
    }

    .loading-container, .error-container {
      text-align: center;
      padding: 60px 20px;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f4f6;
      border-top: 4px solid #9c27b0;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .error-message {
      background: #fee2e2;
      border-radius: 12px;
      padding: 24px;
      max-width: 400px;
      margin: 0 auto;
    }

    .error-message h3 {
      margin: 0 0 8px 0;
      color: #dc2626;
    }

    .error-message p {
      margin: 0 0 16px 0;
      color: #dc2626;
    }

    .profile-content {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .info-card {
      background: white;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 15px rgba(156, 39, 176, 0.1);
      border: 2px solid rgba(156, 39, 176, 0.1);
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 20px;
    }

    .user-avatar {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: linear-gradient(135deg, #9c27b0, #673ab7);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      font-weight: bold;
      box-shadow: 0 8px 25px rgba(156, 39, 176, 0.3);
    }

    .user-basic-info h2 {
      margin: 0 0 8px 0;
      font-size: 2rem;
      font-weight: 700;
      color: #4a148c;
    }

    .user-email {
      margin: 0 0 12px 0;
      color: #6b7280;
      font-size: 1.1rem;
    }

    .user-roles {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .role-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
    }

    .role-system_admin {
      background: #fef3c7;
      color: #92400e;
    }

    .role-manager {
      background: #dbeafe;
      color: #1e40af;
    }

    .role-employee {
      background: #d1fae5;
      color: #065f46;
    }

    .card-title {
      margin-bottom: 16px;
    }

    .card-title h3 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
      color: #4a148c;
    }

    .detail-grid, .permissions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 16px;
    }

    .detail-item, .permission-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f3f4f6;
    }

    .detail-label, .permission-label {
      font-weight: 600;
      color: #374151;
    }

    .detail-value, .permission-value {
      color: #1f2937;
      font-weight: 500;
    }

    .subscription-plan {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 0.875rem;
      font-weight: 600;
    }

    .plan-basic {
      background: #f3f4f6;
      color: #374151;
    }

    .plan-premium {
      background: #dbeafe;
      color: #1e40af;
    }

    .plan-enterprise {
      background: #fef3c7;
      color: #92400e;
    }

    .status-active {
      color: #059669;
      font-weight: 600;
    }

    .status-inactive {
      color: #dc2626;
      font-weight: 600;
    }

    .permission-granted {
      color: #059669;
      font-weight: 600;
    }

    .permission-denied {
      color: #dc2626;
      font-weight: 600;
    }

    .access-note {
      margin-top: 16px;
      padding: 16px;
      background: #f8fafc;
      border-radius: 8px;
      border-left: 4px solid #9c27b0;
    }

    .access-note p {
      margin: 0;
      color: #4b5563;
      font-size: 0.875rem;
    }

    .profile-actions {
      display: flex;
      gap: 16px;
      justify-content: center;
      margin-top: 20px;
    }

    .btn {
      padding: 12px 24px;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .btn-primary {
      background: #9c27b0;
      color: white;
      border: 2px solid #9c27b0;
    }

    .btn-primary:hover {
      background: #8e24aa;
      border-color: #8e24aa;
      transform: translateY(-1px);
    }

    .btn-outline {
      background: transparent;
      color: #9c27b0;
      border: 2px solid #9c27b0;
    }

    .btn-outline:hover {
      background: #9c27b0;
      color: white;
      transform: translateY(-1px);
    }

    .btn-danger {
      background: #dc2626;
      color: white;
      border: 2px solid #dc2626;
    }

    .btn-danger:hover {
      background: #b91c1c;
      border-color: #b91c1c;
      transform: translateY(-1px);
    }

    @media (max-width: 768px) {
      .profile-container {
        padding: 20px;
      }

      .card-header {
        flex-direction: column;
        text-align: center;
        gap: 16px;
      }

      .user-avatar {
        width: 60px;
        height: 60px;
        font-size: 1.5rem;
      }

      .user-basic-info h2 {
        font-size: 1.5rem;
      }

      .detail-grid, .permissions-grid {
        grid-template-columns: 1fr;
      }

      .detail-item, .permission-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
      }

      .profile-actions {
        flex-direction: column;
      }
    }
  `]
})
export class UserProfileComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly organizationService = inject(OrganizationService);
  private readonly router = inject(Router);

  // Component state
  readonly isLoading = computed(() => false); // Simple loading state for now
  readonly error = computed(() => null); // Simple error state for now

  // Data
  readonly organizationInfo = computed(() => null); // We'll keep this simple for now

  // Computed properties
  readonly currentUser = computed(() => this.authService.currentUser());
  readonly orgContext = computed(() => this.authService.getOrganizationContext());

  ngOnInit(): void {
    this.loadProfile();
  }

  /**
   * Load user profile data
   */
  loadProfile(): void {
    // Profile data is already available through auth service
    console.log('User profile loaded:', this.currentUser());
  }

  /**
   * Get user initials for avatar
   */
  getUserInitials(): string {
    const user = this.currentUser();
    if (user?.full_name) {
      const names = user.full_name.split(' ');
      if (names.length >= 2) {
        return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
      }
      return names[0].charAt(0).toUpperCase();
    }
    return user?.email?.charAt(0).toUpperCase() || 'U';
  }

  /**
   * Get role label
   */
  getRoleLabel(role: string): string {
    const labels: Record<string, string> = {
      'system_admin': 'System Admin',
      'manager': 'Manager',
      'employee': 'Employee'
    };
    return labels[role] || role;
  }

  /**
   * Get organization type label
   */
  getOrgTypeLabel(type?: string): string {
    const labels: Record<string, string> = {
      'valuation_company': 'Valuation Company',
      'system': 'System Organization',
      'enterprise': 'Enterprise'
    };
    return labels[type || ''] || type || 'Unknown';
  }

  /**
   * Get subscription plan label
   */
  getSubscriptionLabel(plan?: string): string {
    const labels: Record<string, string> = {
      'basic': 'Basic Plan',
      'premium': 'Premium Plan',
      'enterprise': 'Enterprise Plan'
    };
    return labels[plan || ''] || plan || 'Unknown';
  }

  /**
   * Format date for display
   */
  formatDate(date?: Date): string {
    if (!date) return 'Not available';
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  }

  /**
   * Go back to previous page
   */
  goBack(): void {
    this.router.navigate(['/dashboard']);
  }

  /**
   * Logout user
   */
  logout(): void {
    this.authService.logout().subscribe();
  }
}