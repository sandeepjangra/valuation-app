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
  contact_info: {
    email: string;
    phone: string;
    address: string;
  };
  subscription: {
    plan: string;
    max_reports_per_month: number;
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
                  <span class="value">{{ org.subscription.plan }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Users:</span>
                  <span class="value">{{ org.user_count }} / {{ org.subscription.max_reports_per_month }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Email:</span>
                  <span class="value">{{ org.contact_info.email }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Created:</span>
                  <span class="value">{{ formatDate(org.created_at) }}</span>
                </div>
              </div>

              <div class="org-actions">
                <button class="btn btn-secondary" (click)="viewOrganization(org.organization_id)">
                  👁️ View Details
                </button>
                <button class="btn btn-secondary" (click)="manageUsers(org.organization_id)">
                  👥 Manage Users
                </button>
                <button class="btn btn-warning" (click)="toggleOrgStatus(org)">
                  {{ org.status === 'active' ? '⏸️ Deactivate' : '▶️ Activate' }}
                </button>
                <button class="btn btn-danger" (click)="confirmDelete(org)">
                  🗑️ Delete
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
      <div class="dialog-overlay" (click)="closeDialog()">
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
                  <option value="basic">Basic</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
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

    <!-- Delete Confirmation Dialog -->
    @if (deleteConfirmOrg()) {
      <div class="dialog-overlay" (click)="cancelDelete()">
        <div class="dialog delete-confirm-dialog" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h2>⚠️ Confirm Deletion</h2>
            <button class="close-btn" (click)="cancelDelete()">✕</button>
          </div>

          <div class="dialog-content">
            <div class="warning-box">
              <p><strong>WARNING: This action cannot be undone!</strong></p>
              <p>You are about to permanently delete:</p>
              <ul>
                <li><strong>Organization:</strong> {{ deleteConfirmOrg()?.name }}</li>
                <li><strong>Organization ID:</strong> {{ deleteConfirmOrg()?.organization_id }}</li>
                <li><strong>All user data</strong> ({{ deleteConfirmOrg()?.user_count }} users)</li>
                <li><strong>Entire database</strong> with all reports, templates, and files</li>
              </ul>
              <p class="danger-text">This will drop the entire database and cannot be recovered!</p>
            </div>

            <div class="form-group">
              <label>Type the organization name to confirm:</label>
              <input type="text" [(ngModel)]="deleteConfirmText" name="confirmText"
                     [placeholder]="deleteConfirmOrg()?.name || ''"
                     class="confirm-input">
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-secondary" (click)="cancelDelete()">
                Cancel
              </button>
              <button type="button" class="btn btn-danger" 
                      (click)="executeDelete()"
                      [disabled]="deleteConfirmText !== deleteConfirmOrg()?.name || deleting()">
                {{ deleting() ? 'Deleting...' : '🗑️ Permanently Delete' }}
              </button>
            </div>
          </div>
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

    .btn-warning {
      background: #fbbf24;
      color: #78350f;
      grid-column: span 2;
    }

    .btn-warning:hover {
      background: #f59e0b;
    }

    .btn-danger {
      background: #ef4444;
      color: white;
      grid-column: span 2;
    }

    .btn-danger:hover:not(:disabled) {
      background: #dc2626;
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

    .delete-confirm-dialog {
      max-width: 600px;
    }

    .warning-box {
      background: #fef2f2;
      border: 2px solid #fca5a5;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 20px;
    }

    .warning-box p {
      margin: 8px 0;
      color: #991b1b;
    }

    .warning-box ul {
      margin: 12px 0;
      padding-left: 20px;
      color: #991b1b;
    }

    .warning-box li {
      margin: 6px 0;
    }

    .danger-text {
      font-weight: 700;
      color: #7f1d1d;
      margin-top: 12px !important;
    }

    .confirm-input {
      width: 100%;
      padding: 10px 12px;
      border: 2px solid #d1d5db;
      border-radius: 8px;
      font-size: 14px;
    }

    .confirm-input:focus {
      outline: none;
      border-color: #ef4444;
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
  deleteConfirmOrg = signal<Organization | null>(null);
  deleteConfirmText = '';
  deleting = signal(false);

  newOrg = {
    name: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    max_users: 25,
    plan: 'professional'
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
        }
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load organizations:', err);
        this.error.set('Failed to load organizations. Please try again.');
        this.loading.set(false);
      }
    });
  }

  showCreateDialog() {
    this.showDialog.set(true);
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

  confirmDelete(org: Organization) {
    this.deleteConfirmOrg.set(org);
    this.deleteConfirmText = '';
  }

  cancelDelete() {
    this.deleteConfirmOrg.set(null);
    this.deleteConfirmText = '';
  }

  executeDelete() {
    const org = this.deleteConfirmOrg();
    if (!org) return;

    this.deleting.set(true);

    this.http.delete<any>(`${this.API_BASE}/admin/organizations/${org.organization_id}`).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ Organization deleted:', response);
          alert(`Organization "${org.name}" has been permanently deleted along with all its data.`);
          this.loadOrganizations();
          this.cancelDelete();
        }
        this.deleting.set(false);
      },
      error: (err) => {
        console.error('Failed to delete organization:', err);
        alert('Failed to delete organization. Please try again.');
        this.deleting.set(false);
      }
    });
  }

  toggleOrgStatus(org: Organization) {
    const newStatus = org.status === 'active' ? 'inactive' : 'active';
    const action = newStatus === 'active' ? 'activate' : 'deactivate';
    
    if (!confirm(`Are you sure you want to ${action} "${org.name}"?\n\nThis will ${newStatus === 'inactive' ? 'disable access for all users' : 'restore access for all users'}.`)) {
      return;
    }

    this.http.patch<any>(
      `${this.API_BASE}/admin/organizations/${org.organization_id}/status`,
      { status: newStatus }
    ).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ Organization status updated:', response);
          alert(`Organization "${org.name}" has been ${newStatus === 'active' ? 'activated' : 'deactivated'}.`);
          this.loadOrganizations();
        }
      },
      error: (err) => {
        console.error('Failed to update organization status:', err);
        alert('Failed to update organization status. Please try again.');
      }
    });
  }

  private resetForm() {
    this.newOrg = {
      name: '',
      contact_email: '',
      contact_phone: '',
      address: '',
      max_users: 25,
      plan: 'professional'
    };
  }
}
