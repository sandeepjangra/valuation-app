/**
 * Organizations List Component
 * Displays all organizations for System Admin
 */

import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../../environments/environment';

interface Organization {
  _id: string;
  organization_id: string;
  name: string;
  status: string;
  contact_info?: {
    email?: string;
    phone?: string;
    address?: string;
  };
  subscription?: {
    plan: string;
    max_reports_per_month: number;
  };
  settings?: {
    subscription_plan: string;
    max_users: number;
    max_reports_per_month: number;
    max_storage_gb: number;
  };
  user_count: number;
  created_at: string;
}

@Component({
  selector: 'app-organizations-list',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="admin-container">
      <div class="header">
        <h1>🏢 Organization Management</h1>
        <button class="btn btn-primary" (click)="showCreateDialog()">
          ➕ Create Organization
        </button>
      </div>

      @if (loading()) {
        <div class="loading">
          <div class="spinner"></div>
          <p>Loading organizations...</p>
        </div>
      }

      @if (error()) {
        <div class="error-message">
          {{ error() }}
        </div>
      }

      @if (!loading() && organizations().length > 0) {
        <div class="organizations-grid">
          @for (org of organizations(); track org._id) {
            <div class="org-card">
              <div class="org-header">
                <h3>{{ org.name }}</h3>
                <span class="org-status" [class.active]="org.status === 'active'">
                  {{ org.status }}
                </span>
              </div>

              <div class="org-details">
                <div class="detail-row">
                  <span class="label">ID:</span>
                  <span class="value">{{ org.organization_id }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Plan:</span>
                  <span class="value">{{ formatPlan(org.settings?.subscription_plan) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Users:</span>
                  <span class="value">{{ org.user_count }} / {{ org.settings?.max_users || 25 }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Email:</span>
                  <span class="value">{{ org.contact_info?.email || 'N/A' }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Created:</span>
                  <span class="value">{{ formatDate(org.created_at) }}</span>
                </div>
              </div>

              <div class="org-actions">
                <button class="btn btn-primary" (click)="viewOrganization(org.organization_id)">
                  👁️ View Details
                </button>
                <button class="btn btn-secondary" (click)="manageUsers(org.organization_id)">
                  👥 Manage Users
                </button>
              </div>
            </div>
          }
        </div>
      }

      @if (!loading() && organizations().length === 0 && !error()) {
        <div class="empty-state">
          <p>No organizations found.</p>
          <button class="btn btn-primary" (click)="showCreateDialog()">
            Create First Organization
          </button>
        </div>
      }
    </div>

    <!-- Create Organization Dialog -->
    @if (showDialog()) {
      <div class="dialog-overlay" 
           (mousedown)="onOverlayMouseDown($event)" 
           (click)="onDialogOverlayClick($event)">
        <div class="dialog" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h2>Create New Organization</h2>
            <button class="close-btn" (click)="closeDialog()">✕</button>
          </div>

          <form (ngSubmit)="createOrganization()" class="dialog-content">
            <div class="form-group">
              <label>Organization Name *</label>
              <input type="text" [(ngModel)]="newOrg.name" name="name" required
                     placeholder="e.g., Acme Valuations Inc.">
            </div>

            <div class="form-group">
              <label>Contact Email *</label>
              <input type="email" [(ngModel)]="newOrg.contact_email" name="email" required
                     placeholder="contact@organization.com">
            </div>

            <div class="form-group">
              <label>Contact Phone</label>
              <input type="tel" [(ngModel)]="newOrg.contact_phone" name="phone"
                     placeholder="+1-555-0123">
            </div>

            <div class="form-group">
              <label>Address</label>
              <textarea [(ngModel)]="newOrg.address" name="address" rows="3"
                        placeholder="Street, City, State, ZIP"></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Max Users *</label>
                <input type="number" [(ngModel)]="newOrg.max_users" name="max_users" required min="1"
                       placeholder="25">
              </div>

              <div class="form-group">
                <label>Plan *</label>
                <select [(ngModel)]="newOrg.plan" name="plan" required>
                  <option value="basic">Basic (100 reports/month, 10GB)</option>
                  <option value="premium">Premium (500 reports/month, 50GB)</option>
                  <option value="enterprise">Enterprise (Unlimited)</option>
                </select>
              </div>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-secondary" (click)="closeDialog()">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="creating()">
                {{ creating() ? 'Creating...' : 'Create Organization' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    }
  `,
  styles: [`
    .admin-container {
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 32px;
    }

    .header h1 {
      margin: 0;
      font-size: 28px;
      color: #1f2937;
    }

    .organizations-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 24px;
    }

    .org-card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 24px;
      transition: all 0.2s;
    }

    .org-card:hover {
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }

    .org-header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 2px solid #f3f4f6;
    }

    .org-header h3 {
      margin: 0;
      font-size: 20px;
      color: #111827;
    }

    .org-status {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      background: #fef3c7;
      color: #92400e;
    }

    .org-status.active {
      background: #d1fae5;
      color: #065f46;
    }

    .org-details {
      margin-bottom: 20px;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #f3f4f6;
    }

    .detail-row:last-child {
      border-bottom: none;
    }

    .label {
      color: #6b7280;
      font-size: 14px;
      font-weight: 500;
    }

    .value {
      color: #111827;
      font-size: 14px;
    }

    .org-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .btn {
      padding: 10px 20px;
      border-radius: 8px;
      font-weight: 600;
      border: none;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 14px;
    }

    .btn-primary {
      background: #3b82f6;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #2563eb;
    }

    .btn-secondary {
      background: #f3f4f6;
      color: #374151;
    }

    .btn-secondary:hover {
      background: #e5e7eb;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .loading {
      text-align: center;
      padding: 60px 20px;
    }

    .spinner {
      width: 48px;
      height: 48px;
      border: 4px solid #e5e7eb;
      border-top-color: #3b82f6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 16px;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-message {
      background: #fee2e2;
      color: #991b1b;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 24px;
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #6b7280;
    }

    .dialog-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .dialog {
      background: white;
      border-radius: 12px;
      width: 90%;
      max-width: 600px;
      max-height: 90vh;
      overflow-y: auto;
      user-select: text;
      -webkit-user-select: text;
      -moz-user-select: text;
      -ms-user-select: text;
    }

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24px;
      border-bottom: 1px solid #e5e7eb;
    }

    .dialog-header h2 {
      margin: 0;
      font-size: 24px;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: #6b7280;
      padding: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .close-btn:hover {
      color: #111827;
    }

    .dialog-content {
      padding: 24px;
    }

    .form-group {
      margin-bottom: 20px;
    }

    .form-group label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
      color: #374151;
    }

    .form-group input,
    .form-group textarea,
    .form-group select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 14px;
    }

    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    .dialog-actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #e5e7eb;
    }
  `]
})
export class OrganizationsListComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly API_BASE = environment.apiUrl || 'http://localhost:8000/api';

  organizations = signal<Organization[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);
  showDialog = signal(false);
  creating = signal(false);
  
  // Track if user is currently selecting text to prevent dialog close
  private isSelectingText = false;
  private overlayMouseDownTarget: EventTarget | null = null;

  newOrg = {
    name: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    max_users: 25,
    plan: 'basic'
  };

  ngOnInit() {
    this.loadOrganizations();
  }

  loadOrganizations() {
    this.loading.set(true);
    this.error.set(null);

    this.http.get<any>(`${this.API_BASE}/admin/organizations`).subscribe({
      next: (response) => {
        if (response.success) {
          this.organizations.set(response.data);
        } else {
          console.error('Server returned success=false:', response);
          this.error.set(response.error || 'Failed to load organizations. Please try again.');
        }
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load organizations:', err);
        console.error('Error status:', err.status);
        console.error('Error message:', err.message);
        console.error('Error details:', err.error);
        
        let errorMessage = 'Failed to load organizations. Please try again.';
        
        if (err.status === 0) {
          errorMessage = 'Cannot connect to server. Please ensure the backend is running on port 8000.';
        } else if (err.status === 500) {
          errorMessage = `Server error: ${err.error?.error || 'Internal server error'}`;
        } else if (err.error?.detail) {
          errorMessage = err.error.detail;
        } else if (err.error?.error) {
          errorMessage = err.error.error;
        }
        
        this.error.set(errorMessage);
        this.loading.set(false);
      }
    });
  }

  showCreateDialog() {
    this.showDialog.set(true);
  }
  
  onOverlayMouseDown(event: MouseEvent) {
    // Track where the mousedown started
    const target = event.target as HTMLElement;
    
    // If mousedown is on overlay, track it
    if (target.classList.contains('dialog-overlay')) {
      this.overlayMouseDownTarget = event.target;
      this.isSelectingText = false;
    } else {
      // If mousedown is inside dialog, user might be selecting text
      this.overlayMouseDownTarget = null;
      this.isSelectingText = true;
    }
  }
  
  onDialogOverlayClick(event: MouseEvent) {
    // Don't close if user was selecting text
    if (this.isSelectingText) {
      this.isSelectingText = false;
      return;
    }
    
    // Only close if click is directly on the overlay and mousedown was also on overlay
    const target = event.target as HTMLElement;
    if (this.overlayMouseDownTarget && 
        target === this.overlayMouseDownTarget &&
        target.classList.contains('dialog-overlay')) {
      this.closeDialog();
    }
    this.overlayMouseDownTarget = null;
  }

  closeDialog() {
    this.showDialog.set(false);
    this.resetForm();
  }

  createOrganization() {
    this.creating.set(true);

    this.http.post<any>(`${this.API_BASE}/admin/organizations`, this.newOrg).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ Organization created:', response.data);
          this.loadOrganizations();
          this.closeDialog();
        }
        this.creating.set(false);
      },
      error: (err) => {
        console.error('Failed to create organization:', err);
        alert('Failed to create organization. Please try again.');
        this.creating.set(false);
      }
    });
  }

  viewOrganization(orgId: string) {
    this.router.navigate(['/admin/organizations', orgId]);
  }

  manageUsers(orgId: string) {
    this.router.navigate(['/admin/organizations', orgId, 'users']);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  formatPlan(plan: string | undefined): string {
    if (!plan) return 'N/A';
    
    const planMap: { [key: string]: string } = {
      'basic': 'Basic',
      'premium': 'Premium',
      'professional': 'Professional',
      'enterprise': 'Enterprise'
    };
    
    return planMap[plan] || plan;
  }

  private resetForm() {
    this.newOrg = {
      name: '',
      contact_email: '',
      contact_phone: '',
      address: '',
      max_users: 25,
      plan: 'basic'
    };
  }
}
