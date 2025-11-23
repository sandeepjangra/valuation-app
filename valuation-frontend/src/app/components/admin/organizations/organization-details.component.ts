/**
 * Organization Details Component
 * Shows detailed view of a single organization with user management
 */

import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';
import { environment } from '../../../../environments/environment';

interface User {
  _id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface Organization {
  _id: string;
  organization_id: string;
  org_short_name: string;
  name: string;
  status: string;
  contact_info: {
    email?: string;
    phone?: string;
    address?: string;
  };
  settings: {
    subscription_plan: string;
    max_users: number;
    max_reports_per_month: number;
    max_storage_gb: number;
  };
  subscription: {
    plan: string;
    max_reports_per_month: number;
    storage_limit_gb: number;
  };
  user_count: number;
  users: User[];
  created_at: string;
}

@Component({
  selector: 'app-organization-details',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="admin-container">
      @if (loading()) {
        <div class="loading">
          <div class="spinner"></div>
          <p>Loading organization details...</p>
        </div>
      }

      @if (error()) {
        <div class="error-message">
          {{ error() }}
        </div>
      }

      @if (!loading() && organization()) {
        <div class="header-with-actions">
          <div class="header-left">
            <button class="btn btn-secondary btn-sm" (click)="goBack()">
              ← Back to Organizations
            </button>
            <h1>🏢 {{ organization()!.name }}</h1>
          </div>
          <div class="header-actions">
            <button class="btn btn-primary btn-sm" (click)="showEditDialog()">
              ✏️ Edit
            </button>
            <button class="btn btn-warning btn-sm" (click)="toggleOrgStatus()">
              {{ organization()!.status === 'active' ? '⏸️ Deactivate' : '▶️ Activate' }}
            </button>
            <button class="btn btn-danger btn-sm" (click)="confirmDelete()">
              🗑️ Delete
            </button>
          </div>
        </div>

        <div class="details-grid">
          <!-- Organization Information -->
          <div class="card">
            <div class="card-header">
              <h2>📋 Organization Information</h2>
              <span class="org-status" [class.active]="organization()!.status === 'active'">
                {{ organization()!.status }}
              </span>
            </div>
            <div class="card-content">
              <div class="detail-row">
                <span class="label">Organization ID:</span>
                <span class="value">{{ organization()!.organization_id }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Short Name:</span>
                <span class="value">{{ organization()!.org_short_name }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Plan:</span>
                <span class="value">{{ formatPlan(organization()!.settings?.subscription_plan) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Users:</span>
                <span class="value">{{ organization()!.user_count }} / {{ organization()!.settings?.max_users || 25 }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Created:</span>
                <span class="value">{{ formatDate(organization()!.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Contact Information -->
          <div class="card">
            <div class="card-header">
              <h2>📞 Contact Information</h2>
            </div>
            <div class="card-content">
              <div class="detail-row">
                <span class="label">Email:</span>
                <span class="value">{{ organization()!.contact_info?.email || 'N/A' }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Phone:</span>
                <span class="value">{{ organization()!.contact_info?.phone || 'N/A' }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Address:</span>
                <span class="value">{{ organization()!.contact_info?.address || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <!-- Subscription Details -->
          <div class="card">
            <div class="card-header">
              <h2>💳 Subscription Details</h2>
            </div>
            <div class="card-content">
              <div class="detail-row">
                <span class="label">Plan:</span>
                <span class="value">{{ formatPlan(organization()!.settings?.subscription_plan) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Reports/Month:</span>
                <span class="value">{{ organization()!.settings?.max_reports_per_month || 100 }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Storage:</span>
                <span class="value">{{ organization()!.settings?.max_storage_gb || 10 }} GB</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Users List -->
        <div class="card users-card">
          <div class="card-header">
            <h2>👥 Users ({{ organization()!.user_count }})</h2>
            <button class="btn btn-primary" (click)="showAddUserDialog()">
              ➕ Add User
            </button>
          </div>
          <div class="card-content">
            @if (organization()!.users.length > 0) {
              <div class="table-container">
                <table class="users-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Last Login</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (user of organization()!.users; track user._id) {
                      <tr>
                        <td>{{ user.full_name }}</td>
                        <td>{{ user.email }}</td>
                        <td>
                          <span class="role-badge" [class.manager]="user.role === 'manager'">
                            {{ user.role }}
                          </span>
                        </td>
                        <td>
                          <span class="status-badge" [class.active]="user.is_active">
                            {{ user.is_active ? 'Active' : 'Inactive' }}
                          </span>
                        </td>
                        <td>{{ user.last_login ? formatDate(user.last_login) : 'Never' }}</td>
                        <td>
                          <button class="btn btn-sm btn-secondary" (click)="editUser(user)">
                            ✏️ Edit
                          </button>
                        </td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            } @else {
              <div class="empty-state">
                <p>No users found in this organization.</p>
                <button class="btn btn-primary" (click)="showAddUserDialog()">
                  Add First User
                </button>
              </div>
            }
          </div>
        </div>
      }
    </div>

    <!-- Edit Organization Dialog -->
    @if (showEdit()) {
      <div class="dialog-overlay" 
           (mousedown)="onOverlayMouseDown($event)" 
           (click)="onEditDialogOverlayClick($event)">
        <div class="dialog" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h2>✏️ Edit Organization</h2>
            <button class="close-btn" (click)="closeEditDialog()">✕</button>
          </div>

          <form (ngSubmit)="saveOrganization()" class="dialog-content">
            <div class="form-group">
              <label>Organization Name *</label>
              <input type="text" [(ngModel)]="editForm.org_name" name="org_name" required
                     placeholder="e.g., SK Tindwal Properties">
              <small class="field-note">Display name for the organization</small>
            </div>

            <div class="form-group">
              <label>Organization Short Name (Cannot be changed)</label>
              <input type="text" [value]="organization()!.org_short_name" disabled
                     class="disabled-field">
              <small class="field-note">Used for database and URLs - cannot be modified</small>
            </div>

            <h3 class="section-title">Contact Information</h3>

            <div class="form-group">
              <label>Contact Email *</label>
              <input type="email" [(ngModel)]="editForm.contact_info.email" name="email" required
                     placeholder="contact@organization.com">
            </div>

            <div class="form-group">
              <label>Contact Phone</label>
              <input type="tel" [(ngModel)]="editForm.contact_info.phone" name="phone"
                     placeholder="+91-1234567890">
            </div>

            <div class="form-group">
              <label>Address</label>
              <textarea [(ngModel)]="editForm.contact_info.address" name="address" rows="3"
                        placeholder="Street, City, State, ZIP"></textarea>
            </div>

            <h3 class="section-title">Subscription Settings</h3>

            <div class="form-row">
              <div class="form-group">
                <label>Max Users *</label>
                <input type="number" [(ngModel)]="editForm.settings.max_users" name="max_users" 
                       required min="1" placeholder="50">
              </div>

              <div class="form-group">
                <label>Subscription Plan *</label>
                <select [(ngModel)]="editForm.settings.subscription_plan" name="plan" required>
                  <option value="basic">Basic</option>
                  <option value="premium">Premium</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Max Reports/Month *</label>
                <input type="number" [(ngModel)]="editForm.settings.max_reports_per_month" 
                       name="max_reports" required min="1" placeholder="500">
              </div>

              <div class="form-group">
                <label>Max Storage (GB) *</label>
                <input type="number" [(ngModel)]="editForm.settings.max_storage_gb" 
                       name="max_storage" required min="1" placeholder="50">
              </div>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-secondary" (click)="closeEditDialog()">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="saving()">
                {{ saving() ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- Add User Dialog -->
    @if (showUserDialog()) {
      <div class="dialog-overlay" 
           (mousedown)="onOverlayMouseDown($event)" 
           (click)="onUserDialogOverlayClick($event)">
        <div class="dialog" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h2>➕ Add New User</h2>
            <button class="close-btn" (click)="closeUserDialog()">✕</button>
          </div>

          <form (ngSubmit)="addUser()" class="dialog-content">
            <div class="form-group">
              <label>Full Name *</label>
              <input type="text" [(ngModel)]="newUser.full_name" name="full_name" required
                     placeholder="John Doe">
            </div>

            <div class="form-group">
              <label>Email *</label>
              <input type="email" [(ngModel)]="newUser.email" name="email" required
                     placeholder="john@example.com">
            </div>

            <div class="form-group">
              <label>Password *</label>
              <input type="password" [(ngModel)]="newUser.password" name="password" required
                     placeholder="Enter secure password" minlength="8">
            </div>

            <div class="form-group">
              <label>Phone</label>
              <input type="tel" [(ngModel)]="newUser.phone" name="phone"
                     placeholder="+1-555-0123">
            </div>

            <div class="form-group">
              <label>Role *</label>
              <select [(ngModel)]="newUser.role" name="role" required>
                <option value="employee">Employee</option>
                <option value="manager">Manager</option>
              </select>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-secondary" (click)="closeUserDialog()">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="addingUser()">
                {{ addingUser() ? 'Adding...' : 'Add User' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- Delete Confirmation Dialog -->
    @if (showDeleteConfirm()) {
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
                <li><strong>Organization:</strong> {{ organization()!.name }}</li>
                <li><strong>Database:</strong> {{ organization()!.org_short_name }}</li>
                <li><strong>All user data</strong> ({{ organization()!.user_count }} users)</li>
                <li><strong>All reports, templates, and files</strong></li>
              </ul>
              <p class="danger-text">This will drop the entire database and cannot be recovered!</p>
            </div>

            <div class="form-group">
              <label>Type the organization name to confirm:</label>
              <input type="text" [(ngModel)]="deleteConfirmText" name="confirmText"
                     [placeholder]="organization()!.name"
                     class="confirm-input">
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-secondary" (click)="cancelDelete()">
                Cancel
              </button>
              <button type="button" class="btn btn-danger" 
                      (click)="executeDelete()"
                      [disabled]="deleteConfirmText !== organization()!.name || deleting()">
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
      margin-bottom: 32px;
    }

    .header-with-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 32px;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }

    .header h1 {
      margin: 16px 0 0 0;
      font-size: 32px;
      color: #1f2937;
    }

    .details-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }

    .card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      overflow: hidden;
    }

    .card-header {
      padding: 20px 24px;
      background: #f9fafb;
      border-bottom: 1px solid #e5e7eb;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .card-header h2 {
      margin: 0;
      font-size: 18px;
      color: #111827;
      font-weight: 600;
    }

    .card-content {
      padding: 24px;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
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
      font-weight: 600;
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

    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 12px;
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

    .btn-block {
      width: 100%;
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
    }

    .btn-warning:hover {
      background: #f59e0b;
    }

    .btn-danger {
      background: #ef4444;
      color: white;
    }

    .btn-danger:hover:not(:disabled) {
      background: #dc2626;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-sm {
      padding: 6px 12px;
      font-size: 13px;
    }

    .users-card {
      grid-column: 1 / -1;
    }

    .table-container {
      overflow-x: auto;
    }

    .users-table {
      width: 100%;
      border-collapse: collapse;
    }

    .users-table th {
      text-align: left;
      padding: 12px;
      background: #f9fafb;
      color: #6b7280;
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      border-bottom: 2px solid #e5e7eb;
    }

    .users-table td {
      padding: 12px;
      border-bottom: 1px solid #f3f4f6;
      color: #374151;
    }

    .users-table tr:hover {
      background: #f9fafb;
    }

    .role-badge {
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      background: #dbeafe;
      color: #1e40af;
    }

    .role-badge.manager {
      background: #fef3c7;
      color: #92400e;
    }

    .status-badge {
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      background: #fee2e2;
      color: #991b1b;
    }

    .status-badge.active {
      background: #d1fae5;
      color: #065f46;
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
      padding: 40px 20px;
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
      font-size: 20px;
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
    .form-group select,
    .form-group textarea {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 14px;
      font-family: inherit;
    }

    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .disabled-field {
      background-color: #f3f4f6;
      cursor: not-allowed;
      color: #6b7280;
    }

    .field-note {
      display: block;
      margin-top: 4px;
      font-size: 12px;
      color: #6b7280;
    }

    .section-title {
      margin: 24px 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: #374151;
      border-bottom: 1px solid #e5e7eb;
      padding-bottom: 8px;
    }

    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    @media (max-width: 768px) {
      .form-row {
        grid-template-columns: 1fr;
      }
    }

    .dialog-actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #e5e7eb;
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
export class OrganizationDetailsComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly API_BASE = environment.apiUrl || 'http://localhost:8000/api';

  organization = signal<Organization | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);
  showUserDialog = signal(false);
  showEdit = signal(false);
  saving = signal(false);
  addingUser = signal(false);
  showDeleteConfirm = signal(false);
  deleteConfirmText = '';
  deleting = signal(false);
  
  // Track if user is currently selecting text to prevent dialog close
  private isSelectingText = false;
  private overlayMouseDownTarget: EventTarget | null = null;

  newUser = {
    full_name: '',
    email: '',
    password: '',
    phone: '',
    role: 'employee'
  };

  editForm = {
    org_name: '',
    contact_info: {
      email: '',
      phone: '',
      address: ''
    },
    settings: {
      subscription_plan: 'basic',
      max_users: 10,
      max_reports_per_month: 100,
      max_storage_gb: 10
    }
  };

  ngOnInit() {
    const orgId = this.route.snapshot.paramMap.get('orgId');
    if (orgId) {
      this.loadOrganization(orgId);
    }
  }

  loadOrganization(orgId: string) {
    this.loading.set(true);
    this.error.set(null);

    this.http.get<any>(`${this.API_BASE}/admin/organizations/${orgId}`).subscribe({
      next: (response) => {
        if (response.success) {
          this.organization.set(response.data);
        }
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load organization:', err);
        this.error.set('Failed to load organization details. Please try again.');
        this.loading.set(false);
      }
    });
  }

  showAddUserDialog() {
    this.showUserDialog.set(true);
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
  
  onUserDialogOverlayClick(event: MouseEvent) {
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
      this.closeUserDialog();
    }
    this.overlayMouseDownTarget = null;
  }

  closeUserDialog() {
    this.showUserDialog.set(false);
    this.resetUserForm();
  }

  addUser() {
    const org = this.organization();
    if (!org) return;

    this.addingUser.set(true);

    this.http.post<any>(
      `${this.API_BASE}/admin/organizations/${org.organization_id}/users`,
      this.newUser
    ).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ User added:', response.data);
          alert(`User "${this.newUser.email}" has been added successfully.`);
          this.closeUserDialog();
          this.loadOrganization(org.organization_id);
        }
        this.addingUser.set(false);
      },
      error: (err) => {
        console.error('Failed to add user:', err);
        const errorMessage = err.error?.detail || err.error?.error || 'Failed to add user. Please try again.';
        alert(errorMessage);
        this.addingUser.set(false);
      }
    });
  }

  showEditDialog() {
    const org = this.organization();
    if (!org) return;

    // Pre-populate form with current values
    this.editForm = {
      org_name: org.name,
      contact_info: {
        email: org.contact_info?.email || '',
        phone: org.contact_info?.phone || '',
        address: org.contact_info?.address || ''
      },
      settings: {
        subscription_plan: org.settings?.subscription_plan || 'basic',
        max_users: org.settings?.max_users || 10,
        max_reports_per_month: org.settings?.max_reports_per_month || 100,
        max_storage_gb: org.settings?.max_storage_gb || 10
      }
    };

    this.showEdit.set(true);
  }

  closeEditDialog() {
    this.showEdit.set(false);
  }

  onEditDialogOverlayClick(event: MouseEvent) {
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
      this.closeEditDialog();
    }
    this.overlayMouseDownTarget = null;
  }

  saveOrganization() {
    const org = this.organization();
    if (!org) return;

    this.saving.set(true);

    // Prepare update payload
    const updatePayload = {
      org_name: this.editForm.org_name,
      contact_info: this.editForm.contact_info,
      settings: this.editForm.settings
    };

    this.http.patch<any>(
      `${this.API_BASE}/admin/organizations/${org.organization_id}`,
      updatePayload
    ).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ Organization updated:', response.data);
          const changesCount = response.changes_applied?.length || 0;
          alert(`Organization updated successfully!\n${changesCount} field(s) changed.`);
          this.closeEditDialog();
          this.loadOrganization(org.organization_id);
        }
        this.saving.set(false);
      },
      error: (err) => {
        console.error('Failed to update organization:', err);
        const errorMessage = err.error?.detail || err.error?.error || 'Failed to update organization. Please try again.';
        alert(errorMessage);
        this.saving.set(false);
      }
    });
  }

  editUser(user: User) {
    alert('Edit user functionality coming soon!');
  }

  toggleOrgStatus() {
    const org = this.organization();
    if (!org) return;

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
          this.loadOrganization(org.organization_id);
        }
      },
      error: (err) => {
        console.error('Failed to update organization status:', err);
        alert('Failed to update organization status. Please try again.');
      }
    });
  }

  confirmDelete() {
    this.showDeleteConfirm.set(true);
    this.deleteConfirmText = '';
  }

  cancelDelete() {
    this.showDeleteConfirm.set(false);
    this.deleteConfirmText = '';
  }

  executeDelete() {
    const org = this.organization();
    if (!org) return;

    this.deleting.set(true);

    this.http.delete<any>(`${this.API_BASE}/admin/organizations/${org.organization_id}`).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ Organization deleted:', response);
          alert(`Organization "${org.name}" has been permanently deleted along with all its data.`);
          this.router.navigate(['/admin/organizations']);
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

  goBack() {
    this.router.navigate(['/admin/organizations']);
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

  private resetUserForm() {
    this.newUser = {
      full_name: '',
      email: '',
      password: '',
      phone: '',
      role: 'employee'
    };
  }
}
